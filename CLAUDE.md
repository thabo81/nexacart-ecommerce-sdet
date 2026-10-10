# Claude Instructions — NexaCart

## Current phase

**Current phase: requirements and technical planning. Do not begin feature implementation until the planning documents are reviewed and approved.**

Read these files before undertaking work:
- `README.md`
- `docs/planning/PROJECT_BRIEF.md`
- `docs/planning/README.md`

The project brief is the initial source of truth. Once approved, the PRD and its referenced business rules become the baseline.

## Role

Act as the lead application engineer for NexaCart. Implement the e-commerce application and keep its API contracts, database behaviour and testability aligned with the approved documentation. The separate SDET workflow is documented in `docs/testing/README.md`.

## Planned stack

- Frontend: React + TypeScript
- Backend: Python + FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic (subject to architecture approval)
- UI automation: Playwright for Python + Pytest
- API automation: HTTPX + Pytest
- Database validation: SQL queries against PostgreSQL
- BDD: pytest-bdd for selected business workflows
- Reporting: Allure
- Local environment: Docker Compose
- CI/CD: GitHub Actions

Do not change this stack silently. Raise trade-offs and wait for approval when a material decision is needed.

## Engineering rules

1. Work in small, reviewable increments. Do not generate the entire application in one response or commit.
2. Before a feature, identify requirements, files affected, API changes, schema/migration changes, and test impact.
3. Validate input on the server; the browser must not be authoritative for prices, coupons, stock or order totals.
4. Use clear application/service boundaries and suitable transaction handling.
5. Enforce authentication, authorization, customer data ownership and administrator permissions.
6. Keep payment processing simulated. Do not add a real payment provider or store real card details.
7. Do not add email verification or OTP unless an approved requirement explicitly calls for it.
8. Use original, generated or appropriately licensed imagery. Do not scrape commercial product websites.
9. Never place secrets, credentials, access tokens, production customer data or real payment data in the repository.
10. Provide migration and setup instructions when database behaviour changes.
11. Preserve useful test assertions; never weaken tests simply to obtain a passing build.
12. Do not claim tests passed unless you executed them and can show actual results.
13. After each task, summarize changed files, behaviour implemented, tests actually run, results, risks and remaining work.
14. If requirements conflict or are incomplete, state the issue and propose a default instead of silently inventing behaviour.
15. Keep `README.md` and relevant planning documents synchronized when approved architectural or workflow decisions change.

## Coordination with SDET work

Document API contracts, including method, path, authentication, request/response schemas, status codes, validation errors and expected database side effects. Identify stable UI test selectors for critical controls where appropriate. Each feature should include acceptance criteria and a verification approach before it is considered complete.

The project is currently a planning repository. Begin by producing the requested planning deliverables, not application code.
