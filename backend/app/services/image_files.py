"""Path resolution and media type helpers for workspace images.

This module centralizes:
- Safe resolution of relative paths within raw/ and processed_small/
- Content-type inference for image file responses
"""

from __future__ import annotations

from pathlib import Path

from app.services.workspace import IMAGE_EXTENSIONS, PROCESSED_DIR_NAME, RAW_DIR_NAME


def _is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def resolve_raw_image_path(workspace_root: Path, rel_path: str) -> Path:
    """
    Resolve a relative path to a file under raw/.

    Raises ValueError when the path is invalid or escapes the raw directory.
    """
    if not rel_path or rel_path.startswith("/"):
        raise ValueError("Invalid image path")

    rel = Path(rel_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Invalid image path")

    raw_dir = (workspace_root / RAW_DIR_NAME).resolve()
    candidate = (raw_dir / rel).resolve()

    try:
        candidate.relative_to(raw_dir)
    except ValueError as exc:
        raise ValueError("Invalid image path") from exc

    if not _is_image(candidate):
        raise ValueError("Image not found")

    return candidate


def resolve_processed_image_path(workspace_root: Path, rel_path: str) -> Path:
    """
    Resolve a relative path to a file under processed_small/.

    Raises ValueError when the path is invalid or escapes the processed directory.
    """
    if not rel_path or rel_path.startswith("/"):
        raise ValueError("Invalid image path")

    rel = Path(rel_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Invalid image path")

    processed_dir = (workspace_root / PROCESSED_DIR_NAME).resolve()
    candidate = (processed_dir / rel).resolve()

    try:
        candidate.relative_to(processed_dir)
    except ValueError as exc:
        raise ValueError("Invalid image path") from exc

    if not _is_image(candidate):
        raise ValueError("Image not found")

    return candidate


def media_type_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".heic": "image/heic",
        ".heif": "image/heif",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }.get(suffix, "application/octet-stream")

