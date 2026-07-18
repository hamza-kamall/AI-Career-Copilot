"""Repository for loading verified mentor data."""

import json
from pathlib import Path

from src.config import MENTORS_PATH
from src.models.mentor import Mentor


def load_mentors(path: Path = MENTORS_PATH) -> list[Mentor]:
    """Load mentors from a JSON file and validate each record."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [Mentor.model_validate(item) for item in data]

