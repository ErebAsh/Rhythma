from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from services.scoring_service import get_user_scores

router = APIRouter(tags=["Insights"])


@router.get("/{user_id}/scores")
async def get_scores(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Reuses the exact same computation as GET /dashboard (see
    # services/scoring_service.get_user_scores) instead of duplicating
    # the CVI/MHS prediction logic — one source of truth, so both
    # endpoints always agree for the same user (see issue #86).
    score_data = get_user_scores(user_id)

    return {
        "mhs": score_data["mhs"],
        "cvi": score_data["cvi_risk"],
        "hasEnoughDataForInsights": score_data["has_enough_data_for_insights"],
        "loggedCycleCount": score_data["logged_cycle_count"],
    }