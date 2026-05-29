"""WebSocket status endpoint tests."""

import json

from fastapi.testclient import TestClient

from app.main import app


def test_request_status_returns_workspace_counts(tmp_path, monkeypatch) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "workspace_root", tmp_path)

    raw = tmp_path / "raw"
    processed = tmp_path / "processed_small"
    raw.mkdir()
    processed.mkdir()
    (raw / "set-1").mkdir()
    (raw / "photo.jpg").write_bytes(b"x")

    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            initial = websocket.receive_json()
            assert initial["type"] == "status"
            assert initial["payload"]["total_folder_raw"] == 1
            assert initial["payload"]["total_images_raw"] == 1
            assert initial["payload"]["flags"]["image_found"] is True
            assert initial["payload"]["flags"]["resize_complete"] is False
            assert initial["payload"]["progress_total"] == 1
            assert initial["payload"]["progress_completed"] == 0
            assert initial["payload"]["progress_remaining"] == 1

            websocket.send_text(json.dumps({"type": "request_status"}))
            on_demand = websocket.receive_json()
            assert on_demand["type"] == "status"
            assert on_demand["payload"]["total_images_raw"] == 1

            websocket.send_text(json.dumps({"type": "start_processing"}))
            started = websocket.receive_json()
            assert started["type"] == "status"
            data = json.loads((tmp_path / "pipeline_state.json").read_text(encoding="utf-8"))
            assert data["user_actions"][0]["action"] == "start_processing"
