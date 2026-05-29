"""Wedding album layouts (mirrors frontend wedding-album.json)."""

from __future__ import annotations

from app.page_layouts._colors import (
    HINT_BADGE_TEXT,
    HINT_SANS_BODY,
    HINT_SANS_LABEL,
    HINT_SCRIPT_DISPLAY,
    WEDDING_BACK_COVER_BLEED_COLORS,
    WEDDING_BACK_COVER_BOHO_COLORS,
    WEDDING_BACK_COVER_COLORS,
    WEDDING_BACK_COVER_ORNATE_COLORS,
    WEDDING_CENTER_MOSAIC_COLORS,
    WEDDING_EDITORIAL_COLORS,
    WEDDING_FULL_BLEED_COLORS,
    WEDDING_STORY_LEFT_COLORS,
    WEDDING_STORY_RIGHT_COLORS,
    WEDDING_WHITE_SHEET_COLORS,
)
from app.schemas.photobook import (
    LayoutDefinition,
    LayoutPeopleGuidance,
    LayoutSlotDefinition,
    LayoutTemplateMetadata,
    LayoutTextSlotDefinition,
)
from app.typography.google_fonts import FONT_MONO, FONT_SANS_LABEL, FONT_SCRIPT_DISPLAY

_SCRIPT = FONT_SCRIPT_DISPLAY
_SANS = FONT_SANS_LABEL

