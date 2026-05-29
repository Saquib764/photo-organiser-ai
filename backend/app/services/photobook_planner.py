"""OpenAI photobook planner: story planning from the image category catalog."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from openai import AsyncOpenAI

from app.config import settings
from app.prompts.prompts import PHOTOBOOK_PLANNER_SYSTEM_PROMPT
from app.schemas.photobook import (
    ImageCatalogEntry,
    PhotobookDocument,
    PhotobookPlanResult,
)
from app.page_layouts import layout_catalog_for_prompt
from app.services.image_categoriser import load_categories_document
from app.services.photobook_openai import require_openai_api_key
from app.services.photobook_plan_validation import validate_plan_categories

logger = logging.getLogger(__name__)


def _yaml_dump(data: object) -> str:
    return yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)


def build_image_catalog(workspace_root: Path) -> list[ImageCatalogEntry]:
    """Category catalog for the planner: id and description only."""
    document = load_categories_document(workspace_root)
    return [
        ImageCatalogEntry(id=category.id, description=category.description)
        for category in document.categories
        if category.images
    ]


def require_image_catalog(workspace_root: Path) -> list[ImageCatalogEntry]:
    catalog = build_image_catalog(workspace_root)
    if not catalog:
        msg = "Run categorisation in Library before planning a photobook."
        raise RuntimeError(msg)
    return catalog


def _build_planner_user_message(
    user_message: str,
    image_catalog: list[ImageCatalogEntry],
    document: PhotobookDocument,
) -> str:
    current_pages = [
        {
            "id": p.id,
            "title": p.title,
            "narrative": p.narrative,
            "layout_id": p.layout_id,
            "categories": p.categories,
        }
        for p in document.pages
    ]
    template_catalog = layout_catalog_for_prompt(include_slot_ids=True)
    catalog_payload = [entry.model_dump() for entry in image_catalog]

    sections = [
        "## User request\n\n"
        "What the user wants for this photobook:\n\n"
        f"{user_message.strip()}\n",
        "## Image catalog\n\n"
        "Story categories from the library pipeline. Each entry has an `id` and `description`. "
        "Use these to decide page sequencing, density, and section allocation. "
        "Each page in your output must include 1–3 category `id` values from this catalog "
        "so a later compose step can pick photos.\n\n"
        f"{_yaml_dump(catalog_payload)}",
        "## Layout template catalog\n\n"
        "Available page templates. Each page must use a `layout_id` from this catalog.\n\n"
        "Each entry includes `supports_text` and `text_slot_count`. "
        "When `text_slot_count` is 0, the layout is photo-only. "
        "Non-empty `text_slots` lists the typography areas the compose step will fill.\n\n"
        f"{_yaml_dump(template_catalog)}",
    ]

    if document.title:
        sections.insert(
            1,
            "## Photobook title\n\n"
            f"{document.title.strip()}\n",
        )

    if current_pages:
        sections.append(
            "## Current photobook pages\n\n"
            "Existing pages to update (reuse `id` when editing) or replace.\n\n"
            f"{_yaml_dump(current_pages)}",
        )

    return "\n".join(sections)


async def plan_photobook(
    workspace_root: Path,
    document: PhotobookDocument,
    user_message: str,
) -> PhotobookPlanResult:
    image_catalog = require_image_catalog(workspace_root)
    user_content = _build_planner_user_message(user_message, image_catalog, document)

    api_key = require_openai_api_key(workspace_root)
    client = AsyncOpenAI(api_key=api_key)
    completion = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": PHOTOBOOK_PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format=PhotobookPlanResult,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        msg = "OpenAI returned no structured planner output"
        raise RuntimeError(msg)

    valid_category_ids = {entry.id for entry in image_catalog}
    category_issues = validate_plan_categories(parsed.pages, valid_category_ids)
    if category_issues:
        details = "; ".join(
            f'page {issue.page_index} "{issue.title}": {issue.error}'
            for issue in category_issues
        )
        msg = f"Photobook plan has invalid categories: {details}"
        raise RuntimeError(msg)

    logger.info("Photobook plan: %d pages", len(parsed.pages))
    return parsed
