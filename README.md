# NexaCart — E-Commerce Platform & SDET Automation

NexaCart is a multi-category e-commerce application being planned alongside a professional SDET automation framework. The application will support product discovery, shopping carts, checkout with simulated payments, order management and inventory rules. The portfolio focus is the quality engineering around those workflows: UI automation, REST API testing, database validation, BDD and CI/CD.

> **Project status:** Implementation phase, milestone M0 (engineering foundation). The PRD, user stories, design, technical architecture v0.9, database schema/ERD v0.9 and [implementation plan & backlog v0.1](https://github.com/thabo81/nexacart-ecommerce-sdet/blob/main/docs/planning/IMPLEMENTATION_PLAN_AND_BACKLOG.md) are owner-approved planning baselines. FOUND-001 (project structure) is merged. FOUND-002 (Docker Compose and readiness) is implemented on a feature branch and awaits owner/QA review. No e-commerce features, database models or migrations exist yet. Planned functionality is not implemented or verified until the planning documents say so.

## Project goals

- Build a realistic shopping application across computers, custom PCs, laptops, smartphones, audio/wearables, football shirts and footwear.
- Implement application behaviour with explicit business rules and REST APIs.
- Build a maintainable automation framework using Playwright with Python, Pytest, HTTPX and PostgreSQL validation.
- Verify critical behaviour across UI, API, database and integration layers.
- Run automated checks in GitHub Actions and publish useful failure evidence.

## Technology stack

| Area | Planned technology |
| --- | --- |
| Frontend | React + TypeScript |
| Backend | Python + FastAPI |
| Database / ORM | PostgreSQL + SQLAlchemy |
| UI automation | Playwright for Python + Pytest |
| API testing | HTTPX + Pytest |
| BDD | pytest-bdd / Gherkin for selected business flows |
| Reporting | Allure |
| Local test environment | Docker Compose |
| CI/CD | GitHub Actions |

## Important project boundaries

- Payments are simulated; the application will not process real payments or store payment card details.
- The backend is authoritative for prices, discounts, stock and order totals.
- Product imagery must be generated, owned or used under appropriate licence terms. The project will not scrape retail websites.
- Test cases must check real outcomes; assertions must not be weakened simply to obtain a green build.
- Implementation proceeds in owner-approved milestones. Do not treat planned functionality as implemented until it has been built and verified.

## How we will work

- **Claude:** application implementation, API contracts, database migrations and application defect fixes.
- **ChatGPT:** SDET strategy, test design, Playwright/Pytest automation, API tests, SQL validation, failure analysis and test framework review.
- **Project owner:** reviews requirements, approves design decisions, runs commands and confirms changes.

Both workstreams must use the approved documents in [docs/planning](docs/planning/README.md) as their source of truth.

## Planning documents

Approved planning baselines are maintained in [docs/planning](docs/planning/README.md):

1. [Product Requirements Document (PRD)](docs/planning/PRD.md) — approved v0.7
2. [User Stories & Application Flows](docs/planning/USER_STORIES_AND_FLOWS.md) — approved v0.4
3. [Design Brief & Wireframes](docs/planning/DESIGN_BRIEF_AND_WIREFRAMES.md) — approved v0.4; real-browser verification remains pending
4. [Technical Architecture](docs/planning/TECHNICAL_ARCHITECTURE.md) — owner-approved planning baseline v0.9
5. [Database Schema & ERD](docs/planning/DATABASE_SCHEMA_AND_ERD.md) — owner-approved planning baseline v0.9
6. [Implementation Plan & Backlog](https://github.com/thabo81/nexacart-ecommerce-sdet/blob/main/docs/planning/IMPLEMENTATION_PLAN_AND_BACKLOG.md) — v0.1, owner-approved 2026-10-21; published on `main`

Start with [the master project brief](docs/planning/PROJECT_BRIEF.md).

## Repository layout (FOUND-001)

```text
docs/
  planning/       # Approved product and architecture documents
  testing/        # Test strategy, coverage, execution evidence and defects
app/              # FastAPI backend and worker (one codebase)
  main.py         # API entry point: uvicorn app.main:create_app --factory
  core/           # Typed configuration; observability/health checks (security arrives later)
  api/            # HTTP layer: health.py (/health/live, /health/ready); v1/ versioned routers
  services/       # Application services: use cases and transaction boundaries
  domain/         # Pure domain rules; no HTTP or database imports
  persistence/    # SQLAlchemy base/session; models arrive with DATA-001
  worker/         # Worker entry point: python -m app.worker
docker/           # Backend Dockerfile (shared by API and worker)
docker-compose.yml  # Local environment: frontend, API, worker, PostgreSQL 16
migrations/       # Alembic environment; revisions arrive with DATA-001
frontend/         # React + TypeScript (Vite) application
tests/
  unit/           # Backend unit/service tests
  api/            # REST API tests (HTTPX)
  ui/             # Playwright browser tests
  integration/    # Cross-component workflow tests
  database/       # Persistence and SQL validation tests
  bdd/features/   # pytest-bdd scenarios for selected business flows
```

CI workflows and shared test fixtures are added by TEST-001 and TEST-002. Nothing here implements an e-commerce feature yet.

## Run locally with Docker Compose (FOUND-002)

**Prerequisites:** Docker Engine with Compose v2 (`docker compose`, not `docker-compose`), and free host ports 5173 and 8000 (change them in `.env` if needed).

```bash
cp .env.example .env          # then set your own POSTGRES_PASSWORD (letters and digits only)
docker compose up --build -d --wait
```

`--wait` returns once every service reports healthy. The API is only healthy when its readiness check can run `SELECT 1` against PostgreSQL.

| What | URL |
| --- | --- |
| Frontend (Vite dev server) | http://localhost:5173 |
| API OpenAPI docs | http://localhost:8000/api/v1/docs |
| Liveness (process is up) | http://localhost:8000/health/live |
| Readiness (database reachable) | http://localhost:8000/health/ready |
| PostgreSQL | **not published to the host**; reachable only inside Compose (see below) |

Host ports are bound to `127.0.0.1`. The frontend is given a browser-reachable API URL (`VITE_API_BASE_URL=http://localhost:8000/api/v1`); in GitHub Codespaces, forward ports 5173 and 8000 and note that cross-origin access (CORS) is not configured until the API is consumed by the frontend.

**Verify**

```bash
docker compose ps                               # db, api, worker, frontend should be "healthy"
curl -i http://localhost:8000/health/live       # 200 {"status":"ok"}
curl -i http://localhost:8000/health/ready      # 200 {"status":"ready"}; 503 NOT_READY if the database is down
docker compose exec db psql -U nexacart -d nexacart -c "select version()"   # use your POSTGRES_USER/DB
```

**Logs, stop, restart**

```bash
docker compose logs -f api worker               # follow logs (add db / frontend as needed)
docker compose down                             # stop and remove containers; database data is KEPT
docker compose up -d --wait                     # start again; data persists in the named volume
docker compose up --build -d --wait             # rebuild after changing code (no source bind mounts)
```

**Reset the database (destructive)**

> **Warning:** `docker compose down -v` deletes the `nexacart_postgres-data` volume and **all local database data**. There is no undo.

```bash
docker compose down -v
```

**Measuring startup/readiness time (NFR-010: 120 s or less).** Build first so image builds are not counted, then time the start:

```bash
docker compose build && docker compose down      # keeps the volume (warm start)
time docker compose up -d --wait                 # elapsed time until all services are healthy
curl -fsS http://localhost:8000/health/ready     # confirm readiness
```

For a first-initialisation (cold database) measurement, run `docker compose down -v` first, which deletes local data. Record the host, Docker/Compose versions and the image digests (`docker image inspect --format '{{index .RepoDigests 0}}' postgres:16`). Base images are pinned to `python:3.12-slim-bookworm`, `node:22-bookworm-slim` and `postgres:16`; pin exact digests when recording benchmark runs (Technical Architecture §9.2).

## Local quality checks

Python 3.12 and Node 22 are expected. Dependencies are exact-pinned; copy `.env.example` files before running anything that needs configuration.

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,test]"
ruff check . && ruff format --check . && mypy && pytest
# Optional: also run the real-PostgreSQL readiness test against your own database
# NEXACART_TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost/db pytest -m integration

cd frontend && npm ci
npm run lint && npm run format:check && npm run typecheck && npm run build
```

## Definition of progress

Every feature should have agreed requirements, acceptance criteria, appropriate automated coverage and recorded execution results. A feature is complete only when its intended behaviour is implemented and verified.

