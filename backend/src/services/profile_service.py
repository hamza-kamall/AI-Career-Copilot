"""Profile extraction and validation services.

This increment uses deterministic mock extraction so the backend can return a
validated Pydantic model without requiring an API key. A real LLM provider can
later replace the extractor behind the same public function.
"""

from __future__ import annotations

import re

from src.models.profile import BudgetPreference, ExperienceLevel, UserProfile
from src.services.llm_service import generate_structured, is_gemini_enabled


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


REPLACEABLE_SCALAR_FIELDS = {
    "primary_goal",
    "target_role",
    "deadline_months",
    "hours_per_week",
    "budget_preference",
    "experience_level",
    "location",
}

LIST_FIELDS = {
    "current_skills",
    "learning_preferences",
    "languages",
    "mentor_preferences",
    "constraints",
}


def extract_user_profile(
    user_input: str,
    existing_profile: UserProfile | None = None,
) -> UserProfile:
    """Translate user details into the validated ``UserProfile`` model.

    Gemini is used when configured. The deterministic extractor remains as a
    local fallback so the app can still run without an API key.
    """
    if is_gemini_enabled():
        try:
            profile = generate_structured(
                _profile_prompt(user_input, existing_profile),
                UserProfile,
            )
            profile = _make_profile_presentable(profile, source_input=user_input)
            profile.missing_information = identify_missing_information(profile)
            return merge_user_profiles(existing_profile, profile)
        except Exception:
            pass

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
    profile = _make_profile_presentable(profile, source_input=user_input)
    profile.missing_information = identify_missing_information(profile)
    return merge_user_profiles(existing_profile, profile)


def merge_user_profiles(
    existing_profile: UserProfile | None,
    new_profile: UserProfile,
) -> UserProfile:
    """Merge a latest-message profile into an existing accumulated profile."""
    if existing_profile is None:
        polished_profile = _make_profile_presentable(new_profile)
        polished_profile.missing_information = identify_missing_information(polished_profile)
        return polished_profile

    merged_data = existing_profile.model_dump()
    new_data = new_profile.model_dump()

    for field, new_value in new_data.items():
        if field == "missing_information":
            continue
        existing_value = merged_data.get(field)

        if field in LIST_FIELDS:
            merged_data[field] = _merge_lists(existing_value or [], new_value or [])
            continue

        if field == "current_situation":
            if _is_non_empty(new_value) and (
                not _is_non_empty(existing_value)
                or len(str(new_value)) > len(str(existing_value))
            ):
                merged_data[field] = new_value
            continue

        if not _is_non_empty(existing_value) and _is_non_empty(new_value):
            merged_data[field] = new_value
            continue

        if (
            field in REPLACEABLE_SCALAR_FIELDS
            and _is_non_empty(existing_value)
            and _is_non_empty(new_value)
            and existing_value != new_value
        ):
            merged_data[field] = new_value

    merged = _make_profile_presentable(UserProfile.model_validate(merged_data))
    merged.missing_information = identify_missing_information(merged)
    return merged


def _profile_prompt(
    user_input: str,
    existing_profile: UserProfile | None = None,
) -> str:
    current_profile_text = (
        existing_profile.model_dump_json()
        if existing_profile is not None
        else "No existing profile yet."
    )
    return f"""
Extract or update a structured career profile from the latest user message.

Rules:
- Return only data that fits the supplied schema.
- Use null for unknown optional scalar fields.
- Use empty lists for unknown list fields.
- If an existing profile is supplied, return the best complete updated profile.
- Preserve existing useful details unless the latest message clearly corrects or adds to them.
- Merge list values like skills, languages, preferences, and constraints.
- Write card-ready values that look polished in a compact profile card.
- Keep current_situation and primary_goal concise, professional, and non-duplicative.
- current_situation should describe the user's background only, not repeat the goal.
- Leave current_situation blank if the message does not include a real background.
- Never return standalone pronouns like "I" or "me" for current_situation.
- primary_goal should state the desired outcome only, not repeat the timeline.
- Use natural title casing for roles, tools, and languages.
- Infer target_role only when the user's goal clearly implies one.
- missing_information should be recalculated by the backend, so return an empty list.

Existing profile:
{current_profile_text}

User message:
{user_input}
""".strip()


