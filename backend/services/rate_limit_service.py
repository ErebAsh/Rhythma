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

        timestamps = []

        if doc.exists:
            data = doc.to_dict() or {}
            timestamps = data.get("timestamps", [])

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