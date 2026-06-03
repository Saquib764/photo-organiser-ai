"""OpenAI image analysis integration tests."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

from app.schemas.image_analysis import ImageAnalysisResult
from app.schemas.person import PersonDocument, PersonEntry
from app.services.image_analysis import analyze_processed_image, build_analysis_user_prompt
from app.services.image_metadata import sync_metadata_document
from app.services.image_processing import process_all_raw_images
from app.services.person_store import save_person_document
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


def test_build_analysis_user_prompt_without_people() -> None:
    assert build_analysis_user_prompt(Path("/tmp"), []) == (
        "Analyze this photograph and return the metadata."
    )
    assert build_analysis_user_prompt(Path("/tmp"), None) == (
        "Analyze this photograph and return the metadata."
    )


def test_build_analysis_user_prompt_includes_person_id_and_description(
    tmp_path: Path,
) -> None:
    save_person_document(
        tmp_path,
        PersonDocument(
            persons=[
                PersonEntry(
                    id="person-001",
                    name="Person 1",
                    description="Bride",
                    thumbnail="person-001.jpg",
                ),
                PersonEntry(
                    id="person-002",
                    name="Person 2",
                    description="",
                    thumbnail="person-002.jpg",
                ),
            ],
            updated_at=datetime.now(UTC),
        ),
    )

    prompt = build_analysis_user_prompt(tmp_path, ["person-001", "person-002", "person-missing"])

    assert "person-001" in prompt
    assert "Bride" in prompt
    assert "person-002" in prompt
    assert "Person 2" in prompt
    assert "person-missing" in prompt
    assert "face recognition" in prompt


@pytest.mark.asyncio
async def test_analyze_processed_image_sends_known_people_in_prompt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services.openai_settings import save_openai_api_key

    save_openai_api_key(tmp_path, "test-key")
    processed = tmp_path / "processed_small"
    processed.mkdir()
    _write_image(processed / "a.jpg", (32, 32))
    save_person_document(
        tmp_path,
        PersonDocument(
            persons=[
                PersonEntry(
                    id="person-001",
                    name="Person 1",
                    description="Groom",
                    thumbnail="person-001.jpg",
                ),
            ],
            updated_at=datetime.now(UTC),
        ),
    )

    mock_result = ImageAnalysisResult(
        caption="The groom smiling",
        number_of_people=1,
        has_bride=False,
        has_groom=True,
        has_other_people=False,
        is_blur=False,
        quality_score=8.0,
    )
    captured: dict[str, str] = {}

    async def fake_parse(**kwargs):
        user_content = kwargs["messages"][1]["content"]
        captured["text"] = next(item["text"] for item in user_content if item["type"] == "text")
        message = AsyncMock()
        message.parsed = mock_result
        choice = AsyncMock()
        choice.message = message
        completion = AsyncMock()
        completion.choices = [choice]
        return completion

    mock_client = AsyncMock()
    mock_client.beta.chat.completions.parse = fake_parse

    with patch(
        "app.services.image_analysis.AsyncOpenAI",
        return_value=mock_client,
    ):
        result = await analyze_processed_image(
            tmp_path,
            "a.jpg",
            person_ids=["person-001"],
            client=mock_client,
        )

    assert result.caption == mock_result.caption
    assert "person-001" in captured["text"]
    assert "Groom" in captured["text"]
