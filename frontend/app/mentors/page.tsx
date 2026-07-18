"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "../components/AppShell";
import { recommendMentors } from "../lib/api";
import { loadProfile } from "../lib/storage";
import type { MentorMatch, UserProfile } from "../lib/types";

export default function MentorsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [matches, setMatches] = useState<MentorMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [schedulingMentorId, setSchedulingMentorId] = useState<string | null>(null);
  const [scheduledSession, setScheduledSession] = useState<ScheduledSession | null>(null);
  const [scheduleForm, setScheduleForm] = useState({
    date: "",
    time: "",
    format: "Video call",
    notes: "",
  });

  useEffect(() => {
    const savedProfile = loadProfile();
    setProfile(savedProfile);

    if (!savedProfile) {
      setLoading(false);
      return;
    }

    recommendMentors(savedProfile, 6)
      .then(setMatches)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load mentors."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <main className="stack">
        <section className="panel compact-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Based on your generated profile</p>
              <h2>{profile?.target_role ?? "Mentor matches"}</h2>
            </div>
            <div className="filter-row" aria-label="Visual filters">
              <span className="filter active">All mentors</span>
              <span className="filter">Available now</span>
              <span className="filter">Best match</span>
            </div>
          </div>
        </section>

        {!profile && (
          <EmptyRoute
            title="Create a profile first"
            message="Mentor matching needs your structured career profile."
            href="/profile-builder"
            action="Go to Profile Builder"
          />
        )}
        {loading && <p className="loading-inline">Loading mentor recommendations...</p>}
        {error && <p className="error-text">{error}</p>}

        <section className="mentor-grid">
          {matches.map((match) => {
            const isScheduling = schedulingMentorId === match.mentor.id;

            return (
            <article className="mentor-card" key={match.mentor.id}>
              <div className="mentor-header">
                <div className="avatar large">{initials(match.mentor.name)}</div>
                <div>
                  <h3>{match.mentor.name}</h3>
                  <p>{match.mentor.job_title}</p>
                </div>
                <span className="match-score">{Math.round(match.score)}%</span>
              </div>
              <p className="mentor-bio">{match.mentor.bio}</p>
              <div className="tag-list">
                {match.mentor.expertise.slice(0, 4).map((item) => (
                  <span className="tag" key={item}>
                    {item}
                  </span>
                ))}
              </div>
              <dl className="mentor-meta">
                <div>
                  <dt>Experience</dt>
                  <dd>{match.mentor.years_experience} years</dd>
                </div>
                <div>
                  <dt>Availability</dt>
                  <dd>{match.mentor.available_hours.join(", ")}</dd>
                </div>
                <div>
                  <dt>Price</dt>
                  <dd>{match.mentor.price_category}</dd>
                </div>
              </dl>
              <p className="explanation">{match.explanation}</p>
              <button
                className="secondary-button full"
                onClick={() => {
                  setSchedulingMentorId(match.mentor.id);
                  setScheduledSession(null);
                }}
                type="button"
              >
                {isScheduling ? "Choose session time" : "Schedule 1-hour mentorship session"}
              </button>

              {isScheduling && (
                <form className="schedule-form" onSubmit={(event) => handleScheduleSubmit(event, match)}>
                  <label>
                    Date
                    <input
                      min={new Date().toISOString().split("T")[0]}
                      onChange={(event) => setScheduleForm({ ...scheduleForm, date: event.target.value })}
                      required
                      type="date"
                      value={scheduleForm.date}
                    />
                  </label>
                  <label>
                    Time
                    <input
                      onChange={(event) => setScheduleForm({ ...scheduleForm, time: event.target.value })}
                      required
                      type="time"
                      value={scheduleForm.time}
                    />
                  </label>
                  <label>
                    Session type
                    <select
                      onChange={(event) => setScheduleForm({ ...scheduleForm, format: event.target.value })}
                      value={scheduleForm.format}
                    >
                      <option>Video call</option>
                      <option>Phone call</option>
                      <option>In-person</option>
                    </select>
                  </label>
                  <label className="wide-field">
                    Notes for your mentor
                    <textarea
                      onChange={(event) => setScheduleForm({ ...scheduleForm, notes: event.target.value })}
                      placeholder="Share a goal, question, or topic for the session."
                      rows={3}
                      value={scheduleForm.notes}
                    />
                  </label>
                  <div className="button-row wide-field">
                    <button className="primary-button" type="submit">
                      Request session
                    </button>
                    <button
                      className="ghost-button"
                      onClick={() => setSchedulingMentorId(null)}
                      type="button"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </article>
            );
          })}
        </section>

        {scheduledSession && (
          <section className="panel schedule-confirmation" role="status">
            <div>
              <p className="eyebrow">Mentorship session</p>
              <h2>Session request sent</h2>
              <p>
                Your {scheduledSession.format.toLowerCase()} with {scheduledSession.mentorName} is
                requested for {formatSessionDate(scheduledSession.date)} at {scheduledSession.time}.
              </p>
            </div>
            <button
              className="ghost-button small"
              onClick={() => setScheduledSession(null)}
              type="button"
            >
              Dismiss
            </button>
          </section>
        )}
      </main>
    </AppShell>
  );

  function handleScheduleSubmit(event: FormEvent<HTMLFormElement>, match: MentorMatch) {
    event.preventDefault();
    setScheduledSession({
      mentorName: match.mentor.name,
      date: scheduleForm.date,
      time: scheduleForm.time,
      format: scheduleForm.format,
      notes: scheduleForm.notes,
    });
    setSchedulingMentorId(null);
    setScheduleForm({
      date: "",
      time: "",
      format: "Video call",
      notes: "",
    });
  }
}

type ScheduledSession = {
  mentorName: string;
  date: string;
  time: string;
  format: string;
  notes: string;
};

function EmptyRoute({
  title,
  message,
  href,
  action,
}: {
  title: string;
  message: string;
  href: string;
  action: string;
}) {
  return (
    <section className="panel empty-route">
      <h2>{title}</h2>
      <p>{message}</p>
      <Link className="primary-button link-button" href={href}>
        {action}
      </Link>
    </section>
  );
}

function initials(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function formatSessionDate(date: string) {
  return new Intl.DateTimeFormat("en", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date(`${date}T00:00:00`));
}
