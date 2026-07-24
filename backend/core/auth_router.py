from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import datetime, timedelta, timezone
from core.auth import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from models.user import UserCreate, UserResponse, UserProfileUpdate, UserProfileResponse
from services.firestore_service import UserService
from typing import Dict, List
from pydantic import BaseModel
import firebase_admin.auth

class FirebaseLoginRequest(BaseModel):
    id_token: str

router = APIRouter(tags=["Authentication"])

# ─── Rate Limiting ──────────────────────────────────────────────────────────
# In-memory stores for rate limiting (resets on server restart)
login_attempts: Dict[str, List[datetime]] = {}
register_attempts: Dict[str, List[datetime]] = {}

def is_rate_limited(
    attempts_store: Dict[str, List[datetime]],
    key: str,
    limit: int = 5,
    window_seconds: int = 300,
) -> int | None:
    """
    Returns the number of seconds remaining before the next request is
    allowed if the key has exceeded the rate limit, or None otherwise.
    """
    now = datetime.now(timezone.utc)
    # Clean old entries
    if key in attempts_store:
        attempts_store[key] = [
            t for t in attempts_store[key]
            if now - t < timedelta(seconds=window_seconds)
        ]
    else:
        attempts_store[key] = []

    if len(attempts_store[key]) >= limit:
        # Calculate how many seconds until the oldest entry expires
        oldest = attempts_store[key][0]
        remaining = int((oldest + timedelta(seconds=window_seconds) - now).total_seconds())
        return max(remaining, 1)

    attempts_store[key].append(now)
    return None

def get_client_ip(request: Request) -> str:
    """Extract the client's IP address from the request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host or "unknown"

# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/firebase-login")
async def firebase_login(request: Request, data: FirebaseLoginRequest):
    # Rate limit by IP address (10 attempts per 5 minutes)
    client_ip = get_client_ip(request)
    remaining = is_rate_limited(login_attempts, client_ip, limit=10, window_seconds=300)
    if remaining is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait 5 minutes.",
            headers={"Retry-After": str(remaining)},
        )

    try:
        # Verify the Firebase ID token
        decoded_token = firebase_admin.auth.verify_id_token(data.id_token)
        phone_number = decoded_token.get('phone_number')
        
        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No phone number found in Firebase token"
            )
            
        # Find or create user
        user = UserService.get_user_by_phone(phone_number)
        if not user:
            # Create user
            user_data = {
                "phone": phone_number,
            }
            user_id = UserService.create_user(user_data)
            user = UserService.get_user_by_id(user_id)
            
        # Issue internal JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["id"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "is_new_user": not user.get("updated_at")}
        
    except firebase_admin.auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the signed-in user's basic identity.

    This is deliberately lightweight — its main purpose is to double as a
    token-validation check: `get_current_user` already raises 401 if the
    token is expired, malformed, or the account no longer exists, so a
    successful response here means the stored token is genuinely still
    good (used by the Flutter app at launch, see main.dart).
    """
    return current_user


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Returns the full profile for the authenticated user.

    Fetches the complete Firestore user document which contains both the
    authentication fields (username, email) and any health/preference
    fields written during onboarding or Edit Profile (age, height, cycle
    data, avatar, language, etc.).
    """
    user = UserService.get_user_by_id(current_user["id"])
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.pop("password", None)
    return user


@router.patch("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Merges profile fields onto the authenticated user's Firestore document.

    Uses PATCH semantics: only fields explicitly provided (non-None) are
    written.  This allows the Flutter app to send partial updates (e.g.
    just avatar or just cycle_length) without clobbering unrelated fields.

    Reuses the existing UserService.update_user() method — no new
    service layer introduced.
    """
    updates = {k: v for k, v in profile_data.model_dump().items() if v is not None}
    if updates:
        UserService.update_user(current_user["id"], updates)
    user = UserService.get_user_by_id(current_user["id"])
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.pop("password", None)
    return user