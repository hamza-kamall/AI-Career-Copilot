import type {
  CareerRoadmap,
  MentorMatch,
  ProfileExtractionResponse,
  UserProfile,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const LOCAL_API_FALLBACKS = [
  API_BASE_URL,
  "http://127.0.0.1:8002",
  "http://127.0.0.1:8001",
  "http://127.0.0.1:8000",
];

async function postJson<TResponse>(path: string, body: unknown): Promise<TResponse> {
  let lastError: unknown = null;

  for (const baseUrl of [...new Set(LOCAL_API_FALLBACKS)]) {
    try {
      const response = await fetch(`${baseUrl}${path}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `Request failed with status ${response.status}`);
      }

      return response.json() as Promise<TResponse>;
    } catch (error) {
      if (error instanceof Error && !error.message.includes("fetch")) {
        throw error;
      }
      lastError = error;
    }
  }

  throw lastError instanceof Error
    ? lastError
    : new Error("Could not connect to the backend API.");
}

export function extractProfile(details: string, existingProfile?: UserProfile | null) {
  return postJson<ProfileExtractionResponse>("/profiles/extract", {
    details,
    existing_profile: existingProfile ?? null,
  });
}

export async function recommendMentors(profile: UserProfile, limit = 6) {
  const response = await postJson<{ matches: MentorMatch[] }>("/mentors/recommend", {
    profile,
    limit,
  });
  return response.matches;
}

export async function generateRoadmap(profile: UserProfile) {
  const response = await postJson<{ roadmap: CareerRoadmap }>("/roadmaps/generate", {
    profile,
  });
  return response.roadmap;
}
