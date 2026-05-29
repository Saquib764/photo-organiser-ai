"""REST endpoints for image browser folders, listing, and processed image serving."""

import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas.image_catalog import (
    CategoryListResponse,
    FolderListResponse,
    ImageDeleteResponse,
    ImageListResponse,
)
from app.services.image_files import (
    media_type_for_path,
    resolve_processed_image_path,
    resolve_raw_image_path,
)
from app.services.image_catalog import (
    ImageListFilters,
    list_category_summaries,
    list_folders,
    list_processed_images,
)
from app.services.image_delete import delete_workspace_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.api_v1_prefix, tags=["images"])


@router.get("/folders", response_model=FolderListResponse)
async def get_folders() -> FolderListResponse:
    folders = list_folders(settings.workspace_root)
    return FolderListResponse(folders=folders)


@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    folders: list[str] | None = Query(
        default=None,
        description=(
            "Optional folder scope for per-category image counts. "
            "Repeat for multiple folders; use __root__ for raw root images."
        ),
    ),
) -> CategoryListResponse:
    categories = list_category_summaries(
        settings.workspace_root,
        folders=_parse_folder_filter(folders),
    )
    return CategoryListResponse(categories=categories)


def _parse_folder_filter(folders: list[str] | None) -> set[str] | None:
    if folders is None:
        return None
    parsed: set[str] = set()
    for name in folders:
        parsed.add("" if name == "__root__" else name)
    return parsed


@router.get("/images", response_model=ImageListResponse)
async def get_images(
    folders: list[str] | None = Query(
        default=None,
        description=(
            "Top-level folder names to include. Repeat the param for multiple folders. "
            "Use __root__ for images directly under raw/."
        ),
    ),
    has_bride: bool | None = Query(default=None),
    has_groom: bool | None = Query(default=None),
    has_other_people: bool | None = Query(default=None),
    min_people: int | None = Query(default=None, ge=0),
    max_people: int | None = Query(default=None, ge=0),
    analyzed: bool | None = Query(
        default=None,
        description="True for images with a caption; false for not yet analyzed.",
    ),
    is_blur: bool | None = Query(default=None),
    min_quality_score: float | None = Query(default=None, ge=0, le=10),
    max_quality_score: float | None = Query(default=None, ge=0, le=10),
    categories: list[str] | None = Query(
        default=None,
        description="Story category ids; images in any listed category are included.",
    ),
    uncategorized: bool | None = Query(
        default=None,
        description="True to show only images not assigned to a story category.",
    ),
) -> ImageListResponse:
    category_ids = frozenset(categories) if categories else None
    filters = ImageListFilters(
        has_bride=has_bride,
        has_groom=has_groom,
        has_other_people=has_other_people,
        min_people=min_people,
        max_people=max_people,
        analyzed=analyzed,
        is_blur=is_blur,
        min_quality_score=min_quality_score,
        max_quality_score=max_quality_score,
        category_ids=category_ids,
        uncategorized=uncategorized,
    )
    has_filter = any(
        value is not None
        for value in (
            has_bride,
            has_groom,
            has_other_people,
            min_people,
            max_people,
            analyzed,
            is_blur,
            min_quality_score,
            max_quality_score,
            category_ids,
            uncategorized,
        )
    )
    images = list_processed_images(
        settings.workspace_root,
        folders=_parse_folder_filter(folders),
        filters=filters if has_filter else None,
    )
    return ImageListResponse(images=images, total=len(images))


@router.delete("/images/{rel_path:path}", response_model=ImageDeleteResponse)
async def delete_image(rel_path: str) -> ImageDeleteResponse:
    try:
        result = delete_workspace_image(settings.workspace_root, rel_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ImageDeleteResponse(
        path=result.path,
        deleted_raw=result.deleted_raw,
        deleted_processed=result.deleted_processed,
        removed_from_metadata=result.removed_from_metadata,
        removed_from_categories=result.removed_from_categories,
    )


@router.get("/raw/{rel_path:path}")
async def serve_raw_image(rel_path: str) -> FileResponse:
    try:
        file_path = resolve_raw_image_path(settings.workspace_root, rel_path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Image not found") from exc

    return FileResponse(
        file_path,
        media_type=media_type_for_path(file_path),
        filename=file_path.name,
    )


@router.get("/media/{rel_path:path}")
async def serve_processed_image(rel_path: str) -> FileResponse:
    try:
        file_path = resolve_processed_image_path(settings.workspace_root, rel_path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Image not found") from exc

    return FileResponse(
        file_path,
        media_type=media_type_for_path(file_path),
        filename=file_path.name,
    )
