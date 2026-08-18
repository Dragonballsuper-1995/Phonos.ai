from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.posthog import init_posthog, shutdown_posthog, posthog
from app.routers import health, phones, recommend, compare
from app.db.database import get_db_pool, close_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_posthog()
    await get_db_pool()
    yield
    # Shutdown
    await close_db_pool()
    shutdown_posthog()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def posthog_analytics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000)

    # Skip noisy health-check and docs traffic
    path = request.url.path
    if path not in ("/health", "/docs", "/openapi.json", "/redoc", "/"):
        distinct_id = request.headers.get("x-user-id", "anonymous")
        posthog.capture(
            distinct_id=distinct_id,
            event="api_request",
            properties={
                "path": path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

    return response

app.include_router(health.router, tags=["health"])
app.include_router(phones.router, prefix=f"{settings.API_V1_STR}/phones", tags=["phones"])
app.include_router(recommend.router, prefix=f"{settings.API_V1_STR}/recommend", tags=["recommend"])
app.include_router(compare.router, prefix=f"{settings.API_V1_STR}/compare", tags=["compare"])

@app.get("/", tags=["root"])
async def root():
    return {
        "name": "Phonos.ai API",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
    }
