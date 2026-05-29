"""Load, sync, and persist per-image analysis metadata for processed images."""

from __future__ import annotations

import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.config import settings
from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry
from app.services.image_features import palette_hex_from_file
from app.services.image_files import resolve_processed_image_path
from app.services.image_processing import ResizeProgress
from app.services.workspace import IMAGE_EXTENSIONS, PROCESSED_DIR_NAME

logger = logging.getLogger(__name__)

_palette_progress_lock = threading.Lock()
_live_palette_progress: dict[str, int | bool] = {
    "total": 0,
    "completed": 0,
    "running": False,
}

METADATA_FILENAME = "image_metadata.json"


def metadata_file_path(workspace_root: Path) -> Path:
    return workspace_root / METADATA_FILENAME


def empty_metadata_entry(path: str) -> ImageMetadataEntry:
    """New workspace images start with empty analysis fields."""
    return ImageMetadataEntry(path=path)


def list_processed_image_paths(workspace_root: Path) -> list[str]:
    """Relative paths under ``processed_small/``, sorted for stable storage."""
    processed_dir = workspace_root / PROCESSED_DIR_NAME
    if not processed_dir.is_dir():
        return []

    paths: list[str] = []
    for path in processed_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            paths.append(path.relative_to(processed_dir).as_posix())
    return sorted(paths)


def load_metadata_document(workspace_root: Path) -> ImageMetadataDocument:
    """Load metadata from disk, or return an empty document if the file is missing."""
    path = metadata_file_path(workspace_root)
    if not path.is_file():
        return ImageMetadataDocument()

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return ImageMetadataDocument.model_validate(raw)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Invalid image metadata file at %s, resetting", path)
        return ImageMetadataDocument()


def save_metadata_document(
    workspace_root: Path,
    document: ImageMetadataDocument,
) -> None:
    path = metadata_file_path(workspace_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        document.model_dump_json(indent=2),
        encoding="utf-8",
    )


def sync_metadata_document(workspace_root: Path) -> ImageMetadataDocument:
    """
    Ensure ``image_metadata.json`` exists and lists every processed image.

    New paths are added with empty analysis fields. Removed paths are dropped.
    Existing entries are preserved (keyed by ``path``).
    """
    processed_paths = list_processed_image_paths(workspace_root)
    document = load_metadata_document(workspace_root)
    by_path = {entry.path: entry for entry in document.images}

    document.images = [
        by_path[path] if path in by_path else empty_metadata_entry(path)
        for path in processed_paths
    ]

    save_metadata_document(workspace_root, document)
    return document


def clear_analysis_metadata(document: ImageMetadataDocument) -> None:
    """Clear caption and analysis fields on every entry (e.g. before a full re-run)."""
    for entry in document.images:
        entry.clear_analysis()


def caption_counts(document: ImageMetadataDocument) -> tuple[int, int]:
    """Return ``(completed_count, total_count)`` where completed means analyzed."""
    total = len(document.images)
    completed = sum(1 for entry in document.images if not entry.needs_analysis())
    return completed, total


def is_metadata_analysis_complete(document: ImageMetadataDocument) -> bool:
    """True when there is at least one image and every entry has a caption."""
    if not document.images:
        return False
    return all(not entry.needs_analysis() for entry in document.images)


def needs_palette_extraction(document: ImageMetadataDocument) -> bool:
    """True when at least one image is missing dominant colors."""
    return any(not entry.palette_colors for entry in document.images)


def is_palette_extraction_complete(document: ImageMetadataDocument) -> bool:
    """True when there is at least one image and every entry has palette colors."""
    if not document.images:
        return False
    return not needs_palette_extraction(document)


def palette_counts(document: ImageMetadataDocument) -> tuple[int, int]:
    """Return ``(completed_count, total_count)`` where completed means has palette colors."""
    total = len(document.images)
    completed = sum(1 for entry in document.images if entry.palette_colors)
    return completed, total


def _set_live_palette_progress(*, total: int, completed: int, running: bool) -> None:
    with _palette_progress_lock:
        _live_palette_progress["total"] = total
        _live_palette_progress["completed"] = completed
        _live_palette_progress["running"] = running


