from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers import health, phones, recommend, compare
from app.db.database import get_db_pool, close_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await get_db_pool()
    yield
    # Shutdown
    await close_db_pool()

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

app.include_router(health.router, tags=["health"])
app.include_router(phones.router, prefix=f"{settings.API_V1_STR}/phones", tags=["phones"])
app.include_router(recommend.router, prefix=f"{settings.API_V1_STR}/recommend", tags=["recommend"])
app.include_router(compare.router, prefix=f"{settings.API_V1_STR}/compare", tags=["compare"])
