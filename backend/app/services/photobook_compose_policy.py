"""When a page may be composed or recomposed."""

from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.photobook import PhotobookPage

COMPOSE_RETRY_AFTER_SECONDS = 60


def can_start_compose(page: PhotobookPage, *, now: datetime | None = None) -> bool:
    if page.status != "composing":
        return True
    if not page.composing_started_at:
        return True
    try:
        started = datetime.fromisoformat(page.composing_started_at)
    except ValueError:
        return True
    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    at = now or datetime.now(UTC)
    return (at - started).total_seconds() >= COMPOSE_RETRY_AFTER_SECONDS


def mark_compose_started(page: PhotobookPage) -> None:
    page.status = "composing"
    page.composing_started_at = datetime.now(UTC).isoformat()
    page.error_message = None


def mark_compose_finished(page: PhotobookPage) -> None:
    page.composing_started_at = None
