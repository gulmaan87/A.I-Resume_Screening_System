"""
Authentication dependencies for FastAPI routes.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config import get_settings
from ..database import get_database
from ..models.user_model import UserResponse
from ..services.auth import AuthService, get_auth_service

logger = logging.getLogger(__name__)

# HTTPBearer security scheme for token extraction
security_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="JWT token authentication",
    auto_error=False,  # We'll handle errors ourselves
)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Get the current authenticated user from JWT token.
    
    This dependency extracts the JWT token from the Authorization header
    using FastAPI's HTTPBearer security scheme, validates it, and returns
    the user data.
    
    Args:
        request: FastAPI request object
        credentials: HTTPBearer credentials (automatically extracted)
        db: Database dependency
        auth_service: Auth service dependency
    
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    # Check if credentials were provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Decode token
    payload = auth_service.decode_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id: Optional[str] = payload.get("sub")  # 'sub' is standard JWT claim for subject
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get the current active user.
    
    This dependency ensures the user is not only authenticated but also active.
    
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_superuser(
    current_user: dict = Depends(get_current_active_user),
) -> dict:
    """
    Get the current superuser.
    
    This dependency ensures the user is a superuser (admin).
    
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

