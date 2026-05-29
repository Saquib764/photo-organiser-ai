"""Cover page layouts (mirrors frontend cover-pages.json)."""

from __future__ import annotations

from app.page_layouts._colors import (
    BOHO_SPLIT_COVER_COLORS,
    HINT_SANS_BODY,
    HINT_SANS_LABEL,
    HINT_SCRIPT_DISPLAY,
    WEDDING_COVER_COLORS,
)
from app.schemas.photobook import (
    LayoutDefinition,
    LayoutPeopleGuidance,
    LayoutSlotDefinition,
    LayoutTemplateMetadata,
    LayoutTextSlotDefinition,
)
from app.typography.google_fonts import FONT_SANS_LABEL, FONT_SCRIPT_DISPLAY

_SCRIPT = FONT_SCRIPT_DISPLAY
_SANS = FONT_SANS_LABEL

LAYOUTS: tuple[LayoutDefinition, ...] = (
    LayoutDefinition(
        id="wedding_cover",
        name="Wedding cover",
        description=(
            "Front cover with ornamental side borders, script couple names, "
            "arched hero portrait, date, and tagline."
        ),
        page_role="cover",
        slots=[
            LayoutSlotDefinition(id="hero", label="Couple portrait", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="couple_names",
                label="Couple names",
                default_text="Groomy and Bridey",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.5rem, 5vw, 2.75rem)",
            ),
            LayoutTextSlotDefinition(
                id="wedding_date",
                label="Wedding date",
                default_text="SEPTEMBER 20, 2026",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.65rem",
                default_letter_spacing="0.35em",
                default_text_transform="uppercase",
            ),
            LayoutTextSlotDefinition(
                id="tagline",
                label="Tagline",
                default_text="A LOVE THAT LASTS FOREVER",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.7rem",
                default_letter_spacing="0.2em",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=WEDDING_COVER_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=["cover portraits", "title page"],
            story_positions=["opening"],
            looks_best_on=[
                "single strong couple portrait",
                "centered subject",
                "clean background / negative space (for text legibility)",
                "sharp focus, flattering light",
            ],
            people=LayoutPeopleGuidance(
                min_people=2,
                max_people=4,
                preferred_people_counts=[2],
                focus=["couple"],
                notes="Pick an image with both faces clearly visible; avoid busy backgrounds behind text areas.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_boho_cover",
        name="Wedding boho cover",
        description=(
            "Editorial split cover with overlapping rounded photos on the left and "
            "script couple names with labels on the right. No navigation chrome."
        ),
        page_role="cover",
        slots=[
            LayoutSlotDefinition(
                id="photo_primary",
                label="Primary photo",
                aspect_hint="portrait",
            ),
            LayoutSlotDefinition(
                id="photo_secondary",
                label="Secondary photo",
                aspect_hint="portrait",
            ),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="heading",
                label="Heading",
                default_text="THE WEDDING OF",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.6rem",
                default_letter_spacing="0.4em",
                default_text_transform="uppercase",
            ),
            LayoutTextSlotDefinition(
                id="couple_names",
                label="Couple names",
                default_text="Groomy & Bridey",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.75rem, 6vw, 3.25rem)",
            ),
            LayoutTextSlotDefinition(
                id="subtitle",
                label="Subtitle",
                default_text="A CELEBRATION OF LOVE AND JOY",
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.6rem",
                default_letter_spacing="0.12em",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=BOHO_SPLIT_COVER_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=2,
            suited_scenes=["cover portraits", "title page", "ceremony establishing"],
            story_positions=["opening"],
            looks_best_on=[
                "two complementary couple or scene photos",
                "one wider environmental shot and one tighter portrait",
                "clean backgrounds; right half stays open for typography",
                "warm natural light",
            ],
            people=LayoutPeopleGuidance(
                min_people=2,
                max_people=6,
                preferred_people_counts=[2],
                focus=["couple"],
                notes=(
                    "Primary photo works best as a wider scene; secondary as a closer "
                    "couple moment. Avoid busy detail behind the text column."
                ),
            ),
        ),
    ),
)
