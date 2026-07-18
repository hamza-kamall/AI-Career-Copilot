"""API request and response models."""

from pydantic import BaseModel, ConfigDict, Field

from src.models.mentor import MentorMatch
from src.models.profile import UserProfile
from src.models.roadmap import CareerRoadmap


class ProfileExtractionRequest(BaseModel):
    """Request body for natural-language profile extraction."""

    model_config = ConfigDict(extra="forbid")

    details: str = Field(min_length=1, description="User career details in natural language")
    existing_profile: UserProfile | None = None


class ProfileExtractionResponse(BaseModel):
    """Validated profile extraction response for frontend clients."""

    model_config = ConfigDict(extra="forbid")

    profile: UserProfile
    follow_up_questions: list[str]


class MentorRecommendationRequest(BaseModel):
    """Request body for ranked mentor recommendations."""

    model_config = ConfigDict(extra="forbid")

    profile: UserProfile
    limit: int = Field(default=6, ge=1, le=12)


class MentorRecommendationResponse(BaseModel):
    """Ranked mentor recommendations for a profile."""

    model_config = ConfigDict(extra="forbid")

    matches: list[MentorMatch]


class RoadmapGenerationRequest(BaseModel):
    """Request body for personalized roadmap generation."""

    model_config = ConfigDict(extra="forbid")

    profile: UserProfile


class RoadmapGenerationResponse(BaseModel):
    """Generated career roadmap response."""

    model_config = ConfigDict(extra="forbid")

    roadmap: CareerRoadmap
