from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=6,
        max_length=30,
        description="Username (6-30 characters, alphanumeric and underscore only)"
    )
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, max_length=100)

    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores.')
        if len(v) < 6:
            raise ValueError('Username must be at least 6 characters long.')
        if len(v) > 30:
            raise ValueError('Username must not exceed 30 characters.')
        return v

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None