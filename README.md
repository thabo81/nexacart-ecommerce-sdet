# NexaCart — E-Commerce Platform & SDET Automation

NexaCart is a multi-category e-commerce application being planned alongside a professional SDET automation framework. The application will support product discovery, shopping carts, checkout with simulated payments, order management and inventory rules. The portfolio focus is the quality engineering around those workflows: UI automation, REST API testing, database validation, BDD and CI/CD.

> **Project status:** Planning. Features and test results will only be marked complete after implementation and verification.

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

The following deliverables are being developed before feature implementation:

1. Product Requirements Document (PRD)
2. User Stories & Application Flows
3. Design Brief & UI Wireframes
4. Technical Architecture
5. Database Schema & Entity Relationship Diagram (ERD)
6. Implementation Plan & Product Backlog

Start with [the master project brief](docs/planning/PROJECT_BRIEF.md).

## Planned repository layout

```text
docs/
  planning/       # Approved product and architecture documents
  testing/        # Test strategy, coverage, execution evidence and defects
app/              # FastAPI backend (planned)
frontend/         # React/TypeScript frontend (planned)
tests/
  api/            # REST API tests
  ui/             # Playwright browser tests
  integration/    # Cross-component workflow tests
  database/       # Persistence and SQL validation tests
pages/            # Reusable Page Objects (as appropriate)
.github/
  workflows/      # CI pipelines
```

The folders marked as planned will be added as implementation begins. This repository is not yet a runnable application.

## Definition of progress

Every feature should have agreed requirements, acceptance criteria, appropriate automated coverage and recorded execution results. A feature is complete only when its intended behaviour is implemented and verified.

