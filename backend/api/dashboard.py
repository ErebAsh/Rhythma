from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from core.auth import get_current_user
from services.health_observations_service import (
    build_analysis,
    describe_consistency,
    evaluate,
    top_observation,
)
from services.scoring_service import get_user_scores, as_date, DEFAULT_CYCLE_LENGTH


class DashboardUser(BaseModel):
    name: str


class DashboardCycle(BaseModel):
    day: Optional[int] = None
    total: int
    nextPeriodDays: Optional[int] = None


class DashboardInsights(BaseModel):
    mhs: Optional[float] = None
    cvi: Optional[str] = None
    sleepHours: Optional[str] = None


class CycleHistoryEntry(BaseModel):
    start_date: str
    cycle_length: int


class DashboardObservation(BaseModel):
    """The single highest-priority observation, for the Home screen.

    Nullable: a brand-new user with no logs has nothing to say yet, and a
    client written before this field existed must keep working, so it is
    additive and optional rather than a required object.
    """

    code: str
    severity: str
    title: str
    body: str
    titleKey: str
    bodyKey: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    isMedicalAdvice: bool = False
    disclaimerKey: str


class DashboardResponse(BaseModel):
    user: DashboardUser
    cycle: DashboardCycle
    insights: DashboardInsights
    hasEnoughDataForInsights: bool
    loggedCycleCount: int
    cycleHistory: list[CycleHistoryEntry]
    symptomFrequency: dict[str, float]
    recentStressLevel: Optional[int] = None
    #: Highest-severity factual observation about the user's logged data,
    #: computed from the logs already fetched above — so the Home screen
    #: needs no second round trip. Full list lives at
    #: GET /insights/{user_id}/observations.
    topObservation: Optional[DashboardObservation] = None
    #: Descriptive consistency label (consistent / slightly_variable /
    #: variable / unknown), per menstrual_insights_guidelines.md's summary
    #: card guidance — a word, not a score.
    cycleConsistency: str = "unknown"


router = APIRouter(tags=["Dashboard"])


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get dashboard data",
    description="Returns the user's current cycle summary, computed health scores (MHS/CVI), sleep average, cycle history, symptom frequencies, and recent stress level. All insight data is computed server-side using the same scoring service shared with the Insights endpoint.",
)
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    score_data = get_user_scores(user_id)
    logs = score_data["logs"]

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

    # Observations reuse the logs already fetched above rather than
    # re-querying Firestore, so the Home screen still costs one round trip
    # and one read path. `build_analysis` is called separately from
    # `evaluate` only because the consistency label needs the analysis
    # object; both are pure functions over the same list.
    observations = evaluate(logs)
    highest = top_observation(observations)
    consistency = describe_consistency(build_analysis(logs))

    return {
        "user": {
            "name": current_user.get("username") or "User"
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
        "hasEnoughDataForInsights": score_data["has_enough_data_for_insights"],
        "loggedCycleCount": score_data["logged_cycle_count"],
        "cycleHistory": cycle_history,
        "symptomFrequency": symptom_frequency,
        "recentStressLevel": recent_stress_level,
        "topObservation": highest.to_dict() if highest else None,
        "cycleConsistency": consistency,
    }
