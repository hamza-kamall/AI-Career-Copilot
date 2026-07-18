"""JSON utility helpers."""

import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    """Read JSON from disk."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

