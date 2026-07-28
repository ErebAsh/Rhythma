from datetime import date

from fastapi import APIRouter, Depends
from core.auth import get_current_user
from services.scoring_service import get_user_scores, as_date, DEFAULT_CYCLE_LENGTH

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    # `get_user_scores` is the single source of truth for CVI/MHS —
    # shared with GET /insights/{user_id}/scores so the two endpoints
    # can never return different numbers for the same user (see #86).
    score_data = get_user_scores(user_id)
    logs = score_data["logs"]  # Most recent first, matches CycleService.get_logs_for_user.

    avg_cycle_length = DEFAULT_CYCLE_LENGTH
    cycle_day = None
    next_period_days = None

    if logs:
        most_recent_start = as_date(logs[0].get("start_date"))
        if most_recent_start:
            cycle_day = (date.today() - most_recent_start).days + 1

        if len(logs) >= 2:
            deltas = []
            for i in range(len(logs) - 1):
                newer = as_date(logs[i].get("start_date"))
                older = as_date(logs[i + 1].get("start_date"))
                if newer and older and (newer - older).days > 0:
                    deltas.append((newer - older).days)
            if deltas:
                avg_cycle_length = round(sum(deltas) / len(deltas))

        if cycle_day is not None:
            next_period_days = max(avg_cycle_length - cycle_day, 0)

    avg_sleep = None
    sleep_values = [l.get("sleep_hours") for l in logs if l.get("sleep_hours") is not None]
    if sleep_values:
        avg_sleep = round(sum(sleep_values) / len(sleep_values), 1)

    # Per-cycle length history (oldest first, so a client can plot it
    # left-to-right as a trend line) — the gap in days between each
    # consecutive pair of logged start_dates. `logs` is newest-first, so
    # walk it in reverse.
    cycle_history = []
    ordered = list(reversed(logs))
    for i in range(1, len(ordered)):
        newer = as_date(ordered[i].get("start_date"))
        older = as_date(ordered[i - 1].get("start_date"))
        if newer and older and (newer - older).days > 0:
            cycle_history.append({
                "start_date": newer.isoformat(),
                "cycle_length": (newer - older).days,
            })

    # Symptom frequency: fraction of logs-with-any-symptom-data that
    # recorded each canonical symptom. Computed here (not left for the
    # client to derive from local Hive history) so Insights only ever
    # needs this one endpoint.
    canonical_symptoms = ["cramps", "headache", "bloating", "acne"]
    logs_with_symptoms = [l for l in logs if l.get("symptoms")]
    symptom_frequency = {
        s: round(
            sum(1 for l in logs_with_symptoms if s in (l.get("symptoms") or [])) / len(logs_with_symptoms),
            2,
        )
        for s in canonical_symptoms
    } if logs_with_symptoms else {}

    recent_stress_level = logs[0].get("stress_level") if logs else None

    return {
        "user": {
            "name": current_user.get("username", "User")
        },
        "cycle": {
            "day": cycle_day,
            "total": avg_cycle_length,
            "nextPeriodDays": next_period_days,
        },
        "insights": {
            "mhs": score_data["mhs"],
            "cvi": score_data["cvi_risk"],
            "sleepHours": f"{avg_sleep}h" if avg_sleep is not None else None,
        },
        # Lets the client tell "no data yet" apart from "computed a low
        # score" — the CVI/MHS models need >=3 / >=2 logs respectively to
        # return a real number rather than None.
        "hasEnoughDataForInsights": score_data["has_enough_data_for_insights"],
        "loggedCycleCount": score_data["logged_cycle_count"],
        # Used by Insights' trend chart. Empty until there are at least 2
        # logged cycles to compute a gap between.
        "cycleHistory": cycle_history,
        # Used by Insights' symptom-pattern bars and the "recent stress"
        # mini-card — both computed here so the client never falls back to
        # deriving anything from local Hive history for this screen.
        "symptomFrequency": symptom_frequency,
        "recentStressLevel": recent_stress_level,
    }