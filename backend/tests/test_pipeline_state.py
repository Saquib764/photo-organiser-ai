"""Pipeline state persistence tests."""

from pathlib import Path

from app.services.pipeline_state import load_state_document, refresh_pipeline_state
from app.services.status import build_workspace_status


def test_processing_busy_is_in_memory_only(tmp_path: Path) -> None:
    """Stale processing_busy on disk must not affect WebSocket status."""
    (tmp_path / "raw").mkdir()
    (tmp_path / "processed_small").mkdir()

    import json

    from app.services.pipeline_state import state_file_path

    state_file_path(tmp_path).write_text(
        json.dumps({"processing_busy": True, "flags": {}, "user_actions": []}),
        encoding="utf-8",
    )

    refresh_pipeline_state(tmp_path)
    status = build_workspace_status(tmp_path)

    assert status.processing_busy is False
    assert status.processing_phase is None
