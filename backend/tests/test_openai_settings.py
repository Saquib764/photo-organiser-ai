"""Tests for workspace OpenAI API key storage and settings API."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.openai_settings import (
    delete_openai_api_key,
    is_openai_configured,
    load_openai_api_key,
    mask_api_key,
    save_openai_api_key,
)


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(settings, "workspace_root", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_save_load_and_delete_key(workspace: Path) -> None:
    assert load_openai_api_key(workspace) == ""
    assert not is_openai_configured(workspace)

    save_openai_api_key(workspace, "  sk-test-secret-key  ")
    assert load_openai_api_key(workspace) == "sk-test-secret-key"
    assert is_openai_configured(workspace)

    delete_openai_api_key(workspace)
    assert load_openai_api_key(workspace) == ""


def test_mask_api_key() -> None:
    assert mask_api_key("sk-abcdefghijklmnop") == "sk-…mnop"
    assert mask_api_key("") is None


def test_settings_api_crud(workspace: Path) -> None:
    client = TestClient(app)

    get_empty = client.get("/api/v1/settings/openai-key")
    assert get_empty.status_code == 200
    assert get_empty.json() == {"configured": False, "masked_key": None}

    put_resp = client.put(
        "/api/v1/settings/openai-key",
        json={"api_key": "sk-test-workspace-key"},
    )
    assert put_resp.status_code == 200
    payload = put_resp.json()
    assert payload["configured"] is True
    assert payload["masked_key"] == "sk-…-key"

    get_saved = client.get("/api/v1/settings/openai-key")
    assert get_saved.json()["configured"] is True
    assert "sk-test-workspace-key" not in str(get_saved.json())

    delete_resp = client.delete("/api/v1/settings/openai-key")
    assert delete_resp.status_code == 204

    get_after = client.get("/api/v1/settings/openai-key")
    assert get_after.json()["configured"] is False
