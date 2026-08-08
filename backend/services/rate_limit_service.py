from datetime import datetime, timedelta, timezone
from typing import Optional

from services.firestore_service import db


class RateLimitService:
    COLLECTION = "rate_limits"

    @staticmethod
    def _document(key: str):
        return db.collection(RateLimitService.COLLECTION).document(key)

    @staticmethod
    def is_rate_limited(
        key: str,
        limit: int = 5,
        window_seconds: int = 300,
    ) -> Optional[int]:
        now = datetime.now(timezone.utc)
        doc_ref = RateLimitService._document(key)
        doc = doc_ref.get()

        raw_timestamps = []
        if doc.exists:
            data = doc.to_dict() or {}
            raw_timestamps = data.get("timestamps", [])

        timestamps = []
        for t in raw_timestamps:
            if isinstance(t, str):
                try:
                    dt = datetime.fromisoformat(t)
                    timestamps.append(dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc))
                except Exception:
                    pass
            elif isinstance(t, datetime):
                timestamps.append(t if t.tzinfo else t.replace(tzinfo=timezone.utc))

        timestamps = [
            t for t in timestamps
            if now - t < timedelta(seconds=window_seconds)
        ]

        if len(timestamps) >= limit:
            oldest = timestamps[0]
            remaining = int(
                (oldest + timedelta(seconds=window_seconds) - now).total_seconds()
            )

            doc_ref.set({"timestamps": timestamps})
            return max(remaining, 1)

        timestamps.append(now)
        doc_ref.set({"timestamps": timestamps})
        return None

    @staticmethod
    def reset(key: str) -> None:
        """Drop one key's window, so the next request starts from zero.

        ``clear_all`` empties the whole collection, which is fine for a
        test fixture but wrong for the case this exists for: clearing a
        single user's counter — after a successful login, say — without
        also clearing everybody else's. ``test_firestore_mock`` has been
        calling this since the mock gained real ``delete`` support; the
        method itself was never written, which is why that module and
        twenty others have been failing at runtime.

        Deleting the document rather than writing an empty list keeps the
        collection from filling up with tombstones, and ``is_rate_limited``
        already treats a missing document as an empty window.
        """
        try:
            RateLimitService._document(key).delete()
        except Exception:
            # A rate-limit reset is never worth failing a request over. The
            # worst case is that the caller keeps its existing window.
            pass

    @staticmethod
    def clear_all():
        """
        Clear all rate limit entries.
        Used only for tests.
        """
        try:
            if hasattr(db, "_collections"):
                db._collections.pop(RateLimitService.COLLECTION, None)
        except Exception:
            pass