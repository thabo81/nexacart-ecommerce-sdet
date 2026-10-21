# Planning Documents

This directory contains the source-of-truth product decisions and engineering planning artifacts for NexaCart. The approval state of each artifact is recorded below. These documents are shared by implementation and SDET work.

## Source of truth

Start with [PROJECT_BRIEF.md](PROJECT_BRIEF.md). The planning sequence is listed below. Current approval status is recorded at the end of this document:

1. `PRD.md` — Product Requirements Document
2. `USER_STORIES_AND_FLOWS.md` — epics, user stories, acceptance criteria and application flows
3. `DESIGN_BRIEF_AND_WIREFRAMES.md` — UX, page layouts, responsive behaviour and wireframes
4. `TECHNICAL_ARCHITECTURE.md` — frontend/backend boundaries, API contracts, services and environments
5. `DATABASE_SCHEMA_AND_ERD.md` — entities, columns, constraints, relationships and ER diagram
6. [Implementation Plan & Backlog v0.1](IMPLEMENTATION_PLAN_AND_BACKLOG.md) — owner-approved work items, dependencies and milestones; implementation awaits explicit AI role allocation

## Document control

- Treat the PRD and its approved business rules as the baseline for later documents.
- Use stable IDs for requirements, business rules, user stories and test references.
- Record assumptions, decisions and open questions explicitly.
- If a decision changes, identify all documents and tests that need updates.
- Do not mark a feature implemented or verified until implementation and execution evidence exists.
- Keep real credentials, access tokens and production customer data out of this repository.

## Current status

Approved product/design baselines: `PRD.md` v0.7, `USER_STORIES_AND_FLOWS.md` v0.4, and `DESIGN_BRIEF_AND_WIREFRAMES.md` v0.4. Gallery (A) and the N-and-dot logo concept are owner-approved. On 2026-10-20, the owner approved `TECHNICAL_ARCHITECTURE.md` v0.9 and `DATABASE_SCHEMA_AND_ERD.md` v0.9 as planning baselines, including the modular-monolith approach, catalogue-field caps, reference performance profile, and configurable 02:00 UTC nightly-cleanup default. GAP-02 and GAP-11 decisions remain explicit; PostgreSQL 16, native `gen_random_uuid()`, named CHECK/partial-index registries, nightly expiry cleanup and product-row locking are included. Local Docker Compose and public deployment are in scope; provider/region selection remains deferred. `IMPLEMENTATION_PLAN_AND_BACKLOG.md` v0.1 was owner-approved on 2026-10-21 and is being published with this change. The design prototype still requires real-browser visual verification. **Do not begin application feature code, SQLAlchemy model implementation or Alembic migrations until the owner explicitly assigns one AI assistant to software engineering and the other to QA, then authorises the implementation gate to close.**
