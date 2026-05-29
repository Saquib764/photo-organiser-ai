"""Tests for raw → processed_small image resizing."""

from pathlib import Path

from PIL import Image

from app.services.image_processing import (
    is_processed_up_to_date,
    process_all_raw_images,
)
from app.services.workspace import collect_workspace_status


def _write_image(path: Path, size: tuple[int, int], mode: str = "RGB") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new(mode, size, color="red").save(path)


def test_process_all_raw_images_resizes_and_mirrors_structure(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    processed = tmp_path / "processed_small"
    raw.mkdir()
    processed.mkdir()

    _write_image(raw / "wide.jpg", (400, 200))
    _write_image(raw / "album" / "tall.png", (100, 400))
    (raw / "album" / "notes.txt").write_text("skip", encoding="utf-8")

    result = process_all_raw_images(tmp_path, max_dimension=200, worker_count=4)

    assert result.processed == 2
    assert result.skipped == 0
    assert result.failed == 0

    with Image.open(processed / "wide.jpg") as wide:
        assert wide.size == (200, 100)

    with Image.open(processed / "album" / "tall.png") as tall:
        assert tall.size == (50, 200)

    status = collect_workspace_status(tmp_path)
    assert status.total_images_processed == 2


def test_process_all_raw_images_uses_config_default(
    tmp_path: Path, monkeypatch
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "processed_max_dimension", 100)
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()

    _write_image(raw / "photo.jpg", (300, 300))

    process_all_raw_images(tmp_path)

    with Image.open(tmp_path / "processed_small" / "photo.jpg") as img:
        assert img.size == (100, 100)


def test_process_all_raw_images_skips_up_to_date(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    processed = tmp_path / "processed_small"
    raw.mkdir()
    processed.mkdir()

    source = raw / "photo.jpg"
    dest = processed / "photo.jpg"
    _write_image(source, (400, 300))
    first = process_all_raw_images(tmp_path, max_dimension=200, worker_count=4)
    assert first.processed == 1

    assert is_processed_up_to_date(source, dest)

    second = process_all_raw_images(tmp_path, max_dimension=200, worker_count=4)

    assert second.processed == 0
    assert second.skipped == 1
    assert second.failed == 0
    with Image.open(dest) as img:
        assert img.size == (200, 150)


def test_process_all_raw_images_resizes_stale_outputs(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    processed = tmp_path / "processed_small"
    raw.mkdir()
    processed.mkdir()

    source = raw / "photo.jpg"
    dest = processed / "photo.jpg"
    _write_image(dest, (50, 50))
    _write_image(source, (400, 300))

    assert not is_processed_up_to_date(source, dest)

    result = process_all_raw_images(tmp_path, max_dimension=200, worker_count=4)

    assert result.processed == 1
    assert result.skipped == 0
    with Image.open(dest) as img:
        assert img.size == (200, 150)
