"""Mentor data models."""

from pydantic import BaseModel, ConfigDict, Field


class Mentor(BaseModel):
    """Verified mentor profile used by deterministic matching."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    job_title: str
    bio: str
    expertise: list[str]
    industries: list[str]
    years_experience: int = Field(ge=0)
    supported_levels: list[str]
    languages: list[str]
    available_hours: list[str]
    price_category: str
    mentoring_style: list[str]
    profile_image: str | None = None


class MentorMatch(BaseModel):
    """Ranked mentor result with score breakdown."""

    mentor: Mentor
    score: float = Field(ge=0, le=100)
    component_scores: dict[str, float]
    explanation: str

