"""Application configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent
DEFAULT_WORKSPACE_ROOT = PROJECT_ROOT / "workspace"


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    service_name: str = "photo-organiser-api"
    environment: str = "development"
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Override for Electron or custom installs (env: WORKSPACE_ROOT)
    workspace_root: Path = Field(default=DEFAULT_WORKSPACE_ROOT)
    processed_max_dimension: int = Field(
        default=200,
        ge=1,
        description="Max width or height in pixels for processed_small thumbnails",
    )
    resize_worker_count: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Thread pool size for parallel image resizing",
    )
    palette_batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Number of images per palette extraction batch before saving metadata",
    )
    analysis_batch_size: int = Field(
        default=40,
        ge=1,
        le=100,
        description="Number of OpenAI vision requests to run in parallel per analysis batch",
    )
    categorisation_batch_size: int = Field(
        default=10,
        ge=1,
        le=400,
        description="Maximum images per categoriser OpenAI call",
    )
    face_match_threshold: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Cosine similarity threshold for matching the same person (DeepFace)",
    )
    deepface_model: str = Field(
        default="ArcFace",
        description="DeepFace recognition model (e.g. ArcFace, Facenet, VGG-Face)",
    )
    deepface_detector: str = Field(
        default="opencv",
        description="DeepFace detector backend (opencv avoids dlib)",
    )
    face_max_dimension: int = Field(
        default=400,
        ge=64,
        le=4096,
        description="Max width or height when resizing raw images before face detection",
    )
    person_thumbnail_size: int = Field(
        default=128,
        ge=32,
        le=512,
        description="Max width/height for person thumbnail crops",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Vision-capable OpenAI model for image analysis",
    )

    service_version: str = "0.1.0"
    git_commit: str = "unknown"
    build_timestamp: str = "unknown"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
