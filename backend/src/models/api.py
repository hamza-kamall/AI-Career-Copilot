"""API request and response models."""

from pydantic import BaseModel, ConfigDict, Field

from src.models.profile import UserProfile


class ProfileExtractionRequest(BaseModel):
    """Request body for natural-language profile extraction."""

    model_config = ConfigDict(extra="forbid")

    details: str = Field(min_length=1, description="User career details in natural language")


class ProfileExtractionResponse(BaseModel):
    """Validated profile extraction response for frontend clients."""

    model_config = ConfigDict(extra="forbid")

    profile: UserProfile
    follow_up_questions: list[str]
