"""Build combined workspace + pipeline status payloads."""

from pathlib import Path

from app.schemas.image_metadata import ImageMetadataDocument
from app.schemas.workspace_status import WorkspaceStatus
from app.services.image_processing import (
    RawScan,
    ResizeProgress,
    get_live_resize_progress,
    scan_raw,
)
from app.services.image_metadata import (
    caption_counts,
    get_live_palette_progress,
    load_metadata_document,
    palette_counts,
)
from app.services.face_extraction import (
    face_scan_counts,
    get_live_face_progress,
)
from app.services.image_categoriser import (
    build_categorisation_gallery,
    categorisation_counts,
    get_live_categorisation_progress,
    load_categories_document,
)
from app.services.pipeline_runner import (
    get_active_processing_phase,
    get_analysis_progress,
    is_analysis_running,
    is_any_pipeline_job_running,
    is_categorisation_running,
    is_face_extraction_running,
    is_palette_extract_running,
    is_resize_running,
)
from app.services.person_store import load_person_document
from app.services.openai_settings import is_openai_configured
from app.services.pipeline_state import (
    compute_library_flags,
    discover_workspace_changes,
    load_state_document,
    raw_scan_for_complete_library,
)
from app.services.workspace import PROCESSED_DIR_NAME, count_images


def _resolve_progress(
    workspace_root: Path,
    raw_scan: RawScan,
    metadata: ImageMetadataDocument,
) -> tuple[ResizeProgress, str | None]:
    if is_palette_extract_running():
        live = get_live_palette_progress()
        if live is not None:
            return live, "palette"
        completed, total = palette_counts(metadata)
        pending = max(total - completed, 0)
        return ResizeProgress.from_completed(max(pending, 1), 0), "palette"

    if is_face_extraction_running():
        live = get_live_face_progress()
        if live is not None:
            return live, "faces"
        completed, total = face_scan_counts(metadata)
        pending = max(total - completed, 0)
        return ResizeProgress.from_completed(max(pending, 1), 0), "faces"

    if is_resize_running():
        live = get_live_resize_progress()
        if live is not None:
            return live, "resize"
        total = raw_scan.total_images
        return ResizeProgress.from_completed(total, total), "resize"

    if is_analysis_running():
        return get_analysis_progress(), "analysis"

    if is_categorisation_running():
        live = get_live_categorisation_progress()
        if live is not None:
            return live, "categorise"
        gallery = build_categorisation_gallery(workspace_root, metadata)
        categories = load_categories_document(workspace_root)
        completed, total = categorisation_counts(gallery, categories)
        return ResizeProgress.from_completed(max(total, 1), completed), "categorise"

    return raw_scan.progress, None


def build_workspace_status(
    workspace_root: Path,
    *,
    discover: bool = False,
) -> WorkspaceStatus:
    document = load_state_document(workspace_root)
    # Read-only load — avoid rewriting image_metadata.json on every status poll.
    metadata = load_metadata_document(workspace_root)
    busy = is_any_pipeline_job_running()
    active_phase = get_active_processing_phase()

    if discover and not busy:
        raw_scan = discover_workspace_changes(workspace_root)
        document = load_state_document(workspace_root)
        total_images_processed = count_images(workspace_root / PROCESSED_DIR_NAME)
        use_fast_scan = False
    else:
        use_fast_scan = document.flags.resize_complete and not is_resize_running()
        if use_fast_scan:
            raw_scan = raw_scan_for_complete_library(
                workspace_root,
                image_count=len(metadata.images),
            )
            total_images_processed = len(metadata.images)
        else:
            raw_scan = scan_raw(workspace_root)
            total_images_processed = count_images(workspace_root / PROCESSED_DIR_NAME)

    flags = compute_library_flags(
        workspace_root,
        document,
        raw_scan=raw_scan,
        metadata=metadata,
        assume_resize_complete=use_fast_scan,
    )
    analysis_completed_count, analysis_total_count = caption_counts(metadata)
    palette_completed_count, palette_total_count = palette_counts(metadata)
    face_completed_count, face_total_count = face_scan_counts(metadata)

    resize_completed_count = raw_scan.progress.completed
    resize_total_count = raw_scan.total_images

    if is_resize_running():
        live = get_live_resize_progress()
        if live is not None:
            resize_completed_count = live.completed
            resize_total_count = live.total

    if is_palette_extract_running():
        live = get_live_palette_progress()
        if live is not None:
            palette_completed_count = live.completed
            palette_total_count = live.total

    if is_face_extraction_running():
        live = get_live_face_progress()
        if live is not None:
            face_completed_count = live.completed
            face_total_count = live.total

    if is_analysis_running():
        live = get_analysis_progress()
        analysis_completed_count = live.completed
        analysis_total_count = live.total

    gallery = build_categorisation_gallery(workspace_root, metadata)
    categories = load_categories_document(workspace_root)
    persons_count = len(load_person_document(workspace_root).persons)
    categorisation_completed_count, categorisation_total_count = categorisation_counts(
        gallery,
        categories,
    )

    if is_categorisation_running():
        live = get_live_categorisation_progress()
        if live is not None:
            categorisation_completed_count = live.completed
            categorisation_total_count = live.total

    progress, progress_phase = _resolve_progress(workspace_root, raw_scan, metadata)
    if is_face_extraction_running() and face_total_count > 0:
        progress = ResizeProgress.from_completed(
            face_total_count,
            face_completed_count,
        )
    if is_analysis_running() and analysis_total_count > 0:
        progress = ResizeProgress.from_completed(
            analysis_total_count,
            analysis_completed_count,
        )
    if is_categorisation_running() and categorisation_total_count > 0:
        progress = ResizeProgress.from_completed(
            categorisation_total_count,
            categorisation_completed_count,
        )
    processing_phase = active_phase or progress_phase

    return WorkspaceStatus(
        total_folder_raw=raw_scan.total_folders,
        total_images_raw=raw_scan.total_images,
        total_images_processed=total_images_processed,
        flags=flags,
        processing_busy=busy,
        progress_total=progress.total,
        progress_completed=progress.completed,
        progress_remaining=progress.remaining,
        processing_phase=processing_phase,
        resize_completed_count=resize_completed_count,
        resize_total_count=resize_total_count,
        palette_completed_count=palette_completed_count,
        palette_total_count=palette_total_count,
        analysis_completed_count=analysis_completed_count,
        analysis_total_count=analysis_total_count,
        categorisation_completed_count=categorisation_completed_count,
        categorisation_total_count=categorisation_total_count,
        face_completed_count=face_completed_count,
        face_total_count=face_total_count,
        categories_count=len(categories.categories),
        persons_count=persons_count,
        openai_configured=is_openai_configured(workspace_root),
    )
