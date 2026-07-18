"""User career profile models."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ExperienceLevel(StrEnum):
    """Supported learner experience levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class BudgetPreference(StrEnum):
    """Supported budget preferences from the PRD."""

    FREE = "free"
    LOW_COST = "low-cost"
    FLEXIBLE = "flexible"
    UNSPECIFIED = "unspecified"


class UserProfile(BaseModel):
    """Structured profile extracted from natural-language intake."""

    model_config = ConfigDict(extra="forbid")

    current_situation: str = ""
    primary_goal: str = ""
    target_role: str | None = None
    current_skills: list[str] = Field(default_factory=list)
    experience_level: ExperienceLevel | None = None
    deadline_months: Annotated[int | None, Field(gt=0)] = None
    hours_per_week: Annotated[int | None, Field(gt=0)] = None
    budget_preference: BudgetPreference | None = None
    learning_preferences: list[str] = Field(default_factory=list)
    location: str | None = None
    languages: list[str] = Field(default_factory=list)
    mentor_preferences: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)

