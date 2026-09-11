from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1 import channels, epg, reference, search, streams
from app.core.config import get_settings
from app.core.database import engine
from app.core.logging import configure_logging, logger
from app.core.redis import get_redis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.app_debug)
    logger.info("startup", app=settings.app_name, env=settings.app_env)
    yield
    await engine.dispose()
    logger.info("shutdown")


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(channels.router, prefix="/api/v1")
app.include_router(streams.router, prefix="/api/v1")
app.include_router(reference.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(epg.router, prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
async def ready() -> dict:
    db_status = "ok"
    redis_status = "ok"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        redis_client = await get_redis()
        await redis_client.ping()
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "error"
    return {"status": overall, "database": db_status, "redis": redis_status}