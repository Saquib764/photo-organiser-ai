"""Extract bride/groom names from user chat for compose."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.page_layouts import layout_text_slot_ids, merge_text_slots
from app.schemas.photobook import ChatMessage, TextSlotValue

COUPLE_NAMES_SLOT_ID = "couple_names"

# Layout placeholder copy (cover uses "and", back uses "&").
PLACEHOLDER_COUPLE_TEXTS: frozenset[str] = frozenset(
    {
        "groomy and bridey",
        "groomy & bridey",
    }
)

_BRIDE_GROOM_PATTERN = re.compile(
    r"bride(?:'?s)?\s+name\s+is\s+([A-Za-z][A-Za-z'\-]*).*?"
    r"groom(?:'?s)?(?:\s+name)?\s+is\s+([A-Za-z][A-Za-z'\-]*)",
    re.IGNORECASE | re.DOTALL,
)
_GROOM_BRIDE_PATTERN = re.compile(
    r"groom(?:'?s)?\s+name\s+is\s+([A-Za-z][A-Za-z'\-]*).*?"
    r"bride(?:'?s)?(?:\s+name)?\s+is\s+([A-Za-z][A-Za-z'\-]*)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True, slots=True)
class CoupleNames:
    bride: str
    groom: str

    def display(self, *, separator: str = " & ") -> str:
        return f"{self.bride.strip()}{separator}{self.groom.strip()}"


def extract_couple_names_from_chat(chat: list[ChatMessage]) -> CoupleNames | None:
    """Parse bride/groom names from user chat messages."""
    user_text = "\n".join(message.content for message in chat if message.role == "user")
    if not user_text.strip():
        return None

    match = _BRIDE_GROOM_PATTERN.search(user_text)
    if match:
        return CoupleNames(bride=match.group(1), groom=match.group(2))

    match = _GROOM_BRIDE_PATTERN.search(user_text)
    if match:
        return CoupleNames(bride=match.group(2), groom=match.group(1))

    return None


def _is_placeholder_couple_text(text: str) -> bool:
    normalized = " ".join(text.strip().lower().split())
    return normalized in PLACEHOLDER_COUPLE_TEXTS


def _should_use_extracted_names(composer_text: str) -> bool:
    stripped = composer_text.strip()
    return not stripped or _is_placeholder_couple_text(stripped)


def resolve_couple_names_for_compose(
    layout_id: str,
    text_slots: dict[str, TextSlotValue],
    chat: list[ChatMessage],
) -> dict[str, TextSlotValue]:
    """Set couple_names during compose: user chat names, else layout defaults."""
    if COUPLE_NAMES_SLOT_ID not in layout_text_slot_ids(layout_id):
        return text_slots

    merged = merge_text_slots(layout_id, text_slots)
    default_slot = merged[COUPLE_NAMES_SLOT_ID]
    couple = extract_couple_names_from_chat(chat)

    if couple is None:
        result = dict(text_slots)
        result[COUPLE_NAMES_SLOT_ID] = default_slot
        return result

    composer_slot = text_slots.get(COUPLE_NAMES_SLOT_ID)
    if composer_slot is not None and not _should_use_extracted_names(composer_slot.text):
        return text_slots

    result = dict(text_slots)
    result[COUPLE_NAMES_SLOT_ID] = default_slot.model_copy(update={"text": couple.display()})
    return result
