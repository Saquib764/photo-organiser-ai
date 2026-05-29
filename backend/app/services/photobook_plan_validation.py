"""Validate and repair layout templates on photobook planner output."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import yaml
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import settings
from app.page_layouts import get_layout, layout_catalog_for_prompt, list_layouts
from app.prompts.prompts import PHOTOBOOK_PLAN_LAYOUT_FIX_SYSTEM_PROMPT
from app.schemas.photobook import PhotobookPagePlan, PhotobookPlanResult
from app.services.photobook_openai import require_openai_api_key

logger = logging.getLogger(__name__)

MAX_LAYOUT_FIX_ATTEMPTS = 2


@dataclass(frozen=True)
class PlanCategoryIssue:
    page_index: int
    title: str
    categories: list[str]
    error: str


@dataclass(frozen=True)
class PlanLayoutIssue:
    page_index: int
    title: str
    layout_id: str
    error: str


class PhotobookPageLayoutFix(BaseModel):
    page_index: int = Field(ge=0, description="0-based index in the plan pages list")
    layout_id: str = Field(description="Valid layout_id from the catalog")


class PhotobookPlanLayoutFixResult(BaseModel):
    fixes: list[PhotobookPageLayoutFix] = Field(default_factory=list)


def validate_plan_layouts(pages: list[PhotobookPagePlan]) -> list[PlanLayoutIssue]:
    issues: list[PlanLayoutIssue] = []
    for index, page in enumerate(pages):
        layout_id = page.layout_id.strip()
        if not layout_id:
            issues.append(
                PlanLayoutIssue(
                    page_index=index,
                    title=page.title,
                    layout_id=page.layout_id,
                    error="layout_id is required",
                ),
            )
            continue
        if get_layout(layout_id) is None:
            issues.append(
                PlanLayoutIssue(
                    page_index=index,
                    title=page.title,
                    layout_id=layout_id,
                    error=f"Unknown layout_id: {layout_id}",
                ),
            )
    return issues


def validate_plan_categories(
    pages: list[PhotobookPagePlan],
    valid_category_ids: set[str],
) -> list[PlanCategoryIssue]:
    issues: list[PlanCategoryIssue] = []
    for index, page in enumerate(pages):
        if not page.categories:
            issues.append(
                PlanCategoryIssue(
                    page_index=index,
                    title=page.title,
                    categories=page.categories,
                    error="At least one category is required",
                ),
            )
            continue
        if len(page.categories) > 3:
            issues.append(
                PlanCategoryIssue(
                    page_index=index,
                    title=page.title,
                    categories=page.categories,
                    error="At most 3 categories allowed",
                ),
            )
            continue
        unknown = [cat_id for cat_id in page.categories if cat_id not in valid_category_ids]
        if unknown:
            issues.append(
                PlanCategoryIssue(
                    page_index=index,
                    title=page.title,
                    categories=page.categories,
                    error=f"Unknown category id(s): {', '.join(unknown)}",
                ),
            )
    return issues


def mark_plan_layout_errors(
    pages: list[PhotobookPagePlan],
    issues: list[PlanLayoutIssue],
) -> list[PhotobookPagePlan]:
    errors_by_index = {issue.page_index: issue.error for issue in issues}
    marked: list[PhotobookPagePlan] = []
    for index, page in enumerate(pages):
        error = errors_by_index.get(index)
        if error:
            marked.append(page.model_copy(update={"layout_id_error": error}))
        elif page.layout_id_error:
            marked.append(page.model_copy(update={"layout_id_error": None}))
        else:
            marked.append(page)
    return marked


def apply_layout_fixes(
    plan: PhotobookPlanResult,
    fixes: PhotobookPlanLayoutFixResult,
) -> PhotobookPlanResult:
    valid_ids = {layout.id for layout in list_layouts()}
    pages = list(plan.pages)
    for fix in fixes.fixes:
        if fix.page_index < 0 or fix.page_index >= len(pages):
            continue
        layout_id = fix.layout_id.strip()
        if layout_id not in valid_ids:
            continue
        page = pages[fix.page_index]
        pages[fix.page_index] = page.model_copy(
            update={"layout_id": layout_id, "layout_id_error": None},
        )
    return plan.model_copy(update={"pages": pages})


def _yaml_dump(data: object) -> str:
    return yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)


def _build_layout_fix_user_message(
    plan: PhotobookPlanResult,
    issues: list[PlanLayoutIssue],
) -> str:
    invalid_pages = [
        {
            "page_index": issue.page_index,
            "title": issue.title,
            "invalid_layout_id": issue.layout_id,
            "error": issue.error,
            "narrative": plan.pages[issue.page_index].narrative,
        }
        for issue in issues
    ]
    sections = [
        "## Invalid pages\n\n"
        "These pages use layout templates that are not in the catalog. "
        "Return a fix for each listed page_index.\n\n"
        f"{_yaml_dump(invalid_pages)}",
        "## Full photobook plan\n\n"
        f"{_yaml_dump([p.model_dump() for p in plan.pages])}",
        "## Layout template catalog\n\n"
        f"{_yaml_dump(layout_catalog_for_prompt(include_slot_ids=True))}",
    ]
    return "\n".join(sections)


async def fix_photobook_plan_layouts(
    workspace_root: Path,
    plan: PhotobookPlanResult,
    issues: list[PlanLayoutIssue],
) -> PhotobookPlanResult:
    api_key = require_openai_api_key(workspace_root)
    client = AsyncOpenAI(api_key=api_key)
    user_content = _build_layout_fix_user_message(plan, issues)

    completion = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": PHOTOBOOK_PLAN_LAYOUT_FIX_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format=PhotobookPlanLayoutFixResult,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        msg = "OpenAI returned no structured layout fix output"
        raise RuntimeError(msg)

    logger.info("Layout fix: %d corrections", len(parsed.fixes))
    return apply_layout_fixes(plan, parsed)


async def validate_and_fix_plan_layouts(
    workspace_root: Path,
    plan: PhotobookPlanResult,
) -> PhotobookPlanResult:
    issues = validate_plan_layouts(plan.pages)
    if not issues:
        return plan

    pages = mark_plan_layout_errors(plan.pages, issues)
    plan = plan.model_copy(update={"pages": pages})

    for attempt in range(MAX_LAYOUT_FIX_ATTEMPTS):
        logger.warning(
            "Photobook plan has %d invalid layout(s); fix attempt %d",
            len(issues),
            attempt + 1,
        )
        plan = await fix_photobook_plan_layouts(workspace_root, plan, issues)
        issues = validate_plan_layouts(plan.pages)
        if not issues:
            return plan
        plan = plan.model_copy(
            update={"pages": mark_plan_layout_errors(plan.pages, issues)},
        )

    if issues:
        logger.error(
            "Photobook plan still has invalid layouts after %d fix attempts: %s",
            MAX_LAYOUT_FIX_ATTEMPTS,
            json.dumps([issue.layout_id for issue in issues]),
        )
    return plan
