# NexaCart — E-Commerce Platform & SDET Automation

NexaCart is a multi-category e-commerce application being built alongside a professional SDET automation framework. The application will support product discovery, shopping carts, checkout with simulated payments, order management and inventory rules. The portfolio focus is the quality engineering around those workflows: UI automation, REST API testing, database validation, BDD and CI/CD.

> **Project status:** Implementation phase, milestone M0 (engineering foundation). The PRD, user stories, design, technical architecture v0.9, database schema/ERD v0.9 and [implementation plan & backlog v0.1](https://github.com/thabo81/nexacart-ecommerce-sdet/blob/main/docs/planning/IMPLEMENTATION_PLAN_AND_BACKLOG.md) are owner-approved planning baselines. FOUND-001 (project structure) is merged. FOUND-002 (Docker Compose and readiness) is under owner/QA review; development and test Compose profiles are included, with test-container runtime verification pending. No e-commerce features, database models or migrations exist yet. Planned functionality is not implemented or verified until the planning documents say so.

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
docker-compose.yml  # Local dev/test profiles: frontend, API, worker, PostgreSQL 16
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

**Prerequisites:** Docker Engine with Compose v2 (`docker compose`, not `docker-compose`). Development uses host ports 5173 and 8000. The test profile additionally uses 5273, 8100 and 55432.

### Development profile

Copy the example configuration and edit the local password if needed:

```bash
cp .env.example .env
# If .env already exists from before profile support, add/update COMPOSE_PROFILES=dev once (do not duplicate it).
# Set your own POSTGRES_PASSWORD in .env (letters/digits only unless URL-encoding is used).
docker compose up --build -d --wait
```

The example `.env` sets `COMPOSE_PROFILES=dev`, so the normal command starts only the four-service development stack. All services have health checks; the API is healthy only after it can run `SELECT 1` against PostgreSQL.

| What | URL |
| --- | --- |
| Frontend (Vite dev server) | http://localhost:5173 |
| API OpenAPI docs | http://localhost:8000/api/v1/docs |
| Liveness (process is up) | http://localhost:8000/health/live |
| Readiness (database reachable) | http://localhost:8000/health/ready |
| PostgreSQL | **not published to the host**; reachable only inside Compose |

Host-published ports bind to `127.0.0.1`. The frontend is configured with a browser-reachable API URL (`VITE_API_BASE_URL=http://localhost:8000/api/v1`). In GitHub Codespaces, forward the frontend/API ports as needed; browser cross-origin access (CORS) is not configured until the API is consumed by the frontend.

**Verify the development stack**

```bash
docker compose ps
curl -i http://localhost:8000/health/live       # expect 200 {"status":"ok"}
curl -i http://localhost:8000/health/ready      # expect 200 {"status":"ready"}; 503 NOT_READY if DB is down
docker compose exec db psql -U nexacart -d nexacart -c "select version()"
```

### Test profile (isolated test database)

The test profile runs a separate API, worker, frontend and PostgreSQL service. It sets `APP_ENV=test`; the test database is `nexacart_test` by default and uses tmpfs rather than a persistent volume. It has no development database volume and its data is disposable. Its database port is published only on loopback for host-side integration tests.

```bash
docker compose --profile test up --build -d --wait
docker compose --profile test ps
curl -i http://localhost:8100/health/live       # expect 200
curl -i http://localhost:8100/health/ready      # expect 200 when db-test is reachable
curl -i http://localhost:5273/                  # test frontend
docker compose --profile test exec db-test psql -U nexacart -d nexacart_test -c "select version()"
```

Host-side PostgreSQL readiness integration test (replace credentials/ports to match your `.env`):

```bash
NEXACART_TEST_DATABASE_URL="postgresql+psycopg://nexacart:change-me-local-only@127.0.0.1:55432/nexacart_test" pytest -m integration
```

The `--profile test` command-line option explicitly selects the test profile even though `.env` sets `COMPOSE_PROFILES=dev`. If no profile is active, all application services are profiled and Compose selects no services; keep `COMPOSE_PROFILES=dev` in your local `.env` for the normal development command. Profile selection is documented in the [Docker Compose CLI reference](https://docs.docker.com/reference/cli/docker/compose/).

### Logs, stop and reset

```bash
docker compose logs -f api worker             # development logs
docker compose down                           # stop the active profile (dev by default); dev DB data is kept
docker compose up -d --wait                   # resume development using the named volume
docker compose --profile test logs -f api-test worker-test
docker compose --profile test down            # stop the test stack
docker compose --profile dev --profile test down  # stop both stacks if both are running
```

**Reset the development database (destructive)**

> **Warning:** `docker compose down -v` deletes the active development stack's `postgres-data` volume and **all local development database data**. There is no undo.

```bash
docker compose down -v
```

The test database is ephemeral and is not stored in the development named volume.

### Measuring startup/readiness time (NFR-010: 120 seconds or less)

Build first so image builds are not counted, then measure elapsed time until all development services are healthy:

```bash
docker compose build
docker compose down
time docker compose up -d --wait
curl -fsS http://localhost:8000/health/ready
```

Record the host, Docker/Compose versions, build SHA and image versions/digests. For a cold-initialisation measurement of the development database, `docker compose down -v` deletes local data. The base-image tags are `python:3.12-slim-bookworm`, `node:22-bookworm-slim` and `postgres:16`; record their resolved digests with benchmark results as described in Technical Architecture §9.2.

## API conventions and diagnostics (FOUND-003)

- **Base path** `/api/v1`. Health endpoints stay unversioned (`/health/live`, `/health/ready`) as the PRD specifies (FR-103).
- **Request ID.** Every response carries `X-Request-ID`. A client-supplied ID is echoed only if it is 8-64 characters of `A-Z a-z 0-9 . _ : -`; anything else (including CR/LF, spaces, control characters) is replaced by a generated UUID. The same ID appears in error bodies and in every log line for the request.
- **Error envelope** (PRD Appendix A, AC-070). All errors use one shape:

  ```json
  { "error": { "code": "NOT_FOUND", "message": "...", "details": [], "request_id": "..." } }
  ```

  The HTTP status is always derived from the code (`app/core/errors.py`), so a code can never be paired with a contradictory status; a test compares the catalogue with PRD Appendix A. Services raise `AppError(ErrorCode.X, "message")` and keep their specific business codes. Responses never contain stack traces, SQL, exception text or submitted values.

  | Situation | Status | Code |
  | --- | --- | --- |
  | Known application error | per catalogue | its own code (e.g. `INSUFFICIENT_STOCK` 409) |
  | Unknown route / resource | 404 | `NOT_FOUND` |
  | Unsupported method | 405 | `METHOD_NOT_ALLOWED` |
  | Validation failure | 422 | `VALIDATION_ERROR` |
  | Framework 400, and any other framework 4xx | 400 | `BAD_REQUEST` |
  | Unexpected exception; framework 5xx, **including 503** | 500 | `INTERNAL_ERROR` |
  | Readiness failure (readiness endpoint only) | 503 | `NOT_READY` |

  `BAD_REQUEST`, `METHOD_NOT_ALLOWED` and `INTERNAL_ERROR` were approved by the owner on 2026-10-25 and recorded in PRD Appendix A and Appendix C. Validation `details` are `{field, message, type}` with the input location in the path (`query.page_size`, `body.quantity`, `path.item_id`) and never echo submitted values.
- **Pagination** (BR-016): `page` >= 1 (default 1); `page_size` >= 1, default `PAGE_SIZE_DEFAULT` (12), at most `PAGE_SIZE_MAX` (48). Both are configurable, but settings validation requires `1 <= PAGE_SIZE_DEFAULT <= PAGE_SIZE_MAX <= 48`: configuration may lower the limit, never raise it above the approved contract, and invalid values stop startup with a clear error. Invalid requests return 422 `VALIDATION_ERROR`; a page past the end returns 200 with empty `items` and correct `page`, `page_size`, `total_items`, `total_pages`. Use `PaginationDep` and `build_page` from `app/api/pagination.py`; the published OpenAPI shows the effective default and maximum.
- **Structured logs.** One JSON object per line on stdout: `timestamp`, `level`, `logger`, `message`, `request_id`, `route`, `version`, `build` (set `BUILD_SHA`), and for requests `method`, `status`, `duration_ms`. The route is the route template, never the raw URL or query string. Headers and bodies are never logged.
- **Redaction.** Applied to messages, extra fields, exception text and tracebacks alike: known secret values (secret settings, the database password, sensitive-named environment variables) wherever they appear; URL credentials; JWTs; `Authorization`/`Cookie`/`Set-Cookie` header lines; `Bearer`/`Basic` credentials; and `key=value` / `"key": "value"` pairs whose key contains password, secret, token (so `access_token`, `refresh_token`), cookie, csrf, api key, credential or jwt, including query-string tokens. Exception type and chain are kept for diagnosis. **Limits:** this is practical coverage of recognised patterns. It cannot find an arbitrary unknown secret inside free text, and benign text such as `token: expired` is redacted too. Do not put secrets in log messages or exception text.
- **Reading correlated logs:** `docker compose logs api worker --no-log-prefix | grep <request-id>`.
- **OpenAPI** is served at `/api/v1/openapi.json` (docs at `/api/v1/docs` outside production). Every response declares `X-Request-ID`; every operation has a `default` response referencing the shared `StandardError` envelope for statuses it does not document explicitly; explicit operation responses (success, 404, 409, 503, ...) are preserved. Operation-level contract tests (`tests/api/test_openapi_contract.py`) validate real bodies and headers against the published document. They run with `pytest`; wiring them into CI is TEST-001.

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

