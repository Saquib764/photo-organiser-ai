"""Shared OpenAI helpers for photobook services."""

from __future__ import annotations

from pathlib import Path

from app.services.openai_settings import load_openai_api_key

_OPENAI_KEY_MSG = "OpenAI API key is not configured in workspace settings"


def require_openai_api_key(workspace_root: Path) -> str:
    api_key = load_openai_api_key(workspace_root)
    if not api_key:
        raise RuntimeError(_OPENAI_KEY_MSG)
    return api_key
