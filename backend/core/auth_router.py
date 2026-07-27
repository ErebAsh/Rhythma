from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
from core.auth import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_NAME,
    get_current_user,
)
from models.user import UserCreate, UserResponse, UserProfileUpdate, UserProfileResponse
from services.firestore_service import UserService
import os
import logging
from pydantic import BaseModel
import firebase_admin.auth
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

class FirebaseLoginRequest(BaseModel):
    id_token: str
    fcm_token: Optional[str] = None

router = APIRouter(tags=["Authentication"])
# Env-driven so dev (http://localhost) and prod (https, real domain) differ without code changes.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"  # True if HTTPS-only, False if HTTP allowed (dev)
# CSRF Mitigation: The SameSite attribute (lax or strict) prevents the browser from sending 
# this cookie along with cross-site requests, which provides robust protection against CSRF attacks.
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()  # "lax" or "strict" or "none" | "none" if web + API end up on differrent registrable domains in prod
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)  # e.g. ".example.com" to share across subdomains, or None for default (current domain only)

# ─── Rate Limiting ──────────────────────────────────────────────────────────
# In-memory stores for rate limiting (resets on server restart)
login_attempts: Dict[str, List[datetime]] = {}
register_attempts: Dict[str, List[datetime]] = {}

def is_rate_limited(
    attempts_store: Dict[str, List[datetime]],
    key: str,
    limit: int = 5,
    window_seconds: int = 300,
) -> Optional[int]:
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

def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",  # Cookie is valid for all paths
    )

# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/firebase-login")
async def firebase_login(request: Request, response: Response, data: FirebaseLoginRequest):
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
        decoded_token = await run_in_threadpool(firebase_admin.auth.verify_id_token, data.id_token)
    except firebase_admin.auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token"
        )
    except Exception as e:
        logger.error(f"Error verifying Firebase ID token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    phone_number = decoded_token.get('phone_number')
    
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No phone number found in Firebase token"
        )
        
    try:
        # Find or create user
        is_new_user = False
        user = UserService.get_user_by_phone(phone_number)
        if not user:
            is_new_user = True
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
        
        _set_auth_cookie(response, access_token)
        
        # Web clients rely on the HttpOnly cookie for security and do not need the token in the body.
        # Flutter/Mobile clients still need the token in the response body.
        if request.headers.get("X-Client-Platform") == "web":
            return {"token_type": "bearer", "is_new_user": is_new_user}
            
        return {"access_token": access_token, "token_type": "bearer", "is_new_user": is_new_user}
        
    except Exception as e:
        logger.error(f"Error during firebase login for phone {phone_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        domain=COOKIE_DOMAIN,
    )
    return {"message": "Successfully logged out."}

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


@router.delete("/me")
async def delete_me(current_user: dict = Depends(get_current_user)):
    """Deletes the authenticated user's account permanently.
    
    This deletes their cycle logs, their user document, and their Firebase Auth user.
    """
    UserService.delete_user(current_user["id"])
    return {"status": "success", "detail": "Account deleted successfully"}
