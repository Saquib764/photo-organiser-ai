"""Workspace directory bootstrap and status collection."""

import logging
from pathlib import Path

from app.schemas.workspace_status import WorkspaceCounts

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".heic",
        ".heif",
        ".bmp",
        ".tiff",
        ".tif",
    }
)

RAW_DIR_NAME = "raw"
PROCESSED_DIR_NAME = "processed_small"


def ensure_workspace_dirs(workspace_root: Path) -> None:
    """Create workspace, raw, and processed_small if missing."""
    for path in (
        workspace_root,
        workspace_root / RAW_DIR_NAME,
        workspace_root / PROCESSED_DIR_NAME,
    ):
        path.mkdir(parents=True, exist_ok=True)
    logger.info("Workspace ready at %s", workspace_root.resolve())


def count_images(directory: Path) -> int:
    if not directory.is_dir():
        return 0

    return sum(
        1
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def count_raw_subfolders(raw_dir: Path) -> int:
    if not raw_dir.is_dir():
        return 0
    return sum(1 for path in raw_dir.iterdir() if path.is_dir())


def collect_workspace_counts(workspace_root: Path) -> WorkspaceCounts:
    """Scan workspace folders and return current counts."""
    from app.services.image_processing import scan_raw

    raw_scan = scan_raw(workspace_root)
    processed_dir = workspace_root / PROCESSED_DIR_NAME

    return WorkspaceCounts(
        total_folder_raw=raw_scan.total_folders,
        total_images_raw=raw_scan.total_images,
        total_images_processed=count_images(processed_dir),
    )


# Backwards-compatible alias for tests and callers
collect_workspace_status = collect_workspace_counts
