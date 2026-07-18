"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { isDemoAuthenticated, setDemoAuthenticated } from "./lib/storage";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@career.local");
  const [password, setPassword] = useState("password");

  useEffect(() => {
    if (isDemoAuthenticated()) {
      router.replace("/profile-builder");
    }
  }, [router]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setDemoAuthenticated(true);
    router.push("/profile-builder");
  }

  function startDemo(path = "/profile-builder") {
    setDemoAuthenticated(true);
    router.push(path);
  }

  return (
    <main className="marketing-page">
      <section className="hero-section">
        <nav className="marketing-nav" aria-label="Primary navigation">
          <a className="brand marketing-brand" href="#top">
            <span className="brand-mark">AI</span>
            <span>AI Career Pilot</span>
          </a>
          <div className="marketing-links">
            <a href="#how-it-works">How It Works</a>
            <a href="/mentors">Mentors</a>
            <a href="/roadmap">Roadmaps</a>
            <a href="#resources">Resources</a>
          </div>
          <div className="nav-actions">
            <a className="login-link" href="#login">
              Log In
            </a>
            <button className="primary-button nav-cta" onClick={() => startDemo()} type="button">
              Get Started
            </button>
          </div>
        </nav>

        <div className="hero-grid" id="top">
          <section className="hero-copy">
            <p className="eyebrow hero-eyebrow">Personalized AI career planning</p>
            <h1>Build your career with a plan designed for you.</h1>
            <p className="hero-text">
              Describe your goals, skills, and constraints. AI Career Pilot creates a
              personalized roadmap and connects you with the right mentors.
            </p>
            <div className="button-row hero-actions">
              <button className="primary-button hero-button" onClick={() => startDemo()} type="button">
                Create My Career Plan
              </button>
              <button className="secondary-button hero-secondary" onClick={() => startDemo("/mentors")} type="button">
                Explore Mentors
              </button>
            </div>
          </section>

          <section className="career-profile-card" aria-label="Career profile preview">
            <div className="profile-card-header">
              <div>
                <p className="eyebrow">Profile readiness</p>
                <h2>Data Analyst Track</h2>
              </div>
              <span className="profile-score">82%</span>
            </div>
            <div className="progress-track" aria-hidden="true">
              <span />
            </div>
            <div className="career-card-grid">
              <div>
                <span>Goal</span>
                <strong>Junior data analyst</strong>
              </div>
              <div>
                <span>Timeline</span>
                <strong>16 weeks</strong>
              </div>
              <div>
                <span>Weekly focus</span>
                <strong>8 hours</strong>
              </div>
              <div>
                <span>Mentor match</span>
                <strong>Python + SQL</strong>
              </div>
            </div>
            <div className="roadmap-preview">
              <span className="preview-step active">1</span>
              <span className="preview-line" />
              <span className="preview-step">2</span>
              <span className="preview-line" />
              <span className="preview-step purple">3</span>
            </div>
            <div className="resource-strip">
              <span>SQL portfolio project</span>
              <strong>Next up</strong>
            </div>
          </section>
        </div>
      </section>

      <section className="features-section" id="how-it-works">
        <div className="features-heading">
          <p className="eyebrow">How It Works</p>
          <h2>Guidance that moves from goals to action.</h2>
        </div>
        <div className="feature-grid">
          <article className="feature-card">
            <span className="feature-icon">01</span>
            <h3>Personalized Career Roadmap</h3>
            <p>Get a structured learning plan based on your current skills, timeline, and availability.</p>
          </article>
          <article className="feature-card">
            <span className="feature-icon purple">02</span>
            <h3>Matched with the Right Mentor</h3>
            <p>Discover mentors ranked according to your goals, level, language, and preferences.</p>
          </article>
          <article className="feature-card" id="resources">
            <span className="feature-icon">03</span>
            <h3>Verified Learning Resources</h3>
            <p>Learn from curated courses, documentation, projects, and tutorials without random or broken links.</p>
          </article>
        </div>
      </section>

      <section className="login-section" id="login">
        <div className="login-card">
          <p className="eyebrow">AI Career Pilot</p>
          <h2>Log in to your workspace</h2>
          <p className="muted">Sign in to continue your career planning demo.</p>
          <form className="form-stack" onSubmit={handleSubmit}>
            <label>
              Email
              <input
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                type="email"
                value={email}
              />
            </label>
            <label>
              Password
              <input
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter password"
                type="password"
                value={password}
              />
            </label>
            <button className="primary-button" type="submit">
              Sign in
            </button>
          </form>
          <p className="fine-print">
            Demo auth stores only a local browser flag. No real account is created.
          </p>
        </div>
      </section>
    </main>
  );
}