LAYOUTS: tuple[LayoutDefinition, ...] = (
    LayoutDefinition(
        id="wedding_story_left",
        name="Love story (left)",
        description=(
            "Chapter page with script heading, arched caption area, and a landscape "
            "photo along the bottom — ideal for opening a chapter spread."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="bottom_photo", label="Bottom photo", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="heading",
                label="Heading",
                default_text="A Love Story Unfolding",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.25rem, 4vw, 2rem)",
            ),
            LayoutTextSlotDefinition(
                id="caption",
                label="Caption",
                default_text="Every moment led us here.",
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.75rem",
                default_letter_spacing="0.08em",
            ),
        ],
        color_guidance=WEDDING_STORY_LEFT_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=["chapter opener", "transition page", "story beat with copy"],
            story_positions=["opening", "mid"],
            looks_best_on=[
                "wide establishing or calm romantic frame",
                "clean horizon / simple composition (supports text)",
                "warm tones, soft light",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=10,
                preferred_people_counts=[0, 1, 2],
                focus=["couple", "bride", "groom", "venue"],
                notes="This is text-led; avoid chaotic frames that fight the typography.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_story_right",
        name="Love story (right)",
        description=(
            "Large detail photo on top, square couple portrait in the middle, "
            "and script names at the bottom."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="top_photo", label="Top photo", aspect_hint="landscape"),
            LayoutSlotDefinition(id="center_photo", label="Center photo", aspect_hint="square"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="couple_names",
                label="Couple names",
                default_text="Groomy & Bridey",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.25rem, 4vw, 2rem)",
            ),
        ],
        color_guidance=WEDDING_STORY_RIGHT_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=2,
            suited_scenes=["chapter continuation", "couple feature", "portraits + context"],
            story_positions=["opening", "mid"],
            looks_best_on=[
                "top: wide or medium contextual shot",
                "center: square crop-friendly couple portrait",
                "consistent lighting across both photos",
            ],
            people=LayoutPeopleGuidance(
                min_people=1,
                max_people=12,
                preferred_people_counts=[1, 2, 3, 4],
                focus=["couple", "bride", "groom"],
                notes="Use the center square for the strongest face/connection shot.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_quad_editorial",
        name="Four-photo grid",
        description=(
            "2×2 grid of detail and candid shots with a centered circular script "
            "badge overlay at the grid intersection."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="tl", label="Top left", aspect_hint="square"),
            LayoutSlotDefinition(id="tr", label="Top right", aspect_hint="square"),
            LayoutSlotDefinition(id="bl", label="Bottom left", aspect_hint="square"),
            LayoutSlotDefinition(id="br", label="Bottom right", aspect_hint="square"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="center_badge",
                label="Center badge",
                default_text="Forever Begins",
                color_hint=HINT_BADGE_TEXT,
                default_font_family=_SCRIPT,
                default_font_size="0.9rem",
            ),
        ],
        color_guidance=WEDDING_WHITE_SHEET_COLORS.model_copy(
            update={
                "overlay": (
                    "Near-white semi-opaque circular badge (~92% opacity) "
                    "centered on the grid intersection"
                ),
                "text_primary": (
                    "Dark warm brown script on the center badge; "
                    "must read on white, not on photos"
                ),
            },
        ),
        metadata=LayoutTemplateMetadata(
            required_images=4,
            suited_scenes=["mid-story gallery", "details + candids", "family & friends"],
            story_positions=["mid"],
            looks_best_on=[
                "square-crop-friendly frames",
                "cohesive set (same ritual/segment)",
                "mix of faces + details",
                "open center of grid for badge (avoid key faces at intersection)",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=25,
                preferred_people_counts=[0, 1, 2, 4, 6, 10],
                focus=["family", "guests", "couple", "details"],
                notes=(
                    "Each frame reads at equal size; keep the grid center clear "
                    "for the circular badge."
                ),
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_photo_mosaic",
        name="Eight-photo mosaic",
        description=(
            "Dense middle-page collage: three portrait photos on top, two landscape "
            "photos in the middle row, and three portrait photos on the bottom — "
            "ideal for ceremony details and candid moments."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="t1", label="Top left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="t2", label="Top center", aspect_hint="portrait"),
            LayoutSlotDefinition(id="t3", label="Top right", aspect_hint="portrait"),
            LayoutSlotDefinition(id="m1", label="Middle left", aspect_hint="landscape"),
            LayoutSlotDefinition(id="m2", label="Middle right", aspect_hint="landscape"),
            LayoutSlotDefinition(id="b1", label="Bottom left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="b2", label="Bottom center", aspect_hint="portrait"),
            LayoutSlotDefinition(id="b3", label="Bottom right", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="gallery_title",
                label="Gallery title",
                default_text="Our Wedding Day",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1rem, 3.5vw, 1.5rem)",
            ),
            LayoutTextSlotDefinition(
                id="footer_caption",
                label="Footer caption",
                default_text="Every detail, every smile, forever remembered.",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.6rem",
                default_letter_spacing="0.12em",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=WEDDING_WHITE_SHEET_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=8,
            suited_scenes=["ceremony details", "ritual montage", "candid moments", "party montage"],
            story_positions=["mid"],
            looks_best_on=[
                "many small, readable subjects",
                "mix of details + reactions + ambience",
                "avoid heavy blur (small tiles exaggerate softness)",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=40,
                preferred_people_counts=[0, 1, 2, 3, 4, 6, 10],
                focus=["details", "family", "guests", "couple"],
                notes="Use close-ups and mid shots more than wides; tiny faces in wide shots get lost.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_center_mosaic_8",
        name="Eight-photo center mosaic",
        description=(
            "Dense collage with script title and caption centered on the page, "
            "surrounded by eight photos in a 3×3 ring — ideal for ceremony montages "
            "with a focal headline."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="tl", label="Top left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="t", label="Top center", aspect_hint="portrait"),
            LayoutSlotDefinition(id="tr", label="Top right", aspect_hint="portrait"),
            LayoutSlotDefinition(id="l", label="Middle left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="r", label="Middle right", aspect_hint="portrait"),
            LayoutSlotDefinition(id="bl", label="Bottom left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="b", label="Bottom center", aspect_hint="portrait"),
            LayoutSlotDefinition(id="br", label="Bottom right", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="gallery_title",
                label="Gallery title",
                default_text="Our Wedding Day",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1rem, 3.2vw, 1.45rem)",
            ),
            LayoutTextSlotDefinition(
                id="footer_caption",
                label="Center caption",
                default_text="Every detail, every smile, forever remembered.",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.55rem",
                default_letter_spacing="0.12em",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=WEDDING_CENTER_MOSAIC_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=8,
            suited_scenes=[
                "ceremony montage",
                "ritual highlights",
                "candid ring gallery",
                "section title spread",
            ],
            story_positions=["mid"],
            looks_best_on=[
                "eight small, readable subjects framing the headline",
                "mix of details, reactions, and ambience",
                "consistent exposure across tiles",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=40,
                preferred_people_counts=[0, 1, 2, 3, 4, 6, 10],
                focus=["details", "family", "guests", "couple"],
                notes="Keep faces large enough to read in the outer tiles; center copy stays short.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_center_mosaic_6",
        name="Six-photo center mosaic",
        description=(
            "Six photos framing a centered script title and caption — corner and side "
            "tiles with open top/bottom center for a lighter, airy montage."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="tl", label="Top left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="tr", label="Top right", aspect_hint="portrait"),
            LayoutSlotDefinition(id="l", label="Middle left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="r", label="Middle right", aspect_hint="portrait"),
            LayoutSlotDefinition(id="bl", label="Bottom left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="br", label="Bottom right", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="gallery_title",
                label="Gallery title",
                default_text="Forever & Always",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1rem, 3.2vw, 1.45rem)",
            ),
            LayoutTextSlotDefinition(
                id="footer_caption",
                label="Center caption",
                default_text="A day we will never forget.",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.55rem",
                default_letter_spacing="0.12em",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=WEDDING_CENTER_MOSAIC_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=6,
            suited_scenes=[
                "highlight montage",
                "couple + details",
                "transition spread with headline",
            ],
            story_positions=["mid"],
            looks_best_on=[
                "six strong frames with breathing room at top/bottom center",
                "mix of portraits and detail shots",
                "cohesive color across the ring",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=30,
                preferred_people_counts=[0, 1, 2, 3, 4, 6],
                focus=["couple", "details", "family", "guests"],
                notes="Side tiles carry the story; keep center copy to one title plus a short line.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_center_mosaic_4",
        name="Four-photo center mosaic",
        description=(
            "Four corner photos around a large centered script title and caption — "
            "spacious middle well for chapter headings or a short vow quote."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="tl", label="Top left", aspect_hint="square"),
            LayoutSlotDefinition(id="tr", label="Top right", aspect_hint="square"),
            LayoutSlotDefinition(id="bl", label="Bottom left", aspect_hint="square"),
            LayoutSlotDefinition(id="br", label="Bottom right", aspect_hint="square"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="gallery_title",
                label="Gallery title",
                default_text="Chapter Two",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.1rem, 3.5vw, 1.6rem)",
            ),
            LayoutTextSlotDefinition(
                id="footer_caption",
                label="Center caption",
                default_text="Where our story continues.",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.6rem",
                default_letter_spacing="0.1em",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=WEDDING_CENTER_MOSAIC_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=4,
            suited_scenes=[
                "chapter opener",
                "section title",
                "quote + highlights",
                "minimal montage",
            ],
            story_positions=["opening", "mid"],
            looks_best_on=[
                "four square-crop-friendly frames at the corners",
                "one hero detail or couple shot per corner",
                "calm backgrounds that do not compete with center type",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=20,
                preferred_people_counts=[0, 1, 2, 4],
                focus=["couple", "details", "venue"],
                notes="Generous center well suits a chapter title or 1–2 line quote.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_split_collage",
        name="Split collage spread",
        description=(
            "Two-column middle spread: left has three detail photos, script heading, "
            "and a wide couple portrait; right has a tall group photo, caption line, "
            "and two bottom candids."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="lt1", label="Left top 1", aspect_hint="square"),
            LayoutSlotDefinition(id="lt2", label="Left top 2", aspect_hint="square"),
            LayoutSlotDefinition(id="lt3", label="Left top 3", aspect_hint="square"),
            LayoutSlotDefinition(id="lb", label="Left bottom", aspect_hint="landscape"),
            LayoutSlotDefinition(id="rt", label="Right top", aspect_hint="portrait"),
            LayoutSlotDefinition(id="rb_left", label="Right bottom left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="rb_right", label="Right bottom right", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="heading",
                label="Script heading",
                default_text="Our Forever Begins",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.1rem, 3.5vw, 1.75rem)",
            ),
            LayoutTextSlotDefinition(
                id="subtext",
                label="Caption line",
                default_text="A celebration of love, captured in timeless moments",
                color_hint=HINT_SANS_LABEL,
                default_font_family=FONT_MONO,
                default_font_size="0.55rem",
                default_letter_spacing="0.18em",
                default_text_transform="lowercase",
            ),
        ],
        color_guidance=WEDDING_WHITE_SHEET_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=7,
            suited_scenes=["main ceremony spread", "family + couple + details", "reception highlight spread"],
            story_positions=["mid"],
            looks_best_on=[
                "balanced variety (details + portraits + group)",
                "one strong wide couple portrait",
                "one tall group/formal that crops well to portrait",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=40,
                preferred_people_counts=[1, 2, 4, 6, 10, 15],
                focus=["couple", "family", "guests", "details"],
                notes="Use the tall portrait slot for the largest group/formal; keep faces sharp.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_editorial_text",
        name="Editorial + text",
        description=(
            "Large landscape photo on top, body copy in the middle, and a smaller "
            "landscape photo along the bottom."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="top_photo", label="Top photo", aspect_hint="landscape"),
            LayoutSlotDefinition(id="bottom_photo", label="Bottom photo", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="body",
                label="Body text",
                default_text=(
                    "Surrounded by laughter and love, we celebrated each ritual "
                    "and every quiet glance. These pages hold the joy of our families "
                    "coming together."
                ),
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.7rem",
                default_letter_spacing="0.04em",
                default_text_align="left",
            ),
        ],
        color_guidance=WEDDING_EDITORIAL_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=2,
            suited_scenes=["vows/speeches", "storytelling interlude", "thank-you note section", "reflection page"],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "two calm, uncluttered frames",
                "photos that leave breathing room around text",
                "consistent lighting across top/bottom",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=12,
                preferred_people_counts=[0, 1, 2, 3, 4],
                focus=["couple", "family", "venue", "details"],
                notes="Text is prominent; avoid overly busy images that reduce readability.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_full_bleed_badge",
        name="Full bleed + badge",
        description=(
            "Edge-to-edge sunset or portrait with a circular script badge overlay "
            "near the bottom."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="hero", label="Full bleed", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="badge",
                label="Badge text",
                default_text="Forever Begins",
                color_hint=HINT_BADGE_TEXT,
                default_font_family=_SCRIPT,
                default_font_size="0.9rem",
            ),
        ],
        color_guidance=WEDDING_FULL_BLEED_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=["signature portrait", "golden hour", "hero moment with short headline"],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "portrait-oriented hero",
                "clean area near top for badge",
                "strong subject separation (bokeh/contrast)",
            ],
            people=LayoutPeopleGuidance(
                min_people=1,
                max_people=6,
                preferred_people_counts=[1, 2],
                focus=["couple", "bride", "groom"],
                notes="Avoid placing key faces where the badge overlay sits.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_text_collage",
        name="Text + collage",
        description=(
            "Body copy at the top with one large horizontal photo and two smaller "
            "square detail shots below."
        ),
        page_role="middle",
        slots=[
            LayoutSlotDefinition(id="main", label="Main photo", aspect_hint="landscape"),
            LayoutSlotDefinition(id="left_small", label="Left detail", aspect_hint="square"),
            LayoutSlotDefinition(id="right_small", label="Right detail", aspect_hint="square"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="body",
                label="Body text",
                default_text=(
                    "From the first look to the last dance, we cherished every "
                    "detail — the flowers, the vows, and the hands we held."
                ),
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.7rem",
                default_letter_spacing="0.04em",
                default_text_align="left",
            ),
        ],
        color_guidance=WEDDING_EDITORIAL_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=["story beat with copy + highlights", "details-focused segment", "small recap"],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "main: wide/medium highlight",
                "smalls: close-up details (rings, henna, décor) or reactions",
                "images with cohesive lighting",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=12,
                preferred_people_counts=[0, 1, 2, 3, 4],
                focus=["details", "couple", "family"],
                notes="Small squares should be close enough that faces/details are readable.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_back_cover",
        name="Back cover",
        description=(
            "Circular couple portrait, script names, and a short thank-you message "
            "for the closing page."
        ),
        page_role="back",
        slots=[
            LayoutSlotDefinition(id="portrait", label="Portrait", aspect_hint="square"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="couple_names",
                label="Couple names",
                default_text="Groomy & Bridey",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.25rem, 4vw, 2rem)",
            ),
            LayoutTextSlotDefinition(
                id="thank_you",
                label="Thank you",
                default_text="Thank you for sharing our special day.",
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.7rem",
                default_letter_spacing="0.06em",
            ),
        ],
        color_guidance=WEDDING_BACK_COVER_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=["closing portrait", "farewell", "thank you"],
            story_positions=["ending"],
            looks_best_on=[
                "square-crop-friendly couple portrait",
                "calm, warm closing mood",
                "clean background for text clarity",
            ],
            people=LayoutPeopleGuidance(
                min_people=1,
                max_people=6,
                preferred_people_counts=[2],
                focus=["couple"],
                notes="Prefer a serene couple shot; avoid busy group frames for the ending.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_back_cover_ornate",
        name="Back cover (ornate)",
        description=(
            "Closing page with ornamental side borders, arched couple portrait, "
            "script names, thank-you message, and date — bookend to the classic cover."
        ),
        page_role="back",
        slots=[
            LayoutSlotDefinition(id="hero", label="Couple portrait", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="couple_names",
                label="Couple names",
                default_text="Groomy & Bridey",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.25rem, 4vw, 2rem)",
            ),
            LayoutTextSlotDefinition(
                id="thank_you",
                label="Thank you",
                default_text="Thank you for celebrating with us.",
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.7rem",
                default_letter_spacing="0.06em",
            ),
            LayoutTextSlotDefinition(
                id="closing_date",
                label="Closing date",
                default_text="SEPTEMBER 20, 2026",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.6rem",
                default_letter_spacing="0.3em",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=WEDDING_BACK_COVER_ORNATE_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=["closing portrait", "farewell", "thank you"],
            story_positions=["ending"],
            looks_best_on=[
                "single couple portrait with clean background",
                "centered subject for arch crop",
                "pairs well after wedding_cover front",
            ],
            people=LayoutPeopleGuidance(
                min_people=2,
                max_people=4,
                preferred_people_counts=[2],
                focus=["couple"],
                notes="Match the formal tone of the classic front cover.",
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_back_cover_boho",
        name="Back cover (boho)",
        description=(
            "Editorial split closing page with overlapping rounded photos and "
            "script names with a thank-you message — bookend to the boho cover."
        ),
        page_role="back",
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
                id="label",
                label="Label",
                default_text="WITH GRATITUDE",
                color_hint=HINT_SANS_LABEL,
                default_font_family=_SANS,
                default_font_size="0.6rem",
                default_letter_spacing="0.35em",
                default_text_transform="uppercase",
            ),
            LayoutTextSlotDefinition(
                id="couple_names",
                label="Couple names",
                default_text="Groomy & Bridey",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.5rem, 5vw, 2.5rem)",
            ),
            LayoutTextSlotDefinition(
                id="thank_you",
                label="Thank you",
                default_text="Thank you for sharing our joy and being part of our story.",
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.65rem",
                default_letter_spacing="0.08em",
            ),
        ],
        color_guidance=WEDDING_BACK_COVER_BOHO_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=2,
            suited_scenes=["closing portrait", "farewell", "thank you"],
            story_positions=["ending"],
            looks_best_on=[
                "two complementary couple or scene photos",
                "warm natural light",
                "pairs well after wedding_boho_cover front",
            ],
            people=LayoutPeopleGuidance(
                min_people=2,
                max_people=6,
                preferred_people_counts=[2],
                focus=["couple"],
                notes=(
                    "Primary as wider scene; secondary as closer couple moment. "
                    "Keep the text column uncluttered."
                ),
            ),
        ),
    ),
    LayoutDefinition(
        id="wedding_back_cover_bleed",
        name="Back cover (full bleed)",
        description=(
            "Edge-to-edge closing photo with a white footer band for script names "
            "and a thank-you message."
        ),
        page_role="back",
        slots=[
            LayoutSlotDefinition(id="hero", label="Closing photo", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="couple_names",
                label="Couple names",
                default_text="Groomy & Bridey",
                color_hint=HINT_SCRIPT_DISPLAY,
                default_font_family=_SCRIPT,
                default_font_size="clamp(1.25rem, 4vw, 2rem)",
            ),
            LayoutTextSlotDefinition(
                id="thank_you",
                label="Thank you",
                default_text="Thank you for sharing our special day.",
                color_hint=HINT_SANS_BODY,
                default_font_family=_SANS,
                default_font_size="0.7rem",
                default_letter_spacing="0.06em",
            ),
        ],
        color_guidance=WEDDING_BACK_COVER_BLEED_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=["closing portrait", "farewell", "celebration finale"],
            story_positions=["ending"],
            looks_best_on=[
                "strong emotional wide or tall moment",
                "clean lower third for footer text",
                "dramatic light (sunset, dance floor, ceremony exit)",
            ],
            people=LayoutPeopleGuidance(
                min_people=1,
                max_people=12,
                preferred_people_counts=[2, 4, 6],
                focus=["couple", "family", "celebration"],
                notes="Avoid busy detail in the bottom ~25% where the footer sits.",
            ),
        ),
    ),
)
