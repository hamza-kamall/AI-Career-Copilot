from src.models.profile import ExperienceLevel, UserProfile
from src.models.roadmap import CareerRoadmap, RoadmapPhase, RoadmapProject, WeeklyTask
from src.services import roadmap_service
from src.services.roadmap_service import _align_roadmap_with_profile, _roadmap_prompt


def test_roadmap_prompt_includes_whole_profile_and_time_constraints() -> None:
    profile = UserProfile(
        current_situation="Second-year engineering student in Karachi",
        primary_goal="Get an AI internship",
        target_role="AI engineer",
        current_skills=["Python", "HTML"],
        experience_level=ExperienceLevel.INTERMEDIATE,
        deadline_months=6,
        hours_per_week=10,
        learning_preferences=["project"],
        constraints=["Limited budget"],
    )

    prompt = _roadmap_prompt(profile, resources=[])

    assert "Do not return a generic template" in prompt
    assert "duration_weeks must be deadline_months * 4" in prompt
    assert "weekly_hours must match it exactly" in prompt
    assert "Second-year engineering student in Karachi" in prompt
    assert "Get an AI internship" in prompt
    assert "Python" in prompt
    assert "Limited budget" in prompt


def test_ai_roadmap_alignment_preserves_explicit_user_timing() -> None:
    profile = UserProfile(
        primary_goal="Become a frontend developer",
        target_role="Frontend developer",
        deadline_months=3,
        hours_per_week=7,
    )
    roadmap = CareerRoadmap(
        roadmap_title="Frontend Roadmap",
        career_goal="Become a frontend developer",
        duration_weeks=20,
        weekly_hours=12,
        assumptions=[],
        skill_gaps=["React"],
        phases=[
            RoadmapPhase(
                phase_number=1,
                title="React Foundations",
                duration_weeks=12,
                objective="Learn React through project work.",
                skills=["React"],
                weekly_tasks=[
                    WeeklyTask(
                        week=1,
                        tasks=["Build a component library"],
                        estimated_hours=7,
                    )
                ],
                project=RoadmapProject(
                    title="Portfolio UI",
                    description="Create a portfolio interface.",
                    deliverables=["Published page"],
                ),
                completion_criteria=["Portfolio page complete"],
                resource_ids=[],
            )
        ],
        final_outcome="Portfolio-ready frontend profile",
        next_steps=["Ask a frontend mentor for code review"],
    )

    aligned = _align_roadmap_with_profile(roadmap, profile)

    assert aligned.duration_weeks == 12
    assert aligned.weekly_hours == 7


def test_roadmap_generation_falls_back_when_llm_fails(monkeypatch) -> None:
    profile = UserProfile(
        primary_goal="Become a data analyst",
        target_role="Data analyst",
        current_skills=["Excel"],
        deadline_months=2,
        hours_per_week=6,
    )

    monkeypatch.setattr(roadmap_service, "is_gemini_enabled", lambda: True)

    def fail_generation(*_args, **_kwargs):
        raise OSError("socket access denied")

    monkeypatch.setattr(roadmap_service, "generate_structured", fail_generation)

    roadmap = roadmap_service.generate_career_roadmap(profile)

    assert roadmap.roadmap_title == "Data analyst Roadmap"
    assert roadmap.duration_weeks == 8
    assert roadmap.weekly_hours == 6
    assert roadmap.phases


def test_fallback_roadmap_tasks_are_profile_specific(monkeypatch) -> None:
    monkeypatch.setattr(roadmap_service, "is_gemini_enabled", lambda: False)

    ai_profile = UserProfile(
        current_situation="Second-year engineering student in Karachi",
        primary_goal="Get an AI internship",
        target_role="AI engineer",
        current_skills=["Python"],
        deadline_months=3,
        hours_per_week=8,
        learning_preferences=["project"],
        constraints=["Limited budget"],
    )
    ux_profile = UserProfile(
        current_situation="Freelance graphic designer",
        primary_goal="Move into product design",
        target_role="UI/UX designer",
        current_skills=["Figma"],
        deadline_months=3,
        hours_per_week=8,
        learning_preferences=["visual"],
        location="Lahore",
    )

    ai_roadmap = roadmap_service.generate_career_roadmap(ai_profile)
    ux_roadmap = roadmap_service.generate_career_roadmap(ux_profile)

    ai_tasks = ai_roadmap.phases[0].weekly_tasks[0].tasks
    ux_tasks = ux_roadmap.phases[0].weekly_tasks[0].tasks

    assert ai_tasks != ux_tasks
    assert any("AI engineer" in task for task in ai_tasks)
    assert any("UI/UX designer" in task for task in ux_tasks)
