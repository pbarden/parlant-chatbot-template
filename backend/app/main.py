from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from .core.config import settings
from .api.routes import health, clients, sessions, events
from .middleware import RequestContextMiddleware

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Middleware
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(clients.router, prefix=settings.API_V1_STR)
app.include_router(sessions.router, prefix=settings.API_V1_STR)
app.include_router(events.router, prefix=settings.API_V1_STR)

# Metrics
REQUESTS = Counter("app_requests_total", "Total HTTP requests")

@app.middleware("http")
async def _count_requests(request, call_next):
    REQUESTS.inc()
    return await call_next(request)

@app.get("/metrics")
async def _metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def create_app():  # for uvicorn --factory
    return app