import type { CareerRoadmap, Mentor, MentorMatch, ProfileExtractionResponse, UserProfile } from "./types";

const DEMO_MENTORS_KEY = "career-copilot-demo-mentors";

const defaultMentors: Mentor[] = [
  {
    id: "mentor-ai-001",
    name: "Ayesha Khan",
    job_title: "Senior Machine Learning Engineer",
    bio: "Builds computer vision and recommendation systems, with a track record mentoring university students into AI internships.",
    expertise: ["machine learning", "deep learning", "Python", "portfolio projects"],
    industries: ["AI", "software engineering", "internships"],
    years_experience: 8,
    supported_levels: ["beginner", "intermediate"],
    languages: ["English", "Urdu"],
    available_hours: ["moderate", "intensive"],
    price_category: "low-cost",
    mentoring_style: ["structured", "project-based", "student-friendly"],
    profile_image: null,
  },
  {
    id: "mentor-web-001",
    name: "Daniel Reed",
    job_title: "Frontend Engineering Lead",
    bio: "Leads React teams and helps learners turn HTML, CSS, and JavaScript foundations into portfolio-ready web apps.",
    expertise: ["frontend", "React", "JavaScript", "web development"],
    industries: ["web development", "SaaS"],
    years_experience: 10,
    supported_levels: ["beginner", "intermediate", "advanced"],
    languages: ["English"],
    available_hours: ["light", "moderate"],
    price_category: "premium",
    mentoring_style: ["code review", "portfolio-focused"],
    profile_image: null,
  },
  {
    id: "mentor-data-001",
    name: "Mariam Siddiqui",
    job_title: "Data Analytics Manager",
    bio: "Specializes in SQL, dashboards, and analytics career transitions for non-technical professionals.",
    expertise: ["data analytics", "SQL", "Excel", "dashboards"],
    industries: ["business intelligence", "finance", "career switch"],
    years_experience: 9,
    supported_levels: ["beginner", "intermediate"],
    languages: ["English", "Urdu"],
    available_hours: ["light", "moderate"],
    price_category: "low-cost",
    mentoring_style: ["practical", "career-transition"],
    profile_image: null,
  },
  {
    id: "mentor-cyber-001",
    name: "Omar Farooq",
    job_title: "Cybersecurity Consultant",
    bio: "Guides learners through networking, SOC fundamentals, hands-on labs, and entry-level cybersecurity paths.",
    expertise: ["cybersecurity", "network security", "SOC", "Linux"],
    industries: ["security", "consulting"],
    years_experience: 7,
    supported_levels: ["beginner", "intermediate"],
    languages: ["English", "Urdu"],
    available_hours: ["moderate"],
    price_category: "free",
    mentoring_style: ["hands-on", "lab-based"],
    profile_image: null,
  },
  {
    id: "mentor-ux-001",
    name: "Nina Patel",
    job_title: "Senior Product Designer",
    bio: "Mentors early designers in user research, UX case studies, Figma workflows, and portfolio storytelling.",
    expertise: ["UI/UX", "Figma", "user research", "product design"],
    industries: ["design", "consumer apps"],
    years_experience: 11,
    supported_levels: ["beginner", "intermediate", "advanced"],
    languages: ["English", "Hindi"],
    available_hours: ["light", "moderate"],
    price_category: "premium",
    mentoring_style: ["portfolio-focused", "feedback-heavy"],
    profile_image: null,
  },
  {
    id: "mentor-freelance-001",
    name: "Sara Malik",
    job_title: "Freelance Web Developer",
    bio: "Coaches new freelancers on client discovery, proposals, delivery habits, and small-business web projects.",
    expertise: ["freelancing", "web development", "client work", "WordPress"],
    industries: ["freelancing", "small business"],
    years_experience: 6,
    supported_levels: ["beginner", "intermediate"],
    languages: ["English", "Urdu"],
    available_hours: ["light", "moderate"],
    price_category: "free",
    mentoring_style: ["practical", "accountability"],
    profile_image: null,
  },
];

