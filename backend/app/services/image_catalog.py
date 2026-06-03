"""List workspace folders/images and resolve paths for processed image serving."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.schemas.image_catalog import FolderInfo, ImageCategorySummary, ImageEntry
from app.schemas.image_metadata import ImageMetadataEntry
from app.services.image_categoriser import load_categories_document
from app.services.image_files import (
    media_type_for_path,
    resolve_processed_image_path,
    resolve_raw_image_path,
)
from app.services.image_metadata import load_metadata_document
from app.services.workspace import IMAGE_EXTENSIONS, PROCESSED_DIR_NAME, RAW_DIR_NAME

logger = logging.getLogger(__name__)

ROOT_FOLDER_KEY = ""


@dataclass(frozen=True, slots=True)
class ImageListFilters:
    """Optional metadata filters for the image browser."""

    has_bride: bool | None = None
    has_groom: bool | None = None
    has_other_people: bool | None = None
    min_people: int | None = None
    max_people: int | None = None
    analyzed: bool | None = None
    is_blur: bool | None = None
    min_quality_score: float | None = None
    max_quality_score: float | None = None
    category_ids: frozenset[str] | None = None
    uncategorized: bool | None = None
    person_ids: frozenset[str] | None = None


def _is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def _top_level_folder(rel: Path) -> str:
    """First path segment under raw/, or empty for files at raw root."""
    parts = rel.parts
    return parts[0] if len(parts) > 1 else ROOT_FOLDER_KEY


def _metadata_by_path(workspace_root: Path) -> dict[str, ImageMetadataEntry]:
    document = load_metadata_document(workspace_root)
    return {entry.path: entry for entry in document.images}


def category_id_by_path(workspace_root: Path) -> dict[str, str]:
    """Map processed image paths to story category ids."""
    document = load_categories_document(workspace_root)
    mapping: dict[str, str] = {}
    for category in document.categories:
        for path in category.images:
            mapping.setdefault(path, category.id)
    return mapping


def _build_image_entry(
    rel_path: str,
    folder: str,
    metadata: ImageMetadataEntry | None,
    *,
    category_id: str | None = None,
) -> ImageEntry:
    if metadata is None:
        return ImageEntry(path=rel_path, folder=folder, category_id=category_id)

    caption = metadata.caption.strip()
    return ImageEntry(
        path=rel_path,
        folder=folder,
        category_id=category_id,
        caption=caption,
        number_of_people=metadata.number_of_people,
        has_bride=metadata.has_bride,
        has_groom=metadata.has_groom,
        has_other_people=metadata.has_other_people,
        is_blur=metadata.is_blur,
        quality_score=metadata.quality_score,
        analyzed=bool(caption),
        palette_colors=list(metadata.palette_colors),
        person_ids=list(metadata.person_ids),
    )


def _matches_filters(entry: ImageEntry, filters: ImageListFilters | None) -> bool:
    if filters is None:
        return True

    if filters.has_bride is not None and entry.has_bride != filters.has_bride:
        return False
    if filters.has_groom is not None and entry.has_groom != filters.has_groom:
        return False
    if filters.has_other_people is not None and entry.has_other_people != filters.has_other_people:
        return False
    if filters.min_people is not None and entry.number_of_people < filters.min_people:
        return False
    if filters.max_people is not None and entry.number_of_people > filters.max_people:
        return False
    if filters.analyzed is not None and entry.analyzed != filters.analyzed:
        return False
    if filters.is_blur is not None and entry.is_blur != filters.is_blur:
        return False
    if filters.min_quality_score is not None and entry.quality_score < filters.min_quality_score:
        return False
    if filters.max_quality_score is not None and entry.quality_score > filters.max_quality_score:
        return False
    if filters.category_ids is not None:
        if entry.category_id is None or entry.category_id not in filters.category_ids:
            return False
    if filters.uncategorized is True and entry.category_id is not None:
        return False
    if filters.person_ids is not None:
        if not any(person_id in entry.person_ids for person_id in filters.person_ids):
            return False

    return True


def list_folders(workspace_root: Path) -> list[FolderInfo]:
    """Direct child directories of raw/ with processed image counts."""
    raw_dir = workspace_root / RAW_DIR_NAME
    processed_dir = workspace_root / PROCESSED_DIR_NAME
    if not raw_dir.is_dir():
        return []

    counts: dict[str, int] = {}
    if processed_dir.is_dir():
        for path in processed_dir.rglob("*"):
            if not _is_image(path):
                continue
            rel = path.relative_to(processed_dir)
            folder = _top_level_folder(rel)
            counts[folder] = counts.get(folder, 0) + 1

    folders: list[FolderInfo] = []
    for entry in sorted(raw_dir.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        folders.append(FolderInfo(name=name, image_count=counts.get(name, 0)))

    root_count = counts.get(ROOT_FOLDER_KEY, 0)
    if root_count > 0:
        folders.insert(0, FolderInfo(name=ROOT_FOLDER_KEY, image_count=root_count))

    return folders


def list_processed_images(
    workspace_root: Path,
    *,
    folders: set[str] | None = None,
    filters: ImageListFilters | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[list[ImageEntry], int]:
    """
    List images under processed_small/ with metadata from image_metadata.json.

    When *folders* is None, all images are returned. Otherwise only images whose
    top-level folder (first path segment) is in *folders* are included.

    Returns a page of entries and the total number of matches (for pagination).
    """
    processed_dir = workspace_root / PROCESSED_DIR_NAME
    if not processed_dir.is_dir():
        return [], 0

    if offset < 0:
        offset = 0

    metadata_map = _metadata_by_path(workspace_root)
    categories_map = category_id_by_path(workspace_root)
    page: list[ImageEntry] = []
    total = 0

    for path in sorted(processed_dir.rglob("*")):
        if not _is_image(path):
            continue
        rel = path.relative_to(processed_dir)
        rel_path = rel.as_posix()
        folder = _top_level_folder(rel)
        if folders is not None and folder not in folders:
            continue

        entry = _build_image_entry(
            rel_path,
            folder,
            metadata_map.get(rel_path),
            category_id=categories_map.get(rel_path),
        )
        if not _matches_filters(entry, filters):
            continue

        if total >= offset and (limit is None or len(page) < limit):
            page.append(entry)
        total += 1

    return page, total


def list_category_summaries(
    workspace_root: Path,
    *,
    folders: set[str] | None = None,
) -> list[ImageCategorySummary]:
    """Story categories with image counts scoped to selected folders."""
    document = load_categories_document(workspace_root)
    if not document.categories:
        return []

    processed_dir = workspace_root / PROCESSED_DIR_NAME
    if not processed_dir.is_dir():
        return [
            ImageCategorySummary(id=category.id, description=category.description, image_count=0)
            for category in document.categories
        ]

    categories_map = category_id_by_path(workspace_root)
    counts: dict[str, int] = {category.id: 0 for category in document.categories}
    for path in processed_dir.rglob("*"):
        if not _is_image(path):
            continue
        rel = path.relative_to(processed_dir)
        rel_path = rel.as_posix()
        folder = _top_level_folder(rel)
        if folders is not None and folder not in folders:
            continue
        category_id = categories_map.get(rel_path)
        if category_id is not None and category_id in counts:
            counts[category_id] += 1

    return [
        ImageCategorySummary(
            id=category.id,
            description=category.description,
            image_count=counts.get(category.id, 0),
        )
        for category in document.categories
    ]
