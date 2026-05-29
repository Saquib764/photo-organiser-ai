"""User-triggered palette extraction pipeline tests."""

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from app.services.image_processing import process_all_raw_images
from app.services.pipeline_runner import (
    handle_start_palette_extraction,
    maybe_advance_pipeline,
)


def _write_image(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(120, 80, 200)).save(path)


@pytest.mark.asyncio
async def test_handle_start_palette_extraction_starts_task(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_start_palette_extraction(tmp_path)

    create_task.assert_called_once()
    coro = create_task.call_args[0][0]
    assert coro.cr_code.co_name == "_run_palette_extraction"


@pytest.mark.asyncio
async def test_handle_start_palette_extraction_skips_when_resize_incomplete(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_image(raw / "photo.jpg", (120, 90))

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_start_palette_extraction(tmp_path)

    create_task.assert_not_called()


@pytest.mark.asyncio
async def test_maybe_advance_pipeline_resumes_palette_when_action_recorded(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "photo.jpg", (120, 90))
    process_all_raw_images(tmp_path, max_dimension=50)

    from app.services.pipeline_state import record_user_action

    record_user_action(tmp_path, "start_palette_extraction")

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await maybe_advance_pipeline(tmp_path)

    create_task.assert_called_once()
    coro = create_task.call_args[0][0]
    assert coro.cr_code.co_name == "_run_palette_extraction"
