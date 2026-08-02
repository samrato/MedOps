import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.logging.logger import correlation_id_var, logger, request_id_var
from src.infrastructure.telemetry.metrics import REQUEST_COUNT, REQUEST_LATENCY


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request_id = str(uuid.uuid4())

        correlation_id_token = correlation_id_var.set(correlation_id)
        request_id_token = request_id_var.set(request_id)

        try:
            response: Response = await call_next(request)
            execution_time = time.time() - start_time

            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Execution-Time"] = f"{execution_time:.4f}s"

            endpoint = request.url.path
            REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status_code=response.status_code).inc()
            REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(execution_time)

            logger.info(
                "Request processed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                execution_time_seconds=execution_time,
            )
            return response
        finally:
            correlation_id_var.reset(correlation_id_token)
            request_id_var.reset(request_id_token)
