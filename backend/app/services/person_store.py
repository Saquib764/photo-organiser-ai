"""Load, save, and manage workspace person registry."""

from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.person import PersonDocument, PersonEntry

logger = logging.getLogger(__name__)

PERSONS_DIR_NAME = "persons"
PERSONS_FILENAME = "persons.json"


def persons_dir(workspace_root: Path) -> Path:
    return workspace_root / PERSONS_DIR_NAME


def persons_file_path(workspace_root: Path) -> Path:
    return workspace_root / PERSONS_FILENAME


def ensure_persons_dir(workspace_root: Path) -> Path:
    path = persons_dir(workspace_root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_person_document(workspace_root: Path) -> PersonDocument:
    path = persons_file_path(workspace_root)
    if not path.is_file():
        return PersonDocument()

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return PersonDocument.model_validate(raw)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Invalid persons file at %s, resetting", path)
        return PersonDocument()


def save_person_document(workspace_root: Path, document: PersonDocument) -> None:
    path = persons_file_path(workspace_root)
    document.updated_at = datetime.now(UTC)
    path.write_text(document.model_dump_json(indent=2), encoding="utf-8")


def clear_person_data(workspace_root: Path) -> None:
    """Remove persons.json and all files under persons/."""
    path = persons_file_path(workspace_root)
    if path.is_file():
        path.unlink()

    directory = persons_dir(workspace_root)
    if directory.is_dir():
        shutil.rmtree(directory)
    ensure_persons_dir(workspace_root)


def person_by_id(document: PersonDocument) -> dict[str, PersonEntry]:
    return {person.id: person for person in document.persons}


def next_person_id(document: PersonDocument) -> str:
    existing = {person.id for person in document.persons}
    index = 1
    while True:
        candidate = f"person-{index:03d}"
        if candidate not in existing:
            return candidate
        index += 1


def default_person_name(index: int) -> str:
    return f"Person {index}"


def delete_person(workspace_root: Path, person_id: str) -> int:
    """
    Remove a person from persons.json, delete their thumbnail, and strip person_ids from metadata.

    Returns the number of image metadata entries updated.
    Raises LookupError when the person does not exist.
    """
    document = load_person_document(workspace_root)
    person = person_by_id(document).get(person_id)
    if person is None:
        raise LookupError(person_id)

    thumbnail = persons_dir(workspace_root) / person.thumbnail
    if thumbnail.is_file():
        thumbnail.unlink()

    document.persons = [entry for entry in document.persons if entry.id != person_id]
    save_person_document(workspace_root, document)

    from app.services.image_metadata import load_metadata_document, save_metadata_document

    metadata = load_metadata_document(workspace_root)
    updated = 0
    for entry in metadata.images:
        if person_id not in entry.person_ids:
            continue
        entry.person_ids = [pid for pid in entry.person_ids if pid != person_id]
        updated += 1
    if updated:
        save_metadata_document(workspace_root, metadata)

    logger.info("Deleted person %s (%d metadata entries updated)", person_id, updated)
    return updated
