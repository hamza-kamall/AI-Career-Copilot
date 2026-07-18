"""Roadmap generation service."""

from __future__ import annotations

from src.models.profile import ExperienceLevel, UserProfile
from src.models.resource import LearningResource
from src.models.roadmap import CareerRoadmap, RoadmapPhase, RoadmapProject, WeeklyTask
from src.repositories.resource_repository import load_resources
from src.services.llm_service import generate_structured, is_gemini_enabled


ROLE_SKILLS = {
    "frontend": ["HTML", "CSS", "JavaScript", "React", "TypeScript"],
    "web": ["HTML", "CSS", "JavaScript", "React", "Git"],
    "ai": ["Python", "machine learning", "deep learning", "model evaluation"],
    "machine learning": ["Python", "machine learning", "deep learning", "model evaluation"],
    "data": ["Excel", "SQL", "data analytics", "dashboarding"],
    "cybersecurity": ["Linux", "networking", "cybersecurity", "incident analysis"],
    "ui/ux": ["Figma", "UI/UX", "prototyping", "user research"],
}


def generate_career_roadmap(profile: UserProfile) -> CareerRoadmap:
    """Create a profile-specific career roadmap."""
    resources = load_resources()
    if is_gemini_enabled():
        try:
            roadmap = generate_structured(_roadmap_prompt(profile, resources), CareerRoadmap)
            return _align_roadmap_with_profile(roadmap, profile)
        except Exception:
            pass

    return _generate_deterministic_roadmap(profile, resources)


def _generate_deterministic_roadmap(
    profile: UserProfile,
    resources: list[LearningResource],
) -> CareerRoadmap:
    """Create a local roadmap when an LLM is unavailable."""
    target_role = profile.target_role or _fallback_role(profile)
    weekly_hours = profile.hours_per_week or 8
    duration_weeks = max(8, (profile.deadline_months or 4) * 4)
    skills = _target_skills(profile)
    skill_gaps = [
        skill
        for skill in skills
        if skill.lower() not in {current.lower() for current in profile.current_skills}
    ]
    phases = _build_phases(profile, target_role, duration_weeks, weekly_hours, skill_gaps, resources)

    return CareerRoadmap(
        roadmap_title=f"{target_role} Roadmap",
        career_goal=profile.primary_goal or f"Become a {target_role}",
        duration_weeks=sum(phase.duration_weeks for phase in phases),
        weekly_hours=weekly_hours,
        assumptions=_build_assumptions(profile, duration_weeks, weekly_hours),
        skill_gaps=skill_gaps[:8] or ["Portfolio positioning", "Interview practice"],
        phases=phases,
        final_outcome=(
            f"A focused portfolio and interview-ready skill set for {target_role} roles, "
            f"built around {profile.current_situation or 'the user profile'}."
        ),
        next_steps=_next_steps(profile, target_role, skill_gaps),
    )


def _roadmap_prompt(profile: UserProfile, resources: list[LearningResource]) -> str:
    resource_lines = "\n".join(
        f"- {resource.id}: {resource.title} ({resource.skill}, {resource.level}, {resource.provider})"
        for resource in resources
    )
    return f"""
Generate a custom career roadmap for this exact structured user profile.

Rules:
- Return valid data for the supplied CareerRoadmap schema.
- Do not return a generic template. Every phase, task, project, skill gap, and next step must reflect this profile.
- Consider the whole profile: current_situation, primary_goal, target_role, current_skills, experience_level, deadline_months, hours_per_week, budget_preference, learning_preferences, location, languages, mentor_preferences, and constraints.
- Use the user's target deadline as the roadmap duration. If deadline_months is known, duration_weeks must be deadline_months * 4.
- Use the user's weekly availability. If hours_per_week is known, weekly_hours must match it exactly.
- Estimate workload realistically: each WeeklyTask.estimated_hours should fit within weekly_hours.
- Build from the user's existing skills. Do not make them relearn skills they already have unless practice or review is clearly useful.
- Identify skill gaps by comparing current_skills to the target_role and primary_goal.
- Choose phase durations that add up to duration_weeks.
- Include 4 phases.
- Each phase must include weekly_tasks that describe concrete work for representative weeks in that phase.
- Weekly tasks must be specific action items, not generic labels like "study fundamentals".
- Portfolio projects must be specific to the user's target role and background.
- Use only these verified resource IDs in resource_ids when relevant.
- Include mentor-oriented recommendations in next_steps, such as what kind of mentor to book and what to ask.
- Keep the roadmap realistic for a student or early-career learner.
- If information is missing, state practical assumptions in assumptions and still produce the best possible roadmap.

Profile:
{profile.model_dump_json()}

Verified resources:
{resource_lines}
""".strip()


def _align_roadmap_with_profile(
    roadmap: CareerRoadmap,
    profile: UserProfile,
) -> CareerRoadmap:
    """Keep AI output aligned with the user's explicit timing constraints."""
    updates: dict[str, int] = {}
    if profile.deadline_months is not None:
        updates["duration_weeks"] = profile.deadline_months * 4
    if profile.hours_per_week is not None:
        updates["weekly_hours"] = profile.hours_per_week
    if not updates:
        return roadmap
    return roadmap.model_copy(update=updates)


