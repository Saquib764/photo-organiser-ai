"""Shared pytest fixtures."""

import pytest

from app.services.image_metadata import _set_live_palette_progress
from app.services.image_categoriser import _set_live_categorisation_progress
from app.services.image_processing import _set_live_progress
from app.services.pipeline_runner import reset_pipeline_runner_state


@pytest.fixture(autouse=True)
def _reset_in_memory_pipeline_state() -> None:
    """Prevent task-running flags leaking between tests."""
    reset_pipeline_runner_state()
    _set_live_progress(total=0, completed=0, running=False)
    _set_live_palette_progress(total=0, completed=0, running=False)
    _set_live_categorisation_progress(total=0, completed=0, running=False)
    yield
    reset_pipeline_runner_state()
    _set_live_progress(total=0, completed=0, running=False)
    _set_live_palette_progress(total=0, completed=0, running=False)
    _set_live_categorisation_progress(total=0, completed=0, running=False)
