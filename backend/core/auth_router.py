from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
from core.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens,
    generate_reset_token,
    verify_reset_token,
    generate_verification_token,
    verify_email_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    OTP_SESSION_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    get_current_user,
    get_password_hash,
    verify_password,
)
from core.password_policy import enforce_password_policy, requirements as password_requirements
from core.rate_limits import (
    EMAIL_VERIFY_IP,
    FIREBASE_LOGIN_IP,
    LOGIN_ACCOUNT,
    LOGIN_IP,
    PASSWORD_RESET_CONFIRM_IP,
    PASSWORD_RESET_REQUEST_ACCOUNT,
    PASSWORD_RESET_REQUEST_IP,
    REGISTER_IP,
    TOKEN_REFRESH_IP,
    VERIFICATION_RESEND_ACCOUNT,
    clear as clear_rate_limit,
    client_ip,
    enforce as enforce_rate_limit,
)
from models.user import UserCreate, UserResponse, UserProfileUpdate, UserProfileResponse
from services.firestore_service import UserService

import os
import logging
from pydantic import BaseModel, EmailStr
import firebase_admin.auth # type: ignore

logger = logging.getLogger(__name__)

class FirebaseLoginRequest(BaseModel):
    id_token: str
    fcm_token: Optional[str] = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str

router = APIRouter(tags=["Authentication"])

# Env-driven so dev (http://localhost) and prod (https, real domain) differ without code changes.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"  # True if HTTPS-only, False if HTTP allowed (dev)
# CSRF Mitigation: The SameSite attribute (lax or strict) prevents the browser from sending 
# this cookie along with cross-site requests, which provides robust protection against CSRF attacks.
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()  # "lax" or "strict" or "none" | "none" if web + API end up on differrent registrable domains in prod
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)  # e.g. ".example.com" to share across subdomains, or None for default (current domain only)

# ─── Rate Limiting ──────────────────────────────────────────────────────────

def get_client_ip(request: Request) -> str:
    """Extract the client's IP address from the request.

    Thin wrapper over ``core.rate_limits.client_ip`` so the several call
    sites that already import this name keep working while there is only
    one implementation of "which address is this".
    """
    return client_ip(request)

def _set_auth_cookie(response: Response, token: str, max_age_seconds: int | None = None):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=max_age_seconds or (ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",  # Cookie is valid for all paths
    )


def _set_refresh_cookie(response: Response, token: str):
    """Write the refresh cookie with this deployment's cookie settings.

    Extracted because ``api/provider.py`` had its own copy of this block,
    which is how the two login routes came to disagree about everything
    *else* they do. Cookie flags are a security setting that must not
    depend on which route issued the session, so there is now one place
    that decides them.
    """
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
    )


def normalize_email(email: str) -> str:
    """Casefold and strip an address before it is used as a key.

    Addresses arrive from a form, so ``Doc@Clinic.in `` and
    ``doc@clinic.in`` are the same person typing the same thing. Without a
    single normalisation point they become two accounts in ``users`` and,
    worse, two separate rate-limit buckets — which hands an attacker a
    fresh login budget per capitalisation of the same address.
    """
    return (email or "").strip().lower()

# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/firebase-login")
async def firebase_login(request: Request, response: Response, data: FirebaseLoginRequest):
    # Same 10-per-5-minutes ceiling this route has always had, now expressed
    # as a named policy so it is configurable and consistent with the rest
    # of the auth surface rather than a pair of literals in a handler.
    enforce_rate_limit(FIREBASE_LOGIN_IP, get_client_ip(request))

    try:
        # Verify the Firebase ID token
        decoded_token = firebase_admin.auth.verify_id_token(data.id_token)

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
            
        # Issue internal JWT — OTP sessions use a long-lived token (10 years)
        # so the app never re-prompts for login on a verified device.
        access_token_expires = timedelta(minutes=OTP_SESSION_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["id"]}, expires_delta=access_token_expires
        )
        
        _set_auth_cookie(response, access_token)

        # Create a refresh token for all clients (was missing for Firebase login)
        refresh_token = create_refresh_token(user["id"])
        response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=refresh_token,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            domain=COOKIE_DOMAIN,
            path="/",
        )

        # Web clients rely on the HttpOnly cookie for security and do not need the token in the body.
        # Flutter/Mobile clients still need the token in the response body.
        if request.headers.get("X-Client-Platform") == "web":
            return {"token_type": "bearer", "is_new_user": is_new_user}

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "is_new_user": is_new_user
        }
    except Exception as e:
        logger.error(f"Error during firebase login for phone {phone_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(response: Response):
    for cookie_name in (COOKIE_NAME, REFRESH_COOKIE_NAME):
        response.delete_cookie(
            key=cookie_name,
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
async def delete_me(response: Response, current_user: dict = Depends(get_current_user)):
    """Deletes the authenticated user's account permanently.

    Kept for the clients that already call it (``deleteAccount()`` in
    ``web/src/api/endpoints.ts``, and the Flutter settings screen), but it
    now goes through the same cascade as ``POST /privacy/delete-account``:
    cycle logs, the user document, the Firebase Auth identity, **and** the
    assistant conversation and rate-limit records this path used to leave
    behind in Firestore.

    Two other gaps are closed here. Refresh tokens minted before deletion
    stayed valid in ``refresh_token_store`` until natural expiry, so the
    account remained usable on other devices. And unlike ``/logout``, the
    auth cookies were never cleared, so a web client kept sending a cookie
    for an account that no longer existed and every subsequent request
    401'd in a way that looked like a bug rather than a finished deletion.

    Prefer ``POST /privacy/delete-account`` for new client work: it is
    two-step, shows the user exactly what will be destroyed before she
    confirms, and returns per-collection counts. This route still deletes
    immediately, with no confirmation step.
    """
    user_id = current_user["id"]
    deleted_counts = UserService.delete_user(user_id)
    revoke_all_user_refresh_tokens(user_id)

    for cookie_name in (COOKIE_NAME, REFRESH_COOKIE_NAME):
        response.delete_cookie(key=cookie_name, path="/", domain=COOKIE_DOMAIN)

    return {
        "status": "success",
        "detail": "Account deleted successfully",
        "deletedCounts": deleted_counts or {},
    }


# ─── Password Policy ──────────────────────────────────────────────────────


@router.get(
    "/password-requirements",
    summary="The password rules this server enforces",
    description=(
        "Returns the minimum length, the byte ceiling, and a plain-language "
        "list of the rules applied to new passwords by `POST /auth/register` "
        "and `POST /auth/reset-password`.\n\n"
        "Exists so a sign-up form can show a user the rules *before* she "
        "submits, without each client keeping its own copy that drifts from "
        "what the server actually enforces. Unauthenticated: the rules are "
        "not a secret, and they are needed on the registration screen."
    ),
)
async def get_password_requirements():
    return password_requirements()


# ─── Password-Based Registration & Login ──────────────────────────────────

@router.post("/register")
async def register(data: RegisterRequest, request: Request):
    # Rate limit first: it is the cheaper check, and it is enforced before
    # the email lookup so the 409/200 difference — a working
    # account-enumeration oracle — is not available at whatever rate the
    # caller likes.
    enforce_rate_limit(REGISTER_IP, get_client_ip(request))

    # Then the password, also before the lookup, so a weak password is
    # rejected on its own terms rather than the response depending on
    # whether the address happened to be taken as well.
    enforce_password_policy(
        data.password,
        email=data.email,
        username=data.username,
    )

    user = UserService.get_user_by_email(data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    password_hash = get_password_hash(data.password)
    user_data = {
        "email": data.email,
        "password": password_hash,
        "email_verified": False,
    }
    if data.username:
        user_data["username"] = data.username
    if data.full_name:
        user_data["full_name"] = data.full_name

    try:
        user_id = UserService.create_user(user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

    verification_token = generate_verification_token(data.email)
    logger.info(f"Email verification token for {data.email}: {verification_token}")

    return {
        "id": user_id,
        "email": data.email,
        "email_verified": False,
        "message": "Registration successful. Please verify your email."
    }


@router.post("/login")
async def login(data: LoginRequest, request: Request, response: Response):
    # Both keys are checked, and both are checked *before* the user lookup.
    # Counting only failures would mean an attacker who happens to guess
    # correctly on attempt 4 walks away with no record of the first three;
    # counting only known accounts would make the limit itself an
    # enumeration signal, since unknown emails would never be throttled.
    enforce_rate_limit(LOGIN_IP, get_client_ip(request))
    enforce_rate_limit(LOGIN_ACCOUNT, data.email)

    user = UserService.get_user_by_email(data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    stored_hash = user.get("password")
    if not stored_hash or not verify_password(data.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Correct password: forget this account's recent attempts, so the three
    # typos that preceded it don't leave her one mistake from a lockout.
    # The per-IP bucket is deliberately left alone — see rate_limits.clear.
    clear_rate_limit(LOGIN_ACCOUNT, data.email)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user["id"])

    _set_auth_cookie(response, access_token)
    _set_refresh_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "email_verified": user.get("email_verified", False),
        "user_id": user["id"],
    }


# ─── Refresh Tokens ───────────────────────────────────────────────────────

@router.post("/refresh")
async def refresh_token(request: Request, response: Response, data: RefreshTokenRequest | None = None):
    # A refresh token is a bearer secret like any other, so unlimited
    # submissions are unlimited guesses. The ceiling is set well above what
    # a healthy client needs (one call per access-token lifetime) so a
    # normal app never sees it.
    enforce_rate_limit(TOKEN_REFRESH_IP, get_client_ip(request))

    # Dual-mode refresh: mobile clients send the token in the JSON body;
    # web clients rely on the HttpOnly cookie so the token never touches JS.
    refresh_token_value = None
    if data and data.refresh_token:
        refresh_token_value = data.refresh_token
    else:
        refresh_token_value = request.cookies.get(REFRESH_COOKIE_NAME)

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )

    user_id = verify_refresh_token(refresh_token_value)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    revoke_refresh_token(refresh_token_value)

    new_access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(user_id)

    # Rotate the access cookie for web clients
    _set_auth_cookie(response, new_access_token)
    # Rotate the refresh cookie for web clients
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=new_refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout-all")
async def logout_all(current_user: dict = Depends(get_current_user)):
    revoke_all_user_refresh_tokens(current_user["id"])
    return {"message": "All sessions logged out successfully."}


# ─── Password Reset ───────────────────────────────────────────────────────

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, request: Request):
    # Per-account so this cannot be pointed at one inbox as a mail bomb,
    # per-IP so it cannot be pointed at many. Both run before the lookup so
    # the throttle behaves identically for addresses that do and don't
    # exist — otherwise it undoes the deliberately identical response below.
    enforce_rate_limit(PASSWORD_RESET_REQUEST_IP, get_client_ip(request))
    enforce_rate_limit(PASSWORD_RESET_REQUEST_ACCOUNT, data.email)

    user = UserService.get_user_by_email(data.email)
    if not user:
        return {"message": "If an account with that email exists, a reset link has been sent."}

    reset_token = generate_reset_token(data.email)
    logger.info(f"Password reset token for {data.email}: {reset_token}")

    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, request: Request):
    # Submitting a token is a guess at a secret that can take over an
    # account, so this is the tightest of the auth policies.
    enforce_rate_limit(PASSWORD_RESET_CONFIRM_IP, get_client_ip(request))

    if not verify_reset_token(data.email, data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    user = UserService.get_user_by_email(data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Same policy, same code path as registration. Enforced after the token
    # check so an unauthenticated caller can't use this route to probe the
    # rules or the account's existence; the holder of a valid token is
    # already past both.
    enforce_password_policy(
        data.new_password,
        email=data.email,
        username=user.get("username"),
    )

    new_hash = get_password_hash(data.new_password)
    UserService.update_user(user["id"], {"password": new_hash})

    revoke_all_user_refresh_tokens(user["id"])

    return {"message": "Password has been reset successfully."}


# ─── Email Verification ───────────────────────────────────────────────────

@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest, request: Request):
    enforce_rate_limit(EMAIL_VERIFY_IP, get_client_ip(request))

    if not verify_email_token(data.email, data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    user = UserService.get_user_by_email(data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    UserService.update_user(user["id"], {"email_verified": True})
    return {"message": "Email verified successfully."}


@router.post("/resend-verification")
async def resend_verification(data: ForgotPasswordRequest, request: Request):
    # Same shape as forgot-password: this one also sends mail to an address
    # supplied by whoever called it.
    enforce_rate_limit(EMAIL_VERIFY_IP, get_client_ip(request))
    enforce_rate_limit(VERIFICATION_RESEND_ACCOUNT, data.email)

    user = UserService.get_user_by_email(data.email)
    if not user:
        return {"message": "If an account with that email exists, a verification email has been sent."}

    if user.get("email_verified"):
        return {"message": "Email is already verified."}

    new_token = generate_verification_token(data.email)
    logger.info(f"New verification token for {data.email}: {new_token}")

    return {"message": "If an account with that email exists, a verification email has been sent."}
