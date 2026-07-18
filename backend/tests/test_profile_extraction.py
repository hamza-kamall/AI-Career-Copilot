from fastapi.testclient import TestClient

from app.main import app
from src.models.profile import BudgetPreference, ExperienceLevel
import src.services.profile_service as profile_service
from src.services.profile_service import extract_user_profile, merge_user_profiles


client = TestClient(app)


def test_extract_user_profile_from_complete_student_details() -> None:
    profile = extract_user_profile(
        "I am a second-year engineering student. I know Python and basic "
        "machine learning. I want an AI internship within six months. I can "
        "study fourteen hours weekly and only want free resources. I speak "
        "English and Urdu and prefer a student-friendly project-based mentor."
    )

    assert profile.current_situation == "A second-year engineering student"
    assert profile.primary_goal == "Become an AI Engineer"
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


def test_profile_card_content_is_polished_from_single_sentence_input() -> None:
    profile = extract_user_profile(
        "i am a second year student and want to become a data analyst in 6 months. "
        "i know python and can study 10 hours per week."
    )

    assert profile.current_situation == "A second-year student"
    assert profile.primary_goal == "Become a Data Analyst"
    assert profile.target_role == "Data analyst"
    assert profile.current_skills == ["Python"]


def test_profile_card_discards_standalone_current_situation_pronoun() -> None:
    profile = merge_user_profiles(
        None,
        extract_user_profile("I want to become an AI engineer in 6 months.").model_copy(
            update={"current_situation": "I"}
        ),
    )

    assert profile.current_situation == ""
    assert profile.primary_goal == "Become an AI Engineer"


def test_llm_profile_recovers_current_situation_from_user_input(monkeypatch) -> None:
    def fake_generate_structured(prompt, schema):
        return schema(
            current_situation="I",
            primary_goal="Become an AI engineer in 6 months",
            target_role="AI engineer",
            current_skills=["python"],
            deadline_months=6,
            hours_per_week=10,
        )

    monkeypatch.setattr(profile_service, "is_gemini_enabled", lambda: True)
    monkeypatch.setattr(profile_service, "generate_structured", fake_generate_structured)

    profile = extract_user_profile(
        "I am a second year software engineering student and want to become "
        "an AI engineer in 6 months. I know python and can study 10 hours per week."
    )

    assert profile.current_situation == "A second-year software engineering student"
    assert profile.primary_goal == "Become an AI Engineer"


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


def test_profile_merge_accumulates_skills_from_new_message() -> None:
    existing = extract_user_profile(
        "I want to become a frontend developer in six months. I know HTML."
    )

    merged = extract_user_profile(
        "I also know CSS and JavaScript.",
        existing_profile=existing,
    )

    assert merged.target_role == "Frontend developer"
    assert merged.deadline_months == 6
    assert merged.current_skills[0] == "HTML"
    assert set(merged.current_skills) == {"HTML", "CSS", "JavaScript"}


def test_profile_merge_adds_missing_hours_without_deleting_goal() -> None:
    existing = extract_user_profile(
        "I want to become an AI engineer in six months. I know Python."
    )

    merged = extract_user_profile(
        "I can study 8 hours per week.",
        existing_profile=existing,
    )

    assert merged.target_role == "AI engineer"
    assert merged.deadline_months == 6
    assert merged.current_skills == ["Python"]
    assert merged.hours_per_week == 8


def test_profile_merge_allows_target_role_correction() -> None:
    existing = extract_user_profile(
        "I want to become a frontend developer in six months. I know HTML."
    )
    correction = existing.model_copy(
        update={
            "primary_goal": "Become a data analyst",
            "target_role": "Data analyst",
            "current_skills": [],
            "missing_information": [],
        }
    )

    merged = merge_user_profiles(existing, correction)

    assert merged.target_role == "Data analyst"
    assert merged.primary_goal == "Become a data analyst"
    assert merged.current_skills == ["HTML"]
