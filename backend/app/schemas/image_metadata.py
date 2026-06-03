"""Per-image analysis metadata persisted in the workspace."""

from pydantic import BaseModel, Field, field_validator


class ImageMetadataEntry(BaseModel):
    """One processed image; ``path`` is the stable identifier."""

    path: str
    caption: str = ""
    number_of_people: int = 0
    has_bride: bool = False
    has_groom: bool = False
    has_other_people: bool = False
    is_blur: bool = False
    quality_score: float = Field(default=0.0, ge=0, le=10)
    palette_colors: list[str] = Field(
        default_factory=list,
        description="Dominant colors as #rrggbb hex strings (up to 3, from Color Thief)",
    )
    person_ids: list[str] = Field(
        default_factory=list,
        description="Global person ids detected in this image (from face extraction)",
    )
    faces_scanned: bool = Field(
        default=False,
        description="True after this image was processed by face extraction",
    )

    @field_validator("caption", mode="before")
    @classmethod
    def empty_caption_when_missing(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value)

    @field_validator("number_of_people", mode="before")
    @classmethod
    def coerce_people_count(cls, value: object) -> int:
        if value is None:
            return 0
        return int(value)

    @field_validator("quality_score", mode="before")
    @classmethod
    def coerce_quality_score(cls, value: object) -> float:
        if value is None:
            return 0.0
        return float(value)

    def needs_analysis(self) -> bool:
        """True until a caption has been generated."""
        return not self.caption.strip()

    def clear_analysis(self) -> None:
        """Reset OpenAI-derived fields; keeps path, palette, and face fields."""
        self.caption = ""
        self.number_of_people = 0
        self.has_bride = False
        self.has_groom = False
        self.has_other_people = False
        self.is_blur = False
        self.quality_score = 0.0

    def clear_faces(self) -> None:
        self.person_ids = []
        self.faces_scanned = False

    def apply_analysis(
        self,
        *,
        caption: str,
        number_of_people: int,
        has_bride: bool,
        has_groom: bool,
        has_other_people: bool,
        is_blur: bool,
        quality_score: float,
    ) -> None:
        self.caption = caption
        self.number_of_people = number_of_people
        self.has_bride = has_bride
        self.has_groom = has_groom
        self.has_other_people = has_other_people
        self.is_blur = is_blur
        self.quality_score = quality_score


class ImageMetadataDocument(BaseModel):
    """All processed images keyed by path."""

    images: list[ImageMetadataEntry] = Field(default_factory=list)

    def get_by_path(self, path: str) -> ImageMetadataEntry | None:
        for entry in self.images:
            if entry.path == path:
                return entry
        return None
