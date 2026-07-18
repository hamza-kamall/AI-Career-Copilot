from src.models.profile import BudgetPreference, ExperienceLevel, UserProfile
from src.repositories.mentor_repository import load_mentors
from src.services.mentor_service import calculate_mentor_match, rank_mentors


def test_rank_mentors_prioritizes_ai_student_match() -> None:
    profile = UserProfile(
        current_situation="Second-year computer systems engineering student",
        primary_goal="Get an AI internship",
        target_role="AI engineer",
        current_skills=["Python", "basic machine learning"],
        experience_level=ExperienceLevel.INTERMEDIATE,
        deadline_months=6,
        hours_per_week=14,
        budget_preference=BudgetPreference.FREE,
        languages=["English", "Urdu"],
        mentor_preferences=["student-friendly", "project-based"],
    )

    matches = rank_mentors(profile, load_mentors(), limit=3)

    assert [match.mentor.id for match in matches] == [
        "mentor-ai-001",
        "mentor-product-001",
        "mentor-research-001",
    ]
    assert matches[0].score > matches[1].score
    assert matches[0].component_scores["expertise"] == 100


def test_frontend_profile_ranks_frontend_mentor_first() -> None:
    profile = UserProfile(
        current_situation="Student learning web basics",
        primary_goal="Become a frontend developer",
        target_role="Frontend developer",
        current_skills=["HTML", "CSS"],
        experience_level=ExperienceLevel.BEGINNER,
        hours_per_week=8,
        budget_preference=BudgetPreference.FLEXIBLE,
        languages=["English"],
    )

    matches = rank_mentors(profile, load_mentors(), limit=1)

    assert matches[0].mentor.id == "mentor-web-001"
    assert matches[0].score >= 80


def test_budget_preference_affects_score_without_overriding_expertise() -> None:
    free_profile = UserProfile(
        current_situation="Engineering student",
        primary_goal="Learn academic research for AI",
        target_role="AI research assistant",
        current_skills=["Python", "machine learning"],
        experience_level=ExperienceLevel.INTERMEDIATE,
        hours_per_week=8,
        budget_preference=BudgetPreference.FREE,
        languages=["English"],
    )
    flexible_profile = free_profile.model_copy(
        update={"budget_preference": BudgetPreference.FLEXIBLE}
    )
    research_mentor = next(
        mentor for mentor in load_mentors() if mentor.id == "mentor-research-001"
    )

    free_score = calculate_mentor_match(free_profile, research_mentor)
    flexible_score = calculate_mentor_match(flexible_profile, research_mentor)

    assert flexible_score > free_score
    assert flexible_score - free_score <= 5


def test_rank_mentors_is_deterministic() -> None:
    profile = UserProfile(
        current_situation="Accountant moving into analytics",
        primary_goal="Move into data analytics",
        target_role="Data analyst",
        current_skills=["Excel"],
        experience_level=ExperienceLevel.BEGINNER,
        deadline_months=9,
        hours_per_week=8,
        budget_preference=BudgetPreference.LOW_COST,
        languages=["English", "Urdu"],
    )

    first_run = rank_mentors(profile, load_mentors(), limit=5)
    second_run = rank_mentors(profile, load_mentors(), limit=5)

    assert [match.mentor.id for match in first_run] == [
        match.mentor.id for match in second_run
    ]
    assert first_run[0].mentor.id == "mentor-data-001"
