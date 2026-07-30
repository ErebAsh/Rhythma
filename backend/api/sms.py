from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import get_current_user
from services.firestore_service import UserService
from services.rate_limit_service import RateLimitService
from pydantic import BaseModel, Field
from typing import Optional
import os
import re

PHONE_PATTERN = r"^\+[1-9]\d{1,14}$"


class SMSRequest(BaseModel):
    phone_number: str = Field(..., pattern=PHONE_PATTERN)
    message: str


class SMSSettings(BaseModel):
    phoneNumber: Optional[str] = ""
    enabled: bool = False

    @property
    def normalized_phone(self) -> Optional[str]:
        return self.phoneNumber.strip() if self.phoneNumber else None


class SMSSettingsResponse(BaseModel):
    phoneNumber: str
    enabled: bool


class SMSSendResponse(BaseModel):
    message: str
    sid: str


router = APIRouter(tags=["SMS"])

# Legacy compatibility for existing tests
# SMS rate limiting is now handled by Firestore RateLimitService
sms_history = []


@router.get(
    "/settings",
    response_model=SMSSettingsResponse,
    summary="Get SMS notification settings",
    description="Returns the user's current SMS notification preferences, including the registered phone number and whether SMS summaries are enabled.",
)
async def get_sms_settings(current_user: dict = Depends(get_current_user)):
    user = UserService.get_user_by_id(current_user["id"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    phone = user.get("phone") or user.get("sms_phone_number") or ""

    return {
        "phoneNumber": phone,
        "enabled": bool(user.get("sms_enabled", False)),
    }


@router.post(
    "/settings",
    response_model=SMSSettingsResponse,
    summary="Save SMS notification settings",
    description="Updates the user's SMS notification preferences. A phone number is required when enabling SMS summaries, and must be in E.164 format.",
)
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
    if phone and not re.match(PHONE_PATTERN, phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be in E.164 format, e.g. +919876543210.",
        )

    UserService.update_user(
        current_user["id"],
        {
            "phone": phone or "",
            "sms_phone_number": phone or "",
            "sms_enabled": settings.enabled,
        },
    )
    return {"phoneNumber": phone or "", "enabled": settings.enabled}


@router.post(
    "/send-summary",
    response_model=SMSSendResponse,
    summary="Send SMS summary",
    description="Sends a cycle summary message via Twilio to the specified phone number. Rate-limited to one message per 60 seconds per user.",
)
async def send_sms_summary(
    request: SMSRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]

    remaining = RateLimitService.is_rate_limited(
        key=f"sms:{user_id}",
        limit=1,
        window_seconds=60,
    )

    if remaining is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait 60 seconds before sending another SMS.",
            headers={"Retry-After": str(remaining)},
        )

    try:
        from twilio.rest import Client
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Twilio is not installed. Please install it with `pip install twilio`."
        )

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
