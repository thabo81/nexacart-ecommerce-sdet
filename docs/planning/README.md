# Planning Documents

This directory contains the approved product and engineering decisions for NexaCart. These documents are the shared source of truth for Claude's implementation work and ChatGPT's SDET work.

## Source of truth

Start with [PROJECT_BRIEF.md](PROJECT_BRIEF.md). The remaining documents are to be created and approved in this order:

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

Planning foundation established. Formal deliverables have not yet been approved. Application feature implementation should begin only after the requirements and initial architecture have been reviewed.
