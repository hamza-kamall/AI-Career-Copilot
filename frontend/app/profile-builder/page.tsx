"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "../components/AppShell";
import { extractProfile } from "../lib/api";
import {
  loadChatMessages,
  loadProfile,
  saveChatMessages,
  saveLastPrompt,
  saveProfile,
  type StoredChatMessage,
} from "../lib/storage";
import type { UserProfile } from "../lib/types";

export default function ProfileBuilderPage() {
  const router = useRouter();
  const [details, setDetails] = useState("");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [followUps, setFollowUps] = useState<string[]>([]);
  const [messages, setMessages] = useState<StoredChatMessage[]>(defaultMessages);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setProfile(loadProfile());
    const savedMessages = loadChatMessages();
    if (savedMessages.length > 0) {
      setMessages(savedMessages);
    }
  }, []);

  useEffect(() => {
    saveChatMessages(messages);
  }, [messages]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedDetails = details.trim();
    if (!trimmedDetails) {
      setError("Enter your profile details before generating a profile.");
      return;
    }

    setLoading(true);
    setError("");
    const existingProfile = profile;
    const userMessage: StoredChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      title: "You",
      body: trimmedDetails,
    };
    setMessages((current) => [...current, userMessage]);

    try {
      const response = await extractProfile(trimmedDetails, existingProfile);
      setProfile(response.profile);
      setFollowUps(response.follow_up_questions);
      saveProfile(response.profile);
      saveLastPrompt(trimmedDetails);
      setDetails("");
      setMessages((current) => [
        ...current,
        {
          id: `ai-${Date.now()}`,
          role: "ai",
          title: existingProfile ? "Profile updated" : "Profile generated",
          body: profileResponseText(response.profile, Boolean(existingProfile)),
          items: response.follow_up_questions,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not extract profile.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <main className="two-column">
        <section className="panel chat-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">AI intake</p>
              <h2>Chat with the assistant</h2>
            </div>
            <span className="status-pill">Live API</span>
          </div>

          <div className="chat-stream">
            {messages.map((message) => (
              <div className={`message ${message.role}`} key={message.id}>
                <strong>{message.title}</strong>
                <p>{message.body}</p>
                {message.items && message.items.length > 0 && (
                  <ul>
                    {message.items.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>

          <form className="chat-form" onSubmit={handleSubmit}>
            <textarea
              onChange={(event) => setDetails(event.target.value)}
              rows={5}
              value={details}
            />
            {error && <p className="error-text">{error}</p>}
            <div className="button-row">
              <button className="primary-button" disabled={loading} type="submit">
                {loading ? "Generating..." : "Generate Profile"}
              </button>
              <button
                className="secondary-button"
                disabled={!profile}
                onClick={() => router.push("/mentors")}
                type="button"
              >
                Submit Profile
              </button>
            </div>
          </form>
        </section>

        <section className="panel profile-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Generated resume card</p>
              <h2>{profile?.target_role ?? "Profile preview"}</h2>
            </div>
            <span className="score-ring">{profile ? "75%" : "0%"}</span>
          </div>
          {profile ? <ProfileSummary profile={profile} /> : <EmptyProfile />}
        </section>
      </main>
    </AppShell>
  );
}

const defaultMessages: StoredChatMessage[] = [
  {
    id: "welcome",
    role: "ai",
    title: "AI Career Copilot",
    body:
      "Tell me your current situation, target role, skills, timeline, budget, and weekly availability.",
  },
];

function profileResponseText(profile: UserProfile, wasUpdated: boolean) {
  const role = profile.target_role ?? "your target role";
  const skillText = profile.current_skills.length
    ? `Your strongest current signals are ${profile.current_skills.join(", ")}.`
    : "I still need your current skills to improve the recommendation quality.";
  const action = wasUpdated ? "updated your profile" : "built a structured profile";
  return `I ${action} for ${role}. ${skillText} Next, submit this profile to match mentors and generate your roadmap.`;
}

function ProfileSummary({ profile }: { profile: UserProfile }) {
  return (
    <div className="profile-grid">
      <InfoBlock title="Goal" value={profile.primary_goal || "Not provided"} />
      <InfoBlock title="Current situation" value={profile.current_situation || "Not provided"} />
      <InfoBlock title="Timeline" value={profile.deadline_months ? `${profile.deadline_months} months` : "Not provided"} />
      <InfoBlock title="Weekly time" value={profile.hours_per_week ? `${profile.hours_per_week} hours` : "Not provided"} />
      <InfoBlock title="Experience" value={profile.experience_level ?? "Not provided"} />
      <InfoBlock title="Budget" value={profile.budget_preference ?? "Not provided"} />
      <TagBlock title="Skills" values={profile.current_skills} />
      <TagBlock title="Learning style" values={profile.learning_preferences} />
      <TagBlock title="Languages" values={profile.languages} />
      <TagBlock title="Mentor preferences" values={profile.mentor_preferences} />
    </div>
  );
}

function InfoBlock({ title, value }: { title: string; value: string }) {
  return (
    <div className="info-block">
      <span>{title}</span>
      <strong>{value}</strong>
    </div>
  );
}

function TagBlock({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="info-block wide">
      <span>{title}</span>
      <div className="tag-list">
        {(values.length ? values : ["Not provided"]).map((value) => (
          <span className="tag" key={value}>
            {value}
          </span>
        ))}
      </div>
    </div>
  );
}

function EmptyProfile() {
  return (
    <div className="empty-state">
      <strong>No profile generated yet</strong>
      <p>Send a career prompt and the backend will convert it into structured profile data.</p>
    </div>
  );
}
