"""Workspace status payload tests."""

from pathlib import Path

from PIL import Image

from app.services.image_processing import process_all_raw_images
from app.services.pipeline_state import load_state_document, refresh_pipeline_state
from app.services.status import build_workspace_status
from app.services.workspace import collect_workspace_counts


def _write_image(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(100, 120, 140)).save(path)


def test_build_workspace_status_includes_progress(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "a.jpg", (200, 150))
    _write_image(raw / "b.jpg", (200, 150))

    status = build_workspace_status(tmp_path)

    assert status.progress_total == 2
    assert status.progress_completed == 0
    assert status.progress_remaining == 2


def test_build_workspace_status_reflects_completed_resize(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "a.jpg", (200, 150))
    _write_image(raw / "b.jpg", (200, 150))

    process_all_raw_images(tmp_path, max_dimension=80)
    status = build_workspace_status(tmp_path)

    assert status.progress_total == 2
    assert status.progress_completed == 2
    assert status.progress_remaining == 0


def test_discover_finds_new_raw_images_on_refresh(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "a.jpg", (200, 150))
    process_all_raw_images(tmp_path, max_dimension=80)
    refresh_pipeline_state(tmp_path)

    status = build_workspace_status(tmp_path)
    assert status.flags.resize_complete is True
    assert status.total_images_raw == 1

    _write_image(raw / "b.jpg", (200, 150))

    status = build_workspace_status(tmp_path, discover=True)

    assert status.total_images_raw == 2
    assert status.flags.image_found is True
    assert status.flags.resize_complete is False
    assert status.progress_remaining == 1

    document = load_state_document(tmp_path)
    assert document.flags.resize_complete is False


def test_collect_workspace_counts_reuses_single_raw_scan(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "only.jpg", (100, 80))

    counts = collect_workspace_counts(tmp_path)

    assert counts.total_images_raw == 1
    assert counts.total_images_processed == 0
