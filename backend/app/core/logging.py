import logging
import os
import sys
import structlog

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

shared_processors = [
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.stdlib.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]

if os.getenv("LOG_FORMAT", "json").lower() == "json":
    renderer = structlog.processors.JSONRenderer()
else:
    renderer = structlog.dev.ConsoleRenderer()

structlog.configure(
    processors=[
        *shared_processors,
        renderer,
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)

logger = structlog.get_logger()