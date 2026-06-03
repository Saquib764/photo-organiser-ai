"""Face detection and clustering with DeepFace."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from PIL import Image

from app.services.face_extraction import (
    _DetectedFace,
    _cluster_and_persist,
    _cluster_faces,
    _facial_area_to_bbox,
    _get_deepface,
    extract_people_from_library,
)
from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry
from app.services.image_metadata import load_metadata_document
from app.services.image_processing import process_all_raw_images


def _write_image(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(120, 80, 200)).save(path)


def test_facial_area_to_bbox() -> None:
    assert _facial_area_to_bbox({"x": 10, "y": 20, "w": 30, "h": 40}) == (
        10.0,
        20.0,
        40.0,
        60.0,
    )


def test_cluster_faces_groups_identical_embeddings() -> None:
    embedding = np.array([1.0, 0.0], dtype=np.float32)
    faces = [
        _DetectedFace("a.jpg", (0, 0, 10, 10), embedding.copy()),
        _DetectedFace("b.jpg", (0, 0, 10, 10), embedding.copy()),
    ]
    assert _cluster_faces(faces) == [0, 0]


def test_cluster_faces_splits_distant_embeddings() -> None:
    near = np.array([1.0, 0.0], dtype=np.float32)
    far = np.array([0.0, 1.0], dtype=np.float32)
    faces = [
        _DetectedFace("a.jpg", (0, 0, 10, 10), near.copy()),
        _DetectedFace("b.jpg", (0, 0, 10, 10), far.copy()),
    ]
    assert _cluster_faces(faces) == [0, 1]


def test_scale_bbox_maps_detection_coords_to_raw() -> None:
    from app.services.face_extraction import _scale_bbox

    assert _scale_bbox((10.0, 20.0, 30.0, 40.0), 2.0, 3.0) == (20.0, 60.0, 60.0, 120.0)


def test_cluster_and_persist_keeps_multiple_faces_in_one_photo(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_image(raw / "photo.jpg", (80, 60))
    _write_image(raw / "other.jpg", (80, 60))

    same_person = np.array([1.0, 0.0], dtype=np.float32)
    different_person = np.array([0.0, 1.0], dtype=np.float32)
    faces = [
        _DetectedFace("photo.jpg", (0, 0, 10, 10), same_person.copy()),
        _DetectedFace("photo.jpg", (20, 0, 30, 10), same_person.copy()),
        _DetectedFace("other.jpg", (0, 0, 10, 10), different_person.copy()),
    ]
    metadata = ImageMetadataDocument(
        images=[
            ImageMetadataEntry(path="photo.jpg"),
            ImageMetadataEntry(path="other.jpg"),
        ],
    )

    _cluster_and_persist(tmp_path, metadata, faces)

    assert (tmp_path / "persons.json").is_file()
    from app.services.person_store import load_person_document

    document = load_person_document(tmp_path)
    assert len(document.persons) == 2
    by_id = {person.id: person for person in document.persons}
    assert by_id["person-001"].face_count == 2
    assert by_id["person-001"].image_count == 1
    assert by_id["person-002"].face_count == 1
    assert metadata.images[0].person_ids == ["person-001"]
    assert metadata.images[1].person_ids == ["person-002"]


def test_extract_people_from_library_persists_persons(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (200, 150))
    process_all_raw_images(tmp_path, max_dimension=80)

    mock_deepface = MagicMock()
    mock_deepface.represent.return_value = [
        {
            "embedding": [0.0] * 512,
            "facial_area": {"x": 60, "y": 30, "w": 60, "h": 60},
        },
    ]

    _get_deepface.cache_clear()
    with patch(
        "app.services.face_extraction._get_deepface",
        return_value=mock_deepface,
    ):
        updated = extract_people_from_library(tmp_path, only_missing=False)

    assert updated == 1
    assert (tmp_path / "persons.json").is_file()
    assert (tmp_path / "persons" / "person-001.jpg").is_file()

    metadata = load_metadata_document(tmp_path)
    assert metadata.images[0].faces_scanned is True
    assert metadata.images[0].person_ids == ["person-001"]
