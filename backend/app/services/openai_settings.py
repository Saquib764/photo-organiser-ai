"""Persist and load the OpenAI API key from the workspace."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import HTTPException, status

from app.schemas.openai_settings import OpenAiKeyDocument

logger = logging.getLogger(__name__)

OPENAI_CONFIG_FILENAME = "openai_config.json"


def config_file_path(workspace_root: Path) -> Path:
    return workspace_root / OPENAI_CONFIG_FILENAME


def load_openai_api_key(workspace_root: Path) -> str:
    path = config_file_path(workspace_root)
    if not path.is_file():
        return ""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        document = OpenAiKeyDocument.model_validate(raw)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Invalid OpenAI config at %s, ignoring", path)
        return ""

    return document.api_key.strip()


def save_openai_api_key(workspace_root: Path, api_key: str) -> None:
    workspace_root.mkdir(parents=True, exist_ok=True)
    document = OpenAiKeyDocument(api_key=api_key.strip())
    path = config_file_path(workspace_root)
    path.write_text(document.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Saved OpenAI API key to workspace config")


def delete_openai_api_key(workspace_root: Path) -> None:
    path = config_file_path(workspace_root)
    if path.is_file():
        path.unlink()
        logger.info("Removed OpenAI API key from workspace")


def is_openai_configured(workspace_root: Path) -> bool:
    return bool(load_openai_api_key(workspace_root))


def require_openai_configured(workspace_root: Path) -> None:
    """Raise an HTTP 503 when the workspace has no OpenAI API key configured."""
    if not is_openai_configured(workspace_root):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured. Add it in Settings.",
        )


def mask_api_key(api_key: str) -> str | None:
    key = api_key.strip()
    if not key:
        return None
    if len(key) <= 8:
        return "••••••••"
    return f"{key[:3]}…{key[-4:]}"
