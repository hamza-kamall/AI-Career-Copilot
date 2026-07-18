"""Repository for loading verified learning resources."""

import json
from pathlib import Path

from src.config import RESOURCES_PATH
from src.models.resource import LearningResource


def load_resources(path: Path = RESOURCES_PATH) -> list[LearningResource]:
    """Load resources from a JSON file and validate each record."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [LearningResource.model_validate(item) for item in data]

