from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.exceptions.domain_exceptions import DomainException
from src.infrastructure.logging.logger import logger


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    logger.warning("Domain exception occurred", code=exc.code, message=exc.message, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Validation error occurred", errors=exc.errors(), path=request.url.path)
    first_error = exc.errors()[0] if exc.errors() else {}
    msg = f"{first_error.get('loc', [])}: {first_error.get('msg', 'Validation error')}"
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": msg,
            },
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled internal server error", error=str(exc), path=request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred. Please contact support.",
            },
        },
    )
