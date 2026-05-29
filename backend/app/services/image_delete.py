"""Delete workspace images from disk and JSON sidecars."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.services.image_categoriser import (
    load_categories_document,
    remove_empty_categories,
    save_categories_document,
)
from app.services.image_metadata import load_metadata_document, save_metadata_document
from app.services.workspace import PROCESSED_DIR_NAME, RAW_DIR_NAME

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ImageDeleteResult:
    path: str
    deleted_raw: bool
    deleted_processed: bool
    removed_from_metadata: bool
    removed_from_categories: bool


def _validated_rel_path(rel_path: str) -> Path:
    if not rel_path or rel_path.startswith("/"):
        raise ValueError("Invalid image path")

    rel = Path(rel_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Invalid image path")
    return rel


def _unlink_if_exists(path: Path) -> bool:
    if not path.is_file():
        return False
    path.unlink()
    return True


def remove_path_from_metadata(workspace_root: Path, rel_path: str) -> bool:
    document = load_metadata_document(workspace_root)
    before = len(document.images)
    document.images = [entry for entry in document.images if entry.path != rel_path]
    if len(document.images) == before:
        return False
    save_metadata_document(workspace_root, document)
    return True


def remove_path_from_categories(workspace_root: Path, rel_path: str) -> bool:
    document = load_categories_document(workspace_root)
    removed = False
    for category in document.categories:
        before = len(category.images)
        category.images = [path for path in category.images if path != rel_path]
        if len(category.images) != before:
            removed = True
    if not removed:
        return False
    remove_empty_categories(document)
    save_categories_document(workspace_root, document)
    return True


def delete_workspace_image(workspace_root: Path, rel_path: str) -> ImageDeleteResult:
    """
    Remove an image from raw/, processed_small/, image_metadata.json, and image_categories.json.

    Raises ValueError for invalid paths. Raises FileNotFoundError when nothing was removed.
    """
    rel = _validated_rel_path(rel_path)
    posix_path = rel.as_posix()

    raw_dir = (workspace_root / RAW_DIR_NAME).resolve()
    processed_dir = (workspace_root / PROCESSED_DIR_NAME).resolve()

    raw_candidate = (raw_dir / rel).resolve()
    processed_candidate = (processed_dir / rel).resolve()
    try:
        raw_candidate.relative_to(raw_dir)
        processed_candidate.relative_to(processed_dir)
    except ValueError as exc:
        raise ValueError("Invalid image path") from exc

    deleted_raw = _unlink_if_exists(raw_candidate)
    deleted_processed = _unlink_if_exists(processed_candidate)

    removed_from_metadata = remove_path_from_metadata(workspace_root, posix_path)
    removed_from_categories = remove_path_from_categories(workspace_root, posix_path)

    if not any(
        (
            deleted_raw,
            deleted_processed,
            removed_from_metadata,
            removed_from_categories,
        )
    ):
        raise FileNotFoundError(f"Image not found: {posix_path}")

    logger.info(
        "Deleted workspace image %s (raw=%s processed=%s metadata=%s categories=%s)",
        posix_path,
        deleted_raw,
        deleted_processed,
        removed_from_metadata,
        removed_from_categories,
    )

    return ImageDeleteResult(
        path=posix_path,
        deleted_raw=deleted_raw,
        deleted_processed=deleted_processed,
        removed_from_metadata=removed_from_metadata,
        removed_from_categories=removed_from_categories,
    )
