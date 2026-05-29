"""Sync photobook page sheet colors from slot images."""

from __future__ import annotations

from pathlib import Path

from app.schemas.photobook import PhotobookDocument, PhotobookPage
from app.services.image_features import palette_hex_from_file
from app.services.image_files import resolve_processed_image_path
from app.services.photobook_gallery import path_exists_in_processed

_PREFERRED_SLOT_KEYS = (
    "hero",
    "feature",
    "left",
    "right",
    "tl",
    "tr",
    "bl",
    "br",
    "s1",
    "s2",
    "s3",
)


def preferred_slot_path(slots: dict[str, str]) -> str | None:
    for key in _PREFERRED_SLOT_KEYS:
        if path := slots.get(key):
            return path
    return next((path for path in slots.values() if path), None)


def sync_page_sheet_colors(workspace_root: Path, page: PhotobookPage) -> None:
    """Extract palette (up to 3) and select the first as background_color."""
    rel = preferred_slot_path(page.slots)
    if not rel or not path_exists_in_processed(workspace_root, rel):
        page.palette_colors = []
        page.background_color = None
        return
    page.palette_colors = palette_hex_from_file(resolve_processed_image_path(workspace_root, rel))
    page.background_color = page.palette_colors[0] if page.palette_colors else None


def sync_missing_page_palettes(workspace_root: Path, document: PhotobookDocument) -> bool:
    """Backfill palettes for pages with images but no stored palette. Returns True if any changed."""
    changed = False
    for page in document.pages:
        if page.slots and any(page.slots.values()) and not page.palette_colors:
            sync_page_sheet_colors(workspace_root, page)
            changed = True
    return changed
