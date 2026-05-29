"""Batch categorisation of processed images for photobook planning."""

from __future__ import annotations

import json
import logging
import random
import re
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

from openai import AsyncOpenAI

from app.config import settings
from app.prompts.prompts import IMAGE_CATEGORISER_SYSTEM_PROMPT
from app.schemas.image_categories import (
    CategoryBatchAssignment,
    CategoriserBatchResult,
    CategoriserImageInput,
    ExistingCategorySummary,
    ImageCategoriesDocument,
    ImageCategory,
)
from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry
from app.services.image_metadata import (
    is_metadata_analysis_complete,
    list_processed_image_paths,
    load_metadata_document,
)
from app.services.image_processing import ResizeProgress
from app.services.openai_settings import load_openai_api_key

logger = logging.getLogger(__name__)

CATEGORIES_FILENAME = "image_categories.json"
MAX_CATEGORIES = 50
MIN_IMAGES_TO_KEEP_STANDALONE = 3
DESCRIPTION_SIMILARITY_THRESHOLD = 0.45

_categorisation_progress_lock = threading.Lock()
_live_categorisation_progress: dict[str, int | bool] = {
    "total": 0,
    "completed": 0,
    "running": False,
}


def categories_file_path(workspace_root: Path) -> Path:
    return workspace_root / CATEGORIES_FILENAME


def load_categories_document(workspace_root: Path) -> ImageCategoriesDocument:
    path = categories_file_path(workspace_root)
    if not path.is_file():
        return ImageCategoriesDocument()

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return ImageCategoriesDocument.model_validate(raw)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Invalid categories file at %s, resetting", path)
        return ImageCategoriesDocument()


def save_categories_document(
    workspace_root: Path,
    document: ImageCategoriesDocument,
) -> None:
    path = categories_file_path(workspace_root)
    document.updated_at = datetime.now(UTC)
    path.write_text(document.model_dump_json(indent=2), encoding="utf-8")


def clear_categories_document(workspace_root: Path) -> ImageCategoriesDocument:
    document = ImageCategoriesDocument()
    save_categories_document(workspace_root, document)
    return document


def _set_live_categorisation_progress(*, total: int, completed: int, running: bool) -> None:
    with _categorisation_progress_lock:
        _live_categorisation_progress["total"] = total
        _live_categorisation_progress["completed"] = completed
        _live_categorisation_progress["running"] = running


def get_live_categorisation_progress() -> ResizeProgress | None:
    with _categorisation_progress_lock:
        if not _live_categorisation_progress["running"]:
            return None
        total = int(_live_categorisation_progress["total"])
        completed = int(_live_categorisation_progress["completed"])
        return ResizeProgress.from_completed(max(total, 1), completed)


def build_categorisation_gallery(
    workspace_root: Path,
    metadata: ImageMetadataDocument,
) -> set[str]:
    """Valid analysed image paths eligible for categorisation."""
    on_disk = set(list_processed_image_paths(workspace_root))
    analysed = {
        entry.path for entry in metadata.images if entry.caption.strip()
    }
    return on_disk & analysed


def categorized_paths(categories_doc: ImageCategoriesDocument) -> set[str]:
    return {path for category in categories_doc.categories for path in category.images}


def remaining_paths(gallery: set[str], categories_doc: ImageCategoriesDocument) -> set[str]:
    return gallery - categorized_paths(categories_doc)


def categorisation_counts(
    gallery: set[str],
    categories_doc: ImageCategoriesDocument,
) -> tuple[int, int]:
    total = len(gallery)
    completed = total - len(remaining_paths(gallery, categories_doc))
    return completed, total


def is_categorisation_complete(
    gallery: set[str],
    categories_doc: ImageCategoriesDocument,
) -> bool:
    if not gallery:
        return False
    return remaining_paths(gallery, categories_doc) == set()


def build_categoriser_input(entry: ImageMetadataEntry) -> CategoriserImageInput:
    folder = entry.path.split("/", 1)[0] if "/" in entry.path else ""
    return CategoriserImageInput(
        path=entry.path,
        folder=folder,
        caption=entry.caption,
        number_of_people=entry.number_of_people,
        has_bride=entry.has_bride,
        has_groom=entry.has_groom,
        has_other_people=entry.has_other_people,
        is_blur=entry.is_blur,
        quality_score=entry.quality_score,
    )


def sample_batch(remaining: set[str], size: int, rng: random.Random | None = None) -> list[str]:
    if not remaining:
        return []
    picker = rng or random
    k = min(size, len(remaining))
    return picker.sample(sorted(remaining), k)


