"""Deterministic mentor matching service."""

from __future__ import annotations

import re
from collections.abc import Iterable

from src.models.mentor import Mentor, MentorMatch
from src.models.profile import BudgetPreference, UserProfile


WEIGHTS = {
    "expertise": 0.40,
    "goal": 0.20,
    "level": 0.15,
    "availability": 0.10,
    "language": 0.10,
    "budget": 0.05,
}

SKILL_ALIASES = {
    "ai": {"ai", "artificial intelligence", "machine learning", "ml", "deep learning"},
    "machine learning": {"machine learning", "ml", "ai", "deep learning"},
    "frontend": {"frontend", "front-end", "react", "javascript", "html", "css"},
    "web development": {"web development", "frontend", "backend", "full stack", "react"},
    "data analytics": {"data analytics", "data analysis", "sql", "dashboarding", "business intelligence"},
    "cybersecurity": {"cybersecurity", "security", "network security", "soc"},
    "ui/ux": {"ui/ux", "ux", "ui", "product design", "figma"},
    "entrepreneurship": {"entrepreneurship", "startup", "founder", "business"},
    "business": {"business", "entrepreneurship", "marketing", "sales", "operations", "management"},
    "marketing": {"marketing", "digital marketing", "content strategy", "social media", "brand"},
    "finance": {"finance", "accounting", "financial analysis", "investment", "banking"},
    "healthcare": {"healthcare", "public health", "nursing", "clinical", "patient care"},
    "education": {"education", "teaching", "instructional design", "tutoring", "curriculum"},
    "creative": {"creative", "content creation", "writing", "video", "storytelling", "media"},
    "freelancing": {"freelancing", "remote work", "client work", "upwork"},
    "academic research": {"academic research", "research", "publication", "graduate school"},
}

PRICE_COMPATIBILITY = {
    BudgetPreference.FREE: {"free": 100, "low-cost": 60, "premium": 10},
    BudgetPreference.LOW_COST: {"free": 100, "low-cost": 100, "premium": 35},
    BudgetPreference.FLEXIBLE: {"free": 90, "low-cost": 95, "premium": 100},
    BudgetPreference.UNSPECIFIED: {"free": 90, "low-cost": 90, "premium": 90},
}


def calculate_mentor_match(profile: UserProfile, mentor: Mentor) -> float:
    """Calculate a normalized mentor match score between 0 and 100."""
    return round(sum(_score_breakdown(profile, mentor).values()), 2)


def rank_mentors(
    profile: UserProfile,
    mentors: list[Mentor],
    limit: int = 3,
) -> list[MentorMatch]:
    """Rank mentors by deterministic score, returning the requested limit."""
    matches = [
        MentorMatch(
            mentor=mentor,
            score=calculate_mentor_match(profile, mentor),
            component_scores=_component_scores(profile, mentor),
            explanation=generate_mentor_explanation(
                profile,
                mentor,
                calculate_mentor_match(profile, mentor),
            ),
        )
        for mentor in mentors
    ]
    return sorted(
        matches,
        key=lambda match: (-match.score, -match.mentor.years_experience, match.mentor.name),
    )[:limit]


def generate_mentor_explanation(profile: UserProfile, mentor: Mentor, score: float) -> str:
    """Generate a concise deterministic explanation for a mentor match."""
    strongest = _strongest_overlap(
        _profile_terms(profile),
        [*mentor.expertise, *mentor.industries, *mentor.mentoring_style],
    )
    level = profile.experience_level.value if profile.experience_level else "your level"
    if strongest:
        return (
            f"{mentor.name} scores {score:.1f} because their {strongest} background "
            f"fits your goal, supports {level} learners, and matches key preferences."
        )
    return (
        f"{mentor.name} scores {score:.1f} as a nearby match based on level, "
        "availability, language, and budget compatibility."
    )


def _score_breakdown(profile: UserProfile, mentor: Mentor) -> dict[str, float]:
    components = _component_scores(profile, mentor)
    return {key: components[key] * WEIGHTS[key] for key in WEIGHTS}


def _component_scores(profile: UserProfile, mentor: Mentor) -> dict[str, float]:
    return {
        "expertise": _expertise_score(profile, mentor),
        "goal": _goal_score(profile, mentor),
        "level": _level_score(profile, mentor),
        "availability": _availability_score(profile, mentor),
        "language": _language_score(profile, mentor),
        "budget": _budget_score(profile, mentor),
    }


def _expertise_score(profile: UserProfile, mentor: Mentor) -> float:
    profile_terms = _profile_terms(profile)
    return _overlap_score(profile_terms, mentor.expertise)


def _goal_score(profile: UserProfile, mentor: Mentor) -> float:
    goal_terms = _normalize_terms([profile.primary_goal, profile.target_role or ""])
    return _overlap_score(goal_terms, [*mentor.industries, *mentor.expertise])


def _level_score(profile: UserProfile, mentor: Mentor) -> float:
    if profile.experience_level is None:
        return 50
    return 100 if profile.experience_level.value in _normalize_terms(mentor.supported_levels) else 0


def _availability_score(profile: UserProfile, mentor: Mentor) -> float:
    if profile.hours_per_week is None:
        return 50
    slots = _normalize_terms(mentor.available_hours)
    if profile.hours_per_week <= 5:
        return 100 if "light" in slots else 60 if "moderate" in slots else 25
    if profile.hours_per_week <= 12:
        return 100 if "moderate" in slots else 75 if "light" in slots or "intensive" in slots else 40
    return 100 if "intensive" in slots else 70 if "moderate" in slots else 35


def _language_score(profile: UserProfile, mentor: Mentor) -> float:
    if not profile.languages:
        return 80
    return _overlap_score(profile.languages, mentor.languages)


def _budget_score(profile: UserProfile, mentor: Mentor) -> float:
    preference = profile.budget_preference or BudgetPreference.UNSPECIFIED
    return PRICE_COMPATIBILITY[preference].get(mentor.price_category.lower(), 50)


def _profile_terms(profile: UserProfile) -> set[str]:
    return _normalize_terms(
        [
            profile.primary_goal,
            profile.target_role or "",
            *profile.current_skills,
            *profile.learning_preferences,
            *profile.mentor_preferences,
        ]
    )


def _overlap_score(profile_terms: Iterable[str], mentor_terms: Iterable[str]) -> float:
    expanded_profile = _expand_terms(profile_terms)
    expanded_mentor = _expand_terms(_normalize_terms(mentor_terms))
    if not expanded_profile:
        return 50
    overlap = expanded_profile & expanded_mentor
    if not overlap:
        return 0
    return min(100, (len(overlap) / min(len(expanded_profile), 5)) * 100)


def _strongest_overlap(profile_terms: Iterable[str], mentor_terms: Iterable[str]) -> str | None:
    overlap = _expand_terms(profile_terms) & _expand_terms(_normalize_terms(mentor_terms))
    return sorted(overlap, key=len, reverse=True)[0] if overlap else None


def _expand_terms(terms: Iterable[str]) -> set[str]:
    expanded = set(terms)
    for term in list(expanded):
        expanded.update(SKILL_ALIASES.get(term, set()))
    return expanded


def _normalize_terms(values: Iterable[str]) -> set[str]:
    terms: set[str] = set()
    for value in values:
        lowered = value.strip().lower()
        if not lowered:
            continue
        terms.add(lowered)
        terms.update(token for token in re.split(r"[^a-z0-9+#/.-]+", lowered) if token)
    return terms
