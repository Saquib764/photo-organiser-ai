"""Schemas for photobook prompt template ideas."""

from pydantic import BaseModel, Field


class PromptTemplateSummary(BaseModel):
    """A prompt template file available in prompt-template/."""

    id: str = Field(description="Filename stem (e.g. office-event for office-event.md)")
    name: str = Field(description="Human-readable label derived from the filename")


class PromptTemplateListResponse(BaseModel):
    templates: list[PromptTemplateSummary]


class PromptTemplateContentResponse(BaseModel):
    id: str
    name: str
    content: str