const roleKeywords: Array<[string, string]> = [
  ["frontend", "Frontend developer"],
  ["front-end", "Frontend developer"],
  ["web developer", "Web developer"],
  ["machine learning", "Machine learning engineer"],
  ["ai", "AI engineer"],
  ["data", "Data analyst"],
  ["cybersecurity", "Cybersecurity analyst"],
  ["ui/ux", "UI/UX designer"],
  ["ux", "UI/UX designer"],
  ["freelance", "Freelancer"],
];

const skillKeywords: Array<[string, string]> = [
  ["python", "Python"],
  ["machine learning", "machine learning"],
  ["javascript", "JavaScript"],
  ["typescript", "TypeScript"],
  ["react", "React"],
  ["html", "HTML"],
  ["css", "CSS"],
  ["sql", "SQL"],
  ["excel", "Excel"],
  ["figma", "Figma"],
  ["linux", "Linux"],
];

export function extractDemoProfile(details: string, existingProfile?: UserProfile | null): ProfileExtractionResponse {
  const lowerDetails = details.toLowerCase();
  const targetRole = findKeyword(lowerDetails, roleKeywords) ?? existingProfile?.target_role ?? "Career starter";
  const currentSkills = unique([
    ...(existingProfile?.current_skills ?? []),
    ...skillKeywords.filter(([keyword]) => lowerDetails.includes(keyword)).map(([, skill]) => skill),
  ]);
  const profile: UserProfile = {
    current_situation: firstSentence(details) || existingProfile?.current_situation || "Career learner",
    primary_goal: inferGoal(details, targetRole) || existingProfile?.primary_goal || `Become a ${targetRole}`,
    target_role: targetRole,
    current_skills: currentSkills,
    experience_level: inferExperience(lowerDetails) ?? existingProfile?.experience_level ?? "beginner",
    deadline_months: inferNumberBefore(lowerDetails, "month") ?? existingProfile?.deadline_months ?? 4,
    hours_per_week: inferNumberBefore(lowerDetails, "hour") ?? existingProfile?.hours_per_week ?? 8,
    budget_preference: inferBudget(lowerDetails) ?? existingProfile?.budget_preference ?? "free",
    learning_preferences: unique([
      ...(existingProfile?.learning_preferences ?? []),
      lowerDetails.includes("project") ? "Project-based" : "Hands-on",
    ]),
    location: lowerDetails.includes("pakistan") ? "Pakistan" : existingProfile?.location ?? null,
    languages: unique([
      ...(existingProfile?.languages ?? []),
      ...(lowerDetails.includes("urdu") ? ["Urdu"] : []),
      ...(lowerDetails.includes("english") ? ["English"] : []),
    ]),
    mentor_preferences: unique([...(existingProfile?.mentor_preferences ?? []), "Portfolio-focused"]),
    constraints: unique([
      ...(existingProfile?.constraints ?? []),
      ...(lowerDetails.includes("free") || lowerDetails.includes("low cost") ? ["Prefers free or low-cost resources"] : []),
    ]),
    missing_information: [],
  };

  return {
    profile,
    follow_up_questions: missingQuestions(profile),
  };
}

export function getDemoMentors() {
  return readMentors();
}

export function createDemoMentor(mentor: Mentor) {
  const mentors = readMentors();
  if (mentors.some((item) => item.id === mentor.id)) {
    throw new Error(`Mentor ${mentor.id} already exists in the demo dataset.`);
  }
  writeMentors([...mentors, mentor]);
  return mentor;
}

export function updateDemoMentor(mentor: Mentor) {
  const mentors = readMentors();
  const index = mentors.findIndex((item) => item.id === mentor.id);
  if (index === -1) {
    throw new Error(`Mentor ${mentor.id} was not found in the demo dataset.`);
  }
  const nextMentors = [...mentors];
  nextMentors[index] = mentor;
  writeMentors(nextMentors);
  return mentor;
}

