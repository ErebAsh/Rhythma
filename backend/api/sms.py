from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from services.firestore_service import UserService
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta, timezone
import os
import re

# ─── Pydantic Models ─────────────────────────────────────────────────────────
class SMSRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")
    message: str


class SMSSettings(BaseModel):
    phoneNumber: Optional[str] = ""
    enabled: bool = False

    @property
    def normalized_phone(self) -> Optional[str]:
        return self.phoneNumber.strip() if self.phoneNumber else None


# ─── Rate Limiter (in-memory) ──────────────────────────────────────────────
sms_history = {}

def is_rate_limited(user_id: str, limit: int = 1, window_seconds: int = 60) -> int | None:
    now = datetime.now(timezone.utc)
    if user_id in sms_history:
        sms_history[user_id] = [t for t in sms_history[user_id] if now - t < timedelta(seconds=window_seconds)]
    else:
        sms_history[user_id] = []

    if len(sms_history[user_id]) >= limit:
        oldest = sms_history[user_id][0]
        remaining = int((oldest + timedelta(seconds=window_seconds) - now).total_seconds())
        return max(remaining, 1)

    sms_history[user_id].append(now)
    return None


# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(tags=["SMS"])


@router.get("/settings")
async def get_sms_settings(current_user: dict = Depends(get_current_user)):
    user = UserService.get_user_by_id(current_user["id"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "phoneNumber": user.get("sms_phone_number", "") or "",
        "enabled": bool(user.get("sms_enabled", False)),
    }


@router.post("/settings")
async def save_sms_settings(
    settings: SMSSettings,
    current_user: dict = Depends(get_current_user),
):
    phone = settings.normalized_phone
    if settings.enabled and not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A phone number is required to enable SMS summaries.",
        )
    if phone and not re.match(r"^\+[1-9]\d{1,14}$", phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be in E.164 format, e.g. +919876543210.",
        )

    UserService.update_user(
        current_user["id"],
        {"sms_phone_number": phone or "", "sms_enabled": settings.enabled},
    )
    return {"phoneNumber": phone or "", "enabled": settings.enabled}


@router.post("/send-summary")
async def send_sms_summary(
    request: SMSRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    # Rate limit check
    remaining = is_rate_limited(user_id)
    if remaining is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait 60 seconds before sending another SMS.",
            headers={"Retry-After": str(remaining)},
        )

    # ─── Twilio Integration ──────────────────────────────────────────────────
    # Check if Twilio is installed
    try:
        from twilio.rest import Client
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Twilio is not installed. Please install it with `pip install twilio`."
        )

    # Check if environment variables are set
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not from_phone:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Twilio credentials are not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env."
        )

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=request.message,
            from_=from_phone,
            to=request.phone_number
        )
        return {"message": "SMS sent successfully", "sid": message.sid}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS: {str(e)}"
        )