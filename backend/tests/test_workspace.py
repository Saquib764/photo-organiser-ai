"""Tests for workspace directory helpers."""

from pathlib import Path

from app.services.workspace import (
    collect_workspace_status,
    ensure_workspace_dirs,
)


def test_ensure_workspace_dirs_creates_expected_paths(tmp_path: Path) -> None:
    ensure_workspace_dirs(tmp_path)

    assert (tmp_path / "raw").is_dir()
    assert (tmp_path / "processed_small").is_dir()
    ensure_workspace_dirs(tmp_path)


def test_collect_workspace_status_counts_files_and_folders(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    processed = tmp_path / "processed_small"
    raw.mkdir()
    processed.mkdir()

    (raw / "album-a").mkdir()
    (raw / "album-b").mkdir()
    (raw / "root.jpg").write_bytes(b"x")
    (raw / "album-a" / "nested.png").write_bytes(b"x")
    (processed / "thumb.webp").write_bytes(b"x")
    (processed / "nested").mkdir()
    (processed / "nested" / "out.jpeg").write_bytes(b"x")
    (raw / "album-a" / "notes.txt").write_bytes(b"skip")

    status = collect_workspace_status(tmp_path)

    assert status.total_folder_raw == 2
    assert status.total_images_raw == 2
    assert status.total_images_processed == 2
