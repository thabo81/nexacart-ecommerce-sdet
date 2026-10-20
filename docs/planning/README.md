# Planning Documents

This directory contains the source-of-truth product decisions and engineering planning artifacts for NexaCart. The approval state of each artifact is recorded below. These documents are shared by implementation and SDET work.

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

Approved product/design baselines: `PRD.md` v0.7, `USER_STORIES_AND_FLOWS.md` v0.4, and `DESIGN_BRIEF_AND_WIREFRAMES.md` v0.4. Gallery (A) and the N-and-dot logo concept are owner-approved. The owner-confirmed GAP-02 unavailable-item response and GAP-11 coupon validation precedence are recorded in Technical Architecture v0.8. The architecture and database drafts also record PostgreSQL 16, native `gen_random_uuid()`, explicit CHECK/partial-index names, nightly expired-session/idempotency cleanup, and product-row `SELECT ... FOR UPDATE` review aggregate recalculation. Deployment scope is local Docker Compose plus a public portfolio deployment; provider selection is deferred. `TECHNICAL_ARCHITECTURE.md` v0.8 and `DATABASE_SCHEMA_AND_ERD.md` v0.8 are under owner review; the proposed catalogue-field maximums not specified by the PRD, the reference performance profile, the proposed modular-monolith approach, and the configurable 02:00 UTC cleanup time still await owner review. `IMPLEMENTATION_PLAN_AND_BACKLOG.md` has not yet been created. Do not begin application feature implementation until architecture, database design and delivery backlog are reviewed and approved.
