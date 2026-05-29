"""Build image gallery summaries for photobook OpenAI prompts."""

from __future__ import annotations

import random
from pathlib import Path

from app.schemas.photobook import GalleryImageSummary, PhotobookPage
from app.services.image_catalog import list_processed_images
from app.services.image_categoriser import load_categories_document
from app.services.image_metadata import list_processed_image_paths
from app.page_layouts import validate_slots

MAX_COMPOSE_GALLERY_SIZE = 150
MIN_PAGE_EXTRA_IMAGES = 4
MAX_PAGE_EXTRA_IMAGES = 12


def ensure_compose_extra_images(
    gallery: list[GalleryImageSummary],
    slot_paths: set[str],
    assigned_paths: set[str],
    model_extras: list[str],
    *,
    min_count: int = MIN_PAGE_EXTRA_IMAGES,
    max_count: int = MAX_PAGE_EXTRA_IMAGES,
) -> list[str]:
    """
    Build extra_images for a composed page.

    Keeps model picks first, then fills from the compose gallery until at least
    min_count alternates (when enough unused images exist). Never returns empty
    when the gallery has any path not already in a slot.
    """
    merged: list[str] = []
    seen: set[str] = set()

    for path in model_extras:
        if path and path not in slot_paths and path not in seen:
            seen.add(path)
            merged.append(path)

    if len(merged) >= min_count:
        return merged[:max_count]

    def candidate_entries(*, exclude_assigned: bool) -> list[GalleryImageSummary]:
        return [
            entry
            for entry in gallery
            if entry.path
            and entry.path not in slot_paths
            and entry.path not in seen
            and (not exclude_assigned or entry.path not in assigned_paths)
        ]

    for exclude_assigned in (True, False):
        candidates = candidate_entries(exclude_assigned=exclude_assigned)
        candidates.sort(key=lambda entry: (entry.is_blur, -entry.quality_score))
        for entry in candidates:
            if len(merged) >= max_count:
                break
            seen.add(entry.path)
            merged.append(entry.path)
            if len(merged) >= min_count:
                break
        if len(merged) >= min_count:
            break

    return merged[:max_count]


def build_gallery(workspace_root: Path) -> list[GalleryImageSummary]:
    entries = list_processed_images(workspace_root, folders=None, filters=None)
    return [GalleryImageSummary.model_validate(entry.model_dump()) for entry in entries]


def paths_for_categories(workspace_root: Path, category_ids: list[str]) -> set[str]:
    """Image paths belonging to any of the given category ids."""
    if not category_ids:
        return set()
    wanted = set(category_ids)
    document = load_categories_document(workspace_root)
    paths: set[str] = set()
    for category in document.categories:
        if category.id in wanted:
            paths.update(category.images)
    return paths


def filter_gallery_by_categories(
    gallery: list[GalleryImageSummary],
    allowed_paths: set[str],
) -> list[GalleryImageSummary]:
    if not allowed_paths:
        return []
    return [entry for entry in gallery if entry.path in allowed_paths]


def gallery_for_compose(
    workspace_root: Path,
    page: PhotobookPage,
    gallery: list[GalleryImageSummary],
    *,
    max_images: int = MAX_COMPOSE_GALLERY_SIZE,
) -> list[GalleryImageSummary]:
    """
    Build the compose prompt gallery from the page's selected categories.

    Combines images across all page categories, then randomly samples up to
    max_images entries to send to the LLM.
    """
    if not page.categories:
        msg = f"Page {page.id} has no categories; run photobook planning first."
        raise RuntimeError(msg)

    allowed = paths_for_categories(workspace_root, page.categories)
    filtered = filter_gallery_by_categories(gallery, allowed)
    if not filtered:
        msg = (
            f"Page {page.id} categories {page.categories} matched no analysed images "
            "in the gallery."
        )
        raise RuntimeError(msg)

    if len(filtered) <= max_images:
        return filtered

    return random.sample(filtered, max_images)


def path_exists_in_processed(workspace_root: Path, relative_path: str) -> bool:
    from app.services.image_files import resolve_processed_image_path

    try:
        resolve_processed_image_path(workspace_root, relative_path)
        return True
    except ValueError:
        return False


def validate_image_paths(
    workspace_root: Path,
    paths: list[str],
) -> list[str]:
    """Return paths that do not exist under processed_small/."""
    valid = set(list_processed_image_paths(workspace_root))
    return [p for p in paths if p not in valid]


def validate_compose_paths(
    workspace_root: Path,
    layout_id: str,
    slots: dict[str, str],
    extra_images: list[str],
) -> list[str]:
    errors = validate_slots(layout_id, slots, require_all=True)
    if errors:
        return errors

    for slot_id, path in slots.items():
        if not path_exists_in_processed(workspace_root, path):
            errors.append(f"Image not found for slot {slot_id}: {path}")

    for path in extra_images:
        if not path_exists_in_processed(workspace_root, path):
            errors.append(f"Extra image not found: {path}")

    return errors
