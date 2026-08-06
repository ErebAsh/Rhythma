import firebase_admin
from firebase_admin import firestore, credentials
import os
import json
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from google.api_core.exceptions import FailedPrecondition  # for missing index detection

# `upstream_error` logs the real Firestore exception (with traceback and the
# current request id) and returns a safe error to raise. It replaces the
# `detail=f"...: {str(e)}"` pattern that used to interpolate raw Google API
# exceptions — project ids, collection paths, index-creation URLs — straight
# into a response body the client renders. See core/errors.py and issue #268.
from core.errors import upstream_error

# The one definition of "are these two addresses the same person?". Applied
# in this module, not only at the routes, so a lookup cannot be performed
# with a form of the address the write path would never have stored (#380).
from core.email_identity import normalize_email

# ─── Mock Firestore Client for Local Development ──────────────────────────
class MockDocumentReference:
    def __init__(self, doc_id, data, collection):
        self.id = doc_id
        self.data = data
        self.collection = collection
        self.exists = data is not None

    def get(self):
        return self

    def to_dict(self):
        return self.data.copy() if self.data is not None else None

    def update(self, update_data):
        if self.data:
            self.data.update(update_data)
            self.collection.store[self.id] = self.data
            
    def set(self, document_data):
        self.data = document_data.copy()
        self.collection.store[self.id] = self.data
        self.exists = True

    def set(self, set_data):
        self.collection.store[self.id] = set_data
        self.data = set_data
        self.exists = True

    def delete(self):
        if self.id in self.collection.store:
            del self.collection.store[self.id]
        self.data = None
        self.exists = False

def _mock_order_key(value):
    """Sort key for ``order_by`` in the mock query.

    ``start_date`` (and anything else date-like) can legitimately be stored
    as a bare ``date`` or as a ``datetime``; Firestore treats both as the
    same point-in-time type, so a query ordering on such a field must
    interleave them by actual value, not crash. Python's default sort
    raises ``TypeError`` comparing ``date`` and ``datetime`` directly, so
    the mock normalizes them to a common type — mirroring the sort key the
    old Python-side fallback in ``get_logs_for_user`` used before the
    composite-index query (issue #129).
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
    return value


#: Comparison operators the mock query understands, matching the subset of
#: Firestore's operators this codebase actually uses.
_MOCK_OPERATORS = {
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    ">": lambda left, right: left is not None and left > right,
    ">=": lambda left, right: left is not None and left >= right,
    "<": lambda left, right: left is not None and left < right,
    "<=": lambda left, right: left is not None and left <= right,
}


class MockQuery:
    def __init__(self, documents):
        # documents is a list of MockDocumentReference
        self._documents = documents
        self._order_by_field = None
        self._order_by_direction = None
        self._limit_count = None
        self._offset_count = 0

    def limit(self, count):
        self._limit_count = count
        return self

    def offset(self, count):
        """Skip the first ``count`` results, as Firestore's offset does."""
        self._offset_count = count
        return self

    def order_by(self, field, direction=None):
        self._order_by_field = field
        self._order_by_direction = direction or firestore.Query.ASCENDING
        return self

    def where(self, field, op, value):
        """Narrow an existing query further.

        Only the collection had a `where` before, so a second filter — a
        date range on top of the `user_id` match, say — had nowhere to go
        and would have silently returned an unfiltered query.
        """
        compare = _MOCK_OPERATORS.get(op)
        if compare is None:
            raise NotImplementedError(f"MockQuery does not support the {op!r} operator")

        filtered = [doc for doc in self._documents if compare(doc.data.get(field), value)]
        narrowed = MockQuery(filtered)
        narrowed._order_by_field = self._order_by_field
        narrowed._order_by_direction = self._order_by_direction
        narrowed._limit_count = self._limit_count
        narrowed._offset_count = self._offset_count
        return narrowed

    def stream(self):
        # Start with the filtered documents
        docs = self._documents[:]

        # Apply sorting if requested
        if self._order_by_field:
            reverse = (self._order_by_direction == firestore.Query.DESCENDING)
            docs.sort(
                key=lambda doc: _mock_order_key(doc.data.get(self._order_by_field)),
                reverse=reverse
            )

        # Offset before limit, matching Firestore: `.offset(10).limit(5)`
        # returns results 11-15, not the first five of everything after 10.
        if self._offset_count:
            docs = docs[self._offset_count:]

        # Apply limit if requested
        if self._limit_count is not None:
            docs = docs[:self._limit_count]

        for doc in docs:
            yield doc

