"""
Health check endpoints for monitoring and orchestration.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from ..database import get_database

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    """
    return {"status": "healthy", "service": "resume-screening-api"}


@router.get("/ready")
async def readiness_check(request: Request):
    """
    Readiness check endpoint.
    Returns 200 if the service is ready to accept traffic.
    Checks database connectivity.
    """
    try:
        # Check if database connection is available
        if not hasattr(request.app.state, "mongo_client") or request.app.state.mongo_client is None:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not ready", "reason": "database_not_connected"}
            )
        
        # Test database connection
        await request.app.state.mongo_client.admin.command("ping")
        
        return {
            "status": "ready",
            "service": "resume-screening-api",
            "database": "connected"
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "reason": "database_connection_failed",
                "error": str(e) if request.app.state.environment == "development" else "internal_error"
            }
        )


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint.
    Returns 200 if the service is alive (not crashed).
    """
    return {"status": "alive", "service": "resume-screening-api"}

