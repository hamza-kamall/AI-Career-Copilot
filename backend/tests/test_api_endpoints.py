import json
import shutil

from fastapi.testclient import TestClient

from src.config import MENTORS_PATH
from app.main import app


client = TestClient(app)


SAMPLE_PROFILE = {
    "current_situation": "Student learning web basics",
    "primary_goal": "Become a frontend developer",
    "target_role": "Frontend developer",
    "current_skills": ["HTML", "CSS"],
    "experience_level": "beginner",
    "deadline_months": 6,
    "hours_per_week": 8,
    "budget_preference": "flexible",
    "learning_preferences": ["project"],
    "location": "Karachi",
    "languages": ["English"],
    "mentor_preferences": ["project-based"],
    "constraints": [],
    "missing_information": [],
}


def test_profile_extract_endpoint_returns_profile_and_questions() -> None:
    response = client.post(
        "/profiles/extract",
        json={
            "details": (
                "I am a student and want to become a frontend developer in 6 months. "
                "I know HTML and CSS and can study 8 hours per week."
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["target_role"] == "Frontend developer"
    assert "follow_up_questions" in body


def test_mentor_recommend_endpoint_returns_ranked_matches() -> None:
    response = client.post(
        "/mentors/recommend",
        json={"profile": SAMPLE_PROFILE, "limit": 3},
    )

    assert response.status_code == 200
    matches = response.json()["matches"]
    assert len(matches) == 3
    assert matches[0]["mentor"]["id"] == "mentor-web-001"
    assert matches[0]["score"] > 0
    assert matches[0]["explanation"]


def test_admin_mentor_crud_persists_and_affects_recommendations(tmp_path, monkeypatch) -> None:
    mentors_path = tmp_path / "mentors.json"
    shutil.copy(MENTORS_PATH, mentors_path)
    monkeypatch.setattr("app.main.MENTORS_PATH", mentors_path)

    mentor = {
        "id": "mentor-test-001",
        "name": "Test Mentor",
        "job_title": "Frontend Coach",
        "bio": "Helps beginners build polished React portfolios.",
        "expertise": ["React", "frontend developer", "CSS"],
        "industries": ["web development"],
        "years_experience": 12,
        "supported_levels": ["beginner", "intermediate"],
        "languages": ["English"],
        "available_hours": ["weekends"],
        "price_category": "flexible",
        "mentoring_style": ["project-based"],
        "profile_image": None,
    }

    create_response = client.post("/admin/mentors", json=mentor)
    assert create_response.status_code == 201

    duplicate_response = client.post("/admin/mentors", json=mentor)
    assert duplicate_response.status_code == 409

    recommend_response = client.post(
        "/mentors/recommend",
        json={"profile": SAMPLE_PROFILE, "limit": 12},
    )
    mentor_ids = [match["mentor"]["id"] for match in recommend_response.json()["matches"]]
    assert "mentor-test-001" in mentor_ids

    updated = {**mentor, "name": "Updated Test Mentor", "years_experience": 14}
    update_response = client.put("/admin/mentors/mentor-test-001", json=updated)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Test Mentor"

    delete_response = client.delete("/admin/mentors/mentor-test-001")
    assert delete_response.status_code == 204

    with mentors_path.open("r", encoding="utf-8") as file:
        saved_ids = [item["id"] for item in json.load(file)]
    assert "mentor-test-001" not in saved_ids


def test_admin_mentor_create_rejects_invalid_payload(tmp_path, monkeypatch) -> None:
    mentors_path = tmp_path / "mentors.json"
    shutil.copy(MENTORS_PATH, mentors_path)
    monkeypatch.setattr("app.main.MENTORS_PATH", mentors_path)

    response = client.post(
        "/admin/mentors",
        json={
            "id": "mentor-invalid-001",
            "name": "Invalid Mentor",
            "years_experience": -1,
        },
    )

    assert response.status_code == 422


def test_roadmap_generate_endpoint_returns_valid_roadmap() -> None:
    response = client.post(
        "/roadmaps/generate",
        json={"profile": SAMPLE_PROFILE},
    )

    assert response.status_code == 200
    roadmap = response.json()["roadmap"]
    assert roadmap["roadmap_title"] == "Frontend developer Roadmap"
    assert roadmap["weekly_hours"] == 8
    assert len(roadmap["phases"]) == 4
    assert roadmap["phases"][0]["weekly_tasks"]
