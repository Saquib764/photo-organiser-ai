"""Tests for compose retry policy."""

from datetime import UTC, datetime, timedelta

from app.schemas.photobook import PhotobookPage
from app.services.photobook_compose_policy import can_start_compose, mark_compose_started


def test_can_start_compose_when_not_composing() -> None:
    page = PhotobookPage(id="p1", status="draft")
    assert can_start_compose(page) is True


def test_cannot_start_compose_within_one_minute() -> None:
    page = PhotobookPage(id="p1", status="composing")
    mark_compose_started(page)
    assert can_start_compose(page) is False


def test_can_start_compose_after_one_minute() -> None:
    page = PhotobookPage(id="p1", status="composing")
    started = datetime.now(UTC) - timedelta(seconds=61)
    page.composing_started_at = started.isoformat()
    assert can_start_compose(page) is True


def test_can_start_compose_without_timestamp() -> None:
    page = PhotobookPage(id="p1", status="composing")
    assert can_start_compose(page) is True
