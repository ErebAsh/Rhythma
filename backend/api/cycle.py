from fastapi import APIRouter, Depends, HTTPException, Query, status
from core.auth import get_current_user
from pydantic import BaseModel, Field
from datetime import date
from typing import Any, Dict, Optional, List

from services.firestore_service import CycleService, UserService
from services.prediction_service import DEFAULT_FORECAST_HORIZON, predict


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


class CycleLengthEstimateModel(BaseModel):
    days: int = Field(..., description="Estimated cycle length in days.")
    source: str = Field(
        ...,
        description=(
            "Where the estimate came from: logged_history, "
            "declared_cycle_length (from onboarding), or population_default."
        ),
    )
    confidence: str = Field(..., description="high, medium, or low.")
    sampleSize: int = Field(
        ..., description="Number of past cycles the estimate is based on."
    )
    spreadDays: float = Field(
        ..., description="Typical variation between this user's cycles, in days."
    )
    excludedCycleLengths: List[int] = Field(
        default_factory=list,
        description=(
            "Cycle lengths discarded as implausible or as statistical "
            "outliers, listed so the estimate is auditable."
        ),
    )


class PredictedRange(BaseModel):
    earliest: Optional[str] = None
    latest: Optional[str] = None


class OvulationEstimate(BaseModel):
    date: Optional[str] = None
    isEstimate: bool = True


class FertileWindowEstimate(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    isEstimate: bool = True
    notForContraception: bool = True


class PredictionResponse(BaseModel):
    today: str
    cycleLength: CycleLengthEstimateModel
    lastPeriodStart: Optional[str] = None
    currentCycleDay: Optional[int] = None
    phase: str
    nextPeriodDate: Optional[str] = None
    daysUntilNextPeriod: Optional[int] = Field(
        None,
        description=(
            "Negative when the period is late. Deliberately not clamped at "
            "zero — 'due today' and 'five days late' are different answers."
        ),
    )
    isOverdue: bool = False
    daysOverdue: int = 0
    predictedRange: PredictedRange
    ovulation: OvulationEstimate
    fertileWindow: FertileWindowEstimate
    upcomingPeriods: List[str] = Field(default_factory=list)
    confidence: str
    disclaimer: str


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
        "data": log.model_dump()
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


@router.get(
    "/predictions",
    response_model=PredictionResponse,
    summary="Predict the next period, fertile window and current phase",
    description=(
        "Returns the authenticated user's predicted next period date with an "
        "explicit earliest/latest range and a confidence tier, her current "
        "cycle day and phase, an estimated ovulation date and fertile window, "
        "and the next few predicted period start dates.\n\n"
        "The cycle-length estimate is an exponentially weighted mean of "
        "recent cycles with outlier rejection, falling back to the length "
        "declared during onboarding and then to a population default; the "
        "`cycleLength.source` field says which was used.\n\n"
        "`daysUntilNextPeriod` goes negative when a period is late — it is "
        "deliberately not clamped at zero. Ovulation and the fertile window "
        "are statistical estimates from logged dates and are not "
        "contraceptive guidance."
    ),
)
async def get_cycle_predictions(
    horizon: int = Query(
        DEFAULT_FORECAST_HORIZON,
        ge=1,
        le=12,
        description="How many future period start dates to project.",
    ),
    current_user: dict = Depends(get_current_user),
):
    """Predictions for the authenticated user.

    Operates on ``current_user["id"]`` rather than a path parameter, so
    there is no cross-user authorization check to get wrong.

    Note this route is declared before ``PUT/DELETE /{log_id}`` but after
    ``/{user_id}/history``; ``/predictions`` is a fixed segment so it can
    never be shadowed by the ``{log_id}`` routes, which are on different
    methods anyway.
    """
    user_id = current_user["id"]
    logs = CycleService.get_logs_for_user(user_id, limit=12)
    profile = UserService.get_user_by_id(user_id) or {}

    return predict(logs, profile=profile, horizon=horizon).to_dict()


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
