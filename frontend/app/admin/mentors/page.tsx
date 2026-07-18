"use client";

import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "../../components/AppShell";
import { createMentor, deleteMentor, listMentors, updateMentor } from "../../lib/api";
import type { Mentor } from "../../lib/types";

const emptyMentor: Mentor = {
  id: "",
  name: "",
  job_title: "",
  bio: "",
  expertise: [],
  industries: [],
  years_experience: 0,
  supported_levels: [],
  languages: [],
  available_hours: [],
  price_category: "free",
  mentoring_style: [],
  profile_image: null,
};

const listFields = [
  "expertise",
  "industries",
  "supported_levels",
  "languages",
  "available_hours",
  "mentoring_style",
] as const;

type ListField = (typeof listFields)[number];
type MentorForm = Omit<Mentor, ListField | "years_experience" | "profile_image"> &
  Record<ListField, string> & {
    years_experience: string;
    profile_image: string;
  };

export default function AdminMentorsPage() {
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [form, setForm] = useState<MentorForm>(toForm(emptyMentor));
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    refreshMentors();
  }, []);

  async function refreshMentors() {
    setLoading(true);
    setError("");
    try {
      setMentors(await listMentors());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load mentors.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const mentor = fromForm(form);
      if (editingId) {
        await updateMentor(mentor);
        setMessage("Mentor updated.");
      } else {
        await createMentor(mentor);
        setMessage("Mentor added.");
      }
      setForm(toForm(emptyMentor));
      setEditingId(null);
      await refreshMentors();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save mentor.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(mentor: Mentor) {
    if (!window.confirm(`Delete ${mentor.name}?`)) {
      return;
    }
    setError("");
    setMessage("");
    try {
      await deleteMentor(mentor.id);
      setMessage("Mentor deleted.");
      if (editingId === mentor.id) {
        setForm(toForm(emptyMentor));
        setEditingId(null);
      }
      await refreshMentors();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete mentor.");
    }
  }

  function startEdit(mentor: Mentor) {
    setEditingId(mentor.id);
    setForm(toForm(mentor));
    setMessage("");
    setError("");
  }

  return (
    <AppShell>
      <main className="admin-layout">
        <section className="panel admin-list-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Demo dataset</p>
              <h2>Mentors</h2>
            </div>
            <button className="secondary-button small" onClick={refreshMentors} type="button">
              Refresh
            </button>
          </div>

          {loading && <p className="loading-inline">Loading mentors...</p>}
          <div className="admin-table">
            {mentors.map((mentor) => (
              <article className="admin-row" key={mentor.id}>
                <div>
                  <strong>{mentor.name}</strong>
                  <span>{mentor.job_title}</span>
                </div>
                <span>{mentor.expertise.slice(0, 3).join(", ")}</span>
                <div className="admin-actions">
                  <button className="secondary-button small" onClick={() => startEdit(mentor)} type="button">
                    Edit
                  </button>
                  <button className="ghost-button small danger-button" onClick={() => handleDelete(mentor)} type="button">
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="panel admin-form-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">{editingId ? "Update mentor" : "Add mentor"}</p>
              <h2>{editingId ? form.name || "Edit mentor" : "New mentor"}</h2>
            </div>
            {editingId && (
              <button
                className="ghost-button small"
                onClick={() => {
                  setEditingId(null);
                  setForm(toForm(emptyMentor));
                }}
                type="button"
              >
                Clear
              </button>
            )}
          </div>

          <form className="mentor-form" onSubmit={handleSubmit}>
            <label>
              ID
              <input
                disabled={Boolean(editingId)}
                onChange={(event) => setForm({ ...form, id: event.target.value })}
                placeholder="mentor-ai-002"
                required
                value={form.id}
              />
            </label>
            <label>
              Name
              <input
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                required
                value={form.name}
              />
            </label>
            <label>
              Job title
              <input
                onChange={(event) => setForm({ ...form, job_title: event.target.value })}
                required
                value={form.job_title}
              />
            </label>
            <label>
              Years experience
              <input
                min="0"
                onChange={(event) => setForm({ ...form, years_experience: event.target.value })}
                required
                type="number"
                value={form.years_experience}
              />
            </label>
            <label className="wide-field">
              Bio
              <textarea
                onChange={(event) => setForm({ ...form, bio: event.target.value })}
                required
                rows={4}
                value={form.bio}
              />
            </label>
            <label>
              Expertise
              <input
                onChange={(event) => setForm({ ...form, expertise: event.target.value })}
                placeholder="React, CSS, portfolio"
                required
                value={form.expertise}
              />
            </label>
            <label>
              Industries
              <input
                onChange={(event) => setForm({ ...form, industries: event.target.value })}
                required
                value={form.industries}
              />
            </label>
            <label>
              Supported levels
              <input
                onChange={(event) => setForm({ ...form, supported_levels: event.target.value })}
                placeholder="beginner, intermediate"
                required
                value={form.supported_levels}
              />
            </label>
            <label>
              Languages
              <input
                onChange={(event) => setForm({ ...form, languages: event.target.value })}
                required
                value={form.languages}
              />
            </label>
            <label>
              Available hours
              <input
                onChange={(event) => setForm({ ...form, available_hours: event.target.value })}
                placeholder="weekends, evenings"
                required
                value={form.available_hours}
              />
            </label>
            <label>
              Price category
              <input
                onChange={(event) => setForm({ ...form, price_category: event.target.value })}
                required
                value={form.price_category}
              />
            </label>
            <label>
              Mentoring style
              <input
                onChange={(event) => setForm({ ...form, mentoring_style: event.target.value })}
                required
                value={form.mentoring_style}
              />
            </label>
            <label>
              Profile image URL
              <input
                onChange={(event) => setForm({ ...form, profile_image: event.target.value })}
                value={form.profile_image}
              />
            </label>

            {error && <p className="error-text wide-field">{error}</p>}
            {message && <p className="success-text wide-field">{message}</p>}
            <button className="primary-button wide-field" disabled={saving} type="submit">
              {saving ? "Saving..." : editingId ? "Save Mentor" : "Add Mentor"}
            </button>
          </form>
        </section>
      </main>
    </AppShell>
  );
}

function toForm(mentor: Mentor): MentorForm {
  return {
    ...mentor,
    years_experience: String(mentor.years_experience),
    profile_image: mentor.profile_image ?? "",
    expertise: mentor.expertise.join(", "),
    industries: mentor.industries.join(", "),
    supported_levels: mentor.supported_levels.join(", "),
    languages: mentor.languages.join(", "),
    available_hours: mentor.available_hours.join(", "),
    mentoring_style: mentor.mentoring_style.join(", "),
  };
}

function fromForm(form: MentorForm): Mentor {
  return {
    ...form,
    years_experience: Number(form.years_experience),
    profile_image: form.profile_image.trim() || null,
    expertise: splitList(form.expertise),
    industries: splitList(form.industries),
    supported_levels: splitList(form.supported_levels),
    languages: splitList(form.languages),
    available_hours: splitList(form.available_hours),
    mentoring_style: splitList(form.mentoring_style),
  };
}

function splitList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
