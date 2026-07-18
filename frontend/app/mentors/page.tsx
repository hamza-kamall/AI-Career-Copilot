"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell } from "../components/AppShell";
import { recommendMentors } from "../lib/api";
import { loadProfile } from "../lib/storage";
import type { MentorMatch, UserProfile } from "../lib/types";

export default function MentorsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [matches, setMatches] = useState<MentorMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
          {matches.map((match) => (
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
              <Link className="secondary-button full" href="/roadmap">
                Continue to Roadmap
              </Link>
            </article>
          ))}
        </section>
      </main>
    </AppShell>
  );
}

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
