from fastapi import APIRouter, HTTPException

from src.core.config import get_settings
from src.db.session import check_database_ready, check_database_schema_ready
from src.integrations.redis import check_redis_ready


router = APIRouter(tags=["health"])


@router.get("/health/live")
@router.get("/health")
def live() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/health/ready")
@router.get("/ready")
def ready() -> dict[str, object]:
    database_ready = check_database_ready()
    redis_ready = check_redis_ready()
    schema_ready = check_database_schema_ready() if database_ready else False
    dependencies = {"database": database_ready, "redis": redis_ready, "schema": schema_ready}
    if not all(dependencies.values()):
        raise HTTPException(status_code=503, detail={"status": "not_ready", "dependencies": dependencies})
    return {"status": "ready", "dependencies": dependencies}
