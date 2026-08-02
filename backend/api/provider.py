"""Provider dashboard endpoints (issue #267).

Healthcare professionals register and log in through their own flow, then
see only the patients who have explicitly granted them consent. Consent
grant/list/revoke live on this router too: they are the patient side of
the same feature, and keeping the new surface in one place makes the
consent contract (and its tests) easy to follow.
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr

from core import auth_router as auth_router_module
from core.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    REFRESH_COOKIE_NAME,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from services.firestore_service import UserService
from services.provider_service import ConsentService, ProviderService
from services.rate_limit_service import RateLimitService

router = APIRouter(tags=["Provider Dashboard"])


class RegisterProviderRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    license_number: Optional[str] = None


class ProviderLoginRequest(BaseModel):
    email: EmailStr
    password: str


class GrantConsentRequest(BaseModel):
    provider_email: EmailStr


def _require_role(current_user: dict, role: str) -> dict:
    if current_user.get("role", "patient") != role:
        if role == "provider":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A healthcare provider account is required",
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A patient account is required",
        )
    return current_user


# ─── Provider account ────────────────────────────────────────────────────


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_provider(data: RegisterProviderRequest):
    """Create a provider account, separate from the patient ``/auth/register``
    flow. Same user store, ``role=provider`` attached at creation."""
    existing = UserService.get_user_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user_data = {
        "email": data.email,
        "password": get_password_hash(data.password),
        "email_verified": False,
        "role": "provider",
        "username": data.username,
        "full_name": data.full_name,
        "specialty": data.specialty,
        "license_number": data.license_number,
    }
    try:
        user_id = UserService.create_user(user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Provider registration failed",
        ) from e

    return {
        "id": user_id,
        "email": data.email,
        "role": "provider",
        "message": "Provider account created.",
    }


@router.post("/login")
async def login_provider(
    data: ProviderLoginRequest, request: Request, response: Response
):
    """Provider login. Rejects patient accounts outright."""
    client_ip = auth_router_module.get_client_ip(request)
    remaining = RateLimitService.is_rate_limited(
        key=f"login:{client_ip}",
        limit=10,
        window_seconds=300,
    )
    if remaining is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait 5 minutes.",
            headers={"Retry-After": str(remaining)},
        )

    user = UserService.get_user_by_email(data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if user.get("role") != "provider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This is not a healthcare provider account",
        )

    stored_hash = user.get("password")
    if not stored_hash or not verify_password(data.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(user["id"])

    auth_router_module._set_auth_cookie(response, access_token)
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=auth_router_module.COOKIE_SECURE,
        samesite=auth_router_module.COOKIE_SAMESITE,
        domain=auth_router_module.COOKIE_DOMAIN,
        path="/",
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "email_verified": user.get("email_verified", False),
        "user_id": user["id"],
        "role": "provider",
    }


@router.get("/me")
async def provider_me(current_user: dict = Depends(get_current_user)):
    """The provider's own profile."""
    _require_role(current_user, "provider")
    user = UserService.get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.pop("password", None)
    return user


# ─── Consent (patient side) ──────────────────────────────────────────────


@router.post("/consents", status_code=status.HTTP_201_CREATED)
async def grant_consent(
    data: GrantConsentRequest, current_user: dict = Depends(get_current_user)
):
    """A patient grants a provider access to her shared data."""
    _require_role(current_user, "patient")
    return ConsentService.grant(current_user["id"], data.provider_email)


@router.get("/consents")
async def list_consents(current_user: dict = Depends(get_current_user)):
    """A patient lists everyone she has shared data with."""
    _require_role(current_user, "patient")
    return {"consents": ConsentService.list_for_patient(current_user["id"])}


@router.delete("/consents/{consent_id}")
async def revoke_consent(
    consent_id: str, current_user: dict = Depends(get_current_user)
):
    """A patient revokes a provider's access."""
    _require_role(current_user, "patient")
    return ConsentService.revoke(current_user["id"], consent_id)


# ─── Provider view ───────────────────────────────────────────────────────


@router.get("/patients")
async def list_patients(current_user: dict = Depends(get_current_user)):
    """Providers see only patients with an active consent."""
    _require_role(current_user, "provider")
    return {"patients": ProviderService.patient_summaries(current_user["id"])}


@router.get("/patients/{patient_id}")
async def patient_detail(
    patient_id: str, current_user: dict = Depends(get_current_user)
):
    """Provider view of one patient's shared data."""
    _require_role(current_user, "provider")
    return ProviderService.patient_detail(current_user["id"], patient_id)
