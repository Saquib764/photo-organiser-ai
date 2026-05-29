"""Curated Google Fonts for photobook typography.

Only families listed here may appear in layout defaults or rendered text slots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from urllib.parse import quote

# --- Role shortcuts (use these in layout definitions) ---

FONT_SCRIPT_DISPLAY: Final = "'Great Vibes', cursive"
FONT_SERIF_DISPLAY: Final = "'Cormorant Garamond', serif"
FONT_SERIF_EDITORIAL: Final = "'Playfair Display', serif"
FONT_SANS_LABEL: Final = "'Montserrat', sans-serif"
FONT_SANS_BODY: Final = "'Lato', sans-serif"
FONT_SANS_EDITORIAL: Final = "'Raleway', sans-serif"
FONT_SERIF_BODY: Final = "'Lora', serif"
FONT_SERIF_NARRATIVE: Final = "'Merriweather', serif"
FONT_MONO: Final = "'Courier Prime', monospace"


@dataclass(frozen=True, slots=True)
class GoogleFont:
    """One Google Font family with CSS stack and loading weights."""

    name: str
    family: str
    category: str
    role: str
    weights: tuple[int, ...]


FONTS: Final[tuple[GoogleFont, ...]] = (
    GoogleFont(
        name="Great Vibes",
        family=FONT_SCRIPT_DISPLAY,
        category="cursive",
        role="Script display — couple names, romantic titles",
        weights=(400,),
    ),
    GoogleFont(
        name="Cormorant Garamond",
        family=FONT_SERIF_DISPLAY,
        category="serif",
        role="Serif display — chapter headings, elegant titles",
        weights=(400, 500, 600),
    ),
    GoogleFont(
        name="Playfair Display",
        family=FONT_SERIF_EDITORIAL,
        category="serif",
        role="Editorial display — formal section titles",
        weights=(400, 500, 600),
    ),
    GoogleFont(
        name="Montserrat",
        family=FONT_SANS_LABEL,
        category="sans-serif",
        role="Sans label — dates, small caps, captions, badges",
        weights=(300, 400, 500),
    ),
    GoogleFont(
        name="Lato",
        family=FONT_SANS_BODY,
        category="sans-serif",
        role="Sans body — readable supporting lines",
        weights=(300, 400, 700),
    ),
    GoogleFont(
        name="Raleway",
        family=FONT_SANS_EDITORIAL,
        category="sans-serif",
        role="Sans editorial — airy labels and subtitles",
        weights=(400, 500, 600),
    ),
    GoogleFont(
        name="Lora",
        family=FONT_SERIF_BODY,
        category="serif",
        role="Serif body — warm narrative paragraphs",
        weights=(400, 500),
    ),
    GoogleFont(
        name="Merriweather",
        family=FONT_SERIF_NARRATIVE,
        category="serif",
        role="Serif narrative — longer story text",
        weights=(400, 700),
    ),
    GoogleFont(
        name="Courier Prime",
        family=FONT_MONO,
        category="monospace",
        role="Monospace — dates, codes, typewriter accents",
        weights=(400,),
    ),
)

ALLOWED_FONT_FAMILIES: Final[frozenset[str]] = frozenset(font.family for font in FONTS)

_FONT_BY_NAME: Final[dict[str, GoogleFont]] = {font.name.lower(): font for font in FONTS}


def coerce_font_family(value: str, *, fallback: str = FONT_SANS_LABEL) -> str:
    """Return an allowed font family string, or fallback if unknown."""
    stripped = value.strip()
    if stripped in ALLOWED_FONT_FAMILIES:
        return stripped
    # Match bare names like "Montserrat" or partial stacks.
    lowered = stripped.lower().strip("'\"")
    for font in FONTS:
        if font.name.lower() in lowered:
            return font.family
    return fallback


def google_fonts_stylesheet_url() -> str:
    """Build a Google Fonts CSS2 URL that loads every curated family."""
    parts: list[str] = []
    for font in FONTS:
        encoded = quote(font.name)
        if len(font.weights) == 1:
            parts.append(f"family={encoded}")
        else:
            weight_axis = ";".join(str(w) for w in font.weights)
            parts.append(f"family={encoded}:wght@{weight_axis}")
    return f"https://fonts.googleapis.com/css2?{'&'.join(parts)}&display=swap"


def typography_for_prompt() -> list[dict[str, str]]:
    """Serialize the font catalog for OpenAI prompts."""
    return [
        {
            "font_family": font.family,
            "name": font.name,
            "role": font.role,
        }
        for font in FONTS
    ]
