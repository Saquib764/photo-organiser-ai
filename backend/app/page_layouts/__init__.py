"""Canonical page layout library (mirrors frontend page_layouts/*.json library files)."""

from app.page_layouts.registry import (
    LAYOUTS,
    default_text_slots,
    get_layout,
    layout_catalog_for_prompt,
    layout_slot_ids,
    layout_text_slot_ids,
    list_layouts,
    merge_text_slots,
    validate_slots,
    validate_text_slots,
)

__all__ = [
    "LAYOUTS",
    "default_text_slots",
    "get_layout",
    "layout_catalog_for_prompt",
    "layout_slot_ids",
    "layout_text_slot_ids",
    "list_layouts",
    "merge_text_slots",
    "validate_slots",
    "validate_text_slots",
]
