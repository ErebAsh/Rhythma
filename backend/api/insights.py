from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.firestore_service import UserService
from services.health_observations_service import get_user_observations
from services.scoring_service import get_user_scores
from models.user import ScoresResponse

router = APIRouter(tags=["Insights"])


class ObservationModel(BaseModel):
    """One factual statement derived from the user's own logged data.

    ``title``/``body`` are English fallbacks. Clients that have a
    translation should render ``titleKey``/``bodyKey`` and interpolate
    ``evidence`` themselves — which is why the numbers behind every
    statement are exposed structurally rather than only baked into the
    sentence.
    """

    code: str = Field(
        ..., description="Stable machine-readable identifier for the rule that fired."
    )
    severity: str = Field(..., description="One of: info, attention, seek_care.")
    title: str
    body: str
    titleKey: str
    bodyKey: str
    evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="The exact values that triggered this observation.",
    )
    isMedicalAdvice: bool = Field(
        False,
        description=(
            "Always false. These statements describe logged data and are "
            "never a diagnosis."
        ),
    )
    disclaimerKey: str


class ObservationsResponse(BaseModel):
    observations: List[ObservationModel]
    topObservation: Optional[ObservationModel] = None
    cycleConsistency: str = Field(
        ...,
        description=(
            "Descriptive label: unknown, consistent, slightly_variable, or variable."
        ),
    )
    averageCycleLength: Optional[int] = None
    analyzedCycleCount: int = 0
    disclaimer: str
    disclaimerKey: str


@router.get(
    "/{user_id}/scores",
    response_model=ScoresResponse,
    summary="Get user scores",
    description="Returns the Menstrual Health Score (MHS) and Cycle Variability Index (CVI) for the specified user. Requires at least 2 cycle logs for CVI and 3 for MHS, otherwise the corresponding fields return None.",
)
async def get_scores(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve computed MHS and CVI scores for the authenticated user.

    Both scores are computed server-side by the scoring service using the
    same logic shared with the dashboard endpoint, guaranteeing consistency
    between the two views.
    """
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    score_data = get_user_scores(user_id)

    return ScoresResponse(
        mhs=score_data["mhs"],
        cvi=score_data["cvi_risk"],
        hasEnoughDataForInsights=score_data["has_enough_data_for_insights"],
        loggedCycleCount=score_data["logged_cycle_count"],
    )


@router.get(
    "/{user_id}/observations",
    response_model=ObservationsResponse,
    summary="Get factual observations about the user's logged data",
    description=(
        "Returns descriptive, evidence-backed statements derived from the user's "
        "own cycle logs — which specific cycle ran long or short, whether bleeding "
        "lasted past the typical range, how much cycle length has varied, and "
        "recent sleep and stress trends. Each observation carries the exact numbers "
        "that produced it, a severity (info, attention, or seek_care), and "
        "localization keys. Observations describe logged data; they are never a "
        "diagnosis, and none of them names a medical condition. Follows the "
        "language and safety rules in menstrual_insights_guidelines.md."
    ),
)
async def get_observations(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Evidence-backed observations for the authenticated user.

    Authorization matches ``/scores``: a user may only read her own data,
    and a mismatched path id is a 403 rather than a silent fallback to the
    caller's own records.

    Reuses ``get_user_scores()`` for its already-fetched log list, so this
    endpoint costs the same Firestore reads as the dashboard rather than
    doubling them.
    """
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    score_data = get_user_scores(user_id)
    profile = UserService.get_user_by_id(user_id) or {}

    return get_user_observations(score_data["logs"], profile=profile)
