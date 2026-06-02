"""Photobook REST API: document, chat planner, and page composer."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas.photobook import (
    PhotobookChatRequest,
    PhotobookChatResponse,
    PhotobookDocument,
    PhotobookPageCreateRequest,
    PhotobookPagePatchRequest,
    PhotobookReorderPagesRequest,
    PageComposeResult,
    PhotobookResponse,
)
from app.services.openai_settings import require_openai_configured
from app.services.photobook_gallery import (
    build_gallery,
    validate_compose_paths,
    validate_image_paths,
)
from app.services.photobook_compose import compose_page
from app.services.photobook_compose_policy import (
    can_start_compose,
    mark_compose_finished,
    mark_compose_started,
)
from app.page_layouts import (
    list_layouts,
    merge_text_slots,
    validate_slots,
)
from app.services.photobook_plan_validation import validate_and_fix_plan_layouts
from app.services.photobook_planner import plan_photobook
from app.services.photobook_background import (
    sync_missing_page_palettes,
    sync_page_sheet_colors,
)
from app.services.photobook_store import (
    add_page,
    append_chat_message,
    apply_plan,
    assigned_image_paths,
    merge_page_extra_images,
    reset_photobook_session,
    ensure_photobook,
    get_page,
    load_photobook,
    remove_page,
    reorder_pages,
    save_photobook,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.api_v1_prefix, tags=["photobook"])


def _normalize_document_text_slots(document: PhotobookDocument) -> None:
    for page in document.pages:
        if page.layout_id:
            page.text_slots = merge_text_slots(page.layout_id, page.text_slots)


def _photobook_response(document) -> PhotobookResponse:
    _normalize_document_text_slots(document)
    return PhotobookResponse(document=document, layouts=list_layouts())


def _save_photobook(document: PhotobookDocument) -> PhotobookResponse:
    save_photobook(settings.workspace_root, document)
    return _photobook_response(document)


def _apply_compose_result(
    workspace_root: Path,
    document: PhotobookDocument,
    page,
    result: PageComposeResult,
) -> None:
    path_errors = validate_compose_paths(
        workspace_root,
        result.layout_id,
        result.slots,
        result.extra_images,
    )
    if path_errors:
        raise RuntimeError("; ".join(path_errors))

    page.layout_id = result.layout_id
    page.slots = result.slots
    page.text_slots = merge_text_slots(result.layout_id, result.text_slots)
    page.slot_offsets = {}
    sync_page_sheet_colors(workspace_root, page)
    page.status = "ready"
    page.composed_at = datetime.now(UTC).isoformat()
    page.error_message = None
    mark_compose_finished(page)

    extra_images = merge_page_extra_images(
        page,
        list(page.extra_images),
        list(result.extra_images),
    )
    invalid_extra = validate_image_paths(workspace_root, extra_images)
    if invalid_extra:
        extra_images = [p for p in extra_images if p not in invalid_extra]
    page.extra_images = extra_images


@router.get("/photobook", response_model=PhotobookResponse)
async def get_photobook() -> PhotobookResponse:
    document = ensure_photobook(settings.workspace_root)
    if sync_missing_page_palettes(settings.workspace_root, document):
        save_photobook(settings.workspace_root, document)
    return _photobook_response(document)


@router.post("/photobook/chat", response_model=PhotobookChatResponse)
async def post_photobook_chat(body: PhotobookChatRequest) -> PhotobookChatResponse:
    require_openai_configured(settings.workspace_root)
    workspace_root = settings.workspace_root
    document = load_photobook(workspace_root)
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

    append_chat_message(document, "user", message)

    try:
        plan = await plan_photobook(workspace_root, document, message)
        plan = await validate_and_fix_plan_layouts(workspace_root, plan)
        apply_plan(document, plan.pages, plan.extra_images)
        append_chat_message(document, "assistant", plan.assistant_message)
        save_photobook(workspace_root, document)
        base = _photobook_response(document)
        return PhotobookChatResponse(
            **base.model_dump(),
            assistant_message=plan.assistant_message,
        )
    except RuntimeError as exc:
        logger.exception("Photobook chat failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.delete("/photobook/chat", response_model=PhotobookResponse)
async def delete_photobook_chat() -> PhotobookResponse:
    """Reset the photobook session (chat + storyboard/storybook). Does not delete images."""
    document = load_photobook(settings.workspace_root)
    reset_photobook_session(document)
    return _save_photobook(document)


@router.post("/photobook/pages", response_model=PhotobookResponse)
async def post_photobook_page(body: PhotobookPageCreateRequest) -> PhotobookResponse:
    document = load_photobook(settings.workspace_root)
    add_page(document, title=body.title, narrative=body.narrative)
    save_photobook(settings.workspace_root, document)
    return _photobook_response(document)


@router.put("/photobook/pages/order", response_model=PhotobookResponse)
async def put_photobook_pages_order(body: PhotobookReorderPagesRequest) -> PhotobookResponse:
    document = load_photobook(settings.workspace_root)
    if not reorder_pages(document, body.page_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page_ids must list every page exactly once",
        )
    return _save_photobook(document)


@router.patch("/photobook/pages/{page_id}", response_model=PhotobookResponse)
async def patch_photobook_page(
    page_id: str,
    body: PhotobookPagePatchRequest,
) -> PhotobookResponse:
    document = load_photobook(settings.workspace_root)
    page = get_page(document, page_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    if body.title is not None:
        page.title = body.title
    if body.narrative is not None:
        page.narrative = body.narrative
    if body.layout_id is not None:
        if body.layout_id != page.layout_id:
            page.slot_offsets = {}
        page.layout_id = body.layout_id
    fields_set = body.model_fields_set

    if body.slots is not None:
        if body.layout_id or page.layout_id:
            layout_id = body.layout_id or page.layout_id
            errors = validate_slots(layout_id, body.slots)
            if errors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="; ".join(errors),
                )
        page.slots = body.slots
        if "background_color" not in fields_set:
            sync_page_sheet_colors(settings.workspace_root, page)
    if body.text_slots is not None:
        layout_id = body.layout_id or page.layout_id
        if layout_id:
            page.text_slots = merge_text_slots(layout_id, body.text_slots)
        else:
            page.text_slots = body.text_slots
    if body.slot_offsets is not None:
        page.slot_offsets = body.slot_offsets
    if "background_color" in fields_set:
        page.background_color = body.background_color
    if body.image_border_radius is not None:
        page.image_border_radius = body.image_border_radius
    if body.status is not None:
        page.status = body.status
    if body.extra_images is not None:
        page.extra_images = merge_page_extra_images(page, body.extra_images)

    return _save_photobook(document)


@router.delete("/photobook/pages/{page_id}", response_model=PhotobookResponse)
async def delete_photobook_page(page_id: str) -> PhotobookResponse:
    document = load_photobook(settings.workspace_root)
    if not remove_page(document, page_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last page",
        )
    save_photobook(settings.workspace_root, document)
    return _photobook_response(document)


@router.post("/photobook/pages/{page_id}/compose", response_model=PhotobookResponse)
async def post_compose_page(page_id: str) -> PhotobookResponse:
    require_openai_configured(settings.workspace_root)
    workspace_root = settings.workspace_root
    document = load_photobook(workspace_root)
    page = get_page(document, page_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    if not page.narrative.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page narrative is required before compose",
        )

    if not can_start_compose(page):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Page is still composing; try again after one minute",
        )

    mark_compose_started(page)
    save_photobook(workspace_root, document)

    try:
        gallery = build_gallery(workspace_root)
        assigned = assigned_image_paths(document)
        result = await compose_page(
            workspace_root,
            page,
            gallery,
            page.extra_images,
            assigned,
            chat=document.chat,
        )

        _apply_compose_result(workspace_root, document, page, result)
        return _save_photobook(document)
    except RuntimeError as exc:
        page.status = "error"
        page.error_message = str(exc)
        mark_compose_finished(page)
        save_photobook(workspace_root, document)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


