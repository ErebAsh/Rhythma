from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get("/", response_model=HealthResponse, summary="Health check", description="Returns the current status of the Rhythma API service.")
async def health_check():
    return {"status": "ok", "service": "Rhythma API"}
