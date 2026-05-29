"""Shared semantic color hints for page layouts (canonical). for photobook layout templates (no hex values)."""

from __future__ import annotations

from app.schemas.photobook import LayoutColorGuidance

# Text slot hints
HINT_SCRIPT_DISPLAY = (
    "Dark warm brown for script display names and titles; high contrast on light backgrounds"
)
HINT_SANS_LABEL = (
    "Dark warm brown for small sans-serif labels (dates, taglines); same hue family as display text"
)
HINT_SANS_BODY = (
    "Dark warm brown for body copy and captions; readable at small sizes on white or blush"
)
HINT_BADGE_TEXT = (
    "Dark warm brown for short badge headline on a near-white circular overlay"
)
HINT_ON_PHOTO_CAPTION = (
    "Dark warm brown caption on a near-white translucent pill over the photo; "
    "short line with padding around text only"
)
HINT_ON_PHOTO_LABEL = (
    "Dark warm brown label on a near-white translucent pill; very short (e.g. Bride, Groom)"
)

# Layout-level guidance presets
IMAGE_LED_BACKGROUND = LayoutColorGuidance(
    page_background=(
        "Neutral sheet or color pulled from the primary image palette; "
        "should not compete with photography"
    ),
)

IMAGE_FULL_BLEED_CAPTION_COLORS = LayoutColorGuidance(
    page_background="Full-bleed photo; no separate sheet color",
    overlay="Near-white translucent pill behind caption text only (not full-image scrim)",
    text_primary="Dark warm brown uppercase caption on the white pill; 3–8 words",
)

IMAGE_HERO_CAPTION_COLORS = LayoutColorGuidance(
    page_background="Neutral sheet or color pulled from the primary image palette",
    overlay="Near-white translucent pill behind hero caption only",
    text_primary="Dark warm brown caption on the white pill",
)

IMAGE_DIPTYCH_CAPTION_COLORS = LayoutColorGuidance(
    page_background="Neutral sheet or color pulled from the primary image palette",
    overlay="Near-white translucent pill behind each panel caption",
    text_primary="Dark warm brown uppercase labels on the white pill",
)

BOHO_SPLIT_COVER_COLORS = LayoutColorGuidance(
    page_background="Warm cream off-white sheet; airy editorial feel",
    text_primary="Dark warm brown for script couple names; strongest contrast on the page",
    text_secondary="Dark warm brown for small caps heading and subtitle",
    decorative=(
        "Muted rose-tan botanical line art in corners when present; "
        "low contrast framing only"
    ),
)

WEDDING_COVER_COLORS = LayoutColorGuidance(
    page_background="Clean near-white sheet; bright and airy so photos and typography stand out",
    text_primary="Dark warm brown for script couple names; strongest contrast on the page",
    text_secondary="Dark warm brown for date and tagline; works at small uppercase sizes",
    accent="Soft dusty blush bar along the bottom edge; subtle warmth, not dominant",
    decorative=(
        "Muted rose-tan ornamental side borders and hairline dividers; "
        "low contrast, framing only"
    ),
)

WEDDING_STORY_LEFT_COLORS = LayoutColorGuidance(
    page_background="Soft blush pink sheet; warm and romantic, lighter than accent tones",
    content_surfaces="White arch/caption well; crisp contrast for centered copy",
    text_primary="Dark warm brown script heading on blush background",
    text_secondary="Dark warm brown sans caption inside the white arch",
)

WEDDING_STORY_RIGHT_COLORS = LayoutColorGuidance(
    page_background="Clean white sheet; neutral so photos carry color",
    text_primary="Dark warm brown script couple names at the foot of the page",
)

WEDDING_CENTER_MOSAIC_COLORS = LayoutColorGuidance(
    page_background="Clean white sheet; neutral gallery feel",
    content_surfaces=(
        "White center typography well amid photo tiles; "
        "crisp contrast for script title and caption"
    ),
    text_primary="Dark warm brown script title centered among photos",
    text_secondary="Dark warm brown sans caption beneath title in the center well",
)

WEDDING_WHITE_SHEET_COLORS = LayoutColorGuidance(
    page_background="Clean white sheet; neutral gallery feel",
    text_primary="Dark warm brown for script titles when present",
    text_secondary="Dark warm brown for footer captions and labels",
)

WEDDING_EDITORIAL_COLORS = LayoutColorGuidance(
    page_background="Clean white sheet with generous margins around photos",
    text_primary="Dark warm brown for script headings",
    text_secondary="Dark warm brown for body copy; left-aligned, comfortable line length",
)

WEDDING_FULL_BLEED_COLORS = LayoutColorGuidance(
    page_background="Full-bleed photo; no separate sheet color",
    overlay="Near-white semi-opaque circular badge (~92% opacity) with soft shadow",
    text_primary="Dark warm brown badge text; must read on the white badge, not on the photo",
)

WEDDING_BACK_COVER_COLORS = LayoutColorGuidance(
    page_background="Clean white closing sheet; calm and minimal",
    text_primary="Dark warm brown script couple names",
    text_secondary="Dark warm brown thank-you message; slightly lighter typographic weight",
    decorative="Muted rose-tan hairline ring around the circular portrait",
)

WEDDING_BACK_COVER_ORNATE_COLORS = LayoutColorGuidance(
    page_background="Clean near-white closing sheet; bright and airy",
    text_primary="Dark warm brown script couple names; strongest contrast on the page",
    text_secondary="Dark warm brown thank-you and date; works at small uppercase sizes",
    accent="Soft dusty blush bar along the bottom edge; subtle warmth, not dominant",
    decorative=(
        "Muted rose-tan ornamental side borders and hairline dividers; "
        "low contrast, framing only"
    ),
)

WEDDING_BACK_COVER_BOHO_COLORS = LayoutColorGuidance(
    page_background="Warm cream off-white closing sheet; airy editorial feel",
    text_primary="Dark warm brown script couple names; strongest contrast on the page",
    text_secondary="Dark warm brown small caps label and thank-you body",
    decorative="Soft shadows on overlapping rounded photos; low contrast framing only",
)

WEDDING_BACK_COVER_BLEED_COLORS = LayoutColorGuidance(
    page_background="Full-bleed photo; no separate sheet color",
    overlay="Near-white footer band (~25% page height) for closing copy",
    text_primary="Dark warm brown script couple names on the footer band",
    text_secondary="Dark warm brown thank-you message on the footer band",
)
