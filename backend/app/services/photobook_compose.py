"""OpenAI page composer: fill a pre-selected layout."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from openai import AsyncOpenAI

from app.config import settings
from app.prompts.prompts import PHOTOBOOK_COMPOSER_SYSTEM_PROMPT
from app.schemas.photobook import (
    ChatMessage,
    GalleryImageSummary,
    PageComposeResult,
    PageComposeStructured,
    PhotobookPage,
)
from app.services.couple_names import resolve_couple_names_for_compose
from app.page_layouts import (
    get_layout,
    validate_slots,
    validate_text_slots,
)
from app.services.photobook_gallery import ensure_compose_extra_images, gallery_for_compose
from app.services.photobook_openai import require_openai_api_key

logger = logging.getLogger(__name__)


async def compose_page(
    workspace_root: Path,
    page: PhotobookPage,
    gallery: list[GalleryImageSummary],
    extra_images: list[str],
    assigned_paths: set[str],
    chat: list[ChatMessage] | None = None,
) -> PageComposeResult:
    api_key = require_openai_api_key(workspace_root)

    if not page.layout_id:
        raise RuntimeError(f"Page {page.id} has no layout_id (expected to be chosen during planning)")
    layout = get_layout(page.layout_id)
    if layout is None:
        raise RuntimeError(f"Unknown layout_id on page {page.id}: {page.layout_id}")

    compose_gallery = gallery_for_compose(workspace_root, page, gallery)
    logger.info(
        "Compose page %s: sending %d images from categories %s",
        page.id,
        len(compose_gallery),
        page.categories,
    )

    user_payload: dict[str, object] = {
        "page": {
            "id": page.id,
            "title": page.title,
            "narrative": page.narrative,
            "layout_id": page.layout_id,
            "categories": page.categories,
        },
        "layout_definition": layout.model_dump(),
        "image_gallery": [c.model_dump() for c in compose_gallery],
        "current_extra_images": extra_images,
        "assigned_paths": sorted(assigned_paths),
    }
    if chat:
        user_payload["chat"] = [message.model_dump() for message in chat]

    # Metadata-only: do not send image bytes/URLs to OpenAI.
    content = json.dumps(user_payload, indent=2)

    client = AsyncOpenAI(api_key=api_key)
    completion = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": PHOTOBOOK_COMPOSER_SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_format=PageComposeStructured,
    )

    parsed_structured = completion.choices[0].message.parsed
    if parsed_structured is None:
        raise RuntimeError(f"OpenAI returned no structured compose output for page {page.id}")

    if parsed_structured.layout_id != page.layout_id:
        raise RuntimeError(
            f"Composer changed layout_id for page {page.id}: expected {page.layout_id}, got {parsed_structured.layout_id}"
        )

    slots = {item.slot_id: item.path for item in parsed_structured.slots}
    text_slots = {item.slot_id: item.value for item in parsed_structured.text_slots}
    text_slots = resolve_couple_names_for_compose(
        parsed_structured.layout_id,
        text_slots,
        chat or [],
    )
    extra_images = ensure_compose_extra_images(
        compose_gallery,
        set(slots.values()),
        assigned_paths,
        parsed_structured.extra_images,
    )
    parsed = PageComposeResult(
        layout_id=parsed_structured.layout_id,
        slots=slots,
        text_slots=text_slots,
        extra_images=extra_images,
        rationale=parsed_structured.rationale,
    )

    slot_errors = validate_slots(parsed.layout_id, parsed.slots, require_all=True)
    if slot_errors:
        msg = f"Invalid compose slots: {'; '.join(slot_errors)}"
        raise RuntimeError(msg)

    text_slot_errors = validate_text_slots(parsed.layout_id, parsed.text_slots, require_all=True)
    if text_slot_errors:
        msg = f"Invalid compose text slots: {'; '.join(text_slot_errors)}"
        raise RuntimeError(msg)

    logger.info("Composed page %s with layout %s", page.id, parsed.layout_id)
    return parsed
