"""Tests for curated Google Fonts typography."""

from app.schemas.photobook import LayoutTextSlotDefinition, TextSlotValue
from app.typography.google_fonts import (
    ALLOWED_FONT_FAMILIES,
    FONT_SANS_LABEL,
    FONT_SCRIPT_DISPLAY,
    coerce_font_family,
    google_fonts_stylesheet_url,
)


def test_allowed_font_families_count() -> None:
    assert len(ALLOWED_FONT_FAMILIES) == 9


def test_coerce_font_family_exact() -> None:
    assert coerce_font_family(FONT_SCRIPT_DISPLAY) == FONT_SCRIPT_DISPLAY


def test_coerce_font_family_bare_name() -> None:
    assert coerce_font_family("Montserrat") == FONT_SANS_LABEL


def test_coerce_font_family_unknown_falls_back() -> None:
    assert coerce_font_family("Comic Sans MS") == FONT_SANS_LABEL


def test_text_slot_value_rejects_unknown_font() -> None:
    slot = TextSlotValue(text="Hello", font_family="Arial, sans-serif")
    assert slot.font_family == FONT_SANS_LABEL


def test_layout_text_slot_definition_rejects_unknown_font() -> None:
    slot = LayoutTextSlotDefinition(
        id="title",
        label="Title",
        default_font_family="Helvetica",
    )
    assert slot.default_font_family == FONT_SANS_LABEL


def test_google_fonts_stylesheet_url_includes_families() -> None:
    url = google_fonts_stylesheet_url()
    assert url.startswith("https://fonts.googleapis.com/css2?")
    assert "Great%20Vibes" in url
    assert "Montserrat" in url
    assert "display=swap" in url
