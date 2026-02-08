# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service following hexagonal architecture. Source in `backend/src/app` with `domain/`, `ports/`, `usecases/`, and `adapters/` (inbound API/SSE and outbound persistence/messaging/notifications).
- `frontend/`: Vite + React client. Code in `frontend/src` with `components/`, `hooks/`, and `api/`.
- `openspec/`: Product specs and change artifacts (not runtime code).
- `docker-compose.yml`: Local dev stack (API, worker, frontend, Postgres, Redis, Mailpit).

## Build, Test, and Development Commands
- `docker compose up --build`: Run the full stack locally.
- `cd backend && uv sync --no-dev`: Install backend deps with `uv`.
- `cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`: Run the API locally.
- `cd backend && uv run python -m app.worker`: Run the background worker.
- `cd frontend && bun install`: Install frontend deps.
- `cd frontend && bun run dev`: Run the Vite dev server on port 5173.

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indentation, keep modules small and aligned with hexagonal layers (`domain`, `ports`, `usecases`, `adapters`).
- TypeScript/React: 2-space indentation, `PascalCase` components (e.g., `JobList.tsx`), `camelCase` hooks/utilities (e.g., `useJobSSE.ts`).
- No formatter or linter configured; match existing file style.

## Testing Guidelines
- No test framework is currently set up. If you add tests:
  - Backend: place under `backend/tests`.
  - Frontend: place under `frontend/tests`.
  - Document how to run them in your PR.

## Commit & Pull Request Guidelines
- Git history isn’t available here; use clear, scoped commit messages (e.g., `backend: add redis event publisher`).
- PRs should include:
  - Short summary of changes.
  - Testing notes (commands + results).
  - Any required environment variables.

## Configuration Notes
- Required env vars are defined in `docker-compose.yml` (e.g., `DATABASE_URL`, `REDIS_URL`, SMTP, Discord settings). Set them when running services outside Docker.
