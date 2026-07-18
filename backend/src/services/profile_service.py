"""Profile extraction and validation services.

This increment uses deterministic mock extraction so the backend can return a
validated Pydantic model without requiring an API key. A real LLM provider can
later replace the extractor behind the same public function.
"""

from __future__ import annotations

import re

from src.models.profile import BudgetPreference, ExperienceLevel, UserProfile


CRITICAL_FIELDS = {
    "primary_goal": "What career goal or target role do you want to pursue?",
    "current_skills": "What skills or tools do you currently know?",
    "hours_per_week": "How many hours can you dedicate each week?",
    "deadline_months": "Do you have a target deadline for achieving this goal?",
}

SKILL_KEYWORDS = {
    "python": "Python",
    "machine learning": "machine learning",
    "basic machine learning": "basic machine learning",
    "deep learning": "deep learning",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "html": "HTML",
    "css": "CSS",
    "sql": "SQL",
    "excel": "Excel",
    "figma": "Figma",
    "linux": "Linux",
}

ROLE_KEYWORDS = {
    "ai engineer": "AI engineer",
    "ai internship": "AI engineer",
    "machine learning engineer": "Machine learning engineer",
    "frontend developer": "Frontend developer",
    "front-end developer": "Frontend developer",
    "web developer": "Web developer",
    "data analyst": "Data analyst",
    "data analytics": "Data analyst",
    "cybersecurity": "Cybersecurity analyst",
    "ui/ux": "UI/UX designer",
    "ux designer": "UI/UX designer",
    "freelancer": "Freelancer",
    "startup": "Founder",
    "research": "Research assistant",
}

LANGUAGE_KEYWORDS = {
    "english": "English",
    "urdu": "Urdu",
    "hindi": "Hindi",
    "arabic": "Arabic",
}


def extract_user_profile(user_input: str) -> UserProfile:
    """Translate user details into the validated ``UserProfile`` model.

    The current implementation is a predictable mock-AI extractor for demo and
    testing. It only captures information that appears in the text and records
    critical unknowns in ``missing_information``.
    """
    cleaned_input = " ".join(user_input.split())
    if not cleaned_input:
        profile = UserProfile()
        profile.missing_information = list(CRITICAL_FIELDS)
        return profile

    profile = UserProfile(
        current_situation=_extract_current_situation(cleaned_input),
        primary_goal=_extract_primary_goal(cleaned_input),
        target_role=_extract_target_role(cleaned_input),
        current_skills=_extract_skills(cleaned_input),
        experience_level=_extract_experience_level(cleaned_input),
        deadline_months=_extract_deadline_months(cleaned_input),
        hours_per_week=_extract_hours_per_week(cleaned_input),
        budget_preference=_extract_budget_preference(cleaned_input),
        learning_preferences=_extract_learning_preferences(cleaned_input),
        location=_extract_location(cleaned_input),
        languages=_extract_languages(cleaned_input),
        mentor_preferences=_extract_mentor_preferences(cleaned_input),
        constraints=_extract_constraints(cleaned_input),
    )
    profile.missing_information = identify_missing_information(profile)
    return profile


def identify_missing_information(profile: UserProfile) -> list[str]:
    """Return missing critical profile fields as machine-readable field names."""
    missing: list[str] = []
    if not profile.primary_goal:
        missing.append("primary_goal")
    if not profile.current_skills and profile.experience_level is None:
        missing.append("current_skills")
    if profile.hours_per_week is None:
        missing.append("hours_per_week")
    if profile.deadline_months is None:
        missing.append("deadline_months")
    return missing[:3]


def get_follow_up_questions(profile: UserProfile) -> list[str]:
    """Return up to three user-facing follow-up questions for missing fields."""
    return [CRITICAL_FIELDS[field] for field in identify_missing_information(profile)]


def _extract_current_situation(text: str) -> str:
    lower_text = text.lower()
    markers = ["i am ", "i'm ", "i work ", "currently ", "my background"]
    if any(marker in lower_text for marker in markers):
        return _first_sentence(text)
    return ""


