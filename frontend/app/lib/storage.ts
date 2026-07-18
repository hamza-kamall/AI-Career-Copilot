"use client";

import type { UserProfile } from "./types";

const AUTH_KEY = "career-copilot-auth";
const ROLE_KEY = "career-copilot-role";
const PROFILE_KEY = "career-copilot-profile";
const PROMPT_KEY = "career-copilot-last-prompt";
const CHAT_KEY = "career-copilot-chat";

export type StoredChatMessage = {
  id: string;
  role: "ai" | "user";
  title: string;
  body: string;
  items?: string[];
};

export type DemoRole = "learner" | "admin";

export function isDemoAuthenticated() {
  return window.localStorage.getItem(AUTH_KEY) === "true";
}

export function setDemoAuthenticated(value: boolean) {
  window.localStorage.setItem(AUTH_KEY, String(value));
  if (!value) {
    window.localStorage.removeItem(ROLE_KEY);
  }
}

export function getDemoRole(): DemoRole {
  return window.localStorage.getItem(ROLE_KEY) === "admin" ? "admin" : "learner";
}

export function setDemoRole(role: DemoRole) {
  window.localStorage.setItem(ROLE_KEY, role);
}

export function signInDemo(role: DemoRole = "learner") {
  setDemoAuthenticated(true);
  setDemoRole(role);
}

export function signOutDemo() {
  setDemoAuthenticated(false);
  window.localStorage.removeItem(PROFILE_KEY);
  window.localStorage.removeItem(PROMPT_KEY);
  window.localStorage.removeItem(CHAT_KEY);
}

export function saveProfile(profile: UserProfile) {
  window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function loadProfile(): UserProfile | null {
  const raw = window.localStorage.getItem(PROFILE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as UserProfile;
  } catch {
    return null;
  }
}

export function saveLastPrompt(prompt: string) {
  window.localStorage.setItem(PROMPT_KEY, prompt);
}

export function loadLastPrompt() {
  return window.localStorage.getItem(PROMPT_KEY) ?? "";
}

export function saveChatMessages(messages: StoredChatMessage[]) {
  window.localStorage.setItem(CHAT_KEY, JSON.stringify(messages));
}

export function loadChatMessages(): StoredChatMessage[] {
  const raw = window.localStorage.getItem(CHAT_KEY);
  if (!raw) {
    return [];
  }

  try {
    return JSON.parse(raw) as StoredChatMessage[];
  } catch {
    return [];
  }
}