def get_live_palette_progress() -> ResizeProgress | None:
    with _palette_progress_lock:
        if not _live_palette_progress["running"]:
            return None
        total = int(_live_palette_progress["total"])
        completed = int(_live_palette_progress["completed"])
    return ResizeProgress.from_completed(total, completed)


def _increment_live_palette_progress() -> None:
    with _palette_progress_lock:
        _live_palette_progress["completed"] = int(_live_palette_progress["completed"]) + 1


def _refresh_pipeline_flags(
    workspace_root: Path,
    metadata: ImageMetadataDocument | None = None,
) -> None:
    from app.services.pipeline_state import refresh_pipeline_flags

    refresh_pipeline_flags(workspace_root, metadata=metadata)


def _pending_palette_entries(
    document: ImageMetadataDocument,
    *,
    only_missing: bool,
) -> list[ImageMetadataEntry]:
    entries = [
        entry
        for entry in document.images
        if not only_missing or not entry.palette_colors
    ]
    return sorted(entries, key=lambda entry: entry.path)


def _apply_batch_palettes(
    document: ImageMetadataDocument,
    palettes_by_path: dict[str, list[str]],
) -> int:
    updated = 0
    for entry in document.images:
        if entry.path not in palettes_by_path:
            continue
        palette = palettes_by_path[entry.path]
        if palette != entry.palette_colors:
            entry.palette_colors = palette
            updated += 1
    return updated


def _extract_palette_batch(
    workspace_root: Path,
    batch_entries: list[ImageMetadataEntry],
) -> dict[str, list[str]]:
    workers = settings.resize_worker_count
    palettes_by_path: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_extract_palette_for_entry, workspace_root, entry)
            for entry in batch_entries
        ]
        for future in as_completed(futures):
            path, palette = future.result()
            palettes_by_path[path] = palette
            _increment_live_palette_progress()
    return palettes_by_path


def _extract_palette_for_entry(
    workspace_root: Path,
    entry: ImageMetadataEntry,
) -> tuple[str, list[str]]:
    try:
        image_path = resolve_processed_image_path(workspace_root, entry.path)
    except ValueError:
        logger.warning("Skipping palette extraction for missing image %s", entry.path)
        return entry.path, []
    return entry.path, palette_hex_from_file(image_path)


def extract_image_palettes(
    workspace_root: Path,
    *,
    only_missing: bool = False,
    batch_size: int | None = None,
) -> int:
    """
    Extract dominant colors for processed images using Color Thief.

    When *only_missing* is True, skip entries that already have palette_colors.
    Processes images in batches (see ``settings.palette_batch_size``) and saves
    metadata after each batch so progress survives restarts.
    Returns the number of entries whose palette was updated.
    """
    size = batch_size if batch_size is not None else settings.palette_batch_size
    document = sync_metadata_document(workspace_root)
    pending = _pending_palette_entries(document, only_missing=only_missing)
    if not pending:
        return 0

    total_pending = len(pending)
    _set_live_palette_progress(total=total_pending, completed=0, running=True)
    total_updated = 0

    try:
        for offset in range(0, total_pending, size):
            batch_paths = {
                entry.path for entry in pending[offset : offset + size]
            }
            document = sync_metadata_document(workspace_root)
            batch_entries = [
                entry
                for entry in document.images
                if entry.path in batch_paths
                and (not only_missing or not entry.palette_colors)
            ]
            if not batch_entries:
                continue

            palettes_by_path = _extract_palette_batch(workspace_root, batch_entries)
            updated_in_batch = _apply_batch_palettes(document, palettes_by_path)
            save_metadata_document(workspace_root, document)
            total_updated += updated_in_batch
            logger.info(
                "Palette batch saved: %d updated (%d/%d processed this run)",
                updated_in_batch,
                min(offset + len(batch_entries), total_pending),
                total_pending,
            )
            _refresh_pipeline_flags(workspace_root, metadata=document)
    finally:
        with _palette_progress_lock:
            completed = int(_live_palette_progress["completed"])
        _set_live_palette_progress(
            total=total_pending,
            completed=completed,
            running=False,
        )

    if total_updated:
        logger.info(
            "Extracted palettes for %d images across batches",
            total_updated,
        )

    return total_updated
