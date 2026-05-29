"""Schemas for image browser folder listing and processed image serving."""

from pydantic import BaseModel, Field


class FolderInfo(BaseModel):
    """A top-level album folder under workspace/raw/."""

    name: str
    image_count: int = Field(ge=0)


class ImageCategorySummary(BaseModel):
    """Story category from image_categories.json for gallery filters."""

    id: str
    description: str = ""
    image_count: int = Field(default=0, ge=0)


class ImageEntry(BaseModel):
    """A processed thumbnail with optional analysis metadata (keyed by path)."""

    path: str
    folder: str = Field(description="Top-level folder name; empty string for root-level images")
    category_id: str | None = Field(
        default=None,
        description="Story category id from image_categories.json, if assigned",
    )
    caption: str = ""
    number_of_people: int = Field(default=0, ge=0)
    has_bride: bool = False
    has_groom: bool = False
    has_other_people: bool = False
    is_blur: bool = False
    quality_score: float = Field(default=0.0, ge=0, le=10)
    analyzed: bool = Field(
        default=False,
        description="True when a non-empty caption exists in image_metadata.json",
    )
    palette_colors: list[str] = Field(
        default_factory=list,
        description="Dominant colors as #rrggbb hex strings (up to 3)",
    )


class FolderListResponse(BaseModel):
    folders: list[FolderInfo]


class CategoryListResponse(BaseModel):
    categories: list[ImageCategorySummary]


class ImageListResponse(BaseModel):
    images: list[ImageEntry]
    total: int = Field(ge=0)


class ImageDeleteResponse(BaseModel):
    path: str
    deleted_raw: bool = False
    deleted_processed: bool = False
    removed_from_metadata: bool = False
    removed_from_categories: bool = False
