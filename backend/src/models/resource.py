"""Learning resource models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ResourceType(StrEnum):
    """Supported resource types from the PRD."""

    COURSE = "Course"
    VIDEO = "Video"
    DOCUMENTATION = "Documentation"
    BOOK = "Book"
    TUTORIAL = "Tutorial"
    PRACTICE_PLATFORM = "Practice platform"
    PROJECT_GUIDE = "Project guide"
    COMMUNITY = "Community"


class LearningResource(BaseModel):
    """Verified learning resource available for roadmap generation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    skill: str
    level: str
    resource_type: ResourceType
    provider: str
    cost_type: str
    estimated_duration: str
    url: str
    description: str

