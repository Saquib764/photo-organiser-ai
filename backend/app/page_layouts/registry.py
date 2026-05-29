"""Registry helpers for the page layout library."""

from __future__ import annotations

from app.page_layouts.cover_pages import LAYOUTS as COVER_PAGE_LAYOUTS
from app.page_layouts.photo_grids import LAYOUTS as PHOTO_GRID_LAYOUTS
from app.page_layouts.wedding_album import LAYOUTS as WEDDING_ALBUM_LAYOUTS
from app.schemas.photobook import LayoutDefinition, TextSlotValue

LAYOUTS: tuple[LayoutDefinition, ...] = (
    *PHOTO_GRID_LAYOUTS,
    *COVER_PAGE_LAYOUTS,
    *WEDDING_ALBUM_LAYOUTS,
)

_LAYOUT_BY_ID: dict[str, LayoutDefinition] = {layout.id: layout for layout in LAYOUTS}


def list_layouts() -> list[LayoutDefinition]:
    return list(LAYOUTS)


def get_layout(layout_id: str) -> LayoutDefinition | None:
    return _LAYOUT_BY_ID.get(layout_id)


def layout_slot_ids(layout_id: str) -> set[str]:
    layout = get_layout(layout_id)
    if layout is None:
        return set()
    return {slot.id for slot in layout.slots}


def layout_text_slot_ids(layout_id: str) -> set[str]:
    layout = get_layout(layout_id)
    if layout is None:
        return set()
    return {slot.id for slot in layout.text_slots}


def default_text_slots(layout_id: str) -> dict[str, TextSlotValue]:
    layout = get_layout(layout_id)
    if layout is None:
        return {}
    return {
        slot.id: TextSlotValue(
            text=slot.default_text,
            font_family=slot.default_font_family,
            font_size=slot.default_font_size,
            font_weight=slot.default_font_weight,
            letter_spacing=slot.default_letter_spacing,
            text_align=slot.default_text_align,
            text_transform=slot.default_text_transform,
        )
        for slot in layout.text_slots
    }


def _text_slot_override_fields(override: TextSlotValue) -> dict[str, str]:
    """Apply page overrides without blank text or typography wiping layout defaults."""
    fields = override.model_dump(exclude_unset=True)
    if not fields.get("text", "").strip():
        fields.pop("text", None)
    for key in ("font_family", "font_size", "font_weight", "letter_spacing", "text_align", "text_transform", "color"):
        if key in fields and not str(fields[key]).strip():
            fields.pop(key)
    return fields


def merge_text_slots(
    layout_id: str,
    page_text_slots: dict[str, TextSlotValue],
) -> dict[str, TextSlotValue]:
    """Merge page overrides with layout defaults for rendering."""
    layout = get_layout(layout_id)
    if layout is None:
        return page_text_slots

    merged: dict[str, TextSlotValue] = {}
    for slot in layout.text_slots:
        defaults = TextSlotValue(
            text=slot.default_text,
            font_family=slot.default_font_family,
            font_size=slot.default_font_size,
            font_weight=slot.default_font_weight,
            letter_spacing=slot.default_letter_spacing,
            text_align=slot.default_text_align,
            text_transform=slot.default_text_transform,
        )
        override = page_text_slots.get(slot.id)
        if override is None:
            merged[slot.id] = defaults
            continue
        merged[slot.id] = defaults.model_copy(
            update=_text_slot_override_fields(override),
        )
    return merged


def layout_catalog_for_prompt(*, include_slot_ids: bool = False) -> list[dict[str, object]]:
    """Serialize layouts for OpenAI prompts."""
    catalog: list[dict[str, object]] = []
    for layout in LAYOUTS:
        item: dict[str, object] = {
            "id": layout.id,
            "name": layout.name,
            "description": layout.description,
        }
        if layout.metadata is not None:
            item["metadata"] = layout.metadata.model_dump()
        if layout.color_guidance is not None:
            item["color_guidance"] = layout.color_guidance.model_dump()
        if include_slot_ids:
            item["slots"] = [slot.id for slot in layout.slots]
            item["text_slots"] = [
                {
                    "id": slot.id,
                    "label": slot.label,
                    "default_text": slot.default_text,
                    "color_hint": slot.color_hint,
                    "default_font_family": slot.default_font_family,
                    "default_font_size": slot.default_font_size,
                    "default_font_weight": slot.default_font_weight,
                    "default_letter_spacing": slot.default_letter_spacing,
                    "default_text_align": slot.default_text_align,
                    "default_text_transform": slot.default_text_transform,
                }
                for slot in layout.text_slots
            ]
        text_count = len(layout.text_slots)
        item["supports_text"] = text_count > 0
        item["text_slot_count"] = text_count
        if layout.page_role:
            item["page_role"] = layout.page_role
        catalog.append(item)
    return catalog


def validate_text_slots(
    layout_id: str,
    text_slots: dict[str, object],
    *,
    require_all: bool = False,
) -> list[str]:
    """Return validation errors for text slot keys (empty if valid)."""
    layout = get_layout(layout_id)
    if layout is None:
        return [f"Unknown layout_id: {layout_id}"]

    expected = {slot.id for slot in layout.text_slots}
    provided = set(text_slots.keys())
    extra = provided - expected
    errors: list[str] = []
    if require_all:
        missing = expected - provided
        if missing:
            errors.append(f"Missing text_slots: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected text_slots: {sorted(extra)}")
    return errors


def validate_slots(
    layout_id: str,
    slots: dict[str, str],
    *,
    require_all: bool = False,
) -> list[str]:
    """Return validation errors (empty if valid)."""
    layout = get_layout(layout_id)
    if layout is None:
        return [f"Unknown layout_id: {layout_id}"]

    expected = {slot.id for slot in layout.slots}
    provided = set(slots.keys())
    extra = provided - expected
    errors: list[str] = []
    if require_all:
        missing = expected - provided
        if missing:
            errors.append(f"Missing slots: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected slots: {sorted(extra)}")
    return errors
