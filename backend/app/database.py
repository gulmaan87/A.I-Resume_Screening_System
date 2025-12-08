from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import Settings, get_settings


async def get_database(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> AsyncIOMotorDatabase:
    """Dependency to get the MongoDB database instance."""
    if not hasattr(request.app.state, "mongo_client") or request.app.state.mongo_client is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Database connection not available. Please check MongoDB configuration."
        )
    return request.app.state.mongo_client[settings.mongo_db_name]

