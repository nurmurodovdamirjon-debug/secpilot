from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.api.errors import ApiError, api_error_handler
from src.api.routes.assets import router as assets_router
from src.api.routes.health import router as health_router
from src.api.routes.intel import router as intel_router
from src.api.routes.metrics import router as metrics_router
from src.core.config import get_settings
from src.core.logging import configure_logging
from src.core.metrics import HTTP_REQUESTS_TOTAL


settings = get_settings()
configure_logging(settings)
logger = structlog.get_logger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.add_exception_handler(ApiError, api_error_handler)
app.include_router(assets_router)
app.include_router(intel_router)
app.include_router(health_router)
app.include_router(metrics_router)


@app.middleware("http")
async def metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
    request.state.correlation_id = correlation_id
    bind_contextvars(correlation_id=correlation_id)
    logger.info("api_request_started", method=request.method, url=str(request.url))
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("api_request_failed", method=request.method, url=str(request.url))
        raise
    finally:
        clear_contextvars()

    response.headers["X-Correlation-ID"] = correlation_id
    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        path=request.url.path,
        status=str(response.status_code),
    ).inc()
    logger.info(
        "api_request_finished",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        correlation_id=correlation_id,
    )
    return response
