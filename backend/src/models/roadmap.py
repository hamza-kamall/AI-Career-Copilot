"""Roadmap models for later roadmap-generation increments."""

from pydantic import BaseModel, ConfigDict, Field


class WeeklyTask(BaseModel):
    """A week of work inside a roadmap phase."""

    model_config = ConfigDict(extra="forbid")

    week: int = Field(gt=0)
    tasks: list[str]
    estimated_hours: int = Field(gt=0)


class RoadmapProject(BaseModel):
    """Portfolio project attached to a roadmap phase."""

    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    deliverables: list[str]


class RoadmapPhase(BaseModel):
    """A phase in the generated career roadmap."""

    model_config = ConfigDict(extra="forbid")

    phase_number: int = Field(gt=0)
    title: str
    duration_weeks: int = Field(gt=0)
    objective: str
    skills: list[str]
    weekly_tasks: list[WeeklyTask]
    project: RoadmapProject
    completion_criteria: list[str]
    resource_ids: list[str]


class CareerRoadmap(BaseModel):
    """Validated roadmap structure from the PRD."""

    model_config = ConfigDict(extra="forbid")

    roadmap_title: str
    career_goal: str
    duration_weeks: int = Field(gt=0)
    weekly_hours: int = Field(gt=0)
    assumptions: list[str]
    skill_gaps: list[str]
    phases: list[RoadmapPhase]
    final_outcome: str
    next_steps: list[str]

