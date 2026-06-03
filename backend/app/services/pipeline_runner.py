"""Background resize and analysis tasks for the processing pipeline."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from pathlib import Path

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.image_metadata import ImageMetadataEntry
from app.services.image_analysis import analyze_processed_image
from app.services.image_categoriser import (
    clear_categories_document,
    run_categorisation,
)
from app.services.image_metadata import (
    caption_counts,
    clear_analysis_metadata,
    extract_image_palettes,
    save_metadata_document,
    sync_metadata_document,
)
from app.services.face_extraction import (
    clear_face_metadata,
    extract_people_from_library,
)
from app.services.image_processing import (
    ResizeProgress,
    process_all_raw_images,
    scan_raw,
)
from app.services.person_store import clear_person_data
from app.services.openai_settings import load_openai_api_key
from app.services.pipeline_state import (
    compute_library_flags,
    load_state_document,
    record_user_action,
    refresh_pipeline_state,
    save_state_document,
)

logger = logging.getLogger(__name__)

_lock = asyncio.Lock()
_resize_running = False
_analysis_running = False
_palette_extract_running = False
_face_extraction_running = False
_categorisation_running = False
_analysis_progress = ResizeProgress.empty()


def is_resize_running() -> bool:
    return _resize_running


def is_analysis_running() -> bool:
    return _analysis_running


def is_palette_extract_running() -> bool:
    return _palette_extract_running


def is_face_extraction_running() -> bool:
    return _face_extraction_running


def is_categorisation_running() -> bool:
    return _categorisation_running


def is_any_pipeline_job_running() -> bool:
    return (
        _resize_running
        or _analysis_running
        or _palette_extract_running
        or _face_extraction_running
        or _categorisation_running
    )


def get_active_processing_phase() -> str | None:
    """In-memory pipeline phase; defaults to idle when no job is running."""
    if _resize_running:
        return "resize"
    if _palette_extract_running:
        return "palette"
    if _face_extraction_running:
        return "faces"
    if _analysis_running:
        return "analysis"
    if _categorisation_running:
        return "categorise"
    return None


def get_analysis_progress() -> ResizeProgress:
    return _analysis_progress


def reset_pipeline_runner_state() -> None:
    """Clear in-memory pipeline flags (used by tests)."""
    global _resize_running, _analysis_running, _palette_extract_running
    global _face_extraction_running, _categorisation_running, _analysis_progress
    _resize_running = False
    _analysis_running = False
    _palette_extract_running = False
    _face_extraction_running = False
    _categorisation_running = False
    _analysis_progress = ResizeProgress.empty()


def _finish_task(workspace_root: Path) -> None:
    refresh_pipeline_state(workspace_root)


async def run_resize(workspace_root: Path) -> None:
    global _resize_running

    async with _lock:
        if is_any_pipeline_job_running():
            return
        _resize_running = True

    document = load_state_document(workspace_root)
    document.processing.resize_started_at = datetime.now(UTC)
    save_state_document(workspace_root, document)

    try:
        result = await asyncio.to_thread(process_all_raw_images, workspace_root)
        logger.info(
            "Resize workers finished: %d processed, %d skipped, %d failed",
            result.processed,
            result.skipped,
            result.failed,
        )
        document = load_state_document(workspace_root)
        document.processing.resize_completed_at = datetime.now(UTC)
        save_state_document(workspace_root, document)
    finally:
        async with _lock:
            _resize_running = False
        _finish_task(workspace_root)


async def _analyze_metadata_entry(
    workspace_root: Path,
    entry: ImageMetadataEntry,
    *,
    client: AsyncOpenAI,
) -> bool:
    """Run OpenAI analysis for one entry; return True on success."""
    try:
        result = await analyze_processed_image(
            workspace_root,
            entry.path,
            person_ids=entry.person_ids,
            client=client,
        )
        entry.apply_analysis(
            caption=result.caption.strip(),
            number_of_people=result.number_of_people,
            has_bride=result.has_bride,
            has_groom=result.has_groom,
            has_other_people=result.has_other_people,
            is_blur=result.is_blur,
            quality_score=result.quality_score,
        )
    except Exception:
        logger.exception("Failed to analyze %s", entry.path)
        return False
    return True


async def run_analysis(workspace_root: Path, *, force: bool = False) -> None:
    global _analysis_running, _analysis_progress

    async with _lock:
        if is_any_pipeline_job_running():
            return
        _analysis_running = True

    if not load_openai_api_key(workspace_root):
        logger.error("OpenAI API key is not set in workspace; cannot run image analysis")
        async with _lock:
            _analysis_running = False
        _finish_task(workspace_root)
        return

    metadata = sync_metadata_document(workspace_root)
    total = len(metadata.images)
    if force:
        _analysis_progress = ResizeProgress.from_completed(max(total, 1), 0)
    else:
        completed, _ = caption_counts(metadata)
        _analysis_progress = ResizeProgress.from_completed(max(total, 1), completed)

    document = load_state_document(workspace_root)
    document.processing.analysis_started_at = datetime.now(UTC)
    document.processing.analysis_completed_at = None
    save_state_document(workspace_root, document)

    pending = [
        entry
        for entry in metadata.images
        if force or entry.needs_analysis()
    ]
    batch_size = settings.analysis_batch_size
    client = AsyncOpenAI(api_key=load_openai_api_key(workspace_root))

    analyzed_count = 0
    try:
        for batch_start in range(0, len(pending), batch_size):
            batch = pending[batch_start : batch_start + batch_size]
            results = await asyncio.gather(
                *[
                    _analyze_metadata_entry(
                        workspace_root,
                        entry,
                        client=client,
                    )
                    for entry in batch
                ],
            )
            analyzed_count += sum(1 for ok in results if ok)
            save_metadata_document(workspace_root, metadata)

            if force:
                _analysis_progress = ResizeProgress.from_completed(
                    max(total, 1),
                    analyzed_count,
                )
            else:
                completed, total = caption_counts(metadata)
                _analysis_progress = ResizeProgress.from_completed(max(total, 1), completed)

        completed, total = caption_counts(metadata)
        logger.info(
            "Analysis finished: %d/%d images with captions",
            completed,
            total,
        )
    finally:
        async with _lock:
            _analysis_running = False
        _finish_task(workspace_root)


async def _claim_palette_extraction() -> bool:
    """Mark palette extraction as running so status updates immediately."""
    global _palette_extract_running

    async with _lock:
        if is_any_pipeline_job_running():
            return False
        _palette_extract_running = True
    return True


async def _run_palette_extraction(workspace_root: Path) -> None:
    global _palette_extract_running

    try:
        metadata = await asyncio.to_thread(sync_metadata_document, workspace_root)
        pending = sum(1 for entry in metadata.images if not entry.palette_colors)
        if pending == 0:
            logger.info("Palette extraction skipped: all images already have colors")
            return

        updated = await asyncio.to_thread(
            extract_image_palettes,
            workspace_root,
            only_missing=True,
        )
        if updated:
            logger.info("Palette extraction finished: %d images updated", updated)
    finally:
        async with _lock:
            _palette_extract_running = False
        _finish_task(workspace_root)


async def _claim_face_extraction() -> bool:
    global _face_extraction_running

    async with _lock:
        if is_any_pipeline_job_running():
            logger.warning(
                "Face extraction not started: another pipeline job is running "
                "(resize=%s palette=%s analysis=%s categorise=%s face=%s)",
                _resize_running,
                _palette_extract_running,
                _analysis_running,
                _categorisation_running,
                _face_extraction_running,
            )
            return False
        _face_extraction_running = True
    logger.info("Face extraction claimed (running flag set)")
    return True


async def _run_face_extraction(workspace_root: Path, *, force: bool) -> None:
    global _face_extraction_running

    logger.info("Face extraction task started (force=%s)", force)
    document = load_state_document(workspace_root)
    document.processing.face_extraction_started_at = datetime.now(UTC)
    document.processing.face_extraction_completed_at = None
    save_state_document(workspace_root, document)

    try:
        updated = await asyncio.to_thread(
            extract_people_from_library,
            workspace_root,
            only_missing=not force,
        )
        if updated:
            logger.info("Face extraction task finished: %d images processed", updated)
        else:
            logger.info("Face extraction task finished: no images processed this run")
        document = load_state_document(workspace_root)
        document.processing.face_extraction_completed_at = datetime.now(UTC)
        save_state_document(workspace_root, document)
    except Exception:
        logger.exception("Face extraction task failed")
        raise
    finally:
        async with _lock:
            _face_extraction_running = False
        _finish_task(workspace_root)


async def maybe_advance_pipeline(workspace_root: Path) -> None:
    """Resume resize or palette extraction when the user has started them."""
    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)

    if not flags.image_found:
        return

    if is_any_pipeline_job_running():
        return

    if (
        document.has_action("start_processing")
        and not flags.resize_complete
    ):
        asyncio.create_task(run_resize(workspace_root))
        return

    if (
        document.has_action("start_face_extraction")
        and flags.resize_complete
        and not flags.people_extraction_complete
    ):
        if await _claim_face_extraction():
            asyncio.create_task(_run_face_extraction(workspace_root, force=False))
            return

    if (
        document.has_action("start_palette_extraction")
        and flags.resize_complete
        and not flags.has_analysed_color
    ):
        if await _claim_palette_extraction():
            asyncio.create_task(_run_palette_extraction(workspace_root))


async def handle_start_processing(workspace_root: Path) -> None:
    record_user_action(workspace_root, "start_processing")

    if is_any_pipeline_job_running():
        return

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)
    if not flags.image_found:
        return

    asyncio.create_task(run_resize(workspace_root))


async def handle_start_face_extraction(workspace_root: Path) -> None:
    logger.info("handle_start_face_extraction invoked for %s", workspace_root)
    record_user_action(workspace_root, "start_face_extraction")

    if is_any_pipeline_job_running():
        logger.warning("handle_start_face_extraction aborted: pipeline busy")
        return

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)
    logger.info(
        "Face extraction preconditions: resize_complete=%s people_complete=%s raw_images=%d",
        flags.resize_complete,
        flags.people_extraction_complete,
        raw_scan.total_images,
    )

    if not flags.resize_complete:
        logger.warning("handle_start_face_extraction aborted: resize not complete")
        return

    if await _claim_face_extraction():
        logger.info("Scheduling face extraction background task")
        asyncio.create_task(_run_face_extraction(workspace_root, force=False))
    else:
        logger.warning("handle_start_face_extraction aborted: could not claim job")


async def handle_rerun_face_extraction(workspace_root: Path) -> None:
    logger.info("handle_rerun_face_extraction invoked for %s", workspace_root)
    record_user_action(workspace_root, "rerun_face_extraction")

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)

    if not flags.resize_complete:
        logger.warning("handle_rerun_face_extraction aborted: resize not complete")
        return

    if is_any_pipeline_job_running():
        logger.warning("handle_rerun_face_extraction aborted: pipeline busy")
        return

    metadata = sync_metadata_document(workspace_root)
    if not metadata.images:
        logger.warning("handle_rerun_face_extraction aborted: no images in metadata")
        return

    clear_person_data(workspace_root)
    clear_face_metadata(metadata)
    save_metadata_document(workspace_root, metadata)

    if await _claim_face_extraction():
        logger.info("Scheduling face extraction rerun (force=true)")
        asyncio.create_task(_run_face_extraction(workspace_root, force=True))
    else:
        logger.warning("handle_rerun_face_extraction aborted: could not claim job")


async def handle_start_palette_extraction(workspace_root: Path) -> None:
    """Extract dominant colors only when explicitly requested by the user."""
    record_user_action(workspace_root, "start_palette_extraction")

    if is_any_pipeline_job_running():
        return

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)

    if not flags.resize_complete:
        return

    if await _claim_palette_extraction():
        asyncio.create_task(_run_palette_extraction(workspace_root))


async def handle_start_analysis(workspace_root: Path) -> None:
    """Start or resume analysis only when explicitly requested by the user."""
    record_user_action(workspace_root, "start_analysis")

    if is_any_pipeline_job_running():
        return

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)

    if not flags.resize_complete or not flags.has_analysed_color:
        return

    asyncio.create_task(run_analysis(workspace_root))


async def handle_rerun_analysis(workspace_root: Path) -> None:
    """Re-run OpenAI analysis on every processed image, overwriting existing metadata."""
    record_user_action(workspace_root, "rerun_analysis")

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)

    if not flags.resize_complete or not flags.has_analysed_color:
        return

    if is_any_pipeline_job_running():
        return

    metadata = sync_metadata_document(workspace_root)
    if not metadata.images:
        return

    clear_analysis_metadata(metadata)
    save_metadata_document(workspace_root, metadata)
    clear_categories_document(workspace_root)
    refresh_pipeline_state(workspace_root)

    asyncio.create_task(run_analysis(workspace_root, force=True))


async def handle_start_categorisation(workspace_root: Path) -> None:
    """Start or resume categorisation when analysis is complete."""
    record_user_action(workspace_root, "start_categorisation")

    if is_any_pipeline_job_running():
        return

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)

    if not flags.image_analysis_complete:
        return

    if not load_openai_api_key(workspace_root):
        logger.error("OpenAI API key is not set; cannot run categorisation")
        return

    asyncio.create_task(_run_categorisation_job(workspace_root, force=False))


async def handle_rerun_categorisation(workspace_root: Path) -> None:
    """Re-run categorisation from scratch."""
    record_user_action(workspace_root, "rerun_categorisation")

    document = load_state_document(workspace_root)
    raw_scan = scan_raw(workspace_root)
    flags = compute_library_flags(workspace_root, document, raw_scan=raw_scan)

    if not flags.image_analysis_complete:
        return

    if is_any_pipeline_job_running():
        return

    if not load_openai_api_key(workspace_root):
        logger.error("OpenAI API key is not set; cannot run categorisation")
        return

    clear_categories_document(workspace_root)
    refresh_pipeline_state(workspace_root)
    asyncio.create_task(_run_categorisation_job(workspace_root, force=True))


async def _run_categorisation_job(workspace_root: Path, *, force: bool) -> None:
    global _categorisation_running

    async with _lock:
        if is_any_pipeline_job_running():
            return
        _categorisation_running = True

    document = load_state_document(workspace_root)
    document.processing.categorisation_started_at = datetime.now(UTC)
    document.processing.categorisation_completed_at = None
    save_state_document(workspace_root, document)

    try:
        await run_categorisation(workspace_root, force=force)
    finally:
        async with _lock:
            _categorisation_running = False
        _finish_task(workspace_root)
