"""Tests for image catalog listing and processed image serving."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.image_catalog import (
    ImageListFilters,
    list_category_summaries,
    list_folders,
    list_processed_images,
    resolve_processed_image_path,
    resolve_raw_image_path,
)
from app.services.image_categoriser import load_categories_document, save_categories_document
from app.services.image_delete import delete_workspace_image
from app.services.image_metadata import load_metadata_document
from app.services.image_metadata import save_metadata_document, sync_metadata_document
from app.schemas.image_categories import ImageCategoriesDocument, ImageCategory
from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(settings, "workspace_root", tmp_path)
    raw = tmp_path / "raw"
    processed = tmp_path / "processed_small"
    raw.mkdir()
    processed.mkdir()
    (raw / "album-a").mkdir()
    (raw / "album-b").mkdir()
    (raw / "root.jpg").write_bytes(b"raw")
    (raw / "album-a" / "one.png").write_bytes(b"raw")
    (raw / "album-b" / "two.webp").write_bytes(b"raw")
    (processed / "album-a").mkdir()
    (processed / "album-b").mkdir()
    (processed / "root.jpg").write_bytes(b"thumb")
    (processed / "album-a" / "one.png").write_bytes(b"thumb")
    (processed / "album-b" / "two.webp").write_bytes(b"thumb")
    return tmp_path


def test_list_folders(workspace: Path) -> None:
    folders = list_folders(workspace)
    names = [f.name for f in folders]
    assert names == ["", "album-a", "album-b"]
    assert folders[0].image_count == 1
    assert folders[1].image_count == 1


def test_list_processed_images_all(workspace: Path) -> None:
    images = list_processed_images(workspace)
    paths = {img.path for img in images}
    assert paths == {"root.jpg", "album-a/one.png", "album-b/two.webp"}


def test_list_processed_images_filtered(workspace: Path) -> None:
    images = list_processed_images(workspace, folders={"album-a"})
    assert [img.path for img in images] == ["album-a/one.png"]


def test_resolve_processed_image_path_rejects_traversal(workspace: Path) -> None:
    with pytest.raises(ValueError):
        resolve_processed_image_path(workspace, "../raw/root.jpg")


def test_resolve_raw_image_path(workspace: Path) -> None:
    path = resolve_raw_image_path(workspace, "album-a/one.png")
    assert path.read_bytes() == b"raw"


def test_resolve_raw_image_path_rejects_traversal(workspace: Path) -> None:
    with pytest.raises(ValueError):
        resolve_raw_image_path(workspace, "../processed_small/root.jpg")


def test_api_folders_and_images(workspace: Path) -> None:
    client = TestClient(app)
    folder_resp = client.get("/api/v1/folders")
    assert folder_resp.status_code == 200
    payload = folder_resp.json()
    assert {f["name"] for f in payload["folders"]} == {"", "album-a", "album-b"}

    images_resp = client.get("/api/v1/images", params=[("folders", "album-a")])
    assert images_resp.status_code == 200
    images = images_resp.json()["images"]
    assert len(images) == 1
    assert images[0]["path"] == "album-a/one.png"
    assert "caption" in images[0]
    assert "has_bride" in images[0]

    bride_resp = client.get(
        "/api/v1/images",
        params=[("folders", "album-a"), ("has_bride", "true")],
    )
    assert bride_resp.status_code == 200
    assert len(bride_resp.json()["images"]) <= 1


def test_list_images_includes_metadata(workspace: Path) -> None:
    save_metadata_document(
        workspace,
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(
                    path="album-a/one.png",
                    caption="Wedding dance",
                    number_of_people=2,
                    has_bride=True,
                    has_groom=True,
                    has_other_people=False,
                ),
            ],
        ),
    )

    images = list_processed_images(workspace)
    entry = next(img for img in images if img.path == "album-a/one.png")
    assert entry.caption == "Wedding dance"
    assert entry.number_of_people == 2
    assert entry.has_bride is True
    assert entry.analyzed is True


def test_list_images_metadata_filters(workspace: Path) -> None:
    sync_metadata_document(workspace)
    save_metadata_document(
        workspace,
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(
                    path="album-a/one.png",
                    caption="Bride portrait",
                    number_of_people=1,
                    has_bride=True,
                    has_groom=False,
                    has_other_people=False,
                ),
                ImageMetadataEntry(
                    path="album-b/two.webp",
                    caption="",
                    number_of_people=0,
                    has_bride=False,
                    has_groom=False,
                    has_other_people=False,
                ),
            ],
        ),
    )

    filtered = list_processed_images(
        workspace,
        filters=ImageListFilters(has_bride=True),
    )
    assert [img.path for img in filtered] == ["album-a/one.png"]


def test_list_images_blur_and_quality_filters(workspace: Path) -> None:
    sync_metadata_document(workspace)
    save_metadata_document(
        workspace,
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(
                    path="album-a/one.png",
                    caption="Sharp portrait",
                    quality_score=9.0,
                    is_blur=False,
                ),
                ImageMetadataEntry(
                    path="album-b/two.webp",
                    caption="Soft focus",
                    quality_score=4.0,
                    is_blur=True,
                ),
            ],
        ),
    )

    scope = {"album-a", "album-b"}
    sharp = list_processed_images(
        workspace,
        folders=scope,
        filters=ImageListFilters(is_blur=False),
    )
    assert {img.path for img in sharp} == {"album-a/one.png"}

    high_quality = list_processed_images(
        workspace,
        folders=scope,
        filters=ImageListFilters(min_quality_score=7.0),
    )
    assert {img.path for img in high_quality} == {"album-a/one.png"}


def test_api_serve_raw_image(workspace: Path) -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/raw/album-a/one.png")
    assert resp.status_code == 200
    assert resp.content == b"raw"
    assert "image/png" in resp.headers["content-type"]

    missing = client.get("/api/v1/raw/missing.png")
    assert missing.status_code == 404


def test_list_images_category_filters(workspace: Path) -> None:
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(
                    id="portraits",
                    description="Couple portraits",
                    images=["album-a/one.png"],
                ),
                ImageCategory(
                    id="groups",
                    description="Group shots",
                    images=["album-b/two.webp"],
                ),
            ],
        ),
    )

    portraits = list_processed_images(
        workspace,
        filters=ImageListFilters(category_ids=frozenset({"portraits"})),
    )
    assert [img.path for img in portraits] == ["album-a/one.png"]
    assert portraits[0].category_id == "portraits"

    either = list_processed_images(
        workspace,
        filters=ImageListFilters(category_ids=frozenset({"portraits", "groups"})),
    )
    assert {img.path for img in either} == {"album-a/one.png", "album-b/two.webp"}

    uncategorized = list_processed_images(
        workspace,
        filters=ImageListFilters(uncategorized=True),
    )
    assert [img.path for img in uncategorized] == ["root.jpg"]


def test_list_category_summaries(workspace: Path) -> None:
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(
                    id="portraits",
                    description="Couple portraits",
                    images=["album-a/one.png"],
                ),
            ],
        ),
    )

    summaries = list_category_summaries(workspace)
    assert len(summaries) == 1
    assert summaries[0].id == "portraits"
    assert summaries[0].image_count == 1

    scoped = list_category_summaries(workspace, folders={"album-a"})
    assert scoped[0].image_count == 1


def test_api_categories_and_category_filter(workspace: Path) -> None:
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(
                    id="portraits",
                    description="Couple portraits",
                    images=["album-a/one.png"],
                ),
            ],
        ),
    )
    client = TestClient(app)

    cat_resp = client.get("/api/v1/categories")
    assert cat_resp.status_code == 200
    payload = cat_resp.json()["categories"]
    assert payload[0]["id"] == "portraits"
    assert payload[0]["image_count"] == 1

    filtered = client.get(
        "/api/v1/images",
        params=[("folders", "album-a"), ("categories", "portraits")],
    )
    assert filtered.status_code == 200
    images = filtered.json()["images"]
    assert len(images) == 1
    assert images[0]["category_id"] == "portraits"


def test_delete_workspace_image(workspace: Path) -> None:
    save_metadata_document(
        workspace,
        ImageMetadataDocument(
            images=[
                ImageMetadataEntry(path="album-a/one.png", caption="Portrait"),
                ImageMetadataEntry(path="album-b/two.webp", caption="Group"),
            ],
        ),
    )
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(
                    id="portraits",
                    description="Portraits",
                    images=["album-a/one.png", "album-b/two.webp"],
                ),
            ],
        ),
    )

    result = delete_workspace_image(workspace, "album-a/one.png")
    assert result.deleted_raw is True
    assert result.deleted_processed is True
    assert result.removed_from_metadata is True
    assert result.removed_from_categories is True

    assert not (workspace / "raw" / "album-a" / "one.png").is_file()
    assert not (workspace / "processed_small" / "album-a" / "one.png").is_file()

    metadata = load_metadata_document(workspace)
    assert [entry.path for entry in metadata.images] == ["album-b/two.webp"]

    categories = load_categories_document(workspace)
    assert categories.categories[0].images == ["album-b/two.webp"]


def test_api_delete_image(workspace: Path) -> None:
    client = TestClient(app)
    resp = client.delete("/api/v1/images/album-a/one.png")
    assert resp.status_code == 200
    assert resp.json()["path"] == "album-a/one.png"
    assert resp.json()["deleted_raw"] is True

    missing = client.delete("/api/v1/images/does-not-exist.jpg")
    assert missing.status_code == 404


def test_api_serve_processed_image(workspace: Path) -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/media/album-a/one.png")
    assert resp.status_code == 200
    assert resp.content == b"thumb"
    assert "image/png" in resp.headers["content-type"]

    missing = client.get("/api/v1/media/missing.png")
    assert missing.status_code == 404
