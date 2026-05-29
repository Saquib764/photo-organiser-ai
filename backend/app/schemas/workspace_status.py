"""Workspace status schemas."""

from pydantic import BaseModel

from app.schemas.pipeline import LibraryFlags


class WorkspaceCounts(BaseModel):
    """Filesystem counts for the photo workspace."""

    total_folder_raw: int
    total_images_raw: int
    total_images_processed: int


class WorkspaceStatus(WorkspaceCounts):
    """Counts, library flags, and processing progress for API / WebSocket."""

    flags: LibraryFlags
    processing_busy: bool = False
    progress_total: int = 0
    progress_completed: int = 0
    progress_remaining: int = 0
    processing_phase: str | None = None
    resize_completed_count: int = 0
    resize_total_count: int = 0
    palette_completed_count: int = 0
    palette_total_count: int = 0
    analysis_completed_count: int = 0
    analysis_total_count: int = 0
    categorisation_completed_count: int = 0
    categorisation_total_count: int = 0
    categories_count: int = 0
    openai_configured: bool = False