def _normalize_category_id(raw_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", raw_id.strip().lower()).strip("_")
    return slug or f"category_{uuid.uuid4().hex[:8]}"


def _description_tokens(description: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", description.lower())
        if len(token) > 2
    }


def description_similarity(left: str, right: str) -> float:
    left_tokens = _description_tokens(left)
    right_tokens = _description_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union)


def _find_category_by_id(
    categories_doc: ImageCategoriesDocument,
    category_id: str,
) -> ImageCategory | None:
    normalized = _normalize_category_id(category_id)
    for category in categories_doc.categories:
        if category.id == category_id or category.id == normalized:
            return category
    return None


def prune_invalid_paths(
    categories_doc: ImageCategoriesDocument,
    gallery: set[str],
) -> int:
    removed = 0
    for category in categories_doc.categories:
        valid = [path for path in category.images if path in gallery]
        removed += len(category.images) - len(valid)
        category.images = valid
    return removed


def dedupe_paths_across_categories(categories_doc: ImageCategoriesDocument) -> None:
    seen: set[str] = set()
    for category in categories_doc.categories:
        unique: list[str] = []
        for path in category.images:
            if path in seen:
                continue
            seen.add(path)
            unique.append(path)
        category.images = unique


def remove_empty_categories(categories_doc: ImageCategoriesDocument) -> None:
    categories_doc.categories = [
        category for category in categories_doc.categories if category.images
    ]


def _best_matching_category(
    categories_doc: ImageCategoriesDocument,
    description: str,
    *,
    exclude_id: str | None = None,
) -> ImageCategory | None:
    best: ImageCategory | None = None
    best_score = DESCRIPTION_SIMILARITY_THRESHOLD
    for category in categories_doc.categories:
        if exclude_id and category.id == exclude_id:
            continue
        score = description_similarity(description, category.description)
        if score > best_score:
            best_score = score
            best = category
    return best


def consolidate_categories(
    categories_doc: ImageCategoriesDocument,
    *,
    max_categories: int = MAX_CATEGORIES,
    min_images_to_keep: int = MIN_IMAGES_TO_KEEP_STANDALONE,
) -> None:
    dedupe_paths_across_categories(categories_doc)

    merged = True
    while merged:
        merged = False
        for category in list(categories_doc.categories):
            if len(category.images) >= min_images_to_keep:
                continue
            target = _best_matching_category(
                categories_doc,
                category.description,
                exclude_id=category.id,
            )
            if target is None:
                continue
            target.images.extend(category.images)
            categories_doc.categories.remove(category)
            merged = True
            break

    while len(categories_doc.categories) > max_categories:
        smallest = min(categories_doc.categories, key=lambda c: len(c.images))
        target = _best_matching_category(
            categories_doc,
            smallest.description,
            exclude_id=smallest.id,
        )
        if target is None:
            others = [c for c in categories_doc.categories if c.id != smallest.id]
            if not others:
                break
            target = max(others, key=lambda c: len(c.images))
        target.images.extend(smallest.images)
        categories_doc.categories.remove(smallest)

    dedupe_paths_across_categories(categories_doc)
    remove_empty_categories(categories_doc)


def _ensure_unique_category_id(
    categories_doc: ImageCategoriesDocument,
    proposed_id: str,
) -> str:
    base = _normalize_category_id(proposed_id)
    if _find_category_by_id(categories_doc, base) is None:
        return base
    suffix = 2
    while _find_category_by_id(categories_doc, f"{base}_{suffix}") is not None:
        suffix += 1
    return f"{base}_{suffix}"


def merge_assignments(
    categories_doc: ImageCategoriesDocument,
    result: CategoriserBatchResult,
    *,
    allowed_paths: set[str],
) -> set[str]:
    """Apply batch assignments. Returns paths successfully assigned."""
    assigned: set[str] = set()

    for assignment in result.assignments:
        valid_images = [path for path in assignment.images if path in allowed_paths]
        if not valid_images and not assignment.description:
            continue

        existing = _find_category_by_id(categories_doc, assignment.id)
        if existing is not None:
            for path in valid_images:
                if path not in assigned:
                    existing.images.append(path)
                    assigned.add(path)
            continue

        if not assignment.description or not assignment.description.strip():
            logger.warning(
                "Skipping new category %r without description",
                assignment.id,
            )
            continue

        if len(categories_doc.categories) >= MAX_CATEGORIES:
            target = _best_matching_category(
                categories_doc,
                assignment.description,
            )
            if target is None:
                logger.warning(
                    "At category limit; dropping assignment for %r",
                    assignment.id,
                )
                continue
            for path in valid_images:
                if path not in assigned:
                    target.images.append(path)
                    assigned.add(path)
            continue

        category_id = _ensure_unique_category_id(categories_doc, assignment.id)
        new_category = ImageCategory(
            id=category_id,
            description=assignment.description.strip(),
            images=[],
        )
        for path in valid_images:
            if path not in assigned:
                new_category.images.append(path)
                assigned.add(path)
        if new_category.images:
            categories_doc.categories.append(new_category)

    return assigned


