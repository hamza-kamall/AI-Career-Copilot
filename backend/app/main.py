"""FastAPI entry point for AI Career Pilot."""

from fastapi import FastAPI

from src.models.api import ProfileExtractionRequest, ProfileExtractionResponse
from src.repositories.mentor_repository import load_mentors
from src.repositories.resource_repository import load_resources
from src.services.profile_service import extract_user_profile, get_follow_up_questions


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


@app.post("/profiles/extract", response_model=ProfileExtractionResponse)
def extract_profile(request: ProfileExtractionRequest) -> ProfileExtractionResponse:
    """Convert natural-language user details into a validated profile model."""
    profile = extract_user_profile(request.details)
    return ProfileExtractionResponse(
        profile=profile,
        follow_up_questions=get_follow_up_questions(profile),
    )
