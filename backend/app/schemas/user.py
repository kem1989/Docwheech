"""
User Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    firebase_uid: str = Field(..., description="Firebase user ID")


class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses"""
    id: str
    firebase_uid: str
    is_active: bool
    is_verified: bool
    profile_picture_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list responses"""
    users: list[UserResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class UserLogin(BaseModel):
    """Schema for user login"""
    id_token: str = Field(..., description="Firebase ID token")


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