def _build_phases(
    profile: UserProfile,
    target_role: str,
    duration_weeks: int,
    weekly_hours: int,
    skill_gaps: list[str],
    resources: list[LearningResource],
) -> list[RoadmapPhase]:
    phase_lengths = _phase_lengths(duration_weeks)
    selected_skills = skill_gaps or ["Foundations", "Portfolio", "Interview practice"]
    phase_specs = _phase_specs(profile, target_role, selected_skills)

    phases: list[RoadmapPhase] = []
    for index, (title, objective) in enumerate(phase_specs, start=1):
        phase_skills = _slice_skills(selected_skills, index)
        phases.append(
            RoadmapPhase(
                phase_number=index,
                title=title,
                duration_weeks=phase_lengths[index - 1],
                objective=objective,
                skills=phase_skills,
                weekly_tasks=_weekly_tasks(
                    profile,
                    target_role,
                    index,
                    phase_lengths[index - 1],
                    weekly_hours,
                    phase_skills,
                    resources,
                ),
                project=_project_for_phase(profile, index, target_role, phase_skills),
                completion_criteria=_completion_criteria(
                    profile,
                    target_role,
                    index,
                    phase_skills,
                ),
                resource_ids=_matching_resource_ids(phase_skills, resources),
            )
        )
    return phases


def _fallback_role(profile: UserProfile) -> str:
    if profile.primary_goal:
        return profile.primary_goal[:60]
    return "Career Growth"


def _target_skills(profile: UserProfile) -> list[str]:
    search_text = " ".join(
        [
            profile.target_role or "",
            profile.primary_goal,
            *profile.current_skills,
        ]
    ).lower()
    for keyword, skills in ROLE_SKILLS.items():
        if keyword in search_text:
            return skills
    if profile.current_skills:
        return [*profile.current_skills, "Portfolio", "Interview practice"]
    return ["Career foundations", "Portfolio", "Interview practice"]


