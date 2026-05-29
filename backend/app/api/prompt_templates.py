"""REST endpoints for photobook prompt template ideas."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas.prompt_templates import (
    PromptTemplateContentResponse,
    PromptTemplateListResponse,
    PromptTemplateSummary,
)
from app.services.prompt_templates import list_prompt_templates, read_prompt_template

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.api_v1_prefix, tags=["prompt-templates"])


@router.get("/prompt-templates", response_model=PromptTemplateListResponse)
async def get_prompt_templates() -> PromptTemplateListResponse:
    templates = [
        PromptTemplateSummary(**item) for item in list_prompt_templates()
    ]
    return PromptTemplateListResponse(templates=templates)


@router.get(
    "/prompt-templates/{template_id}",
    response_model=PromptTemplateContentResponse,
)
async def get_prompt_template(template_id: str) -> PromptTemplateContentResponse:
    try:
        data = read_prompt_template(template_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template id",
        ) from None
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        ) from None
    return PromptTemplateContentResponse(**data)
