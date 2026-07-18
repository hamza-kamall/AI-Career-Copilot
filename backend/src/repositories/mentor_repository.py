"""Repository for loading and updating verified mentor data."""

import json
from pathlib import Path

from src.config import MENTORS_PATH
from src.models.mentor import Mentor


def load_mentors(path: Path = MENTORS_PATH) -> list[Mentor]:
    """Load mentors from a JSON file and validate each record."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [Mentor.model_validate(item) for item in data]


def save_mentors(mentors: list[Mentor], path: Path = MENTORS_PATH) -> None:
    """Persist validated mentors to the JSON dataset."""
    serialized = [mentor.model_dump(mode="json") for mentor in mentors]
    with path.open("w", encoding="utf-8") as file:
        json.dump(serialized, file, indent=2)
        file.write("\n")


def create_mentor(mentor: Mentor, path: Path = MENTORS_PATH) -> Mentor:
    """Add a mentor, rejecting duplicate IDs."""
    mentors = load_mentors(path)
    if any(existing.id == mentor.id for existing in mentors):
        raise ValueError(f"Mentor with id '{mentor.id}' already exists.")
    mentors.append(mentor)
    save_mentors(mentors, path)
    return mentor


def update_mentor(mentor_id: str, mentor: Mentor, path: Path = MENTORS_PATH) -> Mentor:
    """Replace an existing mentor by ID."""
    if mentor.id != mentor_id:
        raise ValueError("Mentor ID in path and payload must match.")

    mentors = load_mentors(path)
    for index, existing in enumerate(mentors):
        if existing.id == mentor_id:
            mentors[index] = mentor
            save_mentors(mentors, path)
            return mentor
    raise LookupError(f"Mentor with id '{mentor_id}' was not found.")


def delete_mentor(mentor_id: str, path: Path = MENTORS_PATH) -> None:
    """Remove a mentor by ID."""
    mentors = load_mentors(path)
    remaining = [mentor for mentor in mentors if mentor.id != mentor_id]
    if len(remaining) == len(mentors):
        raise LookupError(f"Mentor with id '{mentor_id}' was not found.")
    save_mentors(remaining, path)
