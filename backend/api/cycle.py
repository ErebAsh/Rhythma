from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

from services.firestore_service import CycleService

# ─── Pydantic Model ──────────────────────────────────────────────────────────
class CycleLog(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    flow_intensity: Optional[str] = None
    mood: Optional[str] = None
    symptoms: Optional[List[str]] = []
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None
    notes: Optional[str] = None


# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(tags=["Cycle Tracking"])

@router.post("/log")
async def log_cycle(
    log: CycleLog,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    log_id = CycleService.create_log(user_id, log.model_dump())
    return {
        "message": f"Cycle logged for user {user_id}",
        "id": log_id,
        "data": log.model_dump()
    }

@router.get("/{user_id}/history")
async def get_cycle_history(
    user_id: str,
    limit: Optional[int] = 10,        # <-- Added back with default 10
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's data"
        )
    entries = CycleService.get_logs_for_user(user_id, limit=limit or 10)
    return {"message": f"History for user {user_id}", "entries": entries}