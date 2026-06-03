"""Person registry persisted in the workspace."""

from datetime import datetime

from pydantic import BaseModel, Field


class PersonEntry(BaseModel):
    id: str
    name: str
    description: str = ""
    thumbnail: str = Field(description="Filename under workspace/persons/")
    face_count: int = Field(default=0, ge=0)
    image_count: int = Field(default=0, ge=0)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PersonDocument(BaseModel):
    persons: list[PersonEntry] = Field(default_factory=list)
    updated_at: datetime | None = None


class PersonSummary(BaseModel):
    id: str
    name: str
    description: str = ""
    thumbnail_url: str
    face_count: int = Field(default=0, ge=0)
    image_count: int = Field(default=0, ge=0)


class PersonListResponse(BaseModel):
    persons: list[PersonSummary]


class PersonUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class PersonDeleteResponse(BaseModel):
    id: str
    removed_from_metadata: int = Field(
        default=0,
        ge=0,
        description="Number of image metadata entries updated",
    )
