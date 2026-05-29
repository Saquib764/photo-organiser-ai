"""Tests for photobook plan layout validation and repair."""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.photobook import PhotobookPagePlan, PhotobookPlanResult
from app.services.photobook_plan_validation import (
    PhotobookPageLayoutFix,
    PhotobookPlanLayoutFixResult,
    apply_layout_fixes,
    mark_plan_layout_errors,
    validate_and_fix_plan_layouts,
    validate_plan_layouts,
)


def test_validate_plan_layouts_flags_unknown() -> None:
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
            layout_id="not_a_real_layout",
            categories=["ceremony"],
        ),
    ]
    issues = validate_plan_layouts(pages)
    assert len(issues) == 1
    assert issues[0].page_index == 1
    assert issues[0].layout_id == "not_a_real_layout"


def test_mark_plan_layout_errors() -> None:
    pages = [
        PhotobookPagePlan(
            title="Bad",
            narrative="Oops",
            layout_id="fake_layout",
            categories=["ceremony"],
        ),
    ]
    issues = validate_plan_layouts(pages)
    marked = mark_plan_layout_errors(pages, issues)
    assert marked[0].layout_id_error == "Unknown layout_id: fake_layout"


def test_apply_layout_fixes() -> None:
    plan = PhotobookPlanResult(
        assistant_message="Plan",
        pages=[
            PhotobookPagePlan(
                title="Bad",
                narrative="Oops",
                layout_id="fake_layout",
                layout_id_error="Unknown layout_id: fake_layout",
                categories=["ceremony"],
            ),
        ],
    )
    fixes = PhotobookPlanLayoutFixResult(
        fixes=[PhotobookPageLayoutFix(page_index=0, layout_id="hero_pair")],
    )
    fixed = apply_layout_fixes(plan, fixes)
    assert fixed.pages[0].layout_id == "hero_pair"
    assert fixed.pages[0].layout_id_error is None
    assert validate_plan_layouts(fixed.pages) == []


@pytest.mark.asyncio
async def test_validate_and_fix_plan_layouts(tmp_path) -> None:
    plan = PhotobookPlanResult(
        assistant_message="Plan",
        pages=[
            PhotobookPagePlan(
                title="Bad",
                narrative="Oops",
                layout_id="fake_layout",
                categories=["ceremony"],
            ),
        ],
    )
    fix_result = PhotobookPlanLayoutFixResult(
        fixes=[PhotobookPageLayoutFix(page_index=0, layout_id="hero_pair")],
    )

    with patch(
        "app.services.photobook_plan_validation.fix_photobook_plan_layouts",
        new_callable=AsyncMock,
    ) as mock_fix:
        mock_fix.side_effect = lambda _root, current_plan, _issues: apply_layout_fixes(
            current_plan,
            fix_result,
        )
        result = await validate_and_fix_plan_layouts(tmp_path, plan)

    assert validate_plan_layouts(result.pages) == []
    assert result.pages[0].layout_id == "hero_pair"
    mock_fix.assert_awaited_once()
