"""Structured API errors."""

from fastapi import Request
from fastapi.responses import JSONResponse
from structlog.contextvars import get_contextvars


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None) or get_contextvars().get("correlation_id")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}, "correlation_id": correlation_id},
    )
