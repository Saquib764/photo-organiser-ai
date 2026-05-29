"""Read photobook prompt template ideas from backend/prompt-template/."""

from __future__ import annotations

import re
from pathlib import Path

from app.config import BACKEND_ROOT

PROMPT_TEMPLATE_DIR = BACKEND_ROOT / "prompt-template"


def format_template_display_name(stem: str) -> str:
    """Capitalise words and replace dashes/underscores with spaces."""
    words = re.split(r"[-_]+", stem.strip())
    return " ".join(word.capitalize() for word in words if word)


def _template_dir() -> Path:
    PROMPT_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    return PROMPT_TEMPLATE_DIR


def _is_safe_template_id(template_id: str) -> bool:
    if not template_id or template_id in {".", ".."}:
        return False
    if "/" in template_id or "\\" in template_id:
        return False
    return Path(template_id).name == template_id


def _resolve_template_path(template_id: str) -> Path:
    if not _is_safe_template_id(template_id):
        raise ValueError("invalid template id")

    root = _template_dir().resolve()
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        if path.stem != template_id:
            continue
        resolved = path.resolve()
        if not str(resolved).startswith(str(root)):
            raise ValueError("invalid template path")
        return resolved
    raise FileNotFoundError(template_id)


def list_prompt_templates() -> list[dict[str, str]]:
    root = _template_dir()
    templates: list[dict[str, str]] = []
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        stem = path.stem
        templates.append(
            {
                "id": stem,
                "name": format_template_display_name(stem),
            }
        )
    return templates


def read_prompt_template(template_id: str) -> dict[str, str]:
    path = _resolve_template_path(template_id)
    content = path.read_text(encoding="utf-8")
    stem = path.stem
    return {
        "id": stem,
        "name": format_template_display_name(stem),
        "content": content,
    }
