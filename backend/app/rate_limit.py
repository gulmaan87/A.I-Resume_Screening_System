"""
Proper rate limiting implementation using slowapi with FastAPI.

This module provides a clean, maintainable way to add rate limiting to FastAPI routes.
Uses slowapi's proper integration pattern with FastAPI dependency injection.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.extension import _rate_limit_exceeded_handler


def get_limiter(request: Request) -> Limiter:
    """
    Get rate limiter from app state.
    This is the proper way to access the limiter in FastAPI.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Limiter instance from app state
    """
    return request.app.state.limiter


def create_rate_limit_dependency(limit: str):
    """
    Create a rate limit dependency for FastAPI routes using slowapi.
    
    This is the PROPER way to use slowapi with FastAPI - using dependency injection.
    The limiter will raise RateLimitExceeded if the limit is exceeded, which is
    caught by the exception handler in main.py.
    
    Usage:
        @router.post("/endpoint")
        async def my_endpoint(
            request: Request,
            _rate_limit: None = Depends(upload_rate_limit)
        ):
            # Your endpoint code here
            ...
    
    Args:
        limit: Rate limit string (e.g., "10/minute", "100/hour", "5/second")
               Format: "{number}/{unit}" where unit is second, minute, hour, or day
    
    Returns:
        Dependency function that enforces the rate limit
        Returns None if limit not exceeded
        Raises RateLimitExceeded if limit exceeded (handled by exception handler)
    """
    async def rate_limit_dependency(request: Request) -> None:
        """
        FastAPI dependency that enforces rate limiting.
        
        This function is called by FastAPI's dependency injection system before
        the route handler executes. If the rate limit is exceeded, it raises
        RateLimitExceeded, which is caught by the exception handler.
        
        Args:
            request: FastAPI request object
            
        Raises:
            RateLimitExceeded: If the rate limit is exceeded
        """
        limiter = get_limiter(request)
        # Create a properly named async function for the decorator
        # slowapi requires the parameter to be named "request" (not "req")
        async def _rate_limit_check(request: Request):
            """Internal function for rate limit checking"""
            return None
        
        # Apply the limit decorator to the function
        # This creates a wrapped function that checks the rate limit
        decorated_func = limiter.limit(limit)(_rate_limit_check)
        
        # Call the decorated function with the request
        # This will raise RateLimitExceeded if the limit is exceeded
        await decorated_func(request)
        return None  # Dependency doesn't need to return anything
    
    return rate_limit_dependency


# Pre-configured rate limit dependencies for common use cases
# These can be imported and used directly in route handlers

# Upload endpoint: 10 requests per minute per IP
upload_rate_limit = create_rate_limit_dependency("10/minute")

# General API: 100 requests per hour per IP
api_rate_limit = create_rate_limit_dependency("100/hour")

# Strict endpoint: 5 requests per minute per IP
strict_rate_limit = create_rate_limit_dependency("5/minute")

# Very permissive: 1000 requests per hour per IP
permissive_rate_limit = create_rate_limit_dependency("1000/hour")

