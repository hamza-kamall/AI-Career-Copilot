import type {
  CareerRoadmap,
  Mentor,
  MentorMatch,
  ProfileExtractionResponse,
  UserProfile,
} from "./types";
import {
  createDemoMentor,
  deleteDemoMentor,
  extractDemoProfile,
  generateDemoRoadmap,
  getDemoMentors,
  recommendDemoMentors,
  updateDemoMentor,
} from "./demoApi";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function postJson<TResponse>(path: string, body: unknown): Promise<TResponse> {
  return requestJson<TResponse>(path, {
    method: "POST",
    body,
  });
}

async function requestJson<TResponse>(
  path: string,
  options: { method?: string; body?: unknown } = {},
): Promise<TResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method ?? "GET",
      headers:
        options.body === undefined
          ? undefined
          : {
              "Content-Type": "application/json",
            },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || `Request failed with status ${response.status}`);
    }

    if (response.status === 204) {
      return undefined as TResponse;
    }

    return response.json() as Promise<TResponse>;
  } catch (error) {
    if (error instanceof Error && !error.message.includes("fetch")) {
      throw error;
    }
    throw new Error(`Could not connect to the backend API at ${API_BASE_URL}.`);
  }
}

export function extractProfile(details: string, existingProfile?: UserProfile | null) {
  return postJson<ProfileExtractionResponse>("/profiles/extract", {
    details,
    existing_profile: existingProfile ?? null,
  }).catch((error) => {
    if (isConnectionError(error)) {
      return extractDemoProfile(details, existingProfile);
    }
    throw error;
  });
}

export async function recommendMentors(profile: UserProfile, limit = 6) {
  const response = await postJson<{ matches: MentorMatch[] }>("/mentors/recommend", {
    profile,
    limit,
  }).catch((error) => {
    if (isConnectionError(error)) {
      return { matches: recommendDemoMentors(profile, limit) };
    }
    throw error;
  });
  return response.matches;
}

export function listMentors() {
  return requestJson<Mentor[]>("/mentors").catch((error) => {
    if (isConnectionError(error)) {
      return getDemoMentors();
    }
    throw error;
  });
}

export function createMentor(mentor: Mentor) {
  return postJson<Mentor>("/admin/mentors", mentor).catch((error) => {
    if (isConnectionError(error)) {
      return createDemoMentor(mentor);
    }
    throw error;
  });
}

export function updateMentor(mentor: Mentor) {
  return requestJson<Mentor>(`/admin/mentors/${mentor.id}`, {
    method: "PUT",
    body: mentor,
  }).catch((error) => {
    if (isConnectionError(error)) {
      return updateDemoMentor(mentor);
    }
    throw error;
  });
}

export function deleteMentor(mentorId: string) {
  return requestJson<void>(`/admin/mentors/${mentorId}`, {
    method: "DELETE",
  }).catch((error) => {
    if (isConnectionError(error)) {
      deleteDemoMentor(mentorId);
      return undefined;
    }
    throw error;
  });
}

export async function generateRoadmap(profile: UserProfile) {
  const response = await postJson<{ roadmap: CareerRoadmap }>("/roadmaps/generate", {
    profile,
  }).catch((error) => {
    if (isConnectionError(error)) {
      return { roadmap: generateDemoRoadmap(profile) };
    }
    throw error;
  });
  return response.roadmap;
}

function isConnectionError(error: unknown) {
  return error instanceof Error && error.message.startsWith("Could not connect to the backend API");
}
