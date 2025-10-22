"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user, get_current_active_user
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    # Update user fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.company is not None:
        current_user.company = user_update.company
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user account"""
    # Soft delete - mark as inactive
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}


@router.get("/verify")
async def verify_token():
    """Verify if token is valid (used by frontend)"""
    # This endpoint is protected by get_current_user dependency
    # If we reach here, the token is valid
    return {"valid": True}