class MockCollectionReference:
    def __init__(self, name, db):
        self.name = name
        self.db = db
        if name not in db._collections:
            db._collections[name] = {}
        self.store = db._collections[name]

    def add(self, document_data):
        # Per-collection auto-ID counter.
        #
        # Previously this counter was a class-level attribute
        # (`MockCollectionReference._next_id`), which meant every mock
        # collection — `users`, `cycle_logs`, `conversations`, etc. —
        # drew IDs from one shared incrementing sequence, so creating a
        # user then a cycle log produced `mock-doc-id-1` and
        # `mock-doc-id-2` instead of `mock-doc-id-1` in each collection.
        #
        # The counter cannot live on the instance either, because
        # `MockFirestoreClient.collection(name)` builds a *fresh*
        # `MockCollectionReference` on every call — an instance-level
        # counter would reset to 1 each time and collide immediately.
        #
        # Persisting it on the shared `db._counters` dict, keyed by
        # collection name, gives each collection its own independent
        # sequence that survives across `db.collection(name)` calls —
        # matching how real Firestore auto-IDs are namespaced
        # per-collection.
        next_id = self.db._counters.get(self.name, 0) + 1
        self.db._counters[self.name] = next_id
        doc_id = f"mock-doc-id-{next_id}"
        self.store[doc_id] = document_data
        return (None, MockDocumentReference(doc_id, document_data, self))

    def document(self, doc_id):
        data = self.store.get(doc_id)
        return MockDocumentReference(doc_id, data, self)

    def where(self, field, op, value):
        compare = _MOCK_OPERATORS.get(op)
        if compare is None:
            raise NotImplementedError(
                f"MockCollectionReference does not support the {op!r} operator"
            )

        filtered = []
        for doc_id, data in self.store.items():
            if compare(data.get(field), value):
                filtered.append(MockDocumentReference(doc_id, data, self))
        return MockQuery(filtered)

    # These are not called directly on collection; they are chained after where
    def order_by(self, field, direction=None):
        return self

    def limit(self, count):
        return self

class MockFirestoreClient:
    def __init__(self):
        self._collections = {}
        # Per-collection auto-ID counters for MockCollectionReference.add().
        # Keyed by collection name so each collection has its own
        # independent sequence (see MockCollectionReference.add).
        self._counters = {}

    def collection(self, name):
        return MockCollectionReference(name, self)

# ─── Initialize Firebase (only once) ──────────────────────────────────────
db = None

def initialize_firebase():
    global db
    if firebase_admin._apps:
        db = firestore.client()
        return

    # Option 1: JSON string from environment
    cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        return

    # Option 2: Path to JSON file
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        return

    # Fallback to in-memory Firestore mock
    import sys
    print("WARNING: Firebase credentials not found. Falling back to an in-memory mock Firestore database.", file=sys.stderr)
    db = MockFirestoreClient()

initialize_firebase()


