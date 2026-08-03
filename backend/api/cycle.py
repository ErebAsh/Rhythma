from fastapi import APIRouter, Depends, HTTPException, Query, status
from core.auth import get_current_user
from pydantic import BaseModel, Field
from datetime import date
from typing import Any, Dict, List, Optional

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


class CycleHistoryEntry(BaseModel):
    """One stored log, as it comes back from Firestore.

    Every field but ``id`` is optional because a log is built up over
    time — the Home screen's quick-log tiles write a single field for the
    day, so a document holding only ``flow_intensity`` is normal, not
    corrupt. ``model_config`` allows the extra keys Firestore carries
    (``user_id``, ``created_at``, ``updated_at``) through untouched, so
    typing the response does not silently drop fields the clients already
    read.
    """

    model_config = {"extra": "allow"}

    id: str
    start_date: Optional[Any] = None
    end_date: Optional[Any] = None
    flow_intensity: Optional[str] = None
    mood: Optional[str] = None
    symptoms: Optional[List[str]] = None
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None
    notes: Optional[str] = None


class CycleHistoryPage(BaseModel):
    """Where this page sits, and whether there is another one."""

    limit: int = Field(..., description="How many entries were requested.")
    offset: int = Field(..., description="How many entries were skipped.")
    count: int = Field(..., description="How many entries this page holds.")
    hasMore: bool = Field(
        ...,
        description=(
            "True when at least one more entry exists past this page. "
            "Derived from fetching one extra document rather than from a "
            "count query, so paging costs no extra round trip."
        ),
    )
    nextOffset: Optional[int] = Field(
        None,
        description="Offset for the next page, or null when this is the last one.",
    )


class CycleHistoryResponse(BaseModel):
    message: str
    entries: List[CycleHistoryEntry]
    page: CycleHistoryPage


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
        "data": log,
    }


#: Ceiling on one page. High enough that a month view or a year of period
#: starts fits in a single request, low enough that no response can grow
#: without bound on a 2G connection.
MAX_HISTORY_PAGE = 100

#: What a client gets when it asks for nothing in particular.
DEFAULT_HISTORY_PAGE = 20


@router.get(
    "/{user_id}/history",
    response_model=CycleHistoryResponse,
    summary="Get cycle history",
    description=(
        "Returns a page of the user's cycle log entries, ordered by date "
        "descending.\n\n"
        "`limit` and `offset` page through the history; `start_date` and "
        "`end_date` (both inclusive, `YYYY-MM-DD`) restrict it to a window, "
        "so a client can ask for a specific month rather than only for the "
        "most recent N entries.\n\n"
        "The `page` object reports where this page sits and whether another "
        "one exists. `hasMore` comes from fetching one extra document, not "
        "from a count query, so paging costs no additional round trip.\n\n"
        "Calling with no query parameters returns the most recent entries, "
        "newest first, exactly as before."
    ),
)
async def get_cycle_history(
    user_id: str,
    limit: int = Query(
        DEFAULT_HISTORY_PAGE,
        ge=1,
        le=MAX_HISTORY_PAGE,
        description="How many entries to return (1-100).",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="How many entries to skip, for paging.",
    ),
    start_date: Optional[date] = Query(
        None,
        description="Only return entries on or after this date (inclusive).",
    ),
    end_date: Optional[date] = Query(
        None,
        description="Only return entries on or before this date (inclusive).",
    ),
    current_user: dict = Depends(get_current_user)
):
    """One page of the user's own history.

    The bounds on ``limit`` are the point of this signature. It used to be
    an unvalidated ``Optional[int]`` passed straight into the query, where
    ``?limit=-1`` reached a Python slice as ``docs[:-1]`` and returned
    every log *except the oldest* — not an error, not empty, and not what
    anyone asked for — while ``?limit=100000`` was accepted and would
    serialize an entire history into one response. Both are now a 422 from
    FastAPI's own validation, before any handler code runs.
    """
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's data"
        )

    # Checked here rather than by a validator because it is a relationship
    # between two parameters, not a property of either one. An inverted
    # range is a bug in the caller; returning an empty list would let it
    # look like "you have no logs in March".
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must not be after end_date",
        )

    entries, has_more = CycleService.get_logs_page(
        user_id,
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "message": f"History for user {user_id}",
        "entries": entries,
        "page": {
            "limit": limit,
            "offset": offset,
            "count": len(entries),
            "hasMore": has_more,
            "nextOffset": offset + len(entries) if has_more else None,
        },
    }


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
