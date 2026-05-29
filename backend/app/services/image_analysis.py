"""OpenAI vision analysis for processed workspace images."""

from __future__ import annotations

import base64
import logging
from pathlib import Path

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.image_analysis import ImageAnalysisResult
from app.prompts.prompts import IMAGE_ANALYSIS_SYSTEM_PROMPT
from app.services.image_files import media_type_for_path, resolve_processed_image_path
from app.services.openai_settings import load_openai_api_key

logger = logging.getLogger(__name__)

async def analyze_processed_image(
    workspace_root: Path,
    relative_path: str,
    *,
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
                        "text": "Analyze this photograph and return the metadata.",
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
