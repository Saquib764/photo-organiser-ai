"""Schemas for photobook document, layouts, and OpenAI planner/composer output."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.typography.google_fonts import FONT_SCRIPT_DISPLAY, coerce_font_family

PhotobookPageStatus = Literal["draft", "composing", "ready", "error"]
ChatRole = Literal["user", "assistant"]
PageRole = Literal["cover", "middle", "back"]
TemplateStoryPosition = Literal["opening", "mid", "ending"]


class LayoutColorGuidance(BaseModel):
    """Semantic color requirements for a layout (no hex values in templates)."""

    page_background: str = Field(
        default="",
        description="Sheet/page background: tone, warmth, and contrast needs.",
    )
    content_surfaces: str = Field(
        default="",
        description="Inner panels, cards, caption wells, badge fills.",
    )
    text_primary: str = Field(
        default="",
        description="Headings and display names: darkness, warmth, contrast on backgrounds.",
    )
    text_secondary: str = Field(
        default="",
        description="Dates, captions, body copy relative to primary text.",
    )
    accent: str = Field(
        default="",
        description="Accent bars, highlights, subtle brand color blocks.",
    )
    decorative: str = Field(
        default="",
        description="Borders, ornaments, dividers, portrait rings.",
    )
    overlay: str = Field(
        default="",
        description="Semi-opaque layers behind text placed on photos.",
    )


class LayoutPeopleGuidance(BaseModel):
    """How many people / what kind of people this layout suits best."""

    min_people: int | None = Field(default=None, ge=0)
    max_people: int | None = Field(default=None, ge=0)
    preferred_people_counts: list[int] = Field(
        default_factory=list,
        description="Commonly best-looking headcounts (e.g., [0, 1, 2, 4, 8]).",
    )
    focus: list[str] = Field(
        default_factory=list,
        description="Who should be emphasized (e.g., couple, bride, groom, family, guests).",
    )
    notes: str = ""


class LayoutTemplateMetadata(BaseModel):
    """AI-facing metadata to help pick the right template for a page."""

    required_images: int = Field(
        default=0,
        ge=0,
        description="How many images are required to fill this template (must match slot count).",
    )
    suited_scenes: list[str] = Field(
        default_factory=list,
        description=(
            "Scene types this template fits (e.g., cover portraits, ceremony, reception, details, "
            "portraits, family formals, candids)."
        ),
    )
    story_positions: list[TemplateStoryPosition] = Field(
        default_factory=list,
        description="Where this template usually appears in the book: opening, mid, ending.",
    )
    looks_best_on: list[str] = Field(
        default_factory=list,
        description=(
            "Image traits that look great here (e.g., wide establishing, tight portraits, "
            "detail close-ups, high-contrast, soft light, centered subject, negative space)."
        ),
    )
    people: LayoutPeopleGuidance = Field(default_factory=LayoutPeopleGuidance)


class LayoutSlotDefinition(BaseModel):
    id: str
    label: str
    aspect_hint: str = Field(
        default="landscape",
        description="Hint for preview sizing: landscape, portrait, square",
    )


class LayoutTextSlotDefinition(BaseModel):
    """Text region on a layout; defaults apply when the page omits a field."""

    id: str
    label: str
    default_text: str = ""
    color_hint: str = Field(
        default="",
        description="What kind of text color this slot needs (no hex in templates).",
    )
    default_font_family: str = FONT_SCRIPT_DISPLAY
    default_font_size: str = "1.5rem"
    default_font_weight: str = "400"
    default_letter_spacing: str = "normal"
    default_text_align: str = "center"
    default_text_transform: str = "none"

    @field_validator("default_font_family")
    @classmethod
    def _validate_default_font_family(cls, value: str) -> str:
        return coerce_font_family(value)


class TextSlotValue(BaseModel):
    """Rendered text for one layout text slot."""

    text: str = ""
    color: str = Field(
        default="",
        description="Resolved text color hex; leave empty to derive from layout hint or page palette.",
    )
    font_family: str = FONT_SCRIPT_DISPLAY
    font_size: str = "1.5rem"
    font_weight: str = "400"
    letter_spacing: str = "normal"
    text_align: str = "center"
    text_transform: str = "none"

    @field_validator("font_family")
    @classmethod
    def _validate_font_family(cls, value: str) -> str:
        if not value.strip():
            return ""
        return coerce_font_family(value)


class LayoutDefinition(BaseModel):
    id: str
    name: str
    description: str
    slots: list[LayoutSlotDefinition]
    text_slots: list[LayoutTextSlotDefinition] = Field(default_factory=list)
    color_guidance: LayoutColorGuidance | None = Field(
        default=None,
        description="Semantic color needs for page background, text, accents, and decorative elements.",
    )
    page_role: PageRole | None = Field(
        default=None,
        description="cover = first pages, middle = spreads, back = closing pages",
    )
    metadata: LayoutTemplateMetadata | None = Field(
        default=None,
        description="Optional AI-facing template metadata (scene fit, people guidance, etc.).",
    )


class SlotOffset(BaseModel):
    """Pan position for object-cover images (CSS object-position percentages)."""

    x: float = Field(default=50.0, ge=0, le=100)
    y: float = Field(default=50.0, ge=0, le=100)


class ChatMessage(BaseModel):
    id: str
    role: ChatRole
    content: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
    )


class ImageCatalogEntry(BaseModel):
    """Story category sent to the photobook planner (id + description only)."""

    id: str
    description: str


class PhotobookPage(BaseModel):
    id: str
    title: str = "Untitled page"
    narrative: str = ""
    layout_id: str = ""
    categories: list[str] = Field(
        default_factory=list,
        description="Image category ids from image_categories.json for compose to pick photos from.",
    )
    slots: dict[str, str] = Field(default_factory=dict)
    text_slots: dict[str, TextSlotValue] = Field(
        default_factory=dict,
        description="Per-slot typography and copy keyed by layout text slot id",
    )
    slot_offsets: dict[str, SlotOffset] = Field(
        default_factory=dict,
        description="Per-slot pan offsets as object-position percentages (0–100)",
    )
    palette_colors: list[str] = Field(
        default_factory=list,
        description="Top extracted hex colors from the primary slot image (up to 3)",
    )
    background_color: str | None = Field(
        default=None,
        description="Selected sheet background hex (defaults to first palette color)",
    )
    image_border_radius: int = Field(
        default=0,
        ge=0,
        description="Border radius in px for images on this sheet",
    )
    status: PhotobookPageStatus = "draft"
    composing_started_at: str | None = Field(
        default=None,
        description="ISO timestamp when the current compose run started",
    )
    composed_at: str | None = None
    layout_error: str | None = Field(
        default=None,
        description="Planner layout template validation error for this page.",
    )
    error_message: str | None = None
    extra_images: list[str] = Field(
        default_factory=list,
        description="Alternate image paths for this page, populated by compose and manual slot swaps.",
    )


class PhotobookDocument(BaseModel):
    title: str = "Wedding photobook"
    chat: list[ChatMessage] = Field(default_factory=list)
    pages: list[PhotobookPage] = Field(default_factory=list)


class PhotobookPagePlan(BaseModel):
    """Page outline from the planner (includes chosen layout template)."""

    id: str | None = Field(
        default=None,
        description="Existing page id to update; omit for a new page",
    )
    title: str
    narrative: str
    layout_id: str = Field(
        description="Chosen layout id for this page from the layout catalog.",
    )
    categories: list[str] = Field(
        min_length=1,
        max_length=3,
        description=(
            "1–3 image category ids from the image catalog. "
            "Compose will pick photos from these categories."
        ),
    )
    layout_id_error: str | None = Field(
        default=None,
        description="Set when layout_id failed validation (unknown or missing template).",
    )

    @field_validator("categories")
    @classmethod
    def _normalize_categories(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for item in value:
            cat_id = item.strip()
            if not cat_id or cat_id in seen:
                continue
            seen.add(cat_id)
            normalized.append(cat_id)
        if not normalized:
            msg = "Each page must have at least one category"
            raise ValueError(msg)
        if len(normalized) > 3:
            msg = "Each page must have at most 3 categories"
            raise ValueError(msg)
        return normalized


class PhotobookPlanResult(BaseModel):
    """Structured output from the chat planner."""

    assistant_message: str
    pages: list[PhotobookPagePlan] = Field(default_factory=list)
    extra_images: list[str] = Field(default_factory=list)


class PageComposeResult(BaseModel):
    """Structured output from the page composer."""

    layout_id: str = Field(
        description="Chosen layout id for this page. Must match one of the layout ids in the layout catalog.",
    )
    slots: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of image slot id -> image path from the image gallery. Must include every required slot for the chosen layout_id.",
    )
    text_slots: dict[str, TextSlotValue] = Field(
        default_factory=dict,
        description="Mapping of text slot id -> rendered text + typography. Must include every text slot for the chosen layout_id (use layout defaults for typography unless you intentionally change it).",
    )
    extra_images: list[str] = Field(
        default_factory=list,
        description="At least 4 alternate image paths from the gallery (up to 12) not assigned to slots on this page.",
    )
    rationale: str = Field(
        default="",
        description="One-sentence explanation of why this layout and these images/text were chosen for the page narrative.",
    )


class PageComposeSlotAssignment(BaseModel):
    slot_id: str = Field(
        description="Image slot id from the chosen layout definition (e.g. hero, tl, br).",
    )
    path: str = Field(
        description="Image path from the image gallery assigned to this slot (relative path under processed_small/).",
    )


class PageComposeTextSlotAssignment(BaseModel):
    slot_id: str = Field(
        description="Text slot id from the chosen layout definition (e.g. couple_names, wedding_date, body).",
    )
    value: TextSlotValue = Field(
        description="Rendered copy + typography for this text slot. Prefer keeping typography fields aligned with layout defaults; mainly change the text content.",
    )


class PageComposeStructured(BaseModel):
    """OpenAI structured output model (list-based to avoid dynamic dict schemas)."""

    layout_id: str = Field(
        description="Chosen layout id for this page from the layout catalog.",
    )
    slots: list[PageComposeSlotAssignment] = Field(
        description="List of image slot assignments. Must include one entry per required image slot id for the chosen layout_id.",
    )
    text_slots: list[PageComposeTextSlotAssignment] = Field(
        description="List of text slot assignments. Must include one entry per text slot id for the chosen layout_id.",
    )
    extra_images: list[str] = Field(
        description=(
            "Required list of at least 4 alternate image paths (up to 12) from the gallery "
            "that are not used in slots on this page."
        ),
    )
    rationale: str = Field(
        description="One-sentence explanation of the choices made.",
    )


class PhotobookResponse(BaseModel):
    document: PhotobookDocument
    layouts: list[LayoutDefinition]


class PhotobookChatRequest(BaseModel):
    message: str = Field(min_length=1)


class PhotobookChatResponse(BaseModel):
    document: PhotobookDocument
    layouts: list[LayoutDefinition]
    assistant_message: str


class PhotobookPageCreateRequest(BaseModel):
    title: str = "New page"
    narrative: str = ""


class PhotobookPagePatchRequest(BaseModel):
    title: str | None = None
    narrative: str | None = None
    layout_id: str | None = None
    slots: dict[str, str] | None = None
    text_slots: dict[str, TextSlotValue] | None = None
    slot_offsets: dict[str, SlotOffset] | None = None
    background_color: str | None = None
    image_border_radius: int | None = Field(default=None, ge=0)
    status: PhotobookPageStatus | None = None
    extra_images: list[str] | None = None


class GalleryImageSummary(BaseModel):
    """Compact image row for OpenAI prompts."""

    path: str
    folder: str
    caption: str = ""
    number_of_people: int = 0
    has_bride: bool = False
    has_groom: bool = False
    has_other_people: bool = False
    is_blur: bool = False
    quality_score: float = 0.0
    analyzed: bool = False
