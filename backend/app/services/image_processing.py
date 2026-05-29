"""Resize raw workspace images into processed_small, mirroring folder layout."""

from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from app.config import settings
from app.services.workspace import (
    IMAGE_EXTENSIONS,
    PROCESSED_DIR_NAME,
    RAW_DIR_NAME,
    count_images,
    count_raw_subfolders,
)

logger = logging.getLogger(__name__)

_progress_lock = threading.Lock()
_live_progress: dict[str, int | bool] = {
    "total": 0,
    "completed": 0,
    "running": False,
}


@dataclass(frozen=True, slots=True)
class ResizeProgress:
    """Resize completion counts (one entry per raw image)."""

    total: int
    completed: int
    remaining: int

    @classmethod
    def empty(cls) -> ResizeProgress:
        return cls(total=0, completed=0, remaining=0)

    @classmethod
    def from_completed(cls, total: int, completed: int) -> ResizeProgress:
        return cls(total=total, completed=completed, remaining=max(total - completed, 0))


@dataclass(frozen=True, slots=True)
class RawScan:
    """Single-pass scan of the raw library."""

    total_folders: int
    total_images: int
    progress: ResizeProgress


@dataclass(frozen=True, slots=True)
class ImageProcessResult:
    """Summary of a full raw → processed_small pass."""

    processed: int = 0
    skipped: int = 0
    failed: int = 0


@dataclass(frozen=True, slots=True)
class _ResizeJob:
    source: Path
    dest: Path
    rel: Path
    max_dimension: int


def _is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def is_processed_up_to_date(source: Path, dest: Path) -> bool:
    """True when dest exists and is not older than the raw source."""
    if not dest.is_file():
        return False
    return source.stat().st_mtime <= dest.stat().st_mtime


def scan_raw(workspace_root: Path) -> RawScan:
    """Scan raw/ once for folder count, image count, and resize progress."""
    raw_dir = workspace_root / RAW_DIR_NAME
    processed_dir = workspace_root / PROCESSED_DIR_NAME

    if not raw_dir.is_dir():
        return RawScan(0, 0, ResizeProgress.empty())

    total = 0
    completed = 0
    for source in raw_dir.rglob("*"):
        if not _is_image(source):
            continue
        total += 1
        rel = source.relative_to(raw_dir)
        if is_processed_up_to_date(source, processed_dir / rel):
            completed += 1

    return RawScan(
        total_folders=count_raw_subfolders(raw_dir),
        total_images=total,
        progress=ResizeProgress.from_completed(total, completed),
    )


def is_resize_complete(
    workspace_root: Path,
    *,
    raw_scan: RawScan | None = None,
) -> bool:
    """
    True when raw and processed_small are in sync:
    every raw image has an up-to-date processed copy, and every processed
    image has a matching raw source.
    """
    scan = raw_scan or scan_raw(workspace_root)
    if scan.total_images == 0 or scan.progress.remaining > 0:
        return False

    raw_dir = workspace_root / RAW_DIR_NAME
    processed_dir = workspace_root / PROCESSED_DIR_NAME
    if not processed_dir.is_dir():
        return False

    for processed_path in processed_dir.rglob("*"):
        if not _is_image(processed_path):
            continue
        rel = processed_path.relative_to(processed_dir)
        raw_path = raw_dir / rel
        if not _is_image(raw_path):
            return False
        if not is_processed_up_to_date(raw_path, processed_path):
            return False

    return True


def _set_live_progress(*, total: int, completed: int, running: bool) -> None:
    with _progress_lock:
        _live_progress["total"] = total
        _live_progress["completed"] = completed
        _live_progress["running"] = running


def get_live_resize_progress() -> ResizeProgress | None:
    with _progress_lock:
        if not _live_progress["running"]:
            return None
        total = int(_live_progress["total"])
        completed = int(_live_progress["completed"])
    return ResizeProgress.from_completed(total, completed)


def _increment_live_progress() -> None:
    with _progress_lock:
        _live_progress["completed"] = int(_live_progress["completed"]) + 1


def _save_kwargs(image: Image.Image, dest: Path) -> dict:
    suffix = dest.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        return {"format": "JPEG", "quality": 85, "optimize": True}
    if suffix == ".webp":
        return {"format": "WEBP", "quality": 85, "method": 4}
    if suffix == ".png":
        return {"format": "PNG", "optimize": True}
    if suffix == ".gif":
        return {"format": "GIF", "optimize": True}
    if suffix in {".bmp", ".tiff", ".tif"}:
        return {"format": image.format or "PNG"}
    return {}


def _resize_and_save(source: Path, dest: Path, *, max_dimension: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as img:
        img = img.convert("RGBA") if img.mode == "P" else img
        resized = img.copy()
        resized.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        save_kwargs = _save_kwargs(resized, dest)
        resized.save(dest, **save_kwargs)


def _run_resize_job(job: _ResizeJob) -> str:
    """Resize one image. Returns 'processed', 'skipped', or 'failed'."""
    if is_processed_up_to_date(job.source, job.dest):
        logger.debug("Skipping up-to-date %s", job.rel)
        return "skipped"

    try:
        _resize_and_save(job.source, job.dest, max_dimension=job.max_dimension)
        logger.debug("Processed %s", job.rel)
        return "processed"
    except Exception:
        logger.exception("Failed to process %s", job.rel)
        return "failed"


def _collect_resize_jobs(
    raw_dir: Path,
    processed_dir: Path,
    *,
    max_dimension: int,
) -> list[_ResizeJob]:
    jobs: list[_ResizeJob] = []
    for source in sorted(raw_dir.rglob("*")):
        if not _is_image(source):
            continue
        rel = source.relative_to(raw_dir)
        jobs.append(
            _ResizeJob(
                source=source,
                dest=processed_dir / rel,
                rel=rel,
                max_dimension=max_dimension,
            )
        )
    return jobs


def process_all_raw_images(
    workspace_root: Path,
    *,
    max_dimension: int | None = None,
    worker_count: int | None = None,
) -> ImageProcessResult:
    """
    Walk ``raw/``, resize each image with a thread pool (default 4 workers).
    Skips images that already have an up-to-date file in ``processed_small/``.
    """
    limit = max_dimension if max_dimension is not None else settings.processed_max_dimension
    workers = worker_count if worker_count is not None else settings.resize_worker_count
    raw_dir = workspace_root / RAW_DIR_NAME
    processed_dir = workspace_root / PROCESSED_DIR_NAME
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.is_dir():
        logger.warning("Raw directory missing: %s", raw_dir)
        return ImageProcessResult()

    jobs = _collect_resize_jobs(raw_dir, processed_dir, max_dimension=limit)
    if not jobs:
        return ImageProcessResult()

    processed_count = 0
    skipped_count = 0
    failed_count = 0
    _set_live_progress(total=len(jobs), completed=0, running=True)

    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_run_resize_job, job) for job in jobs]
            for future in as_completed(futures):
                outcome = future.result()
                if outcome == "processed":
                    processed_count += 1
                elif outcome == "skipped":
                    skipped_count += 1
                else:
                    failed_count += 1
                _increment_live_progress()
    finally:
        _set_live_progress(total=len(jobs), completed=len(jobs), running=False)

    result = ImageProcessResult(
        processed=processed_count,
        skipped=skipped_count,
        failed=failed_count,
    )
    logger.info(
        "Image processing complete: %d processed, %d skipped, %d failed "
        "(workers=%d, max_dimension=%d)",
        result.processed,
        result.skipped,
        result.failed,
        workers,
        limit,
    )
    return result
