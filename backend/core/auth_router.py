from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from core.auth import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,
    verify_password,
)
from models.user import UserCreate, UserResponse
from services.firestore_service import UserService

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # ─── Check if username already exists ──────────────────────────────
    existing_username = UserService.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    # ─── Check if email already exists ──────────────────────────────────
    existing_email = UserService.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # ─── Hash password and create user ─────────────────────────────────
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    user_dict["password"] = hashed_password

    user_id = UserService.create_user(user_dict)
    created_user = UserService.get_user_by_id(user_id)

    return UserResponse(
        id=created_user["id"],
        username=created_user["username"],
        email=created_user["email"],
        full_name=created_user.get("full_name"),
        created_at=created_user["created_at"],
        updated_at=created_user.get("updated_at")
    )

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserService.get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}