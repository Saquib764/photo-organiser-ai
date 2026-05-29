"""Image metadata file sync and caption-based analysis completion."""

import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app.services.image_metadata import (
    caption_counts,
    extract_image_palettes,
    is_metadata_analysis_complete,
    metadata_file_path,
    needs_palette_extraction,
    save_metadata_document,
    sync_metadata_document,
)
from app.services.image_processing import process_all_raw_images
from app.services.pipeline_state import refresh_pipeline_state


def _write_image(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(120, 80, 200)).save(path)


def test_metadata_file_created_on_sync(tmp_path: Path) -> None:
    (tmp_path / "raw").mkdir()
    (tmp_path / "processed_small").mkdir()

    sync_metadata_document(tmp_path)

    assert metadata_file_path(tmp_path).is_file()
    data = json.loads(metadata_file_path(tmp_path).read_text(encoding="utf-8"))
    assert data == {"images": []}


def test_metadata_sync_adds_processed_paths_with_empty_caption(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "album" / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    document = sync_metadata_document(tmp_path)

    assert len(document.images) == 1
    assert document.images[0].path == "album/photo.jpg"
    entry = document.images[0]
    assert entry.caption == ""
    assert entry.number_of_people == 0
    assert entry.has_bride is False
    assert entry.has_groom is False
    assert entry.has_other_people is False
    assert entry.is_blur is False
    assert entry.quality_score == 0.0


def test_analysis_complete_false_when_any_caption_empty(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "a.jpg", (120, 90))
    _write_image(raw / "b.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    document = sync_metadata_document(tmp_path)
    document.images[0].caption = "Done"
    save_metadata_document(tmp_path, document)

    completed, total = caption_counts(document)
    assert completed == 1
    assert total == 2
    assert not is_metadata_analysis_complete(document)

    flags_doc = refresh_pipeline_state(tmp_path)
    assert flags_doc.flags.resize_complete is True
    assert flags_doc.flags.image_analysis_complete is False


def test_analysis_complete_when_all_captions_filled(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    document = sync_metadata_document(tmp_path)
    for entry in document.images:
        entry.caption = "A scene"
    save_metadata_document(tmp_path, document)

    flags_doc = refresh_pipeline_state(tmp_path)
    assert flags_doc.flags.image_analysis_complete is True


def test_needs_palette_extraction_when_any_empty(tmp_path: Path) -> None:
    from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry

    assert not needs_palette_extraction(ImageMetadataDocument())
    assert needs_palette_extraction(
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(path="a.jpg", palette_colors=["#aabbcc"]),
                ImageMetadataEntry(path="b.jpg"),
            ],
        ),
    )


def test_extract_image_palettes_only_missing(tmp_path: Path) -> None:
    from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry

    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "done.jpg", (120, 90))
    _write_image(raw / "pending.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    extract_image_palettes(tmp_path)
    document = sync_metadata_document(tmp_path)
    done_palette = document.images[0].palette_colors
    document.images[1].palette_colors = []
    save_metadata_document(tmp_path, document)

    updated = extract_image_palettes(tmp_path, only_missing=True)

    document = sync_metadata_document(tmp_path)
    assert updated == 1
    assert document.images[0].palette_colors == done_palette
    assert document.images[1].palette_colors


def test_has_analysed_color_flag_when_palettes_complete(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)
    extract_image_palettes(tmp_path)

    flags_doc = refresh_pipeline_state(tmp_path)

    assert flags_doc.flags.resize_complete is True
    assert flags_doc.flags.has_analysed_color is True
    assert flags_doc.flags.image_analysis_complete is False


def test_extract_image_palettes_saves_each_batch(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    for index in range(5):
        _write_image(raw / f"photo{index}.jpg", (40, 30))
    process_all_raw_images(tmp_path, max_dimension=50)
    sync_metadata_document(tmp_path)

    palettes_saved_per_batch: list[int] = []
    original_save = save_metadata_document

    def tracking_save(workspace_root: Path, document) -> None:
        palettes_saved_per_batch.append(
            sum(1 for entry in document.images if entry.palette_colors),
        )
        original_save(workspace_root, document)

    with (
        patch(
            "app.services.image_metadata.save_metadata_document",
            side_effect=tracking_save,
        ),
        patch("app.services.image_metadata._refresh_pipeline_flags"),
    ):
        updated = extract_image_palettes(tmp_path, batch_size=2)

    assert updated == 5
    batch_save_counts = [
        count for index, count in enumerate(palettes_saved_per_batch) if count > 0
    ]
    assert len(batch_save_counts) >= 3
    assert batch_save_counts[-1] == 5


def test_extract_image_palettes_after_resize(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    sync_metadata_document(tmp_path)
    updated = extract_image_palettes(tmp_path)

    document = sync_metadata_document(tmp_path)
    assert updated == 1
    assert len(document.images) == 1
    palette = document.images[0].palette_colors
    assert palette
    assert palette[0].startswith("#")
    assert len(palette[0]) == 7