export function deleteDemoMentor(mentorId: string) {
  writeMentors(readMentors().filter((mentor) => mentor.id !== mentorId));
}

export function recommendDemoMentors(profile: UserProfile, limit = 6): MentorMatch[] {
  const profileText = [
    profile.target_role,
    profile.primary_goal,
    ...profile.current_skills,
    ...profile.mentor_preferences,
    ...profile.languages,
  ]
    .join(" ")
    .toLowerCase();

  return readMentors()
    .map((mentor) => {
      const expertiseScore = mentor.expertise.reduce(
        (score, item) => score + (profileText.includes(item.toLowerCase()) ? 24 : 0),
        0,
      );
      const languageScore = mentor.languages.some((language) =>
        profile.languages.map((item) => item.toLowerCase()).includes(language.toLowerCase()),
      )
        ? 12
        : 0;
      const levelScore = profile.experience_level && mentor.supported_levels.includes(profile.experience_level) ? 16 : 0;
      const budgetScore = profile.budget_preference === mentor.price_category ? 12 : 0;
      const score = Math.min(96, 34 + expertiseScore + languageScore + levelScore + budgetScore);

      return {
        mentor,
        score,
        component_scores: {
          expertise: expertiseScore,
          language: languageScore,
          level: levelScore,
          budget: budgetScore,
        },
        explanation: `${mentor.name} is a strong demo match because their ${mentor.expertise
          .slice(0, 2)
          .join(" and ")} background fits your profile and mentor preferences.`,
      };
    })
    .sort((left, right) => right.score - left.score)
    .slice(0, limit);
}

export function generateDemoRoadmap(profile: UserProfile): CareerRoadmap {
  const targetRole = profile.target_role ?? "Career Growth";
  const weeklyHours = profile.hours_per_week ?? 8;
  const durationWeeks = Math.max(8, (profile.deadline_months ?? 4) * 4);
  const skills = targetSkills(profile);
  const skillGaps = skills.filter(
    (skill) => !profile.current_skills.some((currentSkill) => currentSkill.toLowerCase() === skill.toLowerCase()),
  );
  const phaseLength = Math.max(2, Math.floor(durationWeeks / 4));
  const phases = ["Foundations", "Applied Practice", "Portfolio Build", "Launch Prep"].map((title, index) => {
    const phaseNumber = index + 1;
    const phaseSkills = phaseNumber === 4 ? ["Portfolio", "Applications", "Interview practice"] : skills.slice(index, index + 2);
    return {
      phase_number: phaseNumber,
      title: `${targetRole} ${title}`,
      duration_weeks: phaseLength,
      objective: `Turn ${phaseSkills.join(", ")} into visible evidence for ${profile.primary_goal || targetRole}.`,
      skills: phaseSkills,
      weekly_tasks: [1, 2, 3, 4].slice(0, phaseLength).map((week) => ({
        week,
        estimated_hours: weeklyHours,
        tasks: [
          `Complete one focused ${phaseSkills[0]} learning block.`,
          `Build or improve a small ${targetRole} portfolio artifact.`,
          `Capture mentor questions and next actions for review.`,
        ],
      })),
      project: {
        title: `${targetRole} ${title} Deliverable`,
        description: `A practical artifact that proves progress toward ${targetRole} roles.`,
        deliverables: ["Project summary", "Evidence of completed work", "Mentor review questions"],
      },
      completion_criteria: [
        `${phaseSkills[0]} evidence is visible in the portfolio.`,
        `Next actions are clear for the following phase.`,
      ],
      resource_ids: [],
    };
  });

  return {
    roadmap_title: `${targetRole} Roadmap`,
    career_goal: profile.primary_goal || `Become a ${targetRole}`,
    duration_weeks: phaseLength * phases.length,
    weekly_hours: weeklyHours,
    assumptions: [
      `Plan assumes ${weeklyHours} focused hours per week.`,
      `Timeline is based on roughly ${durationWeeks} weeks.`,
      `Starting level is treated as ${profile.experience_level ?? "beginner"}.`,
    ],
    skill_gaps: skillGaps.length ? skillGaps : ["Portfolio positioning", "Interview practice"],
    phases,
    final_outcome: `A focused portfolio and interview-ready plan for ${targetRole}.`,
    next_steps: [
      "Start with the first weekly task and keep outputs in one portfolio folder.",
      "Book a mentor session to review the project direction.",
      "Review progress after two weeks and adjust scope before adding new tasks.",
    ],
  };
}

