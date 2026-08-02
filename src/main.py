from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.api.middlewares.correlation import CorrelationMiddleware
from src.api.middlewares.error_handler import (
    domain_exception_handler,
    global_exception_handler,
    validation_exception_handler,
)
from src.api.middlewares.rate_limiter import RateLimiterMiddleware
from src.api.middlewares.security_headers import SecurityHeadersMiddleware
from src.api.v1.router import root_router
from src.domain.exceptions.domain_exceptions import DomainException
from src.infrastructure.cache.redis_client import redis_cache
from src.infrastructure.config.settings import settings
from src.infrastructure.logging.logger import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    setup_logging()
    logger.info("Starting MedOps application...", env=settings.APP_ENV)
    await redis_cache.connect()
    yield
    # Shutdown logic
    logger.info("Shutting down MedOps application...")
    await redis_cache.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Production-Ready Enterprise Clinic Appointment Booking Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security & Custom Middlewares
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(RateLimiterMiddleware)

    # Exception Handlers
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Include Routes
    app.include_router(root_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
