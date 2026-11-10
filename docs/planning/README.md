# Planning Documents

This directory contains the source-of-truth product decisions and engineering planning artifacts for NexaCart. The approval state of each artifact is recorded below. These documents are shared by implementation and SDET work.

## Source of truth

Start with [PROJECT_BRIEF.md](PROJECT_BRIEF.md). The planning sequence is listed below. Current approval status is recorded at the end of this document:

1. `PRD.md` — Product Requirements Document
2. `USER_STORIES_AND_FLOWS.md` — epics, user stories, acceptance criteria and application flows
3. `DESIGN_BRIEF_AND_WIREFRAMES.md` — UX, page layouts, responsive behaviour and wireframes
4. `TECHNICAL_ARCHITECTURE.md` — frontend/backend boundaries, API contracts, services and environments
5. `DATABASE_SCHEMA_AND_ERD.md` — entities, columns, constraints, relationships and ER diagram
6. [Implementation Plan & Backlog v0.1](IMPLEMENTATION_PLAN_AND_BACKLOG.md) — owner-approved work items, dependencies and milestones; implementation and independent QA responsibilities are assigned: Claude builds; owner and ChatGPT test

## Document control

- Treat the PRD and its approved business rules as the baseline for later documents.
- Use stable IDs for requirements, business rules, user stories and test references.
- Record assumptions, decisions and open questions explicitly.
- If a decision changes, identify all documents and tests that need updates.
- Do not mark a feature implemented or verified until implementation and execution evidence exists.
- Keep real credentials, access tokens and production customer data out of this repository.

## Current status

Approved planning baselines remain: `PRD.md` v0.7, `USER_STORIES_AND_FLOWS.md` v0.4, `DESIGN_BRIEF_AND_WIREFRAMES.md` v0.4, `TECHNICAL_ARCHITECTURE.md` v0.9 and `DATABASE_SCHEMA_AND_ERD.md` v0.9. The approved architecture records the modular-monolith approach, PostgreSQL 16, native `gen_random_uuid()`, named CHECK/partial-index registries, catalogue-field caps, reference performance profile, nightly expiry cleanup and product-row locking. The configurable 02:00 UTC cleanup default is retained. GAP-02 and GAP-11 decisions remain part of the approved baseline. Local Docker Compose is implemented; public hosting provider/region selection remains deferred. `IMPLEMENTATION_PLAN_AND_BACKLOG.md` v0.1 was owner-approved on 2026-10-21 and is the dependency/acceptance source for implementation. The design prototype still requires real-browser visual verification.

**Implementation status (2026-11-09):** FOUND-001 (PR #4), FOUND-002 (PR #5), FOUND-003 (PR #6), DATA-001 (PR #7), DATA-002 (PR #9) and TEST-001 (PR #10) are merged into `main`. DATA-001 supplies the PostgreSQL 16 schema, SQLAlchemy models and initial Alembic migration for 25 non-R3 tables. DATA-002 supplies the deterministic synthetic seed data and local assets; two of its negative-path QA follow-ups remain open. TEST-001 (initial CI quality gates and readiness smoke test, PR #10) is merged after the owner verified its GitHub Actions run; TEST-002 (deterministic SDET fixtures) remains outstanding. CAT-001 is the next planned customer-facing item after TEST-002. Core customer-facing ecommerce workflows are not yet implemented or QA-accepted; each remains governed by its backlog item and acceptance criteria.

**Responsibility assignment (recorded 2026-10-21 and clarified 2026-11-03):** Claude owns software engineering and implementation. The repository owner owns QA, test design, test implementation, execution and acceptance. ChatGPT provides independent QA planning, review, coverage analysis, failure analysis and validation support; it does not own feature implementation or QA sign-off. Claude's environment has no GitHub write credentials; the repository owner publishes branches, opens pull requests and merges approved work.
