"""Schemas for workspace-stored OpenAI API key settings."""

from pydantic import BaseModel, Field


class OpenAiKeyDocument(BaseModel):
    api_key: str = ""


class OpenAiKeyStatusResponse(BaseModel):
    configured: bool
    masked_key: str | None = None


class OpenAiKeyUpdateRequest(BaseModel):
    api_key: str = Field(min_length=1)
