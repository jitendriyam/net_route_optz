import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.errors import ConflictError, NotFoundError

logger = logging.getLogger("app.api")


async def not_found(request: Request, error: NotFoundError) -> JSONResponse:
    """Return and log a not-found domain error."""
    logger.warning(
        "not_found method=%s path=%s detail=%s",
        request.method,
        request.url.path,
        error,
    )
    return JSONResponse(status_code=404, content={"detail": str(error)})


async def conflict(request: Request, error: ConflictError) -> JSONResponse:
    """Return and log a conflict domain error."""
    logger.warning(
        "conflict method=%s path=%s detail=%s",
        request.method,
        request.url.path,
        error,
    )
    return JSONResponse(status_code=409, content={"detail": str(error)})


async def database_error(request: Request, error: SQLAlchemyError) -> JSONResponse:
    """Log a database failure and return a sanitized service error."""
    logger.exception(
        "database_error method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(
        status_code=503,
        content={"detail": "Database service unavailable"},
    )


async def unexpected_error(request: Request, error: Exception) -> JSONResponse:
    """Log an unexpected failure and return a sanitized internal error."""
    logger.exception(
        "unexpected_error method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all application exception handlers on a FastAPI instance."""
    app.add_exception_handler(NotFoundError, not_found)
    app.add_exception_handler(ConflictError, conflict)
    app.add_exception_handler(SQLAlchemyError, database_error)
    app.add_exception_handler(Exception, unexpected_error)
