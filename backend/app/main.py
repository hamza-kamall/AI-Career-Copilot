"""FastAPI entry point for AI Career Pilot."""

from fastapi import FastAPI

from src.repositories.mentor_repository import load_mentors
from src.repositories.resource_repository import load_resources


app = FastAPI(
    title="AI Career Pilot API",
    version="0.1.0",
    description="Backend API for the AI Career Pilot MVP.",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple service health response."""
    return {"status": "ok"}


@app.get("/demo-data/summary")
def demo_data_summary() -> dict[str, int]:
    """Return counts for the local verified demo datasets."""
    return {
        "mentors": len(load_mentors()),
        "resources": len(load_resources()),
    }

