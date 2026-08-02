import logging
import sys
from contextvars import ContextVar

import structlog

# ContextVars for request and correlation IDs
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="N/A")
request_id_var: ContextVar[str] = ContextVar("request_id", default="N/A")


def add_correlation_data(logger: logging.Logger, method_name: str, event_dict: dict) -> dict:
    event_dict["correlation_id"] = correlation_id_var.get()
    event_dict["request_id"] = request_id_var.get()
    return event_dict


def setup_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_correlation_data,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()
