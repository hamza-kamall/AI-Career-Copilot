# AI Career Pilot

Hackathon MVP for converting a natural-language career situation into a structured profile, mentor matches, learning resources, and a roadmap.

This repository is being implemented incrementally from the PRD.

## Revised Stack

- Frontend: Next.js
- Backend: FastAPI
- Database: Supabase PostgreSQL
- Deployment: Vercel for frontend, Render for backend

## Current Increment

- Repository structure
- Pydantic data models
- Demo mentor and resource data
- Deterministic mentor matching
- Unit tests for mentor scoring

## Repository Layout

```text
backend/
  app/
    main.py
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
    page.tsx
  package.json
```

