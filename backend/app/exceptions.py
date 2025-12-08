"""
Global exception handlers for production error sanitization.
"""

import logging
from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with sanitized error messages."""
    # Get environment - validated at startup, so safe to access
    environment = getattr(request.app.state, "environment", "development")
    is_production = environment == "production"
    request_id = getattr(request.state, "request_id", "unknown")

    # Log the error with full details
    logger.warning(
        "HTTP exception",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "detail": str(exc.detail),
        },
    )

    # Sanitize error message for production
    if is_production:
        # Don't expose internal error details in production
        if exc.status_code >= 500:
            detail = "Internal server error. Please contact support."
        else:
            detail = exc.detail if exc.status_code < 500 else "An error occurred."
    else:
        detail = exc.detail

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": detail,
            "request_id": request_id,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with sanitized messages."""
    request_id = getattr(request.state, "request_id", "unknown")
    environment = getattr(request.app.state, "environment", "development")
    is_production = environment == "production"

    # Log validation errors with full details
    error_details = exc.errors()
    logger.warning(
        "Validation error",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "errors": error_details,
        },
    )
    # Also log to console for easier debugging
    logger.warning(f"Validation errors: {error_details}")

    # In production, provide generic message; in dev, show details
    if is_production:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "status_code": 422,
                "message": "Validation error. Please check your input.",
                "request_id": request_id,
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "status_code": 422,
                "message": "Validation error",
                "errors": exc.errors(),
                "request_id": request_id,
            },
        )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with sanitized error messages."""
    request_id = getattr(request.state, "request_id", "unknown")
    environment = getattr(request.app.state, "environment", "development")
    is_production = environment == "production"

    # Log the full exception with stack trace
    logger.error(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        },
        exc_info=True,
    )

    # Never expose internal error details in production
    if is_production:
        message = "An internal error occurred. Please contact support."
        detail = None
    else:
        message = f"An unexpected error occurred: {type(exc).__name__}: {str(exc)}"
        detail = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "exception_args": str(exc.args) if hasattr(exc, 'args') else None,
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": message,
            "request_id": request_id,
            **({"detail": detail} if detail else {}),
        },
    )