def _merge_lists(existing_values: list[str], new_values: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for value in [*existing_values, *new_values]:
        if not value:
            continue
        key = str(value).strip().lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(value)
    return merged


def _make_profile_presentable(
    profile: UserProfile,
    source_input: str | None = None,
) -> UserProfile:
    """Polish extracted fields so they render cleanly in the profile card."""
    data = profile.model_dump()
    target_role = profile.target_role
    display_role = _display_phrase(target_role) if target_role else None

    if display_role:
        if not profile.primary_goal or _goal_repeats_timeline(profile.primary_goal):
            data["primary_goal"] = _goal_for_role(display_role)

    if profile.primary_goal:
        data["primary_goal"] = _presentable_goal(profile.primary_goal, display_role)

    if profile.current_situation:
        data["current_situation"] = _presentable_situation(profile.current_situation)
        if not _is_informative_situation(data["current_situation"]):
            data["current_situation"] = _fallback_current_situation(source_input)
    elif source_input:
        data["current_situation"] = _fallback_current_situation(source_input)

    data["current_skills"] = [_display_skill(skill) for skill in profile.current_skills]
    data["learning_preferences"] = [
        _display_phrase(preference) for preference in profile.learning_preferences
    ]
    data["languages"] = [_display_phrase(language) for language in profile.languages]
    data["mentor_preferences"] = [
        _display_phrase(preference) for preference in profile.mentor_preferences
    ]
    data["constraints"] = [
        _sentence_case(constraint) for constraint in profile.constraints
    ]

    polished = UserProfile.model_validate(data)
    polished.missing_information = identify_missing_information(polished)
    return polished


def _presentable_goal(goal: str, target_role: str | None) -> str:
    if target_role and _goal_repeats_timeline(goal):
        return _goal_for_role(target_role)
    cleaned = _clean_phrase(_remove_timeline_phrase(goal))
    if re.match(r"^(?:become|move into|transition into|get|land|secure)\b", cleaned, re.I):
        return cleaned[0].upper() + cleaned[1:]
    return _sentence_case(cleaned)


def _presentable_situation(situation: str) -> str:
    cleaned = _clean_phrase(_remove_goal_clause(situation))
    cleaned = re.sub(r"^i\s+am\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^i'm\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^currently\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("second year", "second-year")
    return _sentence_case(cleaned)


def _is_informative_situation(value: str) -> bool:
    cleaned = _clean_phrase(value).lower()
    return len(cleaned) > 1 and cleaned not in {"i", "me", "myself"}


def _fallback_current_situation(source_input: str | None) -> str:
    if not source_input:
        return ""
    situation = _presentable_situation(_extract_current_situation(source_input))
    return situation if _is_informative_situation(situation) else ""


def _remove_goal_clause(value: str) -> str:
    return re.split(
        r"\s+\b(?:and\s+)?(?:i\s+)?(?:want|aim|plan|hope|looking)\s+to\b",
        value,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]


def _goal_repeats_timeline(goal: str) -> bool:
    return bool(
        re.search(
            r"\b(?:in|within)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+months?\b",
            goal,
            flags=re.IGNORECASE,
        )
    )


def _remove_timeline_phrase(goal: str) -> str:
    return re.sub(
        r"\s+\b(?:in|within)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+months?\b",
        "",
        goal,
        flags=re.IGNORECASE,
    )


def _goal_for_role(role: str) -> str:
    article = "an" if _articleless_role(role).lower().startswith(("a", "e", "i", "o", "u")) else "a"
    return f"Become {article} {_articleless_role(role)}"


def _articleless_role(role: str) -> str:
    return re.sub(r"^(?:a|an)\s+", "", role.strip(), flags=re.IGNORECASE)


def _display_phrase(value: str) -> str:
    special_terms = {
        "ai": "AI",
        "ui/ux": "UI/UX",
        "html": "HTML",
        "css": "CSS",
        "sql": "SQL",
    }
    words = []
    for word in _clean_phrase(value).split():
        key = word.lower()
        words.append(special_terms.get(key, word.capitalize()))
    return " ".join(words)


def _display_skill(skill: str) -> str:
    skill_labels = {value.lower(): value for value in SKILL_KEYWORDS.values()}
    key = skill.strip().lower()
    return skill_labels.get(key, _display_phrase(skill))


def _sentence_case(value: str) -> str:
    cleaned = _clean_phrase(value)
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]


def _is_non_empty(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return True


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
