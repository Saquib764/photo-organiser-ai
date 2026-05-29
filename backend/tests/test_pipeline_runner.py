"""Pipeline runner behaviour tests."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

from app.services.image_processing import process_all_raw_images
from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry
from app.services.image_metadata import (
    extract_image_palettes,
    load_metadata_document,
    save_metadata_document,
    sync_metadata_document,
)
from app.services.pipeline_runner import (
    handle_rerun_analysis,
    handle_start_analysis,
    handle_start_palette_extraction,
    handle_start_processing,
    is_any_pipeline_job_running,
    maybe_advance_pipeline,
    reset_pipeline_runner_state,
)
from app.services import pipeline_runner
from app.services.pipeline_state import record_user_action, refresh_pipeline_state
from app.services.openai_settings import save_openai_api_key


def _write_image(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(120, 80, 200)).save(path)


@pytest.mark.asyncio
async def test_maybe_advance_pipeline_does_not_start_analysis(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)
    record_user_action(tmp_path, "start_processing")

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await maybe_advance_pipeline(tmp_path)

    create_task.assert_not_called()


@pytest.mark.asyncio
async def test_handle_start_analysis_starts_analysis_when_resize_complete(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)
    extract_image_palettes(tmp_path)

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_start_analysis(tmp_path)

    create_task.assert_called_once()
    coro = create_task.call_args[0][0]
    assert coro.cr_code.co_name == "run_analysis"


@pytest.mark.asyncio
async def test_handle_start_analysis_skips_without_palette(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_start_analysis(tmp_path)

    create_task.assert_not_called()


@pytest.mark.asyncio
async def test_handle_start_palette_skipped_while_resize_running(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    pipeline_runner._resize_running = True
    try:
        with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
            await handle_start_palette_extraction(tmp_path)
        create_task.assert_not_called()
        assert is_any_pipeline_job_running()
    finally:
        reset_pipeline_runner_state()


@pytest.mark.asyncio
async def test_handle_start_processing_starts_resize_not_analysis(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_start_processing(tmp_path)

    create_task.assert_called_once()
    coro = create_task.call_args[0][0]
    assert coro.cr_code.co_name == "run_resize"


@pytest.mark.asyncio
async def test_handle_rerun_analysis_when_analysis_complete(
    tmp_path: Path,
) -> None:
    save_openai_api_key(tmp_path, "test-key")
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    save_metadata_document(
        tmp_path,
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(
                    path="photo.jpg",
                    caption="Already done",
                    number_of_people=1,
                    palette_colors=["#787878"],
                ),
            ],
        ),
    )
    refresh_pipeline_state(tmp_path)

    with (
        patch(
            "app.services.pipeline_runner.run_analysis",
            new_callable=AsyncMock,
        ) as run_mock,
        patch("app.services.pipeline_runner.asyncio.create_task") as create_task,
    ):
        await handle_rerun_analysis(tmp_path)

    create_task.assert_called_once()
    run_mock.assert_called_once_with(tmp_path, force=True)

    metadata = load_metadata_document(tmp_path)
    assert metadata.images[0].caption == ""
    assert metadata.images[0].number_of_people == 0


@pytest.mark.asyncio
async def test_handle_start_analysis_starts_even_when_analysis_complete(
    tmp_path: Path,
) -> None:
    save_openai_api_key(tmp_path, "test-key")
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)
    extract_image_palettes(tmp_path)

    save_metadata_document(
        tmp_path,
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(
                    path="photo.jpg",
                    caption="Done",
                    palette_colors=["#787878"],
                ),
            ],
        ),
    )
    refresh_pipeline_state(tmp_path)

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_start_analysis(tmp_path)

    create_task.assert_called_once()


@pytest.mark.asyncio
async def test_handle_rerun_analysis_skips_without_palette(tmp_path: Path) -> None:
    save_openai_api_key(tmp_path, "test-key")
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_rerun_analysis(tmp_path)

    create_task.assert_not_called()
