"""REST endpoints for workspace person registry."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas.person import (
    PersonDeleteResponse,
    PersonListResponse,
    PersonSummary,
    PersonUpdateRequest,
)
from app.services.image_files import media_type_for_path
from app.services.person_store import (
    delete_person,
    load_person_document,
    person_by_id,
    persons_dir,
    save_person_document,
)

router = APIRouter(prefix=settings.api_v1_prefix, tags=["persons"])


def _thumbnail_url(person_id: str) -> str:
    return f"{settings.api_v1_prefix}/persons/{person_id}/thumbnail"


@router.get("/persons", response_model=PersonListResponse)
async def list_persons() -> PersonListResponse:
    document = load_person_document(settings.workspace_root)
    persons = [
        PersonSummary(
            id=person.id,
            name=person.name,
            description=person.description,
            thumbnail_url=_thumbnail_url(person.id),
            face_count=person.face_count,
            image_count=person.image_count,
        )
        for person in document.persons
    ]
    return PersonListResponse(persons=persons)


@router.patch("/persons/{person_id}", response_model=PersonSummary)
async def update_person(person_id: str, body: PersonUpdateRequest) -> PersonSummary:
    document = load_person_document(settings.workspace_root)
    people = person_by_id(document)
    person = people.get(person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    if body.name is not None:
        person.name = body.name.strip() or person.name
    if body.description is not None:
        person.description = body.description.strip()
    person.updated_at = datetime.now(UTC)
    save_person_document(settings.workspace_root, document)

    return PersonSummary(
        id=person.id,
        name=person.name,
        description=person.description,
        thumbnail_url=_thumbnail_url(person.id),
        face_count=person.face_count,
        image_count=person.image_count,
    )


@router.delete("/persons/{person_id}", response_model=PersonDeleteResponse)
async def remove_person(person_id: str) -> PersonDeleteResponse:
    try:
        removed_from_metadata = delete_person(settings.workspace_root, person_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Person not found") from exc

    return PersonDeleteResponse(id=person_id, removed_from_metadata=removed_from_metadata)


@router.get("/persons/{person_id}/thumbnail")
async def get_person_thumbnail(person_id: str) -> FileResponse:
    document = load_person_document(settings.workspace_root)
    person = person_by_id(document).get(person_id)
    if person is None or not person.thumbnail:
        raise HTTPException(status_code=404, detail="Person not found")

    path = (persons_dir(settings.workspace_root) / person.thumbnail).resolve()
    try:
        path.relative_to(persons_dir(settings.workspace_root).resolve())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Thumbnail not found") from exc

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(path, media_type=media_type_for_path(path))
