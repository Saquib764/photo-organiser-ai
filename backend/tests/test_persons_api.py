"""Persons REST API."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry
from app.schemas.person import PersonDocument, PersonEntry
from app.services.image_metadata import load_metadata_document, save_metadata_document
from app.services.person_store import save_person_document


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(settings, "workspace_root", tmp_path)
    (tmp_path / "persons").mkdir()
    return tmp_path


def test_list_persons_returns_registry(workspace: Path) -> None:
    (workspace / "persons" / "person-001.jpg").write_bytes(b"jpeg")

    save_person_document(
        workspace,
        PersonDocument(
            persons=[
                PersonEntry(
                    id="person-001",
                    name="Guest",
                    thumbnail="person-001.jpg",
                    face_count=3,
                    image_count=2,
                ),
            ],
            updated_at=datetime.now(UTC),
        ),
    )

    client = TestClient(app)
    response = client.get("/api/v1/persons")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["persons"]) == 1
    assert payload["persons"][0]["id"] == "person-001"
    assert payload["persons"][0]["face_count"] == 3
    assert payload["persons"][0]["image_count"] == 2


def test_delete_person_removes_registry_thumbnail_and_metadata_refs(
    workspace: Path,
) -> None:
    (workspace / "persons" / "person-001.jpg").write_bytes(b"jpeg")
    (workspace / "persons" / "person-002.jpg").write_bytes(b"jpeg")

    save_person_document(
        workspace,
        PersonDocument(
            persons=[
                PersonEntry(
                    id="person-001",
                    name="Keep",
                    thumbnail="person-001.jpg",
                    face_count=1,
                    image_count=1,
                ),
                PersonEntry(
                    id="person-002",
                    name="Delete me",
                    thumbnail="person-002.jpg",
                    face_count=2,
                    image_count=2,
                ),
            ],
            updated_at=datetime.now(UTC),
        ),
    )
    save_metadata_document(
        workspace,
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(
                    path="a.jpg",
                    person_ids=["person-001", "person-002"],
                    faces_scanned=True,
                ),
                ImageMetadataEntry(
                    path="b.jpg",
                    person_ids=["person-002"],
                    faces_scanned=True,
                ),
            ],
        ),
    )

    client = TestClient(app)
    response = client.delete("/api/v1/persons/person-002")

    assert response.status_code == 200
    assert response.json() == {"id": "person-002", "removed_from_metadata": 2}
    assert not (workspace / "persons" / "person-002.jpg").is_file()
    assert (workspace / "persons" / "person-001.jpg").is_file()

    list_resp = client.get("/api/v1/persons")
    assert [person["id"] for person in list_resp.json()["persons"]] == ["person-001"]

    metadata = load_metadata_document(workspace)
    assert metadata.images[0].person_ids == ["person-001"]
    assert metadata.images[1].person_ids == []


def test_delete_person_not_found(workspace: Path) -> None:
    client = TestClient(app)
    response = client.delete("/api/v1/persons/person-999")
    assert response.status_code == 404