def _phase_lengths(duration_weeks: int) -> list[int]:
    base = max(2, duration_weeks // 4)
    lengths = [base, base, base, base]
    for index in range(duration_weeks - sum(lengths)):
        lengths[index % 4] += 1
    return lengths


def _slice_skills(skills: list[str], phase_number: int) -> list[str]:
    if phase_number == 1:
        return skills[:2] or ["Foundations"]
    if phase_number == 2:
        return skills[1:4] or skills[:2]
    if phase_number == 3:
        return skills[2:5] or skills[-2:]
    return ["Portfolio", "Applications", "Interview practice"]


def _phase_specs(
    profile: UserProfile,
    target_role: str,
    selected_skills: list[str],
) -> list[tuple[str, str]]:
    goal = profile.primary_goal or f"move into {target_role}"
    situation = profile.current_situation or "current background"
    first_skill = selected_skills[0]
    portfolio_skill = selected_skills[min(2, len(selected_skills) - 1)]
    return [
        (
            f"{first_skill} foundations for {target_role}",
            f"Anchor the plan in {first_skill} while using the learner's {situation}.",
        ),
        (
            f"Applied {target_role} practice",
            f"Convert {', '.join(selected_skills[:3])} into weekly evidence toward {goal}.",
        ),
        (
            f"{portfolio_skill} portfolio build",
            f"Create a role-specific project that proves readiness for {target_role}.",
        ),
        (
            f"{target_role} launch",
            f"Package the portfolio, mentor questions, and applications around {goal}.",
        ),
    ]


def _weekly_tasks(
    profile: UserProfile,
    target_role: str,
    phase_number: int,
    duration_weeks: int,
    weekly_hours: int,
    phase_skills: list[str],
    resources: list[LearningResource],
) -> list[WeeklyTask]:
    weeks_to_show = min(duration_weeks, 4)
    return [
        WeeklyTask(
            week=week,
            tasks=_tasks_for_week(
                profile,
                target_role,
                phase_number,
                week,
                phase_skills,
                resources,
            ),
            estimated_hours=weekly_hours,
        )
        for week in range(1, weeks_to_show + 1)
    ]


def _tasks_for_week(
    profile: UserProfile,
    target_role: str,
    phase_number: int,
    week: int,
    phase_skills: list[str],
    resources: list[LearningResource],
) -> list[str]:
    primary_skill = phase_skills[(week - 1) % len(phase_skills)]
    supporting_skill = phase_skills[min(len(phase_skills) - 1, week % len(phase_skills))]
    resource = _resource_for_skill(primary_skill, resources)
    context = _profile_context(profile)
    preference = _learning_preference(profile)
    constraint = _constraint_clause(profile)

    if phase_number == 1:
        return [
            f"Map what you already know about {primary_skill} to {target_role} job requirements.",
            f"Use {resource} to close one {primary_skill} gap with {preference} practice.",
            f"Write a short {context} learning note that explains {primary_skill} in your own words{constraint}.",
        ]
    if phase_number == 2:
        return [
            f"Build a small {target_role} exercise that combines {primary_skill} with {supporting_skill}.",
            f"Turn one mistake from the exercise into a reusable checklist for future {target_role} work.",
            f"Ask for feedback on the exercise from a mentor, classmate, or online community{constraint}.",
        ]
    if phase_number == 3:
        return [
            f"Implement one portfolio feature that demonstrates {primary_skill} for {target_role} roles.",
            f"Document the project decision, tradeoff, and result in a case-study note tied to {profile.primary_goal or target_role}.",
            f"Publish or package the work so a mentor can review it in under five minutes{constraint}.",
        ]
    return [
        f"Rewrite your resume/profile headline around {target_role}, {primary_skill}, and your strongest existing skill.",
        f"Prepare three interview stories from the roadmap work, including one challenge involving {supporting_skill}.",
        f"Apply or reach out to opportunities aligned with {profile.location or 'your target market'} and ask a mentor what to improve next.",
    ]


def _project_for_phase(
    profile: UserProfile,
    phase_number: int,
    target_role: str,
    phase_skills: list[str],
) -> RoadmapProject:
    focus = ", ".join(phase_skills[:2])
    goal = profile.primary_goal or target_role
    titles = {
        1: f"{target_role} Skills Baseline",
        2: f"{focus} Practice Sprint",
        3: f"{target_role} Portfolio Case Study",
        4: f"{target_role} Application Kit",
    }
    return RoadmapProject(
        title=titles[phase_number],
        description=(
            f"A practical deliverable for {goal} that uses {focus} and reflects "
            f"{profile.current_situation or 'the learner background'}."
        ),
        deliverables=[
            f"{target_role} project summary",
            f"Evidence of completed {focus} work",
            f"Short reflection on decisions, tradeoffs, and next mentor questions",
        ],
    )


def _completion_criteria(
    profile: UserProfile,
    target_role: str,
    phase_number: int,
    phase_skills: list[str],
) -> list[str]:
    focus = ", ".join(phase_skills[:2])
    criteria = {
        1: [
            f"{focus} gaps are summarized against {target_role} requirements",
            f"Practice notes reflect {profile.experience_level.value if profile.experience_level else 'current'} level",
        ],
        2: [
            f"Two applied {target_role} exercises are complete",
            f"Weak areas in {focus} are documented with next actions",
        ],
        3: [
            f"{target_role} portfolio project is published or packaged",
            f"Case study connects the work to {profile.primary_goal or target_role}",
        ],
        4: [
            f"Resume/profile is updated for {target_role}",
            "Applications or mentor outreach have started with a prepared question list",
        ],
    }
    return criteria[phase_number]


def _resource_for_skill(skill: str, resources: list[LearningResource]) -> str:
    skill_lower = skill.lower()
    for resource in resources:
        resource_skill = resource.skill.lower()
        if resource_skill in skill_lower or skill_lower in resource_skill:
            return resource.title
    return f"a focused {skill} resource"


def _profile_context(profile: UserProfile) -> str:
    if profile.current_situation:
        return profile.current_situation
    if profile.experience_level:
        return f"{profile.experience_level.value} learner"
    return "career"


def _learning_preference(profile: UserProfile) -> str:
    if profile.learning_preferences:
        return f"{profile.learning_preferences[0]}-based"
    return "hands-on"


def _constraint_clause(profile: UserProfile) -> str:
    if profile.constraints:
        return f" while respecting {profile.constraints[0]}"
    if profile.budget_preference:
        return f" using {profile.budget_preference.value} options"
    return ""


def _next_steps(
    profile: UserProfile,
    target_role: str,
    skill_gaps: list[str],
) -> list[str]:
    first_gap = skill_gaps[0] if skill_gaps else "portfolio positioning"
    mentor_focus = profile.mentor_preferences[0] if profile.mentor_preferences else target_role
    return [
        f"Start this week with the first {first_gap} task and keep the output visible in a portfolio folder.",
        f"Book a {mentor_focus} mentor session and ask which {target_role} proof points are still missing.",
        f"Review the plan after two weeks against {profile.hours_per_week or 8} available hours and adjust scope before adding new tasks.",
    ]


def _matching_resource_ids(
    skills: list[str],
    resources: list[LearningResource],
    limit: int = 3,
) -> list[str]:
    normalized = {skill.lower() for skill in skills}
    matches = [
        resource.id
        for resource in resources
        if resource.skill.lower() in normalized
        or any(resource.skill.lower() in skill for skill in normalized)
    ]
    return matches[:limit]


def _build_assumptions(
    profile: UserProfile,
    duration_weeks: int,
    weekly_hours: int,
) -> list[str]:
    level = profile.experience_level or ExperienceLevel.BEGINNER
    return [
        f"Plan assumes {weekly_hours} focused hours per week.",
        f"Timeline is based on roughly {duration_weeks} weeks.",
        f"Starting level is treated as {level.value}.",
    ]
