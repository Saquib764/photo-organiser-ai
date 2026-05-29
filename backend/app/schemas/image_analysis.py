"""Structured output from OpenAI vision analysis."""

from pydantic import BaseModel, Field


class ImageAnalysisResult(BaseModel):
    """Vision model output for a single processed image."""

    caption: str = Field(description="Short descriptive caption for the photo.")
    number_of_people: int = Field(
        ge=0,
        description="Number of people clearly visible in the image.",
    )
    has_bride: bool = Field(
        description="True if a bride is clearly visible in the image.",
    )
    has_groom: bool = Field(
        description="True if a groom is clearly visible in the image.",
    )
    has_other_people: bool = Field(
        description="True if people other than the bride/groom are clearly visible.",
    )
    is_blur: bool = Field(
        description="True if the image is noticeably blurry, out of focus, or motion-blurred.",
    )
    quality_score: float = Field(
        ge=0,
        le=10,
        description=(
            "Overall quality from 0 to 10. Higher for grand compositions, sharp focus, "
            "and good lighting; lower for blur, poor light, or weak composition."
        ),
    )
