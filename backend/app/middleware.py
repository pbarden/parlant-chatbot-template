from __future__ import annotations
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import uuid
from .core.logging import logger

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = str(uuid.uuid4())
        start = time.monotonic()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            dur_ms = int((time.monotonic() - start) * 1000)
            logger.info("http_request", method=request.method, path=request.url.path, status=getattr(response, "status_code", 0), ms=dur_ms, rid=rid)