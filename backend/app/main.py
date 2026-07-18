"""FastAPI entry point for BootCamp.AI."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.models.api import (
    MentorRecommendationRequest,
    MentorRecommendationResponse,
    ProfileExtractionRequest,
    ProfileExtractionResponse,
    RoadmapGenerationRequest,
    RoadmapGenerationResponse,
)
from src.config import MENTORS_PATH
from src.models.mentor import Mentor
from src.repositories.mentor_repository import (
    create_mentor,
    delete_mentor,
    load_mentors,
    update_mentor,
)
from src.repositories.resource_repository import load_resources
from src.services.mentor_service import rank_mentors
from src.services.profile_service import extract_user_profile, get_follow_up_questions
from src.services.roadmap_service import generate_career_roadmap


app = FastAPI(
    title="BootCamp.AI API",
    version="0.1.0",
    description="Backend API for the BootCamp.AI MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):30\d{2}$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple service health response."""
    return {"status": "ok"}


@app.get("/demo-data/summary")
def demo_data_summary() -> dict[str, int]:
    """Return counts for the local verified demo datasets."""
    return {
        "mentors": len(load_mentors(MENTORS_PATH)),
        "resources": len(load_resources()),
    }


@app.post("/profiles/extract", response_model=ProfileExtractionResponse)
def extract_profile(request: ProfileExtractionRequest) -> ProfileExtractionResponse:
    """Convert natural-language user details into a validated profile model."""
    profile = extract_user_profile(request.details, request.existing_profile)
    return ProfileExtractionResponse(
        profile=profile,
        follow_up_questions=get_follow_up_questions(profile),
    )


@app.post("/mentors/recommend", response_model=MentorRecommendationResponse)
def recommend_mentors(
    request: MentorRecommendationRequest,
) -> MentorRecommendationResponse:
    """Return deterministic mentor recommendations for a profile."""
    return MentorRecommendationResponse(
        matches=rank_mentors(request.profile, load_mentors(MENTORS_PATH), limit=request.limit)
    )


@app.get("/mentors", response_model=list[Mentor])
def list_mentors() -> list[Mentor]:
    """Return all available mentors."""
    return load_mentors(MENTORS_PATH)


@app.post("/admin/mentors", response_model=Mentor, status_code=201)
def add_admin_mentor(mentor: Mentor) -> Mentor:
    """Create a mentor in the local demo dataset."""
    try:
        return create_mentor(mentor, MENTORS_PATH)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.put("/admin/mentors/{mentor_id}", response_model=Mentor)
def update_admin_mentor(mentor_id: str, mentor: Mentor) -> Mentor:
    """Update a mentor in the local demo dataset."""
    try:
        return update_mentor(mentor_id, mentor, MENTORS_PATH)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/admin/mentors/{mentor_id}", status_code=204)
def delete_admin_mentor(mentor_id: str) -> None:
    """Delete a mentor from the local demo dataset."""
    try:
        delete_mentor(mentor_id, MENTORS_PATH)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/roadmaps/generate", response_model=RoadmapGenerationResponse)
def generate_roadmap(
    request: RoadmapGenerationRequest,
) -> RoadmapGenerationResponse:
    """Generate a personalized career roadmap for a profile."""
    try:
        roadmap = generate_career_roadmap(request.profile)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI roadmap generation failed: {exc}",
        ) from exc
    return RoadmapGenerationResponse(roadmap=roadmap)
