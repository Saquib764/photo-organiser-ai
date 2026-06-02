"""Load, save, and mutate workspace photobook.json."""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from app.schemas.photobook import ChatMessage, PhotobookDocument, PhotobookPage, PhotobookPagePlan

logger = logging.getLogger(__name__)

PHOTOBOOK_FILENAME = "photobook.json"


def photobook_file_path(workspace_root: Path) -> Path:
    return workspace_root / PHOTOBOOK_FILENAME


def _new_page_id() -> str:
    return f"page-{uuid.uuid4().hex[:8]}"


def _new_chat_id() -> str:
    return f"msg-{uuid.uuid4().hex[:8]}"


def default_document() -> PhotobookDocument:
    page_id = _new_page_id()
    return PhotobookDocument(
        pages=[
            PhotobookPage(
                id=page_id,
                title="Page 1",
                narrative="",
                status="draft",
            ),
        ],
    )


def load_photobook(workspace_root: Path) -> PhotobookDocument:
    path = photobook_file_path(workspace_root)
    if not path.is_file():
        return default_document()

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        document = PhotobookDocument.model_validate(raw)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Invalid photobook file at %s, resetting", path)
        return default_document()

    if not document.pages:
        document.pages = default_document().pages
    return document


def save_photobook(workspace_root: Path, document: PhotobookDocument) -> None:
    if not document.pages:
        document.pages = default_document().pages

    path = photobook_file_path(workspace_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document.model_dump_json(indent=2), encoding="utf-8")


def ensure_photobook(workspace_root: Path) -> PhotobookDocument:
    path = photobook_file_path(workspace_root)
    if not path.is_file():
        document = default_document()
        save_photobook(workspace_root, document)
        return document
    return load_photobook(workspace_root)


def append_chat_message(
    document: PhotobookDocument,
    role: str,
    content: str,
) -> ChatMessage:
    message = ChatMessage(id=_new_chat_id(), role=role, content=content)  # type: ignore[arg-type]
    document.chat.append(message)
    return message


def clear_chat(document: PhotobookDocument) -> None:
    document.chat = []


def reset_photobook_session(document: PhotobookDocument) -> None:
    """Clear chat and reset the photobook to a fresh default (images are untouched)."""
    fresh = default_document()
    document.title = fresh.title
    document.chat = []
    document.pages = fresh.pages


def assigned_image_paths(document: PhotobookDocument) -> set[str]:
    paths: set[str] = set()
    for page in document.pages:
        paths.update(page.slots.values())
    return paths


def merge_page_extra_images(
    page: PhotobookPage,
    *path_groups: list[str],
) -> list[str]:
    """
    Merge extra-image path lists for one page, preserve first-seen order, dedupe,
    and drop paths already assigned to this page's slots.
    """
    assigned = set(page.slots.values())
    merged: list[str] = []
    seen: set[str] = set()
    for paths in path_groups:
        for path in paths:
            if not path or path in seen or path in assigned:
                continue
            seen.add(path)
            merged.append(path)
    return merged


def apply_plan(
    document: PhotobookDocument,
    pages: list[PhotobookPagePlan],
    extra_images: list[str],
) -> None:
    """Merge planner output into the document.

    ``extra_images`` from the planner is accepted for API compatibility but not
    persisted; per-page alternates are set during compose.
    """
    del extra_images
    by_id = {page.id: page for page in document.pages}
    new_pages: list[PhotobookPage] = []
    used_plan_ids: set[str] = set()
    used_titles: set[str] = set()
    used_narratives: set[str] = set()

    for plan in pages:
        # If the planner repeats an id in the same output, treat subsequent repeats as new pages.
        if plan.id:
            if plan.id in used_plan_ids:
                plan = plan.model_copy(update={"id": None})
            else:
                used_plan_ids.add(plan.id)

        title = plan.title.strip() or "Untitled page"
        if title in used_titles:
            i = 2
            while f"{title} (Part {i})" in used_titles:
                i += 1
            title = f"{title} (Part {i})"
        used_titles.add(title)

        narrative = plan.narrative.strip()
        if narrative in used_narratives:
            i = 2
            while f"{narrative}\n\n(Continued — {i})" in used_narratives:
                i += 1
            narrative = f"{narrative}\n\n(Continued — {i})"
        used_narratives.add(narrative)

        if plan.id and plan.id in by_id:
            existing = by_id[plan.id]
            existing.title = title
            existing.narrative = narrative
            if existing.layout_id != plan.layout_id:
                existing.layout_id = plan.layout_id
                existing.slots = {}
                existing.text_slots = {}
                existing.slot_offsets = {}
                existing.extra_images = []
                existing.palette_colors = []
                existing.background_color = None
                existing.composed_at = None
            existing.status = "draft"
            existing.error_message = None
            existing.composing_started_at = None
            existing.layout_error = plan.layout_id_error
            existing.categories = list(plan.categories)
            new_pages.append(existing)
        else:
            new_pages.append(
                PhotobookPage(
                    id=_new_page_id(),
                    title=title,
                    narrative=narrative,
                    layout_id=plan.layout_id,
                    categories=list(plan.categories),
                    layout_error=plan.layout_id_error,
                    status="draft",
                ),
            )

    if new_pages:
        document.pages = new_pages


def add_page(
    document: PhotobookDocument,
    title: str = "New page",
    narrative: str = "",
) -> PhotobookPage:
    page = PhotobookPage(id=_new_page_id(), title=title, narrative=narrative, status="draft")
    document.pages.append(page)
    return page


def get_page(document: PhotobookDocument, page_id: str) -> PhotobookPage | None:
    for page in document.pages:
        if page.id == page_id:
            return page
    return None


def remove_page(document: PhotobookDocument, page_id: str) -> bool:
    if len(document.pages) <= 1:
        return False
    document.pages = [p for p in document.pages if p.id != page_id]
    return True


def reorder_pages(document: PhotobookDocument, page_ids: list[str]) -> bool:
    """Reorder pages to match ``page_ids`` exactly (same ids, no duplicates)."""
    existing_ids = [page.id for page in document.pages]
    if len(page_ids) != len(existing_ids):
        return False
    if set(page_ids) != set(existing_ids):
        return False
    by_id = {page.id: page for page in document.pages}
    document.pages = [by_id[page_id] for page_id in page_ids]
    return True
