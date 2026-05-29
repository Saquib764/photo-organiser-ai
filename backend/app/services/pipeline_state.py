"""Persist and compute workspace library flags."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.image_metadata import ImageMetadataDocument
from app.schemas.pipeline import (
    LibraryFlags,
    PipelineStateDocument,
    UserAction,
)
from app.services.image_metadata import (
    is_metadata_analysis_complete,
    is_palette_extraction_complete,
    load_metadata_document,
    sync_metadata_document,
)
from app.services.image_categoriser import (
    build_categorisation_gallery,
    is_categorisation_complete,
    load_categories_document,
)
from app.services.image_processing import RawScan, ResizeProgress, is_resize_complete, scan_raw
from app.services.workspace import RAW_DIR_NAME, count_raw_subfolders

logger = logging.getLogger(__name__)

STATE_FILENAME = "pipeline_state.json"


def state_file_path(workspace_root: Path) -> Path:
    return workspace_root / STATE_FILENAME


def load_state_document(workspace_root: Path) -> PipelineStateDocument:
    path = state_file_path(workspace_root)
    if not path.is_file():
        return PipelineStateDocument()

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return PipelineStateDocument.model_validate(raw)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Invalid pipeline state file at %s, resetting", path)
        return PipelineStateDocument()


def save_state_document(workspace_root: Path, document: PipelineStateDocument) -> None:
    path = state_file_path(workspace_root)
    document.updated_at = datetime.now(UTC)
    path.write_text(
        document.model_dump_json(indent=2),
        encoding="utf-8",
    )


def record_user_action(workspace_root: Path, action: str) -> PipelineStateDocument:
    document = load_state_document(workspace_root)
    document.user_actions.append(
        UserAction(action=action, timestamp=datetime.now(UTC)),
    )
    save_state_document(workspace_root, document)
    logger.info("Recorded user action %r", action)
    return document


def raw_scan_for_complete_library(
    workspace_root: Path,
    *,
    image_count: int,
) -> RawScan:
    """Cheap scan snapshot when resize is already known complete."""
    raw_dir = workspace_root / RAW_DIR_NAME
    total = max(image_count, 0)
    return RawScan(
        total_folders=count_raw_subfolders(raw_dir) if raw_dir.is_dir() else 0,
        total_images=total,
        progress=ResizeProgress.from_completed(total, total),
    )


def compute_library_flags(
    workspace_root: Path,
    document: PipelineStateDocument,
    *,
    raw_scan: RawScan | None = None,
    metadata: ImageMetadataDocument | None = None,
    assume_resize_complete: bool = False,
) -> LibraryFlags:
    scan = raw_scan or scan_raw(workspace_root)
    image_found = scan.total_images > 0
    if assume_resize_complete:
        resize_complete = image_found
    else:
        resize_complete = image_found and is_resize_complete(
            workspace_root,
            raw_scan=scan,
        )
    if metadata is None:
        metadata = load_metadata_document(workspace_root)
    has_analysed_color = resize_complete and is_palette_extraction_complete(metadata)
    image_analysis_complete = resize_complete and is_metadata_analysis_complete(
        metadata,
    )
    gallery = build_categorisation_gallery(workspace_root, metadata)
    categories = load_categories_document(workspace_root)
    categorisation_complete = (
        image_analysis_complete
        and is_categorisation_complete(gallery, categories)
    )

    return LibraryFlags(
        image_found=image_found,
        resize_complete=resize_complete,
        has_analysed_color=has_analysed_color,
        image_analysis_complete=image_analysis_complete,
        categorisation_complete=categorisation_complete,
    )


def _apply_flags_to_document(
    workspace_root: Path,
    document: PipelineStateDocument,
    flags: LibraryFlags,
) -> PipelineStateDocument:
    if flags.image_analysis_complete:
        if document.processing.analysis_completed_at is None:
            document.processing.analysis_completed_at = datetime.now(UTC)
    else:
        document.processing.analysis_completed_at = None

    if flags.categorisation_complete:
        if document.processing.categorisation_completed_at is None:
            document.processing.categorisation_completed_at = datetime.now(UTC)
    else:
        document.processing.categorisation_completed_at = None

    document.flags = flags
    save_state_document(workspace_root, document)
    return document


def discover_workspace_changes(workspace_root: Path) -> RawScan:
    """
    Rescan raw/ and update persisted flags when the library may have changed.

    Does not sync or rewrite image_metadata.json (fast enough for page refresh).
    """
    raw_scan = scan_raw(workspace_root)
    document = load_state_document(workspace_root)
    metadata = load_metadata_document(workspace_root)
    flags = compute_library_flags(
        workspace_root,
        document,
        raw_scan=raw_scan,
        metadata=metadata,
        assume_resize_complete=False,
    )
    _apply_flags_to_document(workspace_root, document, flags)
    logger.info(
        "Discovered workspace: %d raw images, resize_complete=%s",
        raw_scan.total_images,
        flags.resize_complete,
    )
    return raw_scan


def refresh_pipeline_flags(
    workspace_root: Path,
    *,
    metadata: ImageMetadataDocument | None = None,
) -> PipelineStateDocument:
    """
    Update persisted flags without syncing metadata or full raw/processed scans.

    Used after each palette batch so status polls stay fast on large libraries.
    """
    from app.services.pipeline_runner import is_resize_running

    document = load_state_document(workspace_root)
    if metadata is None:
        metadata = load_metadata_document(workspace_root)

    assume_resize = document.flags.resize_complete and not is_resize_running()
    if assume_resize:
        raw_scan = raw_scan_for_complete_library(
            workspace_root,
            image_count=len(metadata.images),
        )
    else:
        raw_scan = scan_raw(workspace_root)

    flags = compute_library_flags(
        workspace_root,
        document,
        raw_scan=raw_scan,
        metadata=metadata,
        assume_resize_complete=assume_resize,
    )
    return _apply_flags_to_document(workspace_root, document, flags)


def refresh_pipeline_state(workspace_root: Path) -> PipelineStateDocument:
    raw_scan = scan_raw(workspace_root)
    document = load_state_document(workspace_root)
    metadata = sync_metadata_document(workspace_root)
    flags = compute_library_flags(
        workspace_root,
        document,
        raw_scan=raw_scan,
        metadata=metadata,
    )
    return _apply_flags_to_document(workspace_root, document, flags)
