"""Tests for bride/groom name extraction during compose."""

from app.page_layouts import merge_text_slots
from app.schemas.photobook import ChatMessage, TextSlotValue
from app.services.couple_names import (
    CoupleNames,
    extract_couple_names_from_chat,
    resolve_couple_names_for_compose,
)
from app.typography.google_fonts import FONT_SANS_LABEL, FONT_SCRIPT_DISPLAY


def test_extract_couple_names_from_chat_bride_then_groom() -> None:
    chat = [
        ChatMessage(
            id="m1",
            role="user",
            content="Bride name is Atiya and Groom is Saquib",
        ),
    ]
    couple = extract_couple_names_from_chat(chat)
    assert couple == CoupleNames(bride="Atiya", groom="Saquib")
    assert couple.display() == "Atiya & Saquib"


def test_resolve_couple_names_uses_chat_during_compose() -> None:
    chat = [
        ChatMessage(
            id="m1",
            role="user",
            content="Bride name is Atiya and Groom is Saquib",
        ),
    ]
    resolved = resolve_couple_names_for_compose(
        "wedding_cover",
        {
            "couple_names": TextSlotValue(text="Groomy and Bridey"),
            "wedding_date": TextSlotValue(text="JUNE 1, 2027"),
        },
        chat,
    )
    assert resolved["couple_names"].text == "Atiya & Saquib"
    assert resolved["couple_names"].font_family == FONT_SCRIPT_DISPLAY
    assert resolved["wedding_date"].text == "JUNE 1, 2027"


def test_resolve_couple_names_uses_defaults_when_chat_has_no_names() -> None:
    resolved = resolve_couple_names_for_compose(
        "wedding_cover",
        {"couple_names": TextSlotValue(text="")},
        [],
    )
    assert resolved["couple_names"].text == "Groomy and Bridey"


def test_resolve_couple_names_keeps_custom_composer_text() -> None:
    chat = [
        ChatMessage(
            id="m1",
            role="user",
            content="Bride name is Atiya and Groom is Saquib",
        ),
    ]
    resolved = resolve_couple_names_for_compose(
        "wedding_cover",
        {"couple_names": TextSlotValue(text="Custom Names Here")},
        chat,
    )
    assert resolved["couple_names"].text == "Custom Names Here"


def test_merge_text_slots_keeps_layout_font_when_override_blank() -> None:
    merged = merge_text_slots(
        "wedding_cover",
        {
            "couple_names": TextSlotValue(
                text="",
                font_family="",
                font_size="",
            ),
            "wedding_date": TextSlotValue(text="JUNE 1, 2027"),
        },
    )
    assert merged["couple_names"].text == "Groomy and Bridey"
    assert merged["couple_names"].font_family == FONT_SCRIPT_DISPLAY
    assert merged["wedding_date"].text == "JUNE 1, 2027"
    assert merged["wedding_date"].font_family == FONT_SANS_LABEL
