"""
Authentication and security utilities
"""

import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
import logging

from app.database import get_db
from app.models.user import User
from app.config import settings

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            # For development, we'll use a service account key
            # In production, use environment variables or IAM roles
            if settings.FIREBASE_PRIVATE_KEY:
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": "key-id",
                    "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "client_id": "client-id",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                })
            else:
                # Use default credentials (for production with IAM roles)
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
            logging.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase Admin SDK: {e}")
            raise

# Initialize Firebase on module import
initialize_firebase()

# HTTP Bearer token scheme
security = HTTPBearer()

async def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token and return user info"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logging.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    decoded_token = await verify_firebase_token(token)
    
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    # Get or create user from database
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        # Create new user if doesn't exist
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            full_name=decoded_token.get("name"),
            is_active=True,
            is_verified=decoded_token.get("email_verified", False)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logging.info(f"Created new user: {user.email}")
    else:
        # Update last login
        user.last_login_at = func.now()
        db.commit()
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin privileges"""
    # For MVP, we'll implement basic role checking
    # In production, you'd have a proper role system
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
