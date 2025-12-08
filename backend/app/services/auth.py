"""
Authentication service for user management and JWT tokens.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from passlib.context import CryptContext

from ..config import Settings, get_settings
from .db_utils import convert_mongo_doc

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.secret_key = self.settings.jwt_secret_key
        self.algorithm = self.settings.jwt_algorithm
        self.access_token_expire_minutes = self.settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.jwt_refresh_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
                return None
            return payload
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            return None

    async def get_user_by_email(
        self, db: AsyncIOMotorDatabase, email: str
    ) -> Optional[dict]:
        """Get user by email from database."""
        user = await db.users.find_one({"email": email})
        return convert_mongo_doc(user)

    async def get_user_by_id(
        self, db: AsyncIOMotorDatabase, user_id: str
    ) -> Optional[dict]:
        """Get user by ID from database."""
        from bson import ObjectId
        if not ObjectId.is_valid(user_id):
            return None
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        return convert_mongo_doc(user)

    async def create_user(
        self, db: AsyncIOMotorDatabase, user_data: dict
    ) -> Optional[dict]:
        """
        Create a new user in the database.
        
        Args:
            db: Database instance
            user_data: Dictionary containing user data (email, password, full_name, etc.)
            
        Returns:
            Dictionary with user data including id, or None if user already exists
            
        Raises:
            Exception: Re-raises any database or other exceptions for proper error handling
        """
        # Validate required fields
        if not user_data.get("email"):
            raise ValueError("Email is required")
        if not user_data.get("password"):
            raise ValueError("Password is required")

        # Check if user already exists
        existing_user = await self.get_user_by_email(db, user_data["email"])
        if existing_user:
            return None

        # Create a new dict to avoid mutating the input
        now = datetime.now(timezone.utc)
        user_doc = {
            "email": user_data["email"],
            "hashed_password": self.get_password_hash(user_data["password"]),
            "full_name": user_data.get("full_name"),
            "is_active": user_data.get("is_active", True),
            "is_superuser": user_data.get("is_superuser", False),
            "created_at": now,
            "updated_at": now,
        }

        # Insert user into database - exceptions will bubble up to route handler
        result = await db.users.insert_one(user_doc)
        
        if not result.inserted_id:
            logger.error("Database insert failed - no inserted_id returned")
            raise RuntimeError("Database insert failed - no inserted_id returned")

        # Return user data in API format (with id, not _id)
        return {
            "id": str(result.inserted_id),
            "email": user_doc["email"],
            "full_name": user_doc.get("full_name"),
            "is_active": user_doc["is_active"],
            "is_superuser": user_doc["is_superuser"],
            "created_at": user_doc["created_at"],
            "updated_at": user_doc["updated_at"],
        }

    async def authenticate_user(
        self, db: AsyncIOMotorDatabase, email: str, password: str
    ) -> Optional[dict]:
        """Authenticate a user with email and password."""
        user = await self.get_user_by_email(db, email)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        if not user.get("is_active", True):
            return None
        return user


# Dependency injection pattern - no global state
def get_auth_service(settings: Optional[Settings] = None) -> AuthService:
    """
    Get an auth service instance.
    
    This function creates a new instance each time, allowing proper
    dependency injection and testing. FastAPI will cache dependencies
    automatically if needed.
    
    Args:
        settings: Optional settings override (for testing)
    
    Returns:
        AuthService instance
    """
    return AuthService(settings=settings)

