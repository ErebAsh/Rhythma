from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

from services.firestore_service import CycleService


class CycleLog(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    flow_intensity: Optional[str] = None
    mood: Optional[str] = None
    symptoms: Optional[List[str]] = None
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None
    notes: Optional[str] = None


class CycleLogUpdate(BaseModel):
    end_date: Optional[date] = None
    flow_intensity: Optional[str] = None
    mood: Optional[str] = None
    symptoms: Optional[List[str]] = None
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None
    notes: Optional[str] = None


class CycleLogResponse(BaseModel):
    message: str
    id: str
    data: CycleLog


class CycleHistoryResponse(BaseModel):
    message: str
    entries: list


class CycleLogUpdateResponse(BaseModel):
    message: str
    id: str
    updated_fields: dict


class CycleLogDeleteResponse(BaseModel):
    message: str
    id: str


router = APIRouter(tags=["Cycle Tracking"])


@router.post(
    "/log",
    response_model=CycleLogResponse,
    summary="Log a cycle entry",
    description="Creates or updates a cycle log entry for the specified start date. Partial payloads (e.g. only flow_intensity from a quick-log tile) are merged without overwriting previously saved fields for that day.",
)
async def log_cycle(
    log: CycleLog,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    fields = {k: v for k, v in log.model_dump().items() if k != "start_date" and v is not None}
    log_id = CycleService.upsert_log(user_id, log.start_date, fields)
    return {
        "message": f"Cycle logged for user {user_id}",
        "id": log_id,
        "data": log,
    }


@router.get(
    "/{user_id}/history",
    response_model=CycleHistoryResponse,
    summary="Get cycle history",
    description="Returns the most recent cycle log entries for the specified user, ordered by date descending.",
)
async def get_cycle_history(
    user_id: str,
    limit: Optional[int] = 10,
    current_user: dict = Depends(get_current_user)
):
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's data"
        )
    entries = CycleService.get_logs_for_user(user_id, limit=limit or 10)
    return {"message": f"History for user {user_id}", "entries": entries}


@router.put(
    "/{log_id}",
    response_model=CycleLogUpdateResponse,
    summary="Update a cycle log",
    description="Updates one or more fields of an existing cycle log entry. Only the fields included in the request body are modified; all other existing fields are preserved.",
)
async def update_cycle_log(
    log_id: str,
    log_update: CycleLogUpdate,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    fields = {k: v for k, v in log_update.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    CycleService.update_log(user_id, log_id, fields)
    return {
        "message": f"Cycle log {log_id} updated",
        "id": log_id,
        "updated_fields": fields
    }


@router.delete(
    "/{log_id}",
    response_model=CycleLogDeleteResponse,
    summary="Delete a cycle log",
    description="Permanently removes a cycle log entry identified by its ID.",
)
async def delete_cycle_log(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    CycleService.delete_log(user_id, log_id)
    return {
        "message": f"Cycle log {log_id} deleted",
        "id": log_id
    }
