export type UserProfile = {
  current_situation: string;
  primary_goal: string;
  target_role: string | null;
  current_skills: string[];
  experience_level: "beginner" | "intermediate" | "advanced" | null;
  deadline_months: number | null;
  hours_per_week: number | null;
  budget_preference: "free" | "low-cost" | "flexible" | "unspecified" | null;
  learning_preferences: string[];
  location: string | null;
  languages: string[];
  mentor_preferences: string[];
  constraints: string[];
  missing_information: string[];
};

export type ProfileExtractionResponse = {
  profile: UserProfile;
  follow_up_questions: string[];
};

export type Mentor = {
  id: string;
  name: string;
  job_title: string;
  bio: string;
  expertise: string[];
  industries: string[];
  years_experience: number;
  supported_levels: string[];
  languages: string[];
  available_hours: string[];
  price_category: string;
  mentoring_style: string[];
  profile_image: string | null;
};

export type MentorMatch = {
  mentor: Mentor;
  score: number;
  component_scores: Record<string, number>;
  explanation: string;
};

export type WeeklyTask = {
  week: number;
  tasks: string[];
  estimated_hours: number;
};

export type RoadmapProject = {
  title: string;
  description: string;
  deliverables: string[];
};

export type RoadmapPhase = {
  phase_number: number;
  title: string;
  duration_weeks: number;
  objective: string;
  skills: string[];
  weekly_tasks: WeeklyTask[];
  project: RoadmapProject;
  completion_criteria: string[];
  resource_ids: string[];
};

export type CareerRoadmap = {
  roadmap_title: string;
  career_goal: string;
  duration_weeks: number;
  weekly_hours: number;
  assumptions: string[];
  skill_gaps: string[];
  phases: RoadmapPhase[];
  final_outcome: string;
  next_steps: string[];
};
