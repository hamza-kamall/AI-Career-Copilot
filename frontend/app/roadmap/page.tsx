"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell } from "../components/AppShell";
import { generateRoadmap } from "../lib/api";
import { loadProfile } from "../lib/storage";
import type { CareerRoadmap } from "../lib/types";

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<CareerRoadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const profile = loadProfile();
    if (!profile) {
      setLoading(false);
      return;
    }

    generateRoadmap(profile)
      .then(setRoadmap)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not generate roadmap."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <main className="stack">
        {!roadmap && !loading && !error && (
          <section className="panel empty-route">
            <h2>Create a profile first</h2>
            <p>The roadmap needs your generated career profile.</p>
            <Link className="primary-button link-button" href="/profile-builder">
              Go to Profile Builder
            </Link>
          </section>
        )}
        {loading && <p className="loading-inline">Generating roadmap...</p>}
        {error && <p className="error-text">{error}</p>}
        {roadmap && (
          <>
            <section className="panel roadmap-hero">
              <div>
                <p className="eyebrow">Personalized plan</p>
                <h2>{roadmap.roadmap_title}</h2>
                <p>{roadmap.career_goal}</p>
              </div>
              <div className="roadmap-stats">
                <div>
                  <strong>{roadmap.duration_weeks}</strong>
                  <span>weeks</span>
                </div>
                <div>
                  <strong>{roadmap.weekly_hours}</strong>
                  <span>hrs/week</span>
                </div>
                <div>
                  <strong>{roadmap.phases.length}</strong>
                  <span>phases</span>
                </div>
              </div>
            </section>

            <section className="roadmap-layout">
              <div className="timeline">
                {roadmap.phases.map((phase) => (
                  <article className="panel phase-card" key={phase.phase_number}>
                    <div className="phase-number">{phase.phase_number}</div>
                    <div className="phase-content">
                      <div className="section-heading">
                        <div>
                          <h3>{phase.title}</h3>
                          <p>{phase.objective}</p>
                        </div>
                        <span className="status-pill">{phase.duration_weeks} weeks</span>
                      </div>
                      <div className="tag-list">
                        {phase.skills.map((skill) => (
                          <span className="tag" key={skill}>
                            {skill}
                          </span>
                        ))}
                      </div>
                      <div className="roadmap-detail-grid">
                        <div>
                          <h4>Weekly tasks</h4>
                          <div className="week-list">
                            {phase.weekly_tasks.map((week) => (
                              <div className="week-block" key={week.week}>
                                <strong>
                                  Week {week.week} · {week.estimated_hours} hrs
                                </strong>
                                <ul>
                                  {week.tasks.map((task) => (
                                    <li key={task}>{task}</li>
                                  ))}
                                </ul>
                              </div>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4>{phase.project.title}</h4>
                          <p>{phase.project.description}</p>
                        </div>
                        <div>
                          <h4>Completion</h4>
                          <ul>
                            {phase.completion_criteria.map((item) => (
                              <li key={item}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </article>
                ))}
              </div>

              <aside className="panel roadmap-side">
                <h3>Skill gaps</h3>
                <div className="tag-list">
                  {roadmap.skill_gaps.map((skill) => (
                    <span className="tag" key={skill}>
                      {skill}
                    </span>
                  ))}
                </div>
                <h3>Assumptions</h3>
                <ul>
                  {roadmap.assumptions.map((assumption) => (
                    <li key={assumption}>{assumption}</li>
                  ))}
                </ul>
                <h3>Next steps</h3>
                <ul>
                  {roadmap.next_steps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ul>
              </aside>
            </section>
          </>
        )}
      </main>
    </AppShell>
  );
}
