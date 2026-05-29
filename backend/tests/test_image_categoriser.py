"""Unit tests for image categorisation helpers."""

import random
from pathlib import Path

import pytest

from app.schemas.image_categories import (
    CategoriserBatchResult,
    CategoryBatchAssignment,
    ImageCategoriesDocument,
    ImageCategory,
)
from app.schemas.image_metadata import ImageMetadataDocument, ImageMetadataEntry
from app.services.image_categoriser import (
    build_categorisation_gallery,
    categorisation_counts,
    consolidate_categories,
    dedupe_paths_across_categories,
    is_categorisation_complete,
    merge_assignments,
    prune_invalid_paths,
    remaining_paths,
    sample_batch,
)


def test_remaining_paths_recomputed_after_merge() -> None:
    gallery = {"a.jpg", "b.jpg", "c.jpg"}
    doc = ImageCategoriesDocument(
        categories=[ImageCategory(id="ceremony", description="Ceremony", images=["a.jpg"])],
    )
    assert remaining_paths(gallery, doc) == {"b.jpg", "c.jpg"}


def test_sample_batch_random_subset() -> None:
    remaining = {f"img{i}.jpg" for i in range(10)}
    rng = random.Random(42)
    batch = sample_batch(remaining, 4, rng)
    assert len(batch) == 4
    assert set(batch).issubset(remaining)


def test_prune_invalid_paths_removes_stale_entries() -> None:
    gallery = {"valid.jpg"}
    doc = ImageCategoriesDocument(
        categories=[
            ImageCategory(
                id="group",
                description="Test",
                images=["valid.jpg", "missing.jpg"],
            ),
        ],
    )
    removed = prune_invalid_paths(doc, gallery)
    assert removed == 1
    assert doc.categories[0].images == ["valid.jpg"]


def test_merge_assignments_existing_and_new() -> None:
    doc = ImageCategoriesDocument(
        categories=[
            ImageCategory(id="ceremony", description="Ceremony wide shots", images=[]),
        ],
    )
    result = CategoriserBatchResult(
        assignments=[
            CategoryBatchAssignment(id="ceremony", images=["a.jpg"]),
            CategoryBatchAssignment(
                id="portraits",
                description="Couple portraits outdoors",
                images=["b.jpg"],
            ),
        ],
    )
    assigned = merge_assignments(
        doc,
        result,
        allowed_paths={"a.jpg", "b.jpg"},
    )
    assert assigned == {"a.jpg", "b.jpg"}
    assert len(doc.categories) == 2
    assert doc.categories[0].images == ["a.jpg"]
    assert doc.categories[1].id == "portraits"


def test_merge_assignments_rejects_paths_outside_batch() -> None:
    doc = ImageCategoriesDocument()
    result = CategoriserBatchResult(
        assignments=[
            CategoryBatchAssignment(
                id="misc",
                description="Miscellaneous",
                images=["outside.jpg"],
            ),
        ],
    )
    assigned = merge_assignments(doc, result, allowed_paths={"inside.jpg"})
    assert assigned == set()
    assert doc.categories == []


def test_dedupe_paths_across_categories() -> None:
    doc = ImageCategoriesDocument(
        categories=[
            ImageCategory(id="a", description="A", images=["x.jpg", "y.jpg"]),
            ImageCategory(id="b", description="B", images=["x.jpg"]),
        ],
    )
    dedupe_paths_across_categories(doc)
    assert doc.categories[0].images == ["x.jpg", "y.jpg"]
    assert doc.categories[1].images == []


def test_consolidate_merges_small_category_into_similar() -> None:
    doc = ImageCategoriesDocument(
        categories=[
            ImageCategory(
                id="ceremony_wide",
                description="Ceremony wide shots of aisle and guests",
                images=["a.jpg", "b.jpg", "c.jpg", "d.jpg"],
            ),
            ImageCategory(
                id="ceremony_establishing",
                description="Ceremony wide shots of aisle and guest reactions",
                images=["e.jpg"],
            ),
        ],
    )
    consolidate_categories(doc, min_images_to_keep=3)
    assert len(doc.categories) == 1
    assert set(doc.categories[0].images) == {"a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg"}


def test_is_categorisation_complete_when_all_assigned() -> None:
    gallery = {"a.jpg", "b.jpg"}
    doc = ImageCategoriesDocument(
        categories=[ImageCategory(id="all", description="All", images=["a.jpg", "b.jpg"])],
    )
    assert is_categorisation_complete(gallery, doc)


def test_build_categorisation_gallery_requires_captions(
    tmp_path: Path,
) -> None:
    processed = tmp_path / "processed_small"
    processed.mkdir()
    (processed / "done.jpg").write_bytes(b"x")
    (processed / "pending.jpg").write_bytes(b"x")

    metadata = ImageMetadataDocument(
        images=[
            ImageMetadataEntry(path="done.jpg", caption="Ready"),
            ImageMetadataEntry(path="pending.jpg", caption=""),
        ],
    )
    gallery = build_categorisation_gallery(tmp_path, metadata)
    assert gallery == {"done.jpg"}


def test_categorisation_counts() -> None:
    gallery = {"a.jpg", "b.jpg", "c.jpg"}
    doc = ImageCategoriesDocument(
        categories=[ImageCategory(id="x", description="X", images=["a.jpg"])],
    )
    completed, total = categorisation_counts(gallery, doc)
    assert completed == 1
    assert total == 3


@pytest.mark.asyncio
async def test_handle_start_categorisation_requires_analysis(tmp_path: Path) -> None:
    from unittest.mock import patch

    from app.services.pipeline_runner import handle_start_categorisation

    raw = tmp_path / "raw"
    raw.mkdir()
    (tmp_path / "processed_small").mkdir()

    with patch("app.services.pipeline_runner.asyncio.create_task") as create_task:
        await handle_start_categorisation(tmp_path)

    create_task.assert_not_called()