async def categorise_batch(
    workspace_root: Path,
    *,
    images: list[CategoriserImageInput],
    existing_categories: list[ExistingCategorySummary],
    client: AsyncOpenAI | None = None,
) -> CategoriserBatchResult:
    api_key = load_openai_api_key(workspace_root)
    if not api_key:
        msg = "OpenAI API key is not configured in workspace settings"
        raise RuntimeError(msg)

    user_payload = {
        "batch_image_count": len(images),
        "required_unique_paths_in_output": len(images),
        "existing_categories": [item.model_dump() for item in existing_categories],
        "images": [item.model_dump() for item in images],
    }

    openai_client = client or AsyncOpenAI(api_key=api_key)
    CACHE_KEY = "categoriser_batch"
    completion = await openai_client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": IMAGE_CATEGORISER_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, indent=2)},
        ],
        prompt_cache_key=CACHE_KEY,
        response_format=CategoriserBatchResult,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        msg = "OpenAI returned no structured categorisation output"
        raise RuntimeError(msg)

    logger.info(
        "Categoriser batch: %d assignments for %d images",
        len(parsed.assignments),
        len(images),
    )
    return parsed


async def run_categorisation(
    workspace_root: Path,
    *,
    force: bool = False,
    rng: random.Random | None = None,
) -> None:
    """Iteratively categorise random batches until every gallery image is assigned."""
    if force:
        categories = clear_categories_document(workspace_root)
    else:
        categories = load_categories_document(workspace_root)

    metadata = load_metadata_document(workspace_root)
    if not is_metadata_analysis_complete(metadata):
        logger.error("Cannot categorise: image analysis is not complete")
        return

    gallery = build_categorisation_gallery(workspace_root, metadata)
    batch_size = settings.categorisation_batch_size
    total = len(gallery)

    if total == 0:
        logger.info("Categorisation skipped: no analysed images in gallery")
        _set_live_categorisation_progress(total=0, completed=0, running=False)
        return

    _set_live_categorisation_progress(total=total, completed=0, running=True)
    client = AsyncOpenAI(api_key=load_openai_api_key(workspace_root))

    try:
        while True:
            prune_invalid_paths(categories, gallery)
            remaining = remaining_paths(gallery, categories)
            if not remaining:
                break

            batch_paths = set(sample_batch(remaining, batch_size, rng))
            path_to_entry = {entry.path: entry for entry in metadata.images}
            batch_entries = [
                build_categoriser_input(path_to_entry[path])
                for path in sorted(batch_paths)
                if path in path_to_entry
            ]

            existing = [
                ExistingCategorySummary(id=c.id, description=c.description)
                for c in categories.categories
            ]

            result = await categorise_batch(
                workspace_root,
                images=batch_entries,
                existing_categories=existing,
                client=client,
            )

            allowed = batch_paths & gallery
            assigned = merge_assignments(
                categories,
                result,
                allowed_paths=allowed,
            )
            unassigned = allowed - assigned
            if unassigned:
                logger.warning(
                    "Categoriser left %d/%d batch paths unassigned; will retry",
                    len(unassigned),
                    len(allowed),
                )

            dedupe_paths_across_categories(categories)
            consolidate_categories(categories)
            prune_invalid_paths(categories, gallery)
            save_categories_document(workspace_root, categories)

            completed, _ = categorisation_counts(gallery, categories)
            _set_live_categorisation_progress(
                total=total,
                completed=completed,
                running=True,
            )

            from app.services.pipeline_state import refresh_pipeline_flags

            refresh_pipeline_flags(workspace_root, metadata=metadata)

            logger.info(
                "Categorisation iteration saved: %d/%d complete, %d categories",
                completed,
                total,
                len(categories.categories),
            )
    finally:
        completed, _ = categorisation_counts(gallery, categories)
        _set_live_categorisation_progress(
            total=total,
            completed=completed,
            running=False,
        )

    logger.info(
        "Categorisation finished: %d/%d images in %d categories",
        completed,
        total,
        len(categories.categories),
    )