function readMentors() {
  if (typeof window === "undefined") {
    return defaultMentors;
  }
  const raw = window.localStorage.getItem(DEMO_MENTORS_KEY);
  if (!raw) {
    return defaultMentors;
  }
  try {
    return JSON.parse(raw) as Mentor[];
  } catch {
    return defaultMentors;
  }
}

function writeMentors(mentors: Mentor[]) {
  window.localStorage.setItem(DEMO_MENTORS_KEY, JSON.stringify(mentors));
}

function targetSkills(profile: UserProfile) {
  const searchText = `${profile.target_role ?? ""} ${profile.primary_goal} ${profile.current_skills.join(" ")}`.toLowerCase();
  if (searchText.includes("frontend") || searchText.includes("web")) {
    return ["HTML", "CSS", "JavaScript", "React", "TypeScript"];
  }
  if (searchText.includes("data")) {
    return ["Excel", "SQL", "data analytics", "dashboarding"];
  }
  if (searchText.includes("cyber")) {
    return ["Linux", "networking", "cybersecurity", "incident analysis"];
  }
  if (searchText.includes("ux") || searchText.includes("design")) {
    return ["Figma", "UI/UX", "prototyping", "user research"];
  }
  if (searchText.includes("ai") || searchText.includes("machine learning")) {
    return ["Python", "machine learning", "deep learning", "model evaluation"];
  }
  return [...profile.current_skills, "Portfolio", "Interview practice"].filter(Boolean);
}

function findKeyword(text: string, keywords: Array<[string, string]>) {
  return keywords.find(([keyword]) => text.includes(keyword))?.[1] ?? null;
}

function inferGoal(details: string, targetRole: string) {
  const match = details.match(/(?:want to|goal is to|looking to|aim to)\s+([^.!?]+)/i);
  return match?.[1] ? sentenceCase(match[1]) : `Become a ${targetRole}`;
}

function inferNumberBefore(text: string, label: string) {
  const match = text.match(new RegExp(`(\\d+)\\s+${label}`));
  return match ? Number(match[1]) : null;
}

function inferExperience(text: string): UserProfile["experience_level"] {
  if (text.includes("advanced") || text.includes("senior")) {
    return "advanced";
  }
  if (text.includes("intermediate") || text.includes("basic")) {
    return "intermediate";
  }
  if (text.includes("beginner") || text.includes("new to")) {
    return "beginner";
  }
  return null;
}

function inferBudget(text: string): UserProfile["budget_preference"] {
  if (text.includes("free")) {
    return "free";
  }
  if (text.includes("low cost") || text.includes("low-cost")) {
    return "low-cost";
  }
  if (text.includes("flexible")) {
    return "flexible";
  }
  return null;
}

function firstSentence(text: string) {
  return sentenceCase(text.split(/[.!?]/)[0]?.trim() ?? "");
}

function sentenceCase(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed.charAt(0).toUpperCase() + trimmed.slice(1) : "";
}

function unique(values: string[]) {
  return [...new Set(values.filter(Boolean))];
}

function missingQuestions(profile: UserProfile) {
  const questions = [];
  if (!profile.primary_goal) {
    questions.push("What career goal or target role do you want to pursue?");
  }
  if (!profile.current_skills.length) {
    questions.push("What skills or tools do you currently know?");
  }
  if (!profile.hours_per_week) {
    questions.push("How many hours can you dedicate each week?");
  }
  return questions.slice(0, 3);
}
