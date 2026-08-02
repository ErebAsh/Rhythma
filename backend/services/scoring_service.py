"""
Shared score-computation service.

This module is the single source of truth for turning a user's raw
CycleLog history into the CVI (Cycle Variability Index) and MHS
(Menstrual Health Score) numbers that get surfaced to clients.

Both `GET /dashboard` (api/dashboard.py) and
`GET /insights/{user_id}/scores` (api/insights.py) call
`get_user_scores()` below instead of independently fetching logs and
calling the CVI/MHS models themselves. This guarantees the two
endpoints can never return different scores for the same user (see
issue #86) and keeps route handlers free of business logic, per the
contribution guide.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from services.firestore_service import CycleService, UserService
from models.cvi_model import predict_cvi, risk_level
from models.mhs_model import predict_mhs

# Default assumed cycle length (days) when there isn't enough history
# to compute a real average.
DEFAULT_CYCLE_LENGTH = 28

_FLOW_INTENSITY_TO_SCORE = {"light": 1, "medium": 2, "heavy": 3}

# Number of most-recent cycle logs fetched for scoring. Matches the
# previous behavior of api/dashboard.py.
_LOGS_LIMIT = 10


def as_date(value: Any) -> Optional[date]:
    """Firestore returns date/datetime fields as datetime (or its own
    DatetimeWithNanoseconds subclass); normalize everything to a plain
    `date` for day-math."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def build_model_features(logs_newest_first: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert raw CycleLog documents into the feature shape the CVI/MHS
    models expect (see models/cvi_model.py and models/mhs_model.py)."""
    features = []
    for i, log in enumerate(logs_newest_first):
        start = as_date(log.get("start_date"))
        end = as_date(log.get("end_date"))

        cycle_length = None
        if i + 1 < len(logs_newest_first):
            older_start = as_date(logs_newest_first[i + 1].get("start_date"))
            if start and older_start and (start - older_start).days > 0:
                cycle_length = (start - older_start).days

        if start and end and end >= start:
            flow_duration = max(1, (end - start).days + 1)
        else:
            flow_duration = 5
        flow_intensity = _FLOW_INTENSITY_TO_SCORE.get(
            (log.get("flow_intensity") or "").lower(), 2
        )

        stress = log.get("stress_level")
        sleep = log.get("sleep_hours")

        features.append({
            "cycle_length": cycle_length if cycle_length is not None else DEFAULT_CYCLE_LENGTH,
            "flow_duration": flow_duration,
            "flow_intensity": flow_intensity,
            "symptom_count": len(log.get("symptoms") or []),
            "stress_avg": stress if stress is not None else 2.5,
            "sleep_avg": sleep if sleep is not None else 7.0,
        })
    return features


def get_user_scores(user_id: str) -> Dict[str, Any]:
    """Fetch a user's recent cycle logs and compute their CVI/MHS scores.

    This is the ONLY place in the codebase that should call
    `predict_cvi` / `predict_mhs`. Any endpoint that needs a user's
    scores (dashboard, insights, future SMS summaries, etc.) should
    call this function rather than re-deriving features or calling the
    models directly, so there is exactly one code path that can drift
    from the models' expected input shape.

    Returns:
        A dict with:
            logs: the raw, most-recent-first CycleLog list (so callers
                that need more than scores, like the dashboard's cycle
                day/history, don't have to fetch it again).
            mhs: the Menstrual Health Score (0-100) or None if there's
                insufficient history.
            cvi: the raw Cycle Variability Index (0-100) or None.
            cvi_risk: the capitalized risk tier for `cvi` ("Low" /
                "Medium" / "High") or None.
            has_enough_data_for_insights: whether there are enough logs
                (>=3) for a meaningful CVI; lets clients distinguish
                "no data yet" from "computed a low score".
            logged_cycle_count: total number of logs fetched.
            profile: the user's profile dict (or None), so callers that
                need it for features beyond the two scores — e.g. the
                dashboard's cycle prediction — don't fetch it a second
                time.
    """
    logs = CycleService.get_logs_for_user(user_id, limit=_LOGS_LIMIT)
    features = build_model_features(logs)
    profile = UserService.get_user_by_id(user_id)

    mhs = predict_mhs(features, profile=profile)
    cvi = predict_cvi(features)
    cvi_risk = risk_level(cvi).capitalize() if cvi is not None else None

    return {
        "logs": logs,
        "profile": profile,
        "mhs": mhs,
        "cvi": cvi,
        "cvi_risk": cvi_risk,
        "has_enough_data_for_insights": len(logs) >= 3,
        "logged_cycle_count": len(logs),
    }