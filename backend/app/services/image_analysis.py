"""OpenAI vision analysis for processed workspace images."""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.image_analysis import ImageAnalysisResult
from app.prompts.prompts import IMAGE_ANALYSIS_SYSTEM_PROMPT
from app.services.image_files import media_type_for_path, resolve_processed_image_path
from app.services.openai_settings import load_openai_api_key
from app.services.person_store import load_person_document, person_by_id

logger = logging.getLogger(__name__)


def build_analysis_user_prompt(
    workspace_root: Path,
    person_ids: list[str] | None = None,
) -> str:
    """Build the vision user text, including known people when face extraction tagged them."""
    if not person_ids:
        return "Analyze this photograph and return the metadata."

    people = person_by_id(load_person_document(workspace_root))
    known_people: list[dict[str, str]] = []
    for person_id in person_ids:
        person = people.get(person_id)
        if person is None:
            known_people.append({"id": person_id, "description": ""})
        else:
            known_people.append(
                {
                    "id": person.id,
                    "description": person.description.strip() or person.name,
                },
            )

    people_json = json.dumps(known_people, indent=2)
    return (
        "Known people in this photo (from face recognition):\n"
        f"{people_json}\n\n"
        "Analyze this photograph and return the metadata. "
        "When describing who appears, use these ids and descriptions where relevant."
    )


async def analyze_processed_image(
    workspace_root: Path,
    relative_path: str,
    *,
    person_ids: list[str] | None = None,
    client: AsyncOpenAI | None = None,
) -> ImageAnalysisResult:
    """Send one processed thumbnail to OpenAI and return structured metadata."""
    api_key = load_openai_api_key(workspace_root)
    if not api_key:
        msg = "OpenAI API key is not configured in workspace settings"
        raise RuntimeError(msg)

    try:
        image_path = resolve_processed_image_path(workspace_root, relative_path)
    except ValueError as exc:
        msg = f"Processed image not found: {relative_path}"
        raise FileNotFoundError(msg) from exc

    encoded = base64.standard_b64encode(image_path.read_bytes()).decode("ascii")
    media_type = media_type_for_path(image_path)
    data_url = f"data:{media_type};base64,{encoded}"

    openai_client = client or AsyncOpenAI(api_key=api_key)
    completion = await openai_client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": IMAGE_ANALYSIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": build_analysis_user_prompt(workspace_root, person_ids),
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        response_format=ImageAnalysisResult,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        msg = f"OpenAI returned no structured output for {relative_path}"
        raise RuntimeError(msg)

    logger.debug("Analyzed %s: %d people", relative_path, parsed.number_of_people)
    return parsed
