"""Application configuration helpers."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MENTORS_PATH = DATA_DIR / "mentors.json"
RESOURCES_PATH = DATA_DIR / "resources.json"

