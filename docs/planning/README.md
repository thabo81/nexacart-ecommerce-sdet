# Planning Documents

This directory contains the approved product and engineering decisions for NexaCart. These documents are the shared source of truth for Claude's implementation work and ChatGPT's SDET work.

## Source of truth

Start with [PROJECT_BRIEF.md](PROJECT_BRIEF.md). The planning sequence is listed below. Current approval status is recorded at the end of this document:

1. `PRD.md` — Product Requirements Document
2. `USER_STORIES_AND_FLOWS.md` — epics, user stories, acceptance criteria and application flows
3. `DESIGN_BRIEF_AND_WIREFRAMES.md` — UX, page layouts, responsive behaviour and wireframes
4. `TECHNICAL_ARCHITECTURE.md` — frontend/backend boundaries, API contracts, services and environments
5. `DATABASE_SCHEMA_AND_ERD.md` — entities, columns, constraints, relationships and ER diagram
6. `IMPLEMENTATION_PLAN_AND_BACKLOG.md` — prioritized work items, dependencies and milestones

## Document control

- Treat the PRD and its approved business rules as the baseline for later documents.
- Use stable IDs for requirements, business rules, user stories and test references.
- Record assumptions, decisions and open questions explicitly.
- If a decision changes, identify all documents and tests that need updates.
- Do not mark a feature implemented or verified until implementation and execution evidence exists.
- Keep real credentials, access tokens and production customer data out of this repository.

## Current status

Approved product/design baselines: `PRD.md` v0.7, `USER_STORIES_AND_FLOWS.md` v0.3, and `DESIGN_BRIEF_AND_WIREFRAMES.md` v0.3. Gallery (A) and the N-and-dot logo concept are owner-approved. The architecture draft records owner approval of the GAP-02 unavailable-item response and GAP-11 coupon validation precedence defaults, HttpOnly JWT cookie transport with CSRF protection, Argon2id password hashing, UUID entity identifiers and a PostgreSQL-backed worker. Deployment scope is both local Docker Compose and public portfolio hosting. `TECHNICAL_ARCHITECTURE.md` v0.2 is under final review; hosting-provider selection is deferred. `DATABASE_SCHEMA_AND_ERD.md` v0.1 is drafted for review; `IMPLEMENTATION_PLAN_AND_BACKLOG.md` has not yet been created. Do not begin application feature implementation until architecture, database design and delivery backlog are reviewed and approved.
