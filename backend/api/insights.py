from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from services.scoring_service import get_user_scores
from models.user import ScoresResponse

router = APIRouter(tags=["Insights"])


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
