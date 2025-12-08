"""
Authentication routes for user registration, login, and token management.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, OperationFailure

from pydantic import BaseModel

from ..config import get_settings
from ..database import get_database
from ..dependencies.auth import get_current_active_user
from ..models.user_model import Token, UserCreate, UserLogin, UserResponse
from ..rate_limit import api_rate_limit
from ..services.auth import AuthService, get_auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service),
    _rate_limit: None = Depends(api_rate_limit),
):
    """
    Register a new user.
    
    Creates a new user account with hashed password.
    """
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user - convert Pydantic model to dict
    # Use dict() for Pydantic v1 compatibility, model_dump() for v2
    try:
        user_dict = user_data.model_dump()  # Pydantic v2
    except AttributeError:
        user_dict = user_data.dict()  # Pydantic v1
    
    # Create user in database
    try:
        user = await auth_service.create_user(db, user_dict)
    except DuplicateKeyError:
        # Handle race condition where user was created between check and insert
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    except OperationFailure as e:
        logger.error(f"Database operation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed. Please try again.",
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {type(e).__name__}: {e}", exc_info=True)
        # In development, show the actual error
        import os
        if os.getenv("ENVIRONMENT", "development").lower() != "production":
            detail = f"Failed to create user: {type(e).__name__}: {str(e)}"
        else:
            detail = "Failed to create user. Please try again."
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user. Please try again.",
        )
    
    # Return user response - UserResponse will validate the data
    try:
        response = UserResponse(**user)
        return response
    except Exception as e:
        logger.error(f"Error creating UserResponse: {type(e).__name__}: {e}", exc_info=True)
        logger.error(f"User data that failed: {user}")
        logger.error(f"User data types: {[(k, type(v).__name__) for k, v in user.items()]}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user response: {str(e)}",
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service),  # Proper dependency injection
    _rate_limit: None = Depends(api_rate_limit),  # Rate limit login attempts
):
    """
    Login and get access token.
    
    Authenticates user with email and password, returns JWT tokens.
    """
    
    # Authenticate user
    user = await auth_service.authenticate_user(
        db, credentials.email, credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = auth_service.create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service),  # Proper dependency injection
):
    """
    Refresh access token using refresh token.
    
    Generates a new access token from a valid refresh token.
    """
    
    # Decode refresh token
    payload = auth_service.decode_token(request.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Get user ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Verify user exists and is active
    user = await auth_service.get_user_by_id(db, user_id)
    if user is None or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token = auth_service.create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    new_refresh_token = auth_service.create_refresh_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
):
    """
    Get current authenticated user information.
    
    Returns the user data for the authenticated user.
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        is_active=current_user.get("is_active", True),
        is_superuser=current_user.get("is_superuser", False),
        created_at=current_user.get("created_at"),
        updated_at=current_user.get("updated_at"),
    )

