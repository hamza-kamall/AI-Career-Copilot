"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { BrandLogo } from "./BrandLogo";
import { getDemoRole, isDemoAuthenticated, signOutDemo } from "../lib/storage";

const navItems = [
  { href: "/profile-builder", label: "Profile Builder", icon: "PB" },
  { href: "/mentors", label: "Mentors", icon: "MT" },
  { href: "/roadmap", label: "Career Roadmap", icon: "RM" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [role, setRole] = useState<"learner" | "admin">("learner");

  useEffect(() => {
    if (!isDemoAuthenticated()) {
      router.replace("/");
      return;
    }
    const currentRole = getDemoRole();
    setRole(currentRole);
    if (pathname.startsWith("/admin") && currentRole !== "admin") {
      router.replace("/profile-builder");
      return;
    }
    setReady(true);
  }, [pathname, router]);

  const visibleNavItems =
    role === "admin"
      ? [{ href: "/admin/mentors", label: "Manage Mentors", icon: "AD" }]
      : navItems;

  if (!ready) {
    return <main className="loading-screen">Loading workspace...</main>;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" href="/profile-builder">
          <BrandLogo compact />
        </Link>
        <nav className="nav-list" aria-label="Primary navigation">
          {visibleNavItems.map((item) => (
            <Link
              className={`nav-item ${pathname === item.href ? "active" : ""}`}
              href={item.href}
              key={item.href}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="sidebar-note">
          <strong>Demo MVP</strong>
          <span>
            {role === "admin"
              ? "Manage the local mentor dataset for the demo."
              : "Profile, mentors, and roadmap are powered by the local API."}
          </span>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">BootCamp.AI workspace</p>
            <h1>{titleForPath(pathname)}</h1>
          </div>
          <div className="user-chip">
            <span className="avatar">HK</span>
            <span>{role === "admin" ? "Admin Demo" : "Demo User"}</span>
            <button
              className="ghost-button small"
              onClick={() => {
                signOutDemo();
                router.replace("/");
              }}
              type="button"
            >
              Sign out
            </button>
          </div>
        </header>
        {children}
      </div>
    </div>
  );
}

function titleForPath(pathname: string) {
  if (pathname === "/mentors") {
    return "Recommended Mentors";
  }
  if (pathname === "/roadmap") {
    return "Career Roadmap";
  }
  if (pathname === "/admin/mentors") {
    return "Mentor Admin";
  }
  return "AI Profile Builder";
}
