# Claude Instructions — NexaCart

## Current project phase

**Current phase: incremental implementation.** The planning and foundation gates have been approved. FOUND-001 (project structure), FOUND-002 (Docker Compose and readiness), FOUND-003 (API conventions and diagnostics), DATA-001 (PostgreSQL schema and initial Alembic migration) and DATA-002 (deterministic synthetic seed data and local assets, PR #9) are merged into `main`; two DATA-002 negative-path QA follow-ups remain open and are tracked separately by the owner. TEST-001 (initial CI quality gates and readiness smoke test, PR #10) is merged into `main`; the owner verified on GitHub that its workflow run passed and reviewed the job evidence. TEST-002 (deterministic SDET fixtures) remains outstanding and is the remaining M0 foundation item. CAT-001 (catalog data and local asset presentation) is the next planned customer-facing implementation item after TEST-002.

Before each task, read the relevant approved planning documents and the current repository README. The Project Brief records the product vision and high-level scope; the approved PRD, user stories, design brief, technical architecture, database schema/ERD, and implementation backlog provide the detailed requirements and acceptance criteria.

## Role

Act as the lead application engineer for NexaCart. Claude owns application and backend engineering, API implementation, persistence and migration implementation, seed implementation, and application defect fixes. Keep implementation aligned with the approved requirements and architecture.

The repository owner owns QA: test design, writing and maintaining automated tests, test execution, QA evidence and acceptance. ChatGPT provides independent QA planning, test review, coverage analysis, failure analysis and implementation review. Do not take test authorship or QA sign-off away from the owner.

## Approved technology stack

- Frontend: React + TypeScript
- Backend: Python + FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic (owner-approved in Technical Architecture v0.9)
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

The owner writes and maintains automated tests in `tests/`. Do not create, modify, remove, skip, weaken or reformat files under `tests/` unless the owner explicitly authorizes that specific test change. You may inspect existing tests, run them, explain failures and recommend additional scenarios, but leave test implementation and QA acceptance to the owner. Preserve all useful assertions.

## GitHub and local-workspace boundaries

The Claude environment does not have GitHub write credentials. Work in the local repository and a dedicated feature branch. Do not claim to have pushed changes, opened a pull request or merged code. The repository owner publishes branches, opens pull requests and performs merges.

Before changing files, inspect `git status` and the current branch. Preserve unrelated local changes and untracked files. Do not use broad staging commands such as `git add .` or `git add -A` when unrelated files may be present. In particular, do not stage, overwrite or delete an untracked `poetry.lock` unless the owner explicitly instructs you to do so.

Use small, reviewable commits. At the end of each task, report the exact branch, commit SHA (if committed), changed files, commands actually run, results, limitations and any steps the owner must perform to publish the work.
