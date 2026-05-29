"""OpenAI image analysis integration tests."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

from app.schemas.image_analysis import ImageAnalysisResult
from app.services.image_analysis import analyze_processed_image
from app.services.image_metadata import sync_metadata_document
from app.services.image_processing import process_all_raw_images
from app.services.pipeline_runner import run_analysis


def _write_image(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(200, 100, 50)).save(path)


@pytest.mark.asyncio
async def test_run_analysis_writes_structured_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.openai_settings import save_openai_api_key

    save_openai_api_key(tmp_path, "test-key")

    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()
    _write_image(raw / "event" / "photo.jpg", (64, 64))
    process_all_raw_images(tmp_path, max_dimension=50)

    mock_result = ImageAnalysisResult(
        caption="Bride and groom on the dance floor",
        number_of_people=2,
        has_bride=True,
        has_groom=True,
        has_other_people=False,
        is_blur=False,
        quality_score=8.5,
    )

    with patch(
        "app.services.pipeline_runner.analyze_processed_image",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        await run_analysis(tmp_path)

    document = sync_metadata_document(tmp_path)
    entry = document.images[0]
    assert entry.path == "event/photo.jpg"
    assert entry.caption == mock_result.caption
    assert entry.number_of_people == 2
    assert entry.has_bride is True
    assert entry.has_groom is True
    assert entry.has_other_people is False
    assert entry.is_blur is False
    assert entry.quality_score == 8.5


@pytest.mark.asyncio
async def test_analyze_processed_image_requires_api_key(tmp_path: Path) -> None:
    processed = tmp_path / "processed_small"
    processed.mkdir()
    _write_image(processed / "a.jpg", (32, 32))

    with pytest.raises(RuntimeError, match="OpenAI API key"):
        await analyze_processed_image(tmp_path, "a.jpg")
