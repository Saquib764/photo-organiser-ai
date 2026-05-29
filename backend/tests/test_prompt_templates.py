"""Tests for prompt template listing and content API."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import prompt_templates as svc


@pytest.fixture
def template_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "prompt-template"
    root.mkdir()
    (root / "office-event.md").write_text("Office event brief\n", encoding="utf-8")
    (root / "full_marriage.md").write_text("Full marriage brief\n", encoding="utf-8")
    monkeypatch.setattr(svc, "PROMPT_TEMPLATE_DIR", root)
    return root


def test_format_template_display_name() -> None:
    assert svc.format_template_display_name("office-event") == "Office Event"
    assert svc.format_template_display_name("full_marriage") == "Full Marriage"


def test_list_and_read_templates(template_dir: Path) -> None:
    listed = svc.list_prompt_templates()
    assert len(listed) == 2
    assert {item["id"] for item in listed} == {"office-event", "full_marriage"}

    content = svc.read_prompt_template("office-event")
    assert content["name"] == "Office Event"
    assert content["content"] == "Office event brief\n"


def test_prompt_templates_api(template_dir: Path) -> None:
    client = TestClient(app)

    list_resp = client.get("/api/v1/prompt-templates")
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert len(body["templates"]) == 2
    names = {t["name"] for t in body["templates"]}
    assert names == {"Office Event", "Full Marriage"}

    detail_resp = client.get("/api/v1/prompt-templates/office-event")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["content"] == "Office event brief\n"

    missing = client.get("/api/v1/prompt-templates/missing")
    assert missing.status_code == 404