def _extract_primary_goal(text: str) -> str:
    patterns = [
        r"\b(?:i want to|want to|goal is to|looking to|aim to)\s+([^.!?]+)",
        r"\b(?:i want|want)\s+([^.!?]+)",
        r"\b(?:become|move into|transition into)\s+([^.!?]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _clean_phrase(match.group(1))
    role = _extract_target_role(text)
    return f"Become a {role}" if role else ""


def _extract_target_role(text: str) -> str | None:
    lower_text = text.lower()
    for keyword, role in ROLE_KEYWORDS.items():
        if keyword in lower_text:
            return role
    return None


def _extract_skills(text: str) -> list[str]:
    lower_text = text.lower()
    skills = [
        skill for keyword, skill in SKILL_KEYWORDS.items() if keyword in lower_text
    ]
    return _dedupe_preserving_order(skills)


def _extract_experience_level(text: str) -> ExperienceLevel | None:
    lower_text = text.lower()
    if any(term in lower_text for term in ["advanced", "senior", "expert"]):
        return ExperienceLevel.ADVANCED
    if any(term in lower_text for term in ["intermediate", "basic", "some experience"]):
        return ExperienceLevel.INTERMEDIATE
    if any(term in lower_text for term in ["beginner", "new to", "no experience"]):
        return ExperienceLevel.BEGINNER
    return None


def _extract_deadline_months(text: str) -> int | None:
    lower_text = text.lower()
    word_numbers = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
    }
    number_pattern = r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    match = re.search(number_pattern + r"\s+months?", lower_text)
    if match:
        return _to_int(match.group(1), word_numbers)
    match = re.search(number_pattern + r"\s+years?", lower_text)
    if match:
        return _to_int(match.group(1), word_numbers) * 12
    return None


def _extract_hours_per_week(text: str) -> int | None:
    lower_text = text.lower()
    word_numbers = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "twenty": 20,
    }
    number_pattern = (
        r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
        r"twelve|thirteen|fourteen|fifteen|twenty)"
    )
    match = re.search(
        number_pattern + r"\s+hours?\s+(?:per|a|each|every)?\s*week",
        lower_text,
    )
    if match:
        return _to_int(match.group(1), word_numbers)
    match = re.search(number_pattern + r"\s+hours?\s+(?:per|a|each)?\s*day", lower_text)
    if match:
        return _to_int(match.group(1), word_numbers) * 7
    return None


def _extract_budget_preference(text: str) -> BudgetPreference | None:
    lower_text = text.lower()
    if any(term in lower_text for term in ["only free", "free resources", "free course"]):
        return BudgetPreference.FREE
    if any(term in lower_text for term in ["low-cost", "low cost", "cheap", "affordable"]):
        return BudgetPreference.LOW_COST
    if any(term in lower_text for term in ["paid", "flexible budget", "can pay"]):
        return BudgetPreference.FLEXIBLE
    return None


def _extract_learning_preferences(text: str) -> list[str]:
    lower_text = text.lower()
    preferences = []
    for keyword in ["video", "project", "hands-on", "documentation", "book", "course"]:
        if keyword in lower_text:
            preferences.append(keyword)
    return preferences


def _extract_location(text: str) -> str | None:
    match = re.search(r"\b(?:in|from|based in)\s+([A-Z][A-Za-z\s]+)", text)
    if match:
        return _clean_phrase(match.group(1))
    return None


def _extract_languages(text: str) -> list[str]:
    lower_text = text.lower()
    return [
        language
        for keyword, language in LANGUAGE_KEYWORDS.items()
        if keyword in lower_text
    ]


def _extract_mentor_preferences(text: str) -> list[str]:
    lower_text = text.lower()
    preferences = []
    for keyword in [
        "student-friendly",
        "project-based",
        "structured",
        "hands-on",
        "career-transition",
        "code review",
    ]:
        if keyword in lower_text:
            preferences.append(keyword)
    if "mentor" in lower_text and "student" in lower_text:
        preferences.append("student-friendly")
    return _dedupe_preserving_order(preferences)


def _extract_constraints(text: str) -> list[str]:
    lower_text = text.lower()
    constraints = []
    if "limited" in lower_text:
        constraints.append(_first_sentence(text))
    if "no experience" in lower_text:
        constraints.append("No prior experience")
    if "free" in lower_text:
        constraints.append("Prefers free resources")
    return _dedupe_preserving_order(constraints)


def _first_sentence(text: str) -> str:
    return re.split(r"[.!?]", text, maxsplit=1)[0].strip()


def _clean_phrase(value: str) -> str:
    return value.strip(" .,!?:;")


def _to_int(value: str, word_numbers: dict[str, int]) -> int:
    return int(value) if value.isdigit() else word_numbers[value]


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result
