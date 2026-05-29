"""Photo grid layouts (mirrors frontend photo-grids.json)."""

from __future__ import annotations

from app.page_layouts._colors import (
    HINT_ON_PHOTO_CAPTION,
    HINT_ON_PHOTO_LABEL,
    HINT_SANS_BODY,
    IMAGE_DIPTYCH_CAPTION_COLORS,
    IMAGE_FULL_BLEED_CAPTION_COLORS,
    IMAGE_HERO_CAPTION_COLORS,
    IMAGE_LED_BACKGROUND,
)
from app.schemas.photobook import (
    LayoutDefinition,
    LayoutPeopleGuidance,
    LayoutSlotDefinition,
    LayoutTemplateMetadata,
    LayoutTextSlotDefinition,
)
from app.typography.google_fonts import FONT_SANS_LABEL

LAYOUTS: tuple[LayoutDefinition, ...] = (
    LayoutDefinition(
        id="hero_pair",
        name="Hero + pair",
        description=(
            "One large hero image with two smaller supporting images below. "
            "Good for a main moment plus detail shots."
        ),
        slots=[
            LayoutSlotDefinition(id="hero", label="Hero", aspect_hint="landscape"),
            LayoutSlotDefinition(id="left", label="Left", aspect_hint="landscape"),
            LayoutSlotDefinition(id="right", label="Right", aspect_hint="landscape"),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=[
                "ceremony + details",
                "getting ready + details",
                "portraits + rings/henna/outfit",
                "key ritual + reactions",
            ],
            story_positions=["opening", "mid", "ending"],
            looks_best_on=[
                "one strong hero moment",
                "two supporting details or reaction shots",
                "consistent color/lighting across the trio",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=10,
                preferred_people_counts=[0, 1, 2, 3, 4],
                focus=["couple", "bride", "groom", "family"],
                notes="Hero should be the most emotionally/visually dominant frame.",
            ),
        ),
    ),
    LayoutDefinition(
        id="hero_pair_note_left",
        name="Hero + pair + note (left)",
        description=(
            "Large hero on top with a detail thumbnail and typography cell below — "
            "text on the left, image on the right."
        ),
        slots=[
            LayoutSlotDefinition(id="hero", label="Hero", aspect_hint="landscape"),
            LayoutSlotDefinition(id="right", label="Right", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="note",
                label="Note",
                default_text="Surrounded by love and laughter.",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.7rem",
                default_font_weight="400",
                default_letter_spacing="0.1em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=2,
            suited_scenes=[
                "hero moment + quote or date line",
                "main shot + detail with caption cell",
            ],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "one strong hero landscape",
                "one supporting detail thumbnail",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=10,
                preferred_people_counts=[0, 1, 2, 3, 4],
                focus=["couple", "bride", "groom", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="hero_pair_note_right",
        name="Hero + pair + note (right)",
        description=(
            "Large hero on top with a detail thumbnail and typography cell below — "
            "image on the left, text on the right."
        ),
        slots=[
            LayoutSlotDefinition(id="hero", label="Hero", aspect_hint="landscape"),
            LayoutSlotDefinition(id="left", label="Left", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="note",
                label="Note",
                default_text="Surrounded by love and laughter.",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.7rem",
                default_font_weight="400",
                default_letter_spacing="0.1em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=2,
            suited_scenes=[
                "hero moment + quote or date line",
                "main shot + detail with caption cell",
            ],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "one strong hero landscape",
                "one supporting detail thumbnail",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=10,
                preferred_people_counts=[0, 1, 2, 3, 4],
                focus=["couple", "bride", "groom", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="quad_grid",
        name="Four grid",
        description=(
            "Four equal images in a 2×2 grid. Best for sequences, group shots, "
            "or thematic sets of similar weight."
        ),
        slots=[
            LayoutSlotDefinition(id="tl", label="Top left", aspect_hint="square"),
            LayoutSlotDefinition(id="tr", label="Top right", aspect_hint="square"),
            LayoutSlotDefinition(id="bl", label="Bottom left", aspect_hint="square"),
            LayoutSlotDefinition(id="br", label="Bottom right", aspect_hint="square"),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=4,
            suited_scenes=[
                "sequence / progression",
                "candids set",
                "family & friends mini-gallery",
                "details collage",
            ],
            story_positions=["mid"],
            looks_best_on=[
                "similar visual weight across images",
                "tight framing that crops well to square",
                "varied but coherent set (same event/lighting)",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=25,
                preferred_people_counts=[0, 1, 2, 4, 6, 10],
                focus=["family", "guests", "couple", "details"],
                notes="Great for mixing 0-people details with small group candids.",
            ),
        ),
    ),
    LayoutDefinition(
        id="feature_strip",
        name="Feature + strip",
        description=(
            "One large feature image with three smaller thumbnails in a horizontal strip. "
            "Highlights a key photo with contextual supporting shots."
        ),
        slots=[
            LayoutSlotDefinition(id="feature", label="Feature", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s1", label="Strip 1", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s2", label="Strip 2", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s3", label="Strip 3", aspect_hint="landscape"),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=4,
            suited_scenes=[
                "hero moment + 3 supporting beats",
                "ceremony highlight + reactions",
                "reception highlight + candids",
                "venue/mandap + details",
            ],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "one standout feature image",
                "supporting strip as details/reactions",
                "clear subjects (small strip images must read at small size)",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=20,
                preferred_people_counts=[0, 1, 2, 3, 4, 6],
                focus=["couple", "family", "guests", "details"],
                notes="Choose simple, readable thumbnails for the strip (faces/details with clear subject).",
            ),
        ),
    ),
    LayoutDefinition(
        id="full_bleed_caption",
        name="Full bleed + caption",
        description=(
            "Single full-bleed hero image with a short caption overlaid at the bottom. "
            "Best for iconic moments with a place name or date line."
        ),
        slots=[
            LayoutSlotDefinition(id="hero", label="Hero", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="caption",
                label="Caption",
                default_text="THE WEDDING DAY",
                color_hint=HINT_ON_PHOTO_CAPTION,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.7rem",
                default_font_weight="500",
                default_letter_spacing="0.14em",
                default_text_align="center",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=IMAGE_FULL_BLEED_CAPTION_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=[
                "opening hero with place/date",
                "venue establishing with label",
                "iconic moment with caption",
            ],
            story_positions=["opening", "mid", "ending"],
            looks_best_on=[
                "strong single subject",
                "negative space or bottom area for caption",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=6,
                preferred_people_counts=[0, 1, 2],
                focus=["couple", "bride", "groom"],
            ),
        ),
    ),
    LayoutDefinition(
        id="hero_pair_caption",
        name="Hero + pair + caption",
        description=(
            "Large hero with bottom caption overlay, plus two supporting images below."
        ),
        slots=[
            LayoutSlotDefinition(id="hero", label="Hero", aspect_hint="landscape"),
            LayoutSlotDefinition(id="left", label="Left", aspect_hint="landscape"),
            LayoutSlotDefinition(id="right", label="Right", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="caption",
                label="Caption",
                default_text="OUR FOREVER BEGINS",
                color_hint=HINT_ON_PHOTO_CAPTION,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.65rem",
                default_font_weight="500",
                default_letter_spacing="0.12em",
                default_text_align="left",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=IMAGE_HERO_CAPTION_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=[
                "hero moment + details with label",
                "ceremony highlight + caption",
            ],
            story_positions=["opening", "mid", "ending"],
            looks_best_on=[
                "one strong hero moment",
                "two supporting detail shots",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=10,
                preferred_people_counts=[0, 1, 2, 3, 4],
                focus=["couple", "bride", "groom", "family"],
            ),
        ),
    ),
    LayoutDefinition(
        id="split_diptych_caption",
        name="Diptych + captions",
        description=(
            "Two side-by-side portraits, each with an optional bottom caption overlay."
        ),
        slots=[
            LayoutSlotDefinition(id="left", label="Left", aspect_hint="portrait"),
            LayoutSlotDefinition(id="right", label="Right", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="left_caption",
                label="Left caption",
                default_text="BRIDE",
                color_hint=HINT_ON_PHOTO_LABEL,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.6rem",
                default_font_weight="500",
                default_letter_spacing="0.2em",
                default_text_align="center",
                default_text_transform="uppercase",
            ),
            LayoutTextSlotDefinition(
                id="right_caption",
                label="Right caption",
                default_text="GROOM",
                color_hint=HINT_ON_PHOTO_LABEL,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.6rem",
                default_font_weight="500",
                default_letter_spacing="0.2em",
                default_text_align="center",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=IMAGE_DIPTYCH_CAPTION_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=2,
            suited_scenes=[
                "bride vs groom with labels",
                "couple portrait pair with names",
            ],
            story_positions=["opening", "mid", "ending"],
            looks_best_on=[
                "two portraits with matching framing",
                "room for bottom caption on each panel",
            ],
            people=LayoutPeopleGuidance(
                min_people=1,
                max_people=6,
                preferred_people_counts=[1, 2],
                focus=["bride", "groom", "couple"],
            ),
        ),
    ),
    LayoutDefinition(
        id="feature_strip_caption",
        name="Feature + strip + caption",
        description=(
            "Large feature image with top caption overlay and three supporting thumbnails."
        ),
        slots=[
            LayoutSlotDefinition(id="feature", label="Feature", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s1", label="Strip 1", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s2", label="Strip 2", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s3", label="Strip 3", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="caption",
                label="Caption",
                default_text="THE CELEBRATION",
                color_hint=HINT_ON_PHOTO_CAPTION,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.65rem",
                default_font_weight="500",
                default_letter_spacing="0.12em",
                default_text_align="center",
                default_text_transform="uppercase",
            ),
        ],
        color_guidance=IMAGE_HERO_CAPTION_COLORS,
        metadata=LayoutTemplateMetadata(
            required_images=4,
            suited_scenes=[
                "hero moment + strip with feature caption",
                "ceremony highlight + reactions",
            ],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "one standout feature image",
                "supporting strip as details/reactions",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=20,
                preferred_people_counts=[0, 1, 2, 3, 4, 6],
                focus=["couple", "family", "guests", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="quad_grid_caption",
        name="Three grid + caption (right)",
        description=(
            "Three photos in a 2×2 grid with a typography cell in the bottom-right."
        ),
        slots=[
            LayoutSlotDefinition(id="tl", label="Top left", aspect_hint="square"),
            LayoutSlotDefinition(id="tr", label="Top right", aspect_hint="square"),
            LayoutSlotDefinition(id="bl", label="Bottom left", aspect_hint="square"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="caption",
                label="Caption",
                default_text="Memories we will cherish",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.75rem",
                default_font_weight="400",
                default_letter_spacing="0.08em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=[
                "mini-gallery with quote or date",
                "three moments + caption cell",
            ],
            story_positions=["mid"],
            looks_best_on=[
                "three cohesive square crops",
                "short quote or location line for caption cell",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=25,
                preferred_people_counts=[0, 1, 2, 4, 6],
                focus=["family", "guests", "couple", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="quad_grid_caption_left",
        name="Three grid + caption (left)",
        description=(
            "Three photos in a 2×2 grid with a typography cell in the bottom-left."
        ),
        slots=[
            LayoutSlotDefinition(id="tl", label="Top left", aspect_hint="square"),
            LayoutSlotDefinition(id="tr", label="Top right", aspect_hint="square"),
            LayoutSlotDefinition(id="br", label="Bottom right", aspect_hint="square"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="caption",
                label="Caption",
                default_text="Memories we will cherish",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.75rem",
                default_font_weight="400",
                default_letter_spacing="0.08em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=[
                "mini-gallery with quote or date",
                "three moments + caption cell on the left",
            ],
            story_positions=["mid"],
            looks_best_on=[
                "three cohesive square crops",
                "short quote or location line for caption cell",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=25,
                preferred_people_counts=[0, 1, 2, 4, 6],
                focus=["family", "guests", "couple", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="feature_strip_note",
        name="Feature + strip + note (right)",
        description=(
            "Large feature with two strip thumbnails and a text note cell on the right."
        ),
        slots=[
            LayoutSlotDefinition(id="feature", label="Feature", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s1", label="Strip 1", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s2", label="Strip 2", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="note",
                label="Note",
                default_text="A celebration of love & joy",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.7rem",
                default_font_weight="400",
                default_letter_spacing="0.1em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=[
                "hero + details with location/date note",
                "feature moment + place line",
            ],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "one standout feature",
                "two readable strip thumbnails",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=20,
                preferred_people_counts=[0, 1, 2, 3, 4, 6],
                focus=["couple", "family", "guests", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="feature_strip_note_left",
        name="Feature + strip + note (left)",
        description=(
            "Large feature with a text note cell on the left and two strip thumbnails on the right."
        ),
        slots=[
            LayoutSlotDefinition(id="feature", label="Feature", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s1", label="Strip 1", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s2", label="Strip 2", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="note",
                label="Note",
                default_text="A celebration of love & joy",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.7rem",
                default_font_weight="400",
                default_letter_spacing="0.1em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=[
                "hero + details with location/date note on the left",
                "feature moment + place line",
            ],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "one standout feature",
                "two readable strip thumbnails",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=20,
                preferred_people_counts=[0, 1, 2, 3, 4, 6],
                focus=["couple", "family", "guests", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="feature_strip_note_left_bottom",
        name="Feature + strip + note (left, feature bottom)",
        description=(
            "Strip row on top with a text note cell on the left and two thumbnails on the right; "
            "large feature image along the bottom."
        ),
        slots=[
            LayoutSlotDefinition(id="feature", label="Feature", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s1", label="Strip 1", aspect_hint="landscape"),
            LayoutSlotDefinition(id="s2", label="Strip 2", aspect_hint="landscape"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="note",
                label="Note",
                default_text="A celebration of love & joy",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.7rem",
                default_font_weight="400",
                default_letter_spacing="0.1em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=3,
            suited_scenes=[
                "hero + details with location/date note above the feature",
                "feature moment + place line",
            ],
            story_positions=["mid", "ending"],
            looks_best_on=[
                "one standout feature anchored at the bottom",
                "two readable strip thumbnails above",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=20,
                preferred_people_counts=[0, 1, 2, 3, 4, 6],
                focus=["couple", "family", "guests", "details"],
            ),
        ),
    ),
    LayoutDefinition(
        id="split_column_note_left",
        name="Column note (text left)",
        description=(
            "Two equal columns: typography on the left and a single portrait on the right."
        ),
        slots=[
            LayoutSlotDefinition(id="photo", label="Photo", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="note",
                label="Note",
                default_text="Every moment led us here.",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.8rem",
                default_font_weight="400",
                default_letter_spacing="0.08em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=[
                "quote beside portrait",
                "chapter line with hero shot",
            ],
            story_positions=["mid", "opening"],
            looks_best_on=[
                "strong vertical portrait",
                "short quote or date line",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=6,
                preferred_people_counts=[1, 2],
                focus=["couple", "bride", "groom"],
            ),
        ),
    ),
    LayoutDefinition(
        id="split_column_note_right",
        name="Column note (text right)",
        description=(
            "Two equal columns: single portrait on the left and typography on the right."
        ),
        slots=[
            LayoutSlotDefinition(id="photo", label="Photo", aspect_hint="portrait"),
        ],
        text_slots=[
            LayoutTextSlotDefinition(
                id="note",
                label="Note",
                default_text="Every moment led us here.",
                color_hint=HINT_SANS_BODY,
                default_font_family=FONT_SANS_LABEL,
                default_font_size="0.8rem",
                default_font_weight="400",
                default_letter_spacing="0.08em",
                default_text_align="center",
                default_text_transform="none",
            ),
        ],
        color_guidance=IMAGE_LED_BACKGROUND,
        metadata=LayoutTemplateMetadata(
            required_images=1,
            suited_scenes=[
                "quote beside portrait",
                "chapter line with hero shot",
            ],
            story_positions=["mid", "opening"],
            looks_best_on=[
                "strong vertical portrait",
                "short quote or date line",
            ],
            people=LayoutPeopleGuidance(
                min_people=0,
                max_people=6,
                preferred_people_counts=[1, 2],
                focus=["couple", "bride", "groom"],
            ),
        ),
    ),
)
