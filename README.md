# NexaCart — E-Commerce Platform & SDET Automation

NexaCart is a multi-category e-commerce application being planned alongside a professional SDET automation framework. The application will support product discovery, shopping carts, checkout with simulated payments, order management and inventory rules. The portfolio focus is the quality engineering around those workflows: UI automation, REST API testing, database validation, BDD and CI/CD.

> **Project status:** Planning approval gate. The PRD, user stories, design, technical architecture v0.9 and database schema/ERD v0.9 are owner-approved planning baselines. The implementation plan/backlog v0.1 is a review draft on a separate branch and is not yet published to main. No application feature code or Alembic migrations are authorised until that backlog is approved.

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
- The project is being planned first. Do not treat proposed functionality as implemented.

## How we will work

- **Claude:** application implementation, API contracts, database migrations and application defect fixes.
- **ChatGPT:** SDET strategy, test design, Playwright/Pytest automation, API tests, SQL validation, failure analysis and test framework review.
- **Project owner:** reviews requirements, approves design decisions, runs commands and confirms changes.

Both workstreams must use the approved documents in [docs/planning](docs/planning/README.md) as their source of truth.

## Planning documents

Planning baselines and the remaining approval gate are tracked in [docs/planning](docs/planning/README.md):

1. [Product Requirements Document (PRD)](docs/planning/PRD.md) — approved v0.7
2. [User Stories & Application Flows](docs/planning/USER_STORIES_AND_FLOWS.md) — approved v0.4
3. [Design Brief & Wireframes](docs/planning/DESIGN_BRIEF_AND_WIREFRAMES.md) — approved v0.4; real-browser verification remains pending
4. [Technical Architecture](docs/planning/TECHNICAL_ARCHITECTURE.md) — owner-approved planning baseline v0.9
5. [Database Schema & ERD](docs/planning/DATABASE_SCHEMA_AND_ERD.md) — owner-approved planning baseline v0.9
6. [Implementation Plan & Backlog — review draft](https://github.com/thabo81/nexacart-ecommerce-sdet/blob/docs/implementation-plan-backlog-review/docs/planning/IMPLEMENTATION_PLAN_AND_BACKLOG.md) — v0.1 awaiting owner approval; not yet published to main

Start with [the master project brief](docs/planning/PROJECT_BRIEF.md).

## Repository layout (FOUND-001)

```text
docs/
  planning/       # Approved product and architecture documents
  testing/        # Test strategy, coverage, execution evidence and defects
app/              # FastAPI backend and worker (one codebase)
  main.py         # API entry point: uvicorn app.main:create_app --factory
  core/           # Typed configuration (security and observability arrive later)
  api/v1/         # Versioned HTTP routers; no business rules
  services/       # Application services: use cases and transaction boundaries
  domain/         # Pure domain rules; no HTTP or database imports
  persistence/    # SQLAlchemy base/session; models arrive with DATA-001
  worker/         # Worker entry point: python -m app.worker
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

Docker Compose, CI workflows and test fixtures are added by FOUND-002, TEST-001 and TEST-002. Nothing here implements an e-commerce feature yet.

## Local quality checks

Python 3.12 and Node 22 are expected. Dependencies are exact-pinned; copy `.env.example` files before running anything that needs configuration.

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,test]"
ruff check . && ruff format --check . && mypy && pytest

cd frontend && npm ci
npm run lint && npm run format:check && npm run typecheck && npm run build
```

## Definition of progress

Every feature should have agreed requirements, acceptance criteria, appropriate automated coverage and recorded execution results. A feature is complete only when its intended behaviour is implemented and verified.

