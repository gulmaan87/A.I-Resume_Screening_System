import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import Settings, get_settings
from .exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .logging_config import setup_logging
from .middleware import (
    LoggingMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from .routes import auth, dashboard, feedback, health, screening, upload

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    
    # Setup logging first
    setup_logging(environment=settings.environment)
    logger = logging.getLogger(__name__)
    
    # Validate production configuration
    if settings.environment.lower() == "production":
        validation_errors = settings.validate_production()
        if validation_errors:
            logger.error(
                "Production configuration validation failed",
                extra={"errors": validation_errors, "request_id": "startup"},
            )
            logger.error(
                "Application will start but may not function correctly in production.",
                extra={"request_id": "startup"},
            )
            # In production, we might want to fail fast
            # For now, we'll log and continue
            # sys.exit(1)  # Uncomment to fail fast in production
    
    # Store settings in app state for health checks and middleware
    app.state.environment = settings.environment
    app.state.settings = settings
    app.state.limiter = limiter
    
    logger.info(
        f"Starting application in {settings.environment} mode",
        extra={"request_id": "startup"},
    )
    
    try:
        app.state.mongo_client = AsyncIOMotorClient(settings.database_url)
        app.state.mongo_db = app.state.mongo_client[settings.mongo_db_name]
        # Test connection
        await app.state.mongo_client.admin.command("ping")
        logger.info(
            "MongoDB connection established",
            extra={"request_id": "startup", "database": settings.mongo_db_name},
        )
    except Exception as e:
        logger.warning(
            f"MongoDB connection failed: {e}. Continuing with limited functionality.",
            extra={"request_id": "startup"},
        )
        # Set to None so routes can handle gracefully
        app.state.mongo_client = None
        app.state.mongo_db = None
    
    try:
        yield
    finally:
        if app.state.mongo_client:
            app.state.mongo_client.close()
            logger.info("MongoDB connection closed", extra={"request_id": "shutdown"})


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI-Powered Cloud-Based Resume Screening System for HR",
        lifespan=lifespan,
    )

    # Add rate limiter to app state
    application.state.limiter = limiter

    # Add exception handlers (order matters - most specific first)
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, general_exception_handler)
    
    # Add rate limit exception handler
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add middleware (order matters - first added is outermost)
    # RequestIDMiddleware must be first so all other middleware can use request_id
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(LoggingMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)

    # CORS configuration - more restrictive for production
    allowed_methods = ["GET", "POST", "PUT", "DELETE"] if settings.environment == "production" else ["*"]
    allowed_headers = ["Content-Type", "Authorization", "X-Request-ID"] if settings.environment == "production" else ["*"]
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )

    # Health check endpoints (no prefix, accessible at /health)
    application.include_router(health.router)
    
    # Authentication routes (public)
    application.include_router(auth.router, prefix=settings.api_prefix)
    
    # API routes (protected - will add auth later)
    application.include_router(upload.router, prefix=settings.api_prefix)
    application.include_router(screening.router, prefix=settings.api_prefix)
    application.include_router(dashboard.router, prefix=f"{settings.api_prefix}/dashboard", tags=["Dashboard"])
    application.include_router(feedback.router, prefix=settings.api_prefix)

    # Mount static files for local storage (development only)
    if settings.environment != "production":
        storage_dir = Path(__file__).parent.parent / "storage"
        if storage_dir.exists():
            application.mount("/storage", StaticFiles(directory=str(storage_dir)), name="storage")

    return application


app = create_app()

