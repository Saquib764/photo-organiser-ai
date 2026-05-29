"""Persistent image category groupings for photobook planning."""

from datetime import datetime

from pydantic import BaseModel, Field


class ImageCategory(BaseModel):
    id: str
    description: str
    images: list[str] = Field(default_factory=list)


class ImageCategoriesDocument(BaseModel):
    categories: list[ImageCategory] = Field(default_factory=list)
    updated_at: datetime | None = None


class CategoriserImageInput(BaseModel):
    """Metadata row sent to the categoriser (no palette)."""

    path: str
    folder: str = ""
    caption: str = ""
    number_of_people: int = 0
    has_bride: bool = False
    has_groom: bool = False
    has_other_people: bool = False
    is_blur: bool = False
    quality_score: float = 0.0


class ExistingCategorySummary(BaseModel):
    id: str
    description: str


class CategoryBatchAssignment(BaseModel):
    id: str
    description: str | None = None
    images: list[str] = Field(default_factory=list)


class CategoriserBatchResult(BaseModel):
    assignments: list[CategoryBatchAssignment] = Field(default_factory=list)
