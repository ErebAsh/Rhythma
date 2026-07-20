import firebase_admin
from firebase_admin import firestore, credentials
import os
import json
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

# ─── Mock Firestore Client for Local Development (fallback) ────────────────
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

class MockQuery:
    def __init__(self, stream_generator):
        self.stream_generator = stream_generator

    def limit(self, count):
        return self

    def stream(self):
        return self.stream_generator()

class MockCollectionReference:
    _next_id = 1

    def __init__(self, name, db):
        self.name = name
        self.db = db
        if name not in db._collections:
            db._collections[name] = {}
        self.store = db._collections[name]

    def add(self, document_data):
        doc_id = f"mock-doc-id-{MockCollectionReference._next_id}"
        MockCollectionReference._next_id += 1
        self.store[doc_id] = document_data
        return (None, MockDocumentReference(doc_id, document_data, self))

    def document(self, doc_id):
        data = self.store.get(doc_id)
        return MockDocumentReference(doc_id, data, self)

    def where(self, field, op, value):
        filtered = []
        for doc_id, data in self.store.items():
            if data.get(field) == value:
                filtered.append(MockDocumentReference(doc_id, data, self))
        return MockQuery(lambda: filtered)

    # Mock support for order_by and limit (needed for the new implementation)
    def order_by(self, field, direction=None):
        # For mock, we don't actually sort; just return self
        # We'll implement a simple sort if needed, but for testing the new method,
        # we can keep the existing behavior and sort in Python for mock mode.
        # However, to keep the mock behaviour consistent with the real Firestore,
        # we can at least respect the limit when it's chained.
        return self

class MockFirestoreClient:
    def __init__(self):
        self._collections = {}

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
        """Create a new user document in Firestore."""
        try:
            now = datetime.now(timezone.utc)
            user_data["created_at"] = now
            user_data["updated_at"] = now
            doc_ref = db.collection("users").add(user_data)
            return doc_ref[1].id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user: {str(e)}"
            )

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by email."""
        try:
            users = db.collection("users").where("email", "==", email).limit(1).stream()
            for user in users:
                data = user.to_dict()
                data["id"] = user.id
                return data
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user: {str(e)}"
            )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user: {str(e)}"
            )

    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a user document and set updated_at."""
        try:
            update_data["updated_at"] = datetime.now(timezone.utc)
            doc_ref = db.collection("users").document(user_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )


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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save cycle log: {str(e)}"
            )

    @staticmethod
    def get_logs_for_user(user_id: str, limit: int = 10) -> list:
        """Return a user's cycle logs, most recent (by start_date) first.

        Uses Firestore's native sorting and limiting to fetch only the
        required number of documents. This requires a composite index on
        `(user_id, start_date desc)` for performance.

        If the index is missing, Firestore will raise a FAILED_PRECONDITION
        error with a direct link to create it. Once created, this query
        will run efficiently.

        For users with > 500 logs, consider adding pagination (offset/limit)
        to avoid large data transfers.
        """
        try:
            # Build the query with equality filter and descending order on start_date
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
        except Exception as e:
            # If the error is due to missing composite index, include a helpful note.
            error_msg = str(e)
            if "FAILED_PRECONDITION" in error_msg and "index" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "Missing required Firestore composite index. "
                        "Please create the index using the link provided in the error message, "
                        "or manually create an index on 'cycle_logs' with fields (user_id Ascending, start_date Descending)."
                    )
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch cycle logs: {str(e)}"
            )

    @staticmethod
    def upsert_log(user_id: str, log_date: date, fields: Dict[str, Any]) -> str:
        """Create or update *that day's* cycle log with the given fields.

        Backs the single `POST /cycle/log` endpoint for both the Home
        screen's quick-log tiles (a partial `fields` dict — just the one
        thing being tapped, e.g. `{"flow_intensity": "light"}`) and the
        Cycle screen's "Save" button (a full `fields` dict with everything
        selected for that day). Either way, this finds-or-creates a single
        document for (user_id, log_date) and merges `fields` into it,
        rather than creating a new document per call — without this,
        logging flow then mood then sleep for the same day would produce
        three separate half-filled documents instead of one complete one,
        which would also throw off the day-to-day cycle-length math in the
        dashboard (each same-day duplicate looks like a separate "cycle
        start").

        Deliberately avoids a range filter (`start_date` between day-start
        and day-end) chained onto the `user_id ==` equality filter — that
        combination needs a composite index in Firestore (same as
        `get_logs_for_user` avoids). Instead this fetches all of the user's
        logs (equality filter only) and finds today's match in Python. Fine
        at this app's current scale; would need revisiting if a single
        user's log volume grew large.
        """
        try:
            day_start = datetime.combine(log_date, datetime.min.time(), tzinfo=timezone.utc)
            day_end = datetime.combine(log_date, datetime.max.time(), tzinfo=timezone.utc)

            docs = list(db.collection("cycle_logs").where("user_id", "==", user_id).stream())
            match = None
            for doc in docs:
                start = doc.to_dict().get("start_date")
                if isinstance(start, datetime) and day_start <= start <= day_end:
                    match = doc
                    break

            now = datetime.now(timezone.utc)
            update_fields = dict(fields)
            # Normalize any bare `date` values (e.g. end_date) to UTC datetime,
            # same as create_log did.
            for key, value in list(update_fields.items()):
                if isinstance(value, date) and not isinstance(value, datetime):
                    update_fields[key] = datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)

            if match:
                update_fields["updated_at"] = now
                db.collection("cycle_logs").document(match.id).update(update_fields)
                return match.id

            new_data = {**update_fields, "user_id": user_id, "start_date": day_start, "created_at": now}
            doc_ref = db.collection("cycle_logs").add(new_data)
            return doc_ref[1].id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save cycle log: {str(e)}"
            )