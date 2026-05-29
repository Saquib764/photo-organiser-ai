"""Workspace settings API (OpenAI API key)."""

import logging

from fastapi import APIRouter, Response, status

from app.config import settings
from app.schemas.openai_settings import OpenAiKeyStatusResponse, OpenAiKeyUpdateRequest
from app.services.openai_settings import (
    delete_openai_api_key,
    load_openai_api_key,
    mask_api_key,
    save_openai_api_key,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.api_v1_prefix, tags=["settings"])


@router.get("/settings/openai-key", response_model=OpenAiKeyStatusResponse)
async def get_openai_key() -> OpenAiKeyStatusResponse:
    api_key = load_openai_api_key(settings.workspace_root)
    configured = bool(api_key)
    return OpenAiKeyStatusResponse(
        configured=configured,
        masked_key=mask_api_key(api_key) if configured else None,
    )


@router.put("/settings/openai-key", response_model=OpenAiKeyStatusResponse)
async def put_openai_key(body: OpenAiKeyUpdateRequest) -> OpenAiKeyStatusResponse:
    save_openai_api_key(settings.workspace_root, body.api_key)
    api_key = load_openai_api_key(settings.workspace_root)
    return OpenAiKeyStatusResponse(
        configured=True,
        masked_key=mask_api_key(api_key),
    )


@router.delete("/settings/openai-key", status_code=status.HTTP_204_NO_CONTENT)
async def delete_openai_key() -> Response:
    delete_openai_api_key(settings.workspace_root)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
