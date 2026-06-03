"""Photo Organiser API — FastAPI entry point."""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.images import router as images_router
from app.api.persons import router as persons_router
from app.api.photobook import router as photobook_router
from app.api.prompt_templates import router as prompt_templates_router
from app.api.settings import router as settings_router
from app.api.ws import router as ws_router
from app.config import settings
from app.services.pipeline_runner import maybe_advance_pipeline
from app.services.pipeline_state import refresh_pipeline_state
from app.services.workspace import ensure_workspace_dirs

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.service_name, settings.service_version)
    ensure_workspace_dirs(settings.workspace_root)
    await asyncio.to_thread(refresh_pipeline_state, settings.workspace_root)
    await maybe_advance_pipeline(settings.workspace_root)
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Photo Organiser API",
    description="AI-powered photo album organisation",
    version=settings.service_version,
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(images_router)
app.include_router(persons_router)
app.include_router(photobook_router)
app.include_router(prompt_templates_router)
app.include_router(settings_router)
app.include_router(ws_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    if response.status_code >= 400:
        logger.warning(
            "%s %s -> %s (%.0fms)",
            request.method,
            request.url.path,
            response.status_code,
            (time.time() - start) * 1000,
        )
    return response


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/version")
async def version() -> dict[str, Any]:
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "git_commit": settings.git_commit,
        "build_timestamp": settings.build_timestamp,
        "uptime_seconds": int(time.time() - START_TIME),
    }