class UserService:
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> str:
        """Create a new user document in Firestore.

        The email is canonicalised here rather than only at the routes.
        Three call sites create users today — ``/auth/register``,
        ``/provider/register`` and the Firebase phone flow — and before
        #380 only one of them normalised, which is how the same person
        could hold two accounts differing by a capital letter. Doing it at
        the single write path means a fourth call site added later cannot
        reintroduce that.
        """
        try:
            now = datetime.now(timezone.utc)
            if user_data.get("email") is not None:
                user_data["email"] = normalize_email(user_data["email"])
            user_data["created_at"] = now
            user_data["updated_at"] = now
            doc_ref = db.collection("users").add(user_data)
            return doc_ref[1].id
        except Exception as e:
            raise upstream_error("Creating your account", e)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by username."""
        try:
            users = db.collection("users").where("username", "==", username).limit(1).stream()
            for user in users:
                data = user.to_dict()
                data["id"] = user.id
                return data
            return None
        except Exception as e:
            raise upstream_error("Loading your profile", e)

    @staticmethod
    def _first_user_where(field: str, value: Any) -> Optional[Dict[str, Any]]:
        """The first user matching one equality filter, or ``None``."""
        for user in db.collection("users").where(field, "==", value).limit(1).stream():
            data = user.to_dict()
            data["id"] = user.id
            return data
        return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by email, regardless of how it was capitalised.

        Two queries, not one, and the second only runs on a miss.

        The canonical form is tried first: everything written since #380
        is stored lower-cased, so this is the single query that answers
        virtually every call. The fallback exists for documents created
        *before* that — ``Sana@Example.com`` is sitting in ``users``
        exactly as it was typed, and a query for the lower-cased form
        will never find it. Firestore's ``==`` is byte-exact and it has no
        case-insensitive operator, so the alternative to a second query is
        an offline backfill that must complete before the fix can ship.

        The cost is one extra read on a miss — which, for a login, is
        already the slow path — and it disappears on its own as accounts
        are re-created or a backfill is run. It is deliberately *not* a
        collection scan: only the exact string the caller supplied is
        tried, so a legacy row is found when the user types the address
        the way she originally did, and nothing here degrades with the
        size of the user table.
        """
        try:
            normalized = normalize_email(email)
            user = UserService._first_user_where("email", normalized)
            if user is not None:
                return user

            raw = (email or "").strip()
            if raw and raw != normalized:
                return UserService._first_user_where("email", raw)
            return None
        except Exception as e:
            raise upstream_error("Loading your profile", e)

    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by phone number."""
        try:
            users = db.collection("users").where("phone", "==", phone).limit(1).stream()
            for user in users:
                data = user.to_dict()
                data["id"] = user.id
                return data
            return None
        except Exception as e:
            raise upstream_error("Loading your profile", e)

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by Firestore document ID."""
        try:
            doc = db.collection("users").document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception as e:
            raise upstream_error("Loading your profile", e)

    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a user document and set updated_at.

        An ``email`` in the payload goes through the same canonicalisation
        ``create_user`` applies, so a profile edit cannot put a row back
        into the mixed-case state the lookup fallback above exists to
        cope with.
        """
        try:
            if update_data.get("email") is not None:
                update_data["email"] = normalize_email(update_data["email"])
            update_data["updated_at"] = datetime.now(timezone.utc)
            doc_ref = db.collection("users").document(user_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            raise upstream_error("Saving your profile", e)

    @staticmethod
    def delete_user(user_id: str) -> Dict[str, int]:
        """Delete everything stored for a user. Returns per-collection counts.

        Delegates to ``DataPrivacyService.purge_user_data()`` rather than
        implementing the cascade here. This method used to do it inline and
        covered only ``users``, ``cycle_logs`` and Firebase Auth — it never
        touched ``conversations`` (the assistant chat transcript, one
        document keyed by ``user_id``) or the ``rate_limits`` documents
        keyed ``sms:{user_id}``. So a "successfully deleted" account left
        the user's health conversation in Firestore indefinitely, keyed by
        an id no longer reachable through the app.

        Keeping exactly one implementation of the cascade is what stops
        that class of omission from recurring: a new collection is
        registered once, in ``USER_DATA_COLLECTIONS``, and both deletion
        and the data-summary inventory pick it up.

        The import is local to avoid an import cycle — the privacy service
        imports this module for ``UserService`` and ``db``.
        """
        try:
            from services.data_privacy_service import purge_user_data

            return purge_user_data(user_id)
        except Exception as e:
            raise upstream_error("Deleting your account", e)


class CycleService:
    """Persists and retrieves per-user cycle logs in Firestore."""

    @staticmethod
    def create_log(user_id: str, log_data: Dict[str, Any]) -> str:
        """Create a new cycle log document for a user, always as a new
        document (no day-based upsert).

        Not currently called by `POST /cycle/log` — that endpoint now uses
        `upsert_log` so repeated logs on the same day merge into one
        document instead of creating duplicates. Kept here in case a
        future feature genuinely wants multiple entries per day (e.g. an
        explicit "add another entry" action) rather than day-level upsert
        semantics.
        """
        try:
            data = dict(log_data)
            # Firestore's client stores Python `date` values fine, but to
            # keep this consistent and avoid surprises with the query below,
            # normalize any bare `date` values to UTC `datetime`s.
            from datetime import date as date_type
            for key, value in list(data.items()):
                if isinstance(value, date_type) and not isinstance(value, datetime):
                    data[key] = datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)

            data["user_id"] = user_id
            data["created_at"] = datetime.now(timezone.utc)
            doc_ref = db.collection("cycle_logs").add(data)
            return doc_ref[1].id
        except Exception as e:
            raise upstream_error("Saving your cycle log", e)

    @staticmethod
    def _as_day_start(value) -> datetime:
        """Normalize a date to the UTC midnight `upsert_log` stores."""
        if isinstance(value, datetime):
            return value
        return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)

    @staticmethod
    def get_logs_page(
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        start_date=None,
        end_date=None,
    ) -> tuple:
        """One page of a user's logs, newest first, plus whether more exist.

        Returns ``(entries, has_more)``.

        ``has_more`` comes from asking Firestore for ``limit + 1`` documents
        and checking whether the extra one arrived, rather than from a
        separate count query. A count is a second round trip that grows
        with the collection, and "is there another page" is the only thing
        a client actually needs to render a Next button. The cost of the
        approach is one extra document read per page — flat, and cheaper
        than the count at any history size.

        Both date bounds are inclusive and are normalized to the UTC
        midnight `upsert_log` writes, so `start_date == end_date` returns
        that one day rather than nothing.

        Requires the same composite index on ``(user_id, start_date desc)``
        the unpaginated query needed; a date filter on the field already
        being ordered adds no further index requirement.
        """
        try:
            query = db.collection("cycle_logs").where("user_id", "==", user_id)

            if start_date is not None:
                query = query.where(
                    "start_date", ">=", CycleService._as_day_start(start_date)
                )
            if end_date is not None:
                query = query.where(
                    "start_date", "<=", CycleService._as_day_start(end_date)
                )

            query = query.order_by(
                "start_date", direction=firestore.Query.DESCENDING
            )

            if offset:
                query = query.offset(offset)

            # One more than asked for: its presence is the "has more" answer.
            query = query.limit(limit + 1)

            results = []
            for doc in query.stream():
                data = doc.to_dict()
                data["id"] = doc.id
                results.append(data)

            has_more = len(results) > limit
            return results[:limit], has_more
        except FailedPrecondition as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise upstream_error("Loading your cycle history", e)

    @staticmethod
    def get_logs_for_user(user_id: str, limit: int = 10) -> list:
        """Return a user's cycle logs, most recent (by start_date) first.

        Uses Firestore's native sorting and limiting to fetch only the
        required number of documents. This requires a composite index on
        `(user_id, start_date desc)` for performance.

        If the index is missing, Firestore raises a FailedPrecondition
        exception with a direct link to create it. That error is preserved
        in the response (status 503) so the admin can use the link directly.

        Kept as the plain "most recent N" call used by the dashboard,
        predictions, insights and scoring, none of which page. Anything
        that needs a window rather than a prefix should use
        :meth:`get_logs_page`.
        """
        try:
            query = (
                db.collection("cycle_logs")
                .where("user_id", "==", user_id)
                .order_by("start_date", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                results.append(data)
            return results
        except FailedPrecondition as e:
            # Missing composite index – treat as a configuration issue
            # and preserve the original error message (includes the link)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        except Exception as e:
            # Other Firestore errors
            raise upstream_error("Loading your cycle history", e)

    @staticmethod
    def _log_doc_id(user_id: str, log_date: date) -> str:
        return f"{user_id}_{log_date.isoformat()}"

    @staticmethod
    def upsert_log(user_id: str, log_date: date, fields: Dict[str, Any]) -> str:
        """Create or update *that day's* cycle log with O(1) lookup.

        Uses a deterministic document ID (`{user_id}_{YYYY-MM-DD}`) so
        upsert is a direct get/update-or-set — no full-collection scan.

        Backs the single `POST /cycle/log` endpoint for both the Home
        screen's quick-log tiles (a partial `fields` dict — just the one
        thing being tapped, e.g. `{"flow_intensity": "light"}`) and the
        Cycle screen's "Save" button (a full `fields` dict with everything
        selected for that day).
        """
        try:
            doc_id = CycleService._log_doc_id(user_id, log_date)
            doc_ref = db.collection("cycle_logs").document(doc_id)
            existing = doc_ref.get()

            day_start = datetime.combine(log_date, datetime.min.time(), tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            update_fields = dict(fields)

            for key, value in list(update_fields.items()):
                if isinstance(value, date) and not isinstance(value, datetime):
                    update_fields[key] = datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)

            if existing.exists:
                update_fields["updated_at"] = now
                doc_ref.update(update_fields)
                return doc_id

            new_data = {**update_fields, "user_id": user_id, "start_date": day_start, "created_at": now}
            doc_ref.set(new_data)
            return doc_id
        except Exception as e:
            raise upstream_error("Saving your cycle log", e)

    @staticmethod
    def get_log(user_id: str, log_id: str) -> Dict[str, Any]:
        """One log by id, ownership checked (issue #347).

        Added so a partial update can be validated against the values
        already stored — `PUT /cycle/{log_id}` carries an `end_date` but no
        `start_date`, and "does this end date come before the start date?"
        cannot be answered from the payload alone.

        Raises the same 404/403 as :meth:`update_log` and :meth:`delete_log`
        rather than returning ``None``, so a caller cannot accidentally
        treat "not yours" as "not found" or, worse, as "no constraint to
        check".
        """
        try:
            doc = db.collection("cycle_logs").document(log_id).get()

            if not doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cycle log not found"
                )

            data = doc.to_dict() or {}
            if data.get("user_id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this log"
                )

            data["id"] = doc.id
            return data
        except HTTPException:
            raise
        except Exception as e:
            raise upstream_error("Loading your cycle log", e)

    @staticmethod
    def update_log(user_id: str, log_id: str, fields: Dict[str, Any]) -> str:
        """Update a specific cycle log by ID."""
        try:
            doc_ref = db.collection("cycle_logs").document(log_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cycle log not found"
                )
                
            if doc.to_dict().get("user_id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this log"
                )
                
            update_fields = dict(fields)
            for key, value in list(update_fields.items()):
                if isinstance(value, date) and not isinstance(value, datetime):
                    update_fields[key] = datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
            
            update_fields["updated_at"] = datetime.now(timezone.utc)
            doc_ref.update(update_fields)
            return log_id
        except HTTPException:
            raise
        except Exception as e:
            raise upstream_error("Updating your cycle log", e)

    @staticmethod
    def delete_log(user_id: str, log_id: str) -> None:
        """Delete a specific cycle log by ID."""
        try:
            doc_ref = db.collection("cycle_logs").document(log_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cycle log not found"
                )
                
            if doc.to_dict().get("user_id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this log"
                )
                
            doc_ref.delete()
        except HTTPException:
            raise
        except Exception as e:
            raise upstream_error("Deleting your cycle log", e)


# ─── Maximum number of messages kept per conversation ────────────────────
MAX_CONVERSATION_MESSAGES = 50


class AssistantConversationService:
    """Persists assistant chat messages per user in Firestore.

    Each user has a single document in the ``conversations`` collection,
    keyed by ``user_id``, with a capped ``messages`` array.  When the
    array reaches ``MAX_CONVERSATION_MESSAGES`` (50) the oldest messages
    are trimmed so new ones always fit — effectively a rolling window of
    the most recent exchanges.

    This guarantees the document never grows large enough to hit
    Firestore's 1 MiB per-document limit (each message is ~200 bytes,
    so 50 messages is ~10 KiB) and keeps retrieval of the most recent N
    messages a single document read.
    """

    COLLECTION = "conversations"

    @staticmethod
    def get_or_create(user_id: str) -> dict:
        now = datetime.now(timezone.utc)
        doc_ref = db.collection(AssistantConversationService.COLLECTION).document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        conversation = {
            "user_id": user_id,
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }
        doc_ref.set(conversation)
        return conversation

    @staticmethod
    def get_recent_messages(user_id: str, limit: int = 10) -> list:
        conversation = AssistantConversationService.get_or_create(user_id)
        return conversation.get("messages", [])[-limit:]

    @staticmethod
    def add_messages(user_id: str, new_messages: list) -> None:
        now = datetime.now(timezone.utc)
        doc_ref = db.collection(AssistantConversationService.COLLECTION).document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            conversation = {
                "user_id": user_id,
                "messages": [],
                "created_at": now,
                "updated_at": now,
            }
            doc_ref.set(conversation)
            doc = doc_ref.get()
        current = doc.to_dict().get("messages", [])
        current.extend(new_messages)
        if len(current) > MAX_CONVERSATION_MESSAGES:
            current = current[-MAX_CONVERSATION_MESSAGES:]
        doc_ref.update({
            "messages": current,
            "updated_at": now,
        })
