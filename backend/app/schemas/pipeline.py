"""Pipeline processing state schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class LibraryFlags(BaseModel):
    """Derived workspace readiness flags (persisted and sent over WebSocket)."""

    image_found: bool = False
    resize_complete: bool = False
    people_extraction_complete: bool = False
    has_analysed_color: bool = False
    image_analysis_complete: bool = False
    categorisation_complete: bool = False


class UserAction(BaseModel):
    action: str
    timestamp: datetime


class ProcessingTimestamps(BaseModel):
    resize_started_at: datetime | None = None
    resize_completed_at: datetime | None = None
    face_extraction_started_at: datetime | None = None
    face_extraction_completed_at: datetime | None = None
    analysis_started_at: datetime | None = None
    analysis_completed_at: datetime | None = None
    categorisation_started_at: datetime | None = None
    categorisation_completed_at: datetime | None = None


class PipelineStateDocument(BaseModel):
    flags: LibraryFlags = Field(default_factory=LibraryFlags)
    user_actions: list[UserAction] = Field(default_factory=list)
    processing: ProcessingTimestamps = Field(default_factory=ProcessingTimestamps)
    updated_at: datetime | None = None

    def has_action(self, action: str) -> bool:
        return any(item.action == action for item in self.user_actions)
