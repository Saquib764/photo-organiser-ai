"""Tests for photobook store, layouts, and API."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.schemas.image_categories import ImageCategoriesDocument, ImageCategory
from app.schemas.photobook import GalleryImageSummary, PhotobookPage, PhotobookPagePlan
from app.services.image_categoriser import save_categories_document
from app.services.photobook_gallery import (
    MAX_COMPOSE_GALLERY_SIZE,
    MIN_PAGE_EXTRA_IMAGES,
    ensure_compose_extra_images,
    filter_gallery_by_categories,
    gallery_for_compose,
    paths_for_categories,
)
from app.services.photobook_planner import build_image_catalog, require_image_catalog
from app.services.photobook_plan_validation import validate_plan_categories
from app.page_layouts import (
    get_layout,
    layout_catalog_for_prompt,
    list_layouts,
    validate_slots,
)
from app.services.photobook_store import (
    append_chat_message,
    apply_plan,
    clear_chat,
    default_document,
    ensure_photobook,
    load_photobook,
    merge_page_extra_images,
    remove_page,
    reset_photobook_session,
    save_photobook,
)


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(settings, "workspace_root", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_list_layouts_includes_core_and_wedding() -> None:
    layouts = list_layouts()
    assert len(layouts) == 33
    ids = {layout.id for layout in layouts}
    assert {
        "full_bleed_caption",
        "hero_pair",
        "hero_pair_note_left",
        "hero_pair_note_right",
        "hero_pair_caption",
        "quad_grid",
        "quad_grid_caption",
        "quad_grid_caption_left",
        "split_column_note_left",
        "split_column_note_right",
        "split_diptych_caption",
        "feature_strip",
        "feature_strip_caption",
        "feature_strip_note",
        "feature_strip_note_left",
        "feature_strip_note_left_bottom",
        "wedding_cover",
        "wedding_boho_cover",
        "wedding_story_left",
        "wedding_story_right",
        "wedding_quad_editorial",
        "wedding_photo_mosaic",
        "wedding_center_mosaic_8",
        "wedding_center_mosaic_6",
        "wedding_center_mosaic_4",
        "wedding_split_collage",
        "wedding_editorial_text",
        "wedding_full_bleed_badge",
        "wedding_text_collage",
        "wedding_back_cover",
        "wedding_back_cover_ornate",
        "wedding_back_cover_boho",
        "wedding_back_cover_bleed",
    } <= ids


def test_layout_catalog_for_prompt_includes_text_metadata() -> None:
    catalog = layout_catalog_for_prompt(include_slot_ids=True)
    by_id = {item["id"]: item for item in catalog}
    assert by_id["feature_strip"]["supports_text"] is False
    assert by_id["feature_strip"]["text_slot_count"] == 0
    assert by_id["quad_grid_caption"]["supports_text"] is True
    assert by_id["quad_grid_caption"]["text_slot_count"] == 1
    assert len(by_id["quad_grid_caption"]["text_slots"]) == 1
    assert by_id["feature_strip"]["text_slots"] == []


def test_full_bleed_caption_has_default_caption() -> None:
    from app.page_layouts import get_layout, merge_text_slots

    layout = get_layout("full_bleed_caption")
    assert layout is not None
    assert layout.text_slots[0].default_text == "THE WEDDING DAY"
    merged = merge_text_slots("full_bleed_caption", {})
    assert merged["caption"].text == "THE WEDDING DAY"


def test_validate_slots_full_bleed_caption() -> None:
    assert validate_slots("full_bleed_caption", {"hero": "a.jpg"}) == []
    assert validate_slots("full_bleed_caption", {}) == []
    errors = validate_slots("full_bleed_caption", {}, require_all=True)
    assert any("Missing slots" in e for e in errors)


def test_validate_slots_partial_mosaic() -> None:
    assert validate_slots("wedding_photo_mosaic", {"t1": "a.jpg"}) == []
    errors = validate_slots("wedding_photo_mosaic", {"t1": "a.jpg"}, require_all=True)
    assert any("Missing slots" in e for e in errors)


def test_validate_slots_unknown_layout() -> None:
    errors = validate_slots("unknown", {"hero": "a.jpg"})
    assert errors == ["Unknown layout_id: unknown"]


def test_get_layout() -> None:
    layout = get_layout("quad_grid")
    assert layout is not None
    assert len(layout.slots) == 4


def test_quad_grid_caption_has_three_image_slots() -> None:
    layout = get_layout("quad_grid_caption")
    assert layout is not None
    assert len(layout.slots) == 3
    assert len(layout.text_slots) == 1
    errors = validate_slots(
        "quad_grid_caption",
        {"tl": "a.jpg", "tr": "b.jpg", "bl": "c.jpg"},
        require_all=True,
    )
    assert errors == []


def test_default_document_has_one_page() -> None:
    doc = default_document()
    assert len(doc.pages) == 1
    assert doc.pages[0].title == "Page 1"


def test_ensure_and_save_photobook(workspace: Path) -> None:
    doc = ensure_photobook(workspace)
    assert len(doc.pages) >= 1
    path = workspace / "photobook.json"
    assert path.is_file()

    doc.title = "Test book"
    save_photobook(workspace, doc)
    loaded = load_photobook(workspace)
    assert loaded.title == "Test book"


def _gallery_entry(path: str, *, quality_score: float = 8.0, is_blur: bool = False) -> GalleryImageSummary:
    return GalleryImageSummary(path=path, folder="", quality_score=quality_score, is_blur=is_blur)


def test_ensure_compose_extra_images_fills_when_model_returns_empty() -> None:
    gallery = [_gallery_entry(f"wedding/img{i}.jpg", quality_score=float(i)) for i in range(8)]
    extras = ensure_compose_extra_images(
        gallery,
        slot_paths={"wedding/img0.jpg"},
        assigned_paths=set(),
        model_extras=[],
    )
    assert len(extras) == MIN_PAGE_EXTRA_IMAGES
    assert "wedding/img0.jpg" not in extras
    assert extras[0] == "wedding/img7.jpg"


def test_ensure_compose_extra_images_keeps_model_picks_and_tops_up() -> None:
    gallery = [_gallery_entry(f"wedding/img{i}.jpg", quality_score=float(i)) for i in range(6)]
    extras = ensure_compose_extra_images(
        gallery,
        slot_paths={"wedding/img0.jpg"},
        assigned_paths=set(),
        model_extras=["wedding/img1.jpg"],
    )
    assert extras[0] == "wedding/img1.jpg"
    assert len(extras) == MIN_PAGE_EXTRA_IMAGES


def test_ensure_compose_extra_images_never_empty_when_alternates_exist() -> None:
    gallery = [_gallery_entry("wedding/a.jpg"), _gallery_entry("wedding/b.jpg")]
    extras = ensure_compose_extra_images(
        gallery,
        slot_paths={"wedding/a.jpg"},
        assigned_paths=set(),
        model_extras=[],
        min_count=4,
    )
    assert extras == ["wedding/b.jpg"]


def test_merge_page_extra_images_preserves_existing_and_dedupes() -> None:
    page = default_document().pages[0]
    page.extra_images = ["keep.jpg", "shared.jpg"]
    page.slots = {"hero": "slot.jpg"}

    merged = merge_page_extra_images(page, page.extra_images, ["new.jpg", "shared.jpg", "slot.jpg"])

    assert merged == ["keep.jpg", "shared.jpg", "new.jpg"]


def test_merge_page_extra_images_drops_paths_assigned_to_slots() -> None:
    page = default_document().pages[0]
    page.slots = {"hero": "in-slot.jpg"}

    merged = merge_page_extra_images(page, ["in-slot.jpg", "spare.jpg"])

    assert merged == ["spare.jpg"]


def test_apply_plan_replaces_pages(workspace: Path) -> None:
    doc = default_document()
    apply_plan(
        doc,
            [
                PhotobookPagePlan(
                    title="Intro",
                    narrative="Welcome shots",
                    layout_id="wedding_cover",
                    categories=["cover"],
                ),
                PhotobookPagePlan(
                    title="Ceremony",
                    narrative="Main event",
                    layout_id="full_bleed_caption",
                    categories=["ceremony"],
                ),
            ],
        extra_images=["extra.jpg"],
    )
    assert len(doc.pages) == 2
    assert doc.pages[0].title == "Intro"
    assert doc.pages[0].categories == ["cover"]
    assert all(page.extra_images == [] for page in doc.pages)


def test_build_image_catalog_excludes_empty_categories(workspace: Path) -> None:
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(id="ceremony", description="Ceremony moments", images=["a.jpg"]),
                ImageCategory(id="empty", description="No photos", images=[]),
            ],
        ),
    )
    catalog = build_image_catalog(workspace)
    assert len(catalog) == 1
    assert catalog[0].id == "ceremony"
    assert catalog[0].description == "Ceremony moments"
    assert "images" not in catalog[0].model_dump()


def test_require_image_catalog_raises_when_empty(workspace: Path) -> None:
    with pytest.raises(RuntimeError, match="categorisation"):
        require_image_catalog(workspace)


def test_paths_for_categories_and_filter(workspace: Path) -> None:
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(
                    id="ceremony",
                    description="Ceremony",
                    images=["a.jpg", "b.jpg"],
                ),
                ImageCategory(id="reception", description="Reception", images=["c.jpg"]),
            ],
        ),
    )
    paths = paths_for_categories(workspace, ["ceremony", "missing"])
    assert paths == {"a.jpg", "b.jpg"}
    gallery = [
        GalleryImageSummary(path="a.jpg", folder=""),
        GalleryImageSummary(path="c.jpg", folder=""),
    ]
    filtered = filter_gallery_by_categories(gallery, paths)
    assert [entry.path for entry in filtered] == ["a.jpg"]


def test_gallery_for_compose_requires_categories(workspace: Path) -> None:
    page = PhotobookPage(id="p1", title="T", narrative="N", layout_id="hero_pair")
    with pytest.raises(RuntimeError, match="no categories"):
        gallery_for_compose(workspace, page, [])


def test_gallery_for_compose_samples_from_page_categories(workspace: Path) -> None:
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(
                    id="ceremony",
                    description="Ceremony",
                    images=[f"img-{index}.jpg" for index in range(200)],
                ),
                ImageCategory(
                    id="reception",
                    description="Reception",
                    images=[f"rec-{index}.jpg" for index in range(50)],
                ),
            ],
        ),
    )
    gallery = [
        GalleryImageSummary(path=f"img-{index}.jpg", folder="")
        for index in range(200)
    ] + [
        GalleryImageSummary(path=f"rec-{index}.jpg", folder="")
        for index in range(50)
    ]
    page = PhotobookPage(
        id="p1",
        title="T",
        narrative="N",
        layout_id="hero_pair",
        categories=["ceremony", "reception"],
    )
    sampled = gallery_for_compose(workspace, page, gallery)
    assert len(sampled) == MAX_COMPOSE_GALLERY_SIZE
    allowed = paths_for_categories(workspace, page.categories)
    assert all(entry.path in allowed for entry in sampled)


def test_gallery_for_compose_returns_all_when_under_cap(workspace: Path) -> None:
    save_categories_document(
        workspace,
        ImageCategoriesDocument(
            categories=[
                ImageCategory(
                    id="ceremony",
                    description="Ceremony",
                    images=["a.jpg", "b.jpg"],
                ),
            ],
        ),
    )
    gallery = [
        GalleryImageSummary(path="a.jpg", folder=""),
        GalleryImageSummary(path="b.jpg", folder=""),
        GalleryImageSummary(path="other.jpg", folder=""),
    ]
    page = PhotobookPage(
        id="p1",
        title="T",
        narrative="N",
        layout_id="hero_pair",
        categories=["ceremony"],
    )
    result = gallery_for_compose(workspace, page, gallery)
    assert [entry.path for entry in result] == ["a.jpg", "b.jpg"]


def test_validate_plan_categories() -> None:
    pages = [
        PhotobookPagePlan(
            title="Cover",
            narrative="Hero",
            layout_id="wedding_cover",
            categories=["cover"],
        ),
        PhotobookPagePlan(
            title="Bad",
            narrative="Oops",
            layout_id="hero_pair",
            categories=["unknown"],
        ),
    ]
    issues = validate_plan_categories(pages, {"cover", "ceremony"})
    assert len(issues) == 1
    assert issues[0].page_index == 1
    assert "unknown" in issues[0].error


def test_page_plan_categories_validation() -> None:
    with pytest.raises(ValueError):
        PhotobookPagePlan(
            title="Bad",
            narrative="Oops",
            layout_id="hero_pair",
            categories=[],
        )
    with pytest.raises(ValueError):
        PhotobookPagePlan(
            title="Bad",
            narrative="Oops",
            layout_id="hero_pair",
            categories=["a", "b", "c", "d"],
        )
    plan = PhotobookPagePlan(
        title="Ok",
        narrative="Fine",
        layout_id="hero_pair",
        categories=["ceremony", "ceremony", "reception"],
    )
    assert plan.categories == ["ceremony", "reception"]


def test_cannot_remove_last_page(workspace: Path) -> None:
    doc = default_document()
    page_id = doc.pages[0].id
    assert remove_page(doc, page_id) is False
    assert len(doc.pages) == 1


def test_get_photobook_api(workspace: Path) -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/photobook")
    assert resp.status_code == 200
    data = resp.json()
    assert "document" in data
    assert "layouts" in data
    assert len(data["layouts"]) == 33
    assert len(data["document"]["pages"]) >= 1


def test_get_photobook_normalizes_text_slots(workspace: Path) -> None:
    doc = load_photobook(workspace)
    page = doc.pages[0]
    page.layout_id = "full_bleed_caption"
    page.text_slots = {}
    save_photobook(workspace, doc)

    client = TestClient(app)
    resp = client.get("/api/v1/photobook")
    assert resp.status_code == 200

    page_data = resp.json()["document"]["pages"][0]
    assert page_data["layout_id"] == "full_bleed_caption"
    assert "caption" in page_data["text_slots"]
    assert page_data["text_slots"]["caption"]["text"] == "THE WEDDING DAY"
    assert page_data["text_slots"]["caption"]["font_family"]


def test_clear_chat_store(workspace: Path) -> None:
    doc = default_document()
    append_chat_message(doc, "user", "Hello")
    append_chat_message(doc, "assistant", "Hi there")
    assert len(doc.chat) == 2
    clear_chat(doc)
    assert doc.chat == []


def test_reset_photobook_session_store(workspace: Path) -> None:
    doc = load_photobook(workspace)
    append_chat_message(doc, "user", "Plan my book")
    doc.pages[0].narrative = "Cover story"
    doc.pages[0].layout_id = "cover-classic"
    doc.pages[0].slots = {"hero": "processed_small/a.jpg"}
    doc.pages[0].extra_images = ["processed_small/b.jpg"]
    save_photobook(workspace, doc)

    reset_photobook_session(doc)
    assert doc.chat == []
    assert all(page.extra_images == [] for page in doc.pages)
    assert len(doc.pages) == 1
    assert doc.pages[0].narrative == ""
    assert doc.pages[0].layout_id == ""
    assert doc.pages[0].slots == {}


def test_clear_chat_api(workspace: Path) -> None:
    doc = load_photobook(workspace)
    append_chat_message(doc, "user", "Plan my book")
    doc.pages[0].narrative = "Cover story"
    doc.pages[0].layout_id = "cover-classic"
    save_photobook(workspace, doc)

    client = TestClient(app)
    resp = client.delete("/api/v1/photobook/chat")
    assert resp.status_code == 200
    data = resp.json()["document"]
    assert data["chat"] == []
    assert all(page["extra_images"] == [] for page in data["pages"])
    assert len(data["pages"]) == 1
    assert data["pages"][0]["narrative"] == ""
    assert data["pages"][0]["layout_id"] == ""


def test_chat_requires_openai_key(workspace: Path) -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/photobook/chat",
        json={"message": "Plan my book"},
    )
    assert resp.status_code == 503


def test_add_page_api(workspace: Path) -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/photobook/pages",
        json={"title": "Reception", "narrative": "Party"},
    )
    assert resp.status_code == 200
    pages = resp.json()["document"]["pages"]
    assert any(p["title"] == "Reception" for p in pages)


def test_patch_page_background_color(workspace: Path) -> None:
    client = TestClient(app)
    page_id = client.get("/api/v1/photobook").json()["document"]["pages"][0]["id"]

    resp = client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={"background_color": "#aabbcc"},
    )
    assert resp.status_code == 200
    page = next(
        p for p in resp.json()["document"]["pages"] if p["id"] == page_id
    )
    assert page["background_color"] == "#aabbcc"


def test_patch_page_slot_offsets(workspace: Path) -> None:
    client = TestClient(app)
    page_id = client.get("/api/v1/photobook").json()["document"]["pages"][0]["id"]

    resp = client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={
            "slot_offsets": {
                "hero": {"x": 30.0, "y": 70.0},
            },
        },
    )
    assert resp.status_code == 200
    page = next(
        p for p in resp.json()["document"]["pages"] if p["id"] == page_id
    )
    assert page["slot_offsets"]["hero"] == {"x": 30.0, "y": 70.0}


def test_patch_layout_clears_slot_offsets(workspace: Path) -> None:
    client = TestClient(app)
    page_id = client.get("/api/v1/photobook").json()["document"]["pages"][0]["id"]

    client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={"layout_id": "full_bleed_caption", "slot_offsets": {"hero": {"x": 10, "y": 20}}},
    )
    resp = client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={"layout_id": "hero_pair"},
    )
    assert resp.status_code == 200
    page = next(
        p for p in resp.json()["document"]["pages"] if p["id"] == page_id
    )
    assert page["slot_offsets"] == {}


def test_patch_page_image_border_radius(workspace: Path) -> None:
    client = TestClient(app)
    page_id = client.get("/api/v1/photobook").json()["document"]["pages"][0]["id"]

    resp = client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={"image_border_radius": 12},
    )
    assert resp.status_code == 200
    page = next(
        p for p in resp.json()["document"]["pages"] if p["id"] == page_id
    )
    assert page["image_border_radius"] == 12


def test_get_photobook_syncs_missing_palette(workspace: Path) -> None:
    from PIL import Image

    from app.services.workspace import PROCESSED_DIR_NAME
    from app.services.photobook_store import load_photobook, save_photobook

    client = TestClient(app)
    page_id = client.get("/api/v1/photobook").json()["document"]["pages"][0]["id"]

    rel = "test-bg.jpg"
    processed_dir = workspace / PROCESSED_DIR_NAME
    processed_dir.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (16, 16), (40, 120, 200)).save(processed_dir / "test-bg.jpg")

    client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={"layout_id": "full_bleed_caption", "slots": {"hero": rel}},
    )

    doc = load_photobook(workspace)
    page = next(p for p in doc.pages if p.id == page_id)
    page.palette_colors = []
    page.background_color = None
    save_photobook(workspace, doc)

    resp = client.get("/api/v1/photobook")
    page = next(p for p in resp.json()["document"]["pages"] if p["id"] == page_id)
    assert len(page["palette_colors"]) >= 1
    assert page["background_color"] == page["palette_colors"][0]


def test_patch_slots_clears_background_color(workspace: Path) -> None:
    client = TestClient(app)
    page_id = client.get("/api/v1/photobook").json()["document"]["pages"][0]["id"]

    client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={"background_color": "#112233"},
    )
    resp = client.patch(
        f"/api/v1/photobook/pages/{page_id}",
        json={
            "layout_id": "full_bleed_caption",
            "slots": {"hero": "photos/test.jpg"},
        },
    )
    assert resp.status_code == 200
    page = next(
        p for p in resp.json()["document"]["pages"] if p["id"] == page_id
    )
    assert page["background_color"] is None
