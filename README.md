# BootCamp.AI

Hackathon MVP for converting a natural-language career situation into a structured profile, mentor matches, learning resources, and a personalized roadmap.

## Deployment

Public ChatGPT Sites URL:

https://ai-career-pilot.hothi9022035.chatgpt.site

The deployed Sites build is public, so anybody with the link can access it. The frontend still supports the FastAPI backend for local or hosted API usage. If the backend API is not reachable from the deployed site, the frontend falls back to deterministic browser-side demo responses so evaluators can complete the profile, mentor, roadmap, and admin flows without private infrastructure.

Demo credentials:

- Learner: any email/password except the admin credentials
- Admin: `admin@career.local` / `admin123`

## Stack

- Frontend: Next.js 15, React 19, TypeScript
- Backend: FastAPI, Pydantic, pytest
- AI provider: deterministic mock by default, optional Gemini-compatible structured generation
- Deployment: ChatGPT Sites for the public frontend

## Features

- Marketing landing page with demo sign-in
- AI profile builder from natural-language career input
- Structured profile persistence in browser local storage
- Mentor recommendation and scheduling demo flow
- Personalized roadmap generation
- Admin mentor dataset management
- FastAPI endpoints and unit tests for backend services
- Public deployment fallback mode when no backend URL is available

## Repository Layout

```text
backend/
  app/main.py
  data/
    mentors.json
    resources.json
  src/
    models/
    repositories/
    services/
    prompts/
    utils/
  tests/
frontend/
  app/
    admin/
    components/
    lib/
    mentors/
    profile-builder/
    roadmap/
  public/
  package.json
scripts/
  build-sites.mjs
```

## Environment Variables

Create local env files from the examples:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
```

Backend variables:

```env
LLM_PROVIDER=mock
LLM_MODEL=gemini-3.5-flash
GEMINI_API_KEY=
LLM_API_KEY=
SUPABASE_URL=https://example-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=example-service-role-key
```

Backend variable notes:

- `LLM_PROVIDER`: Use `mock` for deterministic local testing. Use `gemini` when a Gemini API key is available.
- `LLM_MODEL`: Model name passed to the configured LLM provider.
- `GEMINI_API_KEY`: Gemini API key for live AI profile or roadmap generation.
- `LLM_API_KEY`: Generic fallback key slot for future provider integrations.
- `SUPABASE_URL`: Reserved for future persistence features.
- `SUPABASE_SERVICE_ROLE_KEY`: Reserved for future Supabase server-side access.

Frontend variables:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Frontend variable notes:

- `NEXT_PUBLIC_API_BASE_URL`: Public base URL for the FastAPI backend. For local development, keep `http://127.0.0.1:8000`. For hosted API testing, set this to the deployed backend URL, for example `https://bootcamp-ai-api.example.com`.
- If this API is unreachable, the deployed frontend uses deterministic demo fallback data so the app remains testable.

## Local Setup

Install backend dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Install frontend dependencies:

```powershell
cd frontend
pnpm install
```

Run the backend:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If your shell does not accept the path above, use:

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run the frontend in another terminal:

```powershell
cd frontend
pnpm dev
```

Open `http://127.0.0.1:3000`.

## Testing And Build

Backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests
```

Frontend production build:

```powershell
pnpm --dir frontend build
```

Sites build wrapper:

```powershell
pnpm build
```

## Low-Level Design Review

The backend is organized around explicit Pydantic models, repository helpers for local JSON data, and services for profile extraction, mentor scoring, LLM access, and roadmap generation. This keeps API routes thin and makes the deterministic fallback behavior testable.

The frontend keeps route-level UI in `frontend/app/*`, shared shell/branding in `frontend/app/components`, browser persistence in `frontend/app/lib/storage.ts`, API integration in `frontend/app/lib/api.ts`, and deployment-safe demo fallbacks in `frontend/app/lib/demoApi.ts`.

Known limitations:

- Demo authentication is local-storage based and intended only for MVP evaluation.
- Admin changes in the public Sites fallback are stored in the visitor's browser, not a shared database.
- Supabase variables are placeholders for future persistence and are not required for the current MVP.
