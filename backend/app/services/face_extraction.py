"""Detect faces, cluster identities, and persist person registry."""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

from app.config import settings
from app.schemas.image_metadata import ImageMetadataDocument
from app.schemas.person import PersonDocument, PersonEntry
from app.services.image_files import resolve_raw_image_path
from app.services.image_metadata import (
    save_metadata_document,
    sync_metadata_document,
)
from app.services.image_processing import ResizeProgress
from app.services.person_store import (
    clear_person_data,
    default_person_name,
    ensure_persons_dir,
    load_person_document,
    next_person_id,
    persons_file_path,
    save_person_document,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_deepface():
    """Lazy import DeepFace (loads TensorFlow models on first use)."""
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
    logger.info(
        "Loading DeepFace (model=%s, detector=%s)",
        settings.deepface_model,
        settings.deepface_detector,
    )
    try:
        from deepface import DeepFace
    except ImportError:
        logger.exception("Failed to import deepface")
        raise
    logger.info("DeepFace loaded")
    return DeepFace


_progress_lock = threading.Lock()
_live_progress: dict[str, int | bool] = {
    "total": 0,
    "completed": 0,
    "running": False,
}


@dataclass(slots=True)
class _DetectedFace:
    image_path: str
    bbox: tuple[float, float, float, float]
    embedding: np.ndarray

    @property
    def quality(self) -> float:
        x1, y1, x2, y2 = self.bbox
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def _set_live_progress(*, total: int, completed: int, running: bool) -> None:
    with _progress_lock:
        _live_progress["total"] = total
        _live_progress["completed"] = completed
        _live_progress["running"] = running


def get_live_face_progress() -> ResizeProgress | None:
    with _progress_lock:
        if not _live_progress["running"]:
            return None
        total = int(_live_progress["total"])
        completed = int(_live_progress["completed"])
    return ResizeProgress.from_completed(total, completed)


def _increment_live_progress() -> None:
    with _progress_lock:
        _live_progress["completed"] = int(_live_progress["completed"]) + 1


def face_scan_counts(document: ImageMetadataDocument) -> tuple[int, int]:
    total = len(document.images)
    completed = sum(1 for entry in document.images if entry.faces_scanned)
    return completed, total


def is_face_extraction_complete(
    workspace_root: Path,
    document: ImageMetadataDocument,
) -> bool:
    if not document.images:
        return False
    if not all(entry.faces_scanned for entry in document.images):
        return False
    return persons_file_path(workspace_root).is_file()


def clear_face_metadata(document: ImageMetadataDocument) -> None:
    for entry in document.images:
        entry.person_ids = []
        entry.faces_scanned = False


def _facial_area_to_bbox(area: dict[str, int | float]) -> tuple[float, float, float, float]:
    x = float(area["x"])
    y = float(area["y"])
    w = float(area["w"])
    h = float(area["h"])
    return (x, y, x + w, y + h)


def _normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(embedding)
    if norm <= 0:
        return embedding
    return embedding / norm


def _detection_image_and_scales(resolved: Path) -> tuple[np.ndarray, float, float]:
    """Resize for detection; return array and scale factors back to raw pixel coords."""
    with Image.open(resolved) as image:
        original = image.convert("RGB")
        detection = original.copy()
        detection.thumbnail(
            (settings.face_max_dimension, settings.face_max_dimension),
            Image.Resampling.LANCZOS,
        )
        scale_x = original.width / detection.width if detection.width else 1.0
        scale_y = original.height / detection.height if detection.height else 1.0
        return np.asarray(detection), scale_x, scale_y


def _scale_bbox(
    bbox: tuple[float, float, float, float],
    scale_x: float,
    scale_y: float,
) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = bbox
    return (x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y)


def _detect_faces(workspace_root: Path, image_path: str) -> list[_DetectedFace]:
    try:
        resolved = resolve_raw_image_path(workspace_root, image_path)
    except ValueError:
        logger.warning("Raw image missing for face detection: %s", image_path)
        return []

    try:
        detection_img, scale_x, scale_y = _detection_image_and_scales(resolved)
    except Exception:
        logger.exception("Failed to load image for face detection: %s", image_path)
        return []

    DeepFace = _get_deepface()
    try:
        results = DeepFace.represent(
            img_path=detection_img,
            model_name=settings.deepface_model,
            detector_backend=settings.deepface_detector,
            enforce_detection=False,
            align=True,
        )
    except Exception:
        logger.exception("DeepFace failed on %s", image_path)
        return []

    detected: list[_DetectedFace] = []
    for item in results:
        embedding = np.asarray(item["embedding"], dtype=np.float32)
        area = item.get("facial_area")
        if not area:
            continue
        detected.append(
            _DetectedFace(
                image_path=image_path,
                bbox=_scale_bbox(_facial_area_to_bbox(area), scale_x, scale_y),
                embedding=_normalize_embedding(embedding),
            ),
        )
    logger.debug("Detected %d face(s) in %s", len(detected), image_path)
    return detected


def _cluster_faces(faces: list[_DetectedFace]) -> list[int]:
    if not faces:
        return []

    threshold = settings.face_match_threshold
    centroids: list[np.ndarray] = []
    assignments: list[int] = []

    for face in faces:
        if not centroids:
            centroids.append(face.embedding.copy())
            assignments.append(0)
            continue

        similarities = [float(np.dot(face.embedding, c)) for c in centroids]
        best_idx = int(np.argmax(similarities))
        if similarities[best_idx] >= threshold:
            assignments.append(best_idx)
            member_count = sum(1 for item in assignments if item == best_idx)
            centroids[best_idx] = _normalize_embedding(
                (centroids[best_idx] * (member_count - 1)) + face.embedding,
            )
        else:
            centroids.append(face.embedding.copy())
            assignments.append(len(centroids) - 1)

    return assignments


def _save_person_thumbnail(
    workspace_root: Path,
    person_id: str,
    face: _DetectedFace,
) -> str:
    resolved = resolve_raw_image_path(workspace_root, face.image_path)
    image = Image.open(resolved).convert("RGB")
    width, height = image.size
    x1, y1, x2, y2 = face.bbox
    left = max(0, int(x1))
    top = max(0, int(y1))
    right = min(width, int(x2))
    bottom = min(height, int(y2))
    crop = (
        image.crop((left, top, right, bottom))
        if right > left and bottom > top
        else image
    )

    size = settings.person_thumbnail_size
    crop.thumbnail((size, size), Image.Resampling.LANCZOS)
    filename = f"{person_id}.jpg"
    crop.save(ensure_persons_dir(workspace_root) / filename, format="JPEG", quality=90)
    return filename


def _cluster_and_persist(
    workspace_root: Path,
    metadata: ImageMetadataDocument,
    all_faces: list[_DetectedFace],
) -> None:
    if not all_faces:
        for entry in metadata.images:
            entry.person_ids = []
            entry.faces_scanned = True
        save_person_document(workspace_root, PersonDocument())
        return

    cluster_ids = _cluster_faces(all_faces)
    cluster_faces: dict[int, list[_DetectedFace]] = {}
    for face, cluster_id in zip(all_faces, cluster_ids, strict=True):
        cluster_faces.setdefault(cluster_id, []).append(face)

    document = PersonDocument()
    cluster_to_person: dict[int, str] = {}
    person_index = 0
    for cluster_id, members in sorted(
        cluster_faces.items(),
        key=lambda item: len(item[1]),
        reverse=True,
    ):
        image_paths = {face.image_path for face in members}
        person_index += 1
        person_id = next_person_id(document)
        best_face = max(members, key=lambda item: item.quality)
        thumbnail = _save_person_thumbnail(workspace_root, person_id, best_face)
        now = datetime.now(UTC)
        document.persons.append(
            PersonEntry(
                id=person_id,
                name=default_person_name(person_index),
                description="",
                thumbnail=thumbnail,
                face_count=len(members),
                image_count=len(image_paths),
                created_at=now,
                updated_at=now,
            ),
        )
        cluster_to_person[cluster_id] = person_id

    per_image: dict[str, list[str]] = {}
    for face, cluster_id in zip(all_faces, cluster_ids, strict=True):
        person_id = cluster_to_person[cluster_id]
        ids = per_image.setdefault(face.image_path, [])
        if person_id not in ids:
            ids.append(person_id)

    for entry in metadata.images:
        entry.person_ids = per_image.get(entry.path, [])
        entry.faces_scanned = True

    save_person_document(workspace_root, document)


def extract_people_from_library(
    workspace_root: Path,
    *,
    only_missing: bool = True,
) -> int:
    """Detect faces on raw images and cluster into persons."""
    logger.info(
        "Face extraction starting (only_missing=%s, workspace=%s)",
        only_missing,
        workspace_root,
    )
    metadata = sync_metadata_document(workspace_root)
    all_paths = [entry.path for entry in metadata.images]
    if not all_paths:
        logger.warning("Face extraction skipped: no processed images in metadata")
        return 0

    scanned, total = face_scan_counts(metadata)
    logger.info(
        "Face extraction library: %d images, %d already scanned, force=%s",
        total,
        scanned,
        not only_missing,
    )

    if not only_missing:
        clear_person_data(workspace_root)
        clear_face_metadata(metadata)

    pending = [
        entry.path
        for entry in metadata.images
        if not only_missing or not entry.faces_scanned
    ]
    if only_missing and not pending:
        logger.info(
            "Face extraction skipped: all %d images already marked faces_scanned "
            "(use Rerun to re-cluster from scratch)",
            total,
        )
        return 0

    paths_to_process = pending if only_missing else all_paths
    logger.info("Face extraction will scan %d image(s)", len(paths_to_process))
    _set_live_progress(total=len(paths_to_process), completed=0, running=True)
    all_faces: list[_DetectedFace] = []
    try:
        for index, image_path in enumerate(paths_to_process, start=1):
            all_faces.extend(_detect_faces(workspace_root, image_path))
            _increment_live_progress()
            if index == 1 or index % 100 == 0 or index == len(paths_to_process):
                logger.info(
                    "Face scan progress: %d/%d images, %d face(s) collected so far",
                    index,
                    len(paths_to_process),
                    len(all_faces),
                )
    finally:
        _set_live_progress(
            total=len(paths_to_process),
            completed=len(paths_to_process),
            running=False,
        )

    if only_missing:
        rescan_count = 0
        for image_path in all_paths:
            if image_path not in paths_to_process:
                all_faces.extend(_detect_faces(workspace_root, image_path))
                rescan_count += 1
        if rescan_count:
            logger.info(
                "Re-scanned %d previously completed image(s) for clustering",
                rescan_count,
            )

    logger.info(
        "Face detection complete: %d face(s) across library, clustering…",
        len(all_faces),
    )
    clear_person_data(workspace_root)
    _cluster_and_persist(workspace_root, metadata, all_faces)
    save_metadata_document(workspace_root, metadata)

    person_count = len(load_person_document(workspace_root).persons)
    logger.info(
        "Face extraction finished: %d person(s), %d image(s) processed this run",
        person_count,
        len(paths_to_process),
    )
    return len(paths_to_process)
