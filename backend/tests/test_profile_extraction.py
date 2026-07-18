from fastapi.testclient import TestClient

from app.main import app
from src.models.profile import BudgetPreference, ExperienceLevel
from src.services.profile_service import extract_user_profile


client = TestClient(app)


def test_extract_user_profile_from_complete_student_details() -> None:
    profile = extract_user_profile(
        "I am a second-year engineering student. I know Python and basic "
        "machine learning. I want an AI internship within six months. I can "
        "study fourteen hours weekly and only want free resources. I speak "
        "English and Urdu and prefer a student-friendly project-based mentor."
    )

    assert profile.current_situation == "I am a second-year engineering student"
    assert profile.primary_goal.startswith("an AI internship")
    assert profile.target_role == "AI engineer"
    assert profile.current_skills == ["Python", "machine learning", "basic machine learning"]
    assert profile.experience_level == ExperienceLevel.INTERMEDIATE
    assert profile.deadline_months == 6
    assert profile.hours_per_week == 14
    assert profile.budget_preference == BudgetPreference.FREE
    assert profile.languages == ["English", "Urdu"]
    assert profile.missing_information == []


def test_extract_user_profile_records_missing_critical_fields() -> None:
    profile = extract_user_profile("I want to become a frontend developer. I know HTML and CSS.")

    assert profile.target_role == "Frontend developer"
    assert profile.current_skills == ["HTML", "CSS"]
    assert profile.missing_information == ["hours_per_week", "deadline_months"]


def test_profiles_extract_endpoint_returns_pydantic_profile_shape() -> None:
    response = client.post(
        "/profiles/extract",
        json={
            "details": (
                "I work in accounting and want to move into data analytics "
                "within nine months. I can study eight hours every week. "
                "I know Excel and prefer low-cost resources."
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["target_role"] == "Data analyst"
    assert body["profile"]["deadline_months"] == 9
    assert body["profile"]["hours_per_week"] == 8
    assert body["profile"]["budget_preference"] == "low-cost"
    assert body["follow_up_questions"] == []
