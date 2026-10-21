# NexaCart — Implementation Plan and Backlog

| Field | Value |
|---|---|
| Document | docs/planning/IMPLEMENTATION_PLAN_AND_BACKLOG.md |
| Version | 0.1 — owner-approved planning baseline |
| Status | Owner-approved planning baseline (2026-10-21). Implementation remains blocked until the owner explicitly assigns software-engineering and QA responsibilities between the AI assistants. |
| Date | 2026-10-20 |
| Product baseline | PRD v0.7; User Stories & Flows v0.4; Design Brief & Wireframes v0.4 |
| Technical baseline | Technical Architecture v0.9; Database Schema and ERD v0.9 |

## 1. Purpose and delivery rules

This planning artifact translates approved product/design requirements and the owner-approved architecture/schema baselines into a build sequence. It does not promise calendar dates; work is dependency-driven and estimates can be added after tasks are decomposed.

**Current gate:** the owner approved the modular-monolith architecture, database schema/ERD, proposed catalogue field caps, performance reference profile, 02:00 UTC nightly cleanup default, and this implementation plan/backlog on 2026-10-21. The planning baseline is approved, but implementation is not yet authorised. Do not create feature code, SQLAlchemy models, Alembic migrations, frontend implementation, or worker implementation until the owner explicitly assigns one AI assistant to software engineering and the other to QA, then authorises the implementation gate to close.

1. The PRD and its stable requirement IDs are authoritative. Backlog items and tests must trace to FR, BR, AC, US, SEC, NFR or TR identifiers where applicable.
2. Deliver small, reviewable vertical slices. Each slice includes its API contract, service behaviour, persistence implications, UI behaviour, and tests before being marked complete.
3. The backend and PostgreSQL are authoritative for identity, authorization, price, discount, shipping, stock, order totals, order state, payment outcome and refund outcome.
4. Preserve TX-1 order placement and TX-2 payment boundaries, idempotency, lock ordering, deadline semantics and the race outcomes defined by BR-068–074. Do not weaken assertions to get a green build.
5. Establish API, database, UI and CI test foundations early. SDET coverage is cross-cutting, not a final-phase activity.
6. Use synthetic data only. Payments are simulated; never collect or store payment-card details. Use original/generated/licensed local images, not scraped retail content.
7. Keep credentials, tokens, CSRF values and sensitive user data out of source control, logs and CI artifacts.
8. Select the public hosting provider during deployment planning. It is not a dependency for completing the relational model or starting local implementation after approval.

## 2. Milestones and dependency order

| Milestone | Scope | Exit gate |
|---|---|---|
| G0 — Planning and responsibility gate | Review architecture, ERD, backlog, cross-document status and traceability; explicitly allocate AI roles | Owner approval of the backlog is recorded; implementation remains blocked until the owner explicitly assigns one AI assistant to software engineering and the other to QA and authorises the gate to close |
| M0 — Engineering foundation | Repo structure, configuration, Docker Compose, migrations, API conventions, seed/test support and first CI checks | Clean checkout starts; readiness checks the database; migrations and seed repeat; CI gates and health smoke test pass |
| M1 — R1 identity and catalog | Authentication, sessions, profile/addresses, catalog seed/assets, discovery and product detail | Applicable R1 stories and contracts verified across relevant layers |
| M2 — R1 shopping | Cart, wishlist, shipping, coupon rules and authoritative totals | Shopping business rules and edge cases verified; UI is not the source of truth |
| M3 — R1 order lifecycle | TX-1 placement, snapshots, stock reservation, idempotency, cart lock, TX-2 simulated payments, unpaid cancellation, expiry worker and order views | Transaction, replay, concurrency, timeout and expiry tests pass |
| M4 — R1 release hardening | Traceability, accessibility, responsive/browser checks, performance and deployment readiness | Every R1 Must requirement Verified; no open Critical/High defects; evidence recorded |
| M5 — R2 | Paid-order cancellation/refunds, administration, reviews, aggregates and audit events | Every R2 Must requirement Verified; no open Critical/High defects |
| M6 — Optional R3 | In-app notifications or later approved enhancements | Separate owner-approved scope and acceptance criteria |

Framework maturity is cross-cutting. Each milestone expands fixtures, API/UI/database coverage, selected BDD scenarios, Allure evidence and CI gates. The initial CI pipeline and health-check smoke test begin in M0.

## 3. Prioritised backlog

### G0 — Planning approval gate

#### PLN-001 — Approve and baseline the implementation plan
**Priority:** P0 · **Release:** Planning · **Status:** Backlog owner-approved on 2026-10-21; implementation gate awaits explicit AI role allocation

Acceptance criteria:
- Review milestone order, dependencies, release gates, cross-layer verification and explicit non-goals.
- Confirm that no feature-level product decision is silently invented by this plan; unresolved material ambiguity goes through change control.
- Keep public hosting provider and region deferred until deployment planning.
- Align PRD, stories, design, architecture, schema, backlog and SDET strategy references.
- Record owner approval in the planning documents/PR (approval received 2026-10-21).
- Before any feature code or migrations are created, obtain the owner's explicit assignment of one AI assistant to software engineering and the other to QA, then obtain explicit authorisation to close the implementation gate.

### M0 — Engineering foundation

#### FOUND-001 — Establish the application and test project structure
**Priority:** P0 · **Dependencies:** PLN-001

Create the approved React/TypeScript frontend, FastAPI backend, persistence/service/domain boundaries, separate worker entry point, migration folder and test layout.

Done when:
- Code has clear frontend, API, service/domain, persistence, worker, migration and test boundaries.
- Python quality gates use Ruff and mypy; frontend gates use ESLint, Prettier and TypeScript checking (NFR-017).
- Configuration uses environment variables and an example configuration contains placeholders only.
- Tool and container versions are pinned; generated reports and secrets are excluded from Git.

#### FOUND-002 — Define Docker Compose and readiness
**Priority:** P0 · **Dependencies:** FOUND-001

Define local frontend, API, PostgreSQL 16 and worker services.

Done when:
- A clean checkout can start the system using documented commands.
- Readiness confirms database connectivity, not merely that the API process is alive.
- NFR-010 is measured against the documented local setup: ready within 120 seconds.
- Database ingress is not unrestricted; worker process shares the codebase/database but runs separately.

#### FOUND-003 — Establish API conventions and diagnostics
**Priority:** P0 · **Dependencies:** FOUND-001

Establish API versioning under /api/v1, JSON error envelope, pagination conventions, request correlation and structured logging.

Done when:
- Every response carries X-Request-ID; errors echo the same ID (NFR-016, NFR-023).
- Error codes and HTTP status mappings match approved contracts.
- JSON logs contain timestamp, level, request ID and route, never passwords, tokens, raw cookies, CSRF values or secrets (NFR-015).
- OpenAPI matches implemented behaviour and is checked in CI (NFR-024).

#### DATA-001 — Implement PostgreSQL schema and migrations
**Priority:** P0 · **Dependencies:** PLN-001, FOUND-001

Implement SQLAlchemy persistence and Alembic migrations from the approved ERD v0.9. This work is permitted only after G0 approval.

Done when:
- Tables, relationships, FKs, unique rules, CHECK constraints, partial/supporting indexes and stable names match the approved schema.
- Money uses integer minor units; persisted times are UTC-aware; order and address snapshots obey immutability rules.
- Database constraints backstop stock, uniqueness, idempotency and order/payment/refund invariants (NFR-005–009, NFR-021).
- Migrations apply to an empty and a seeded database (NFR-007); production schema is not implicitly created on application startup.

#### DATA-002 — Add deterministic synthetic seed data and local assets
**Priority:** P0 · **Dependencies:** DATA-001

Seed the five product categories, product/variant catalog, shipping options, approved demo coupons and R1 rating aggregates. Track local asset provenance/licensing.

Done when:
- Running the seed twice yields the same baseline (NFR-008).
- Fixtures include zero stock, one unit, stock 5 and 6, inactive products, partially available variants, default variants, no reviews and known rating aggregates.
- Seed data covers coupon, subtotal, shipping and small-goods boundaries.
- Only synthetic data is used; admin accounts are provisioned through seed/CLI, never public registration (FR-010, NFR-022).
- No runtime fetches or scraped commercial images are required.

#### TEST-001 — Add the first CI quality gates and smoke test
**Priority:** P0 · **Dependencies:** FOUND-001–003, DATA-001

Set up GitHub Actions for Python/frontend checks, PostgreSQL-backed tests and a true readiness smoke test.

Done when:
- Pull requests run lint/format/type checks and unit/API smoke tests.
- CI can migrate and seed a disposable PostgreSQL database.
- Failure evidence is actionable and secret-safe.
- Tests are never represented as passing without actual execution evidence.

#### TEST-002 — Establish deterministic SDET fixtures
**Priority:** P0 · **Dependencies:** FOUND-001–003, DATA-001

Create Pytest configuration and reusable fixtures for HTTPX, Playwright, SQL validation, synthetic users, isolated test state and controlled time.

Done when:
- Planned test areas exist under tests/api, tests/ui, tests/integration, tests/database and selected tests/bdd.
- Database reset meets NFR-027 (30 seconds or less).
- Test-support routes, test credentials and clock overrides are local/test only and return 404 in public/prod-like configuration (SEC-018).
- Browser tests use observable waits rather than arbitrary sleeps.

### M1 — R1 identity, addresses and catalog

#### AUTH-001 — Implement account and session security
**Priority:** P0 · **Release:** R1 · **Dependencies:** FOUND-003, DATA-001, TEST-002

Covers FR-001–010, AC-004 and the relevant security requirements.

Done when:
- Registration creates a customer account but no session/token; UI then uses the standard login flow. No email verification, OTP or email-based password reset is added.
- Login delivers JWT in Secure, HttpOnly cookie with CSRF protection; tests verify Set-Cookie and successful access to a protected endpoint.
- Argon2id is used; logout and password change revoke sessions server-side.
- Expired, revoked, malformed and invalid tokens are rejected; bad credentials do not reveal account existence.
- Customer/admin authorization and ownership are enforced by the API, not only by frontend route guards.
- Repeated failed-login throttling and password-change session invalidation are tested.

#### AUTH-002 — Implement profile and saved addresses
**Priority:** P0 · **Release:** R1 · **Dependencies:** AUTH-001, DATA-001

Covers FR-007–015 and BR-008–009.

Done when:
- Address and profile input follow the approved validation contract on client and server.
- Users cannot read or modify another customer's addresses.
- The first address becomes default; exactly one default exists when any address exists.
- Updating/deleting an address never changes a prior order's address snapshot.

#### CAT-001 — Implement catalog data and local asset presentation
**Priority:** P0 · **Release:** R1 · **Dependencies:** FOUND-002, DATA-001–002

Covers FR-016–030, FR-084–089 and FR-097.

Done when:
- All five top-level categories have synthetic budget, mid-range and premium products.
- Product pages use server-authoritative price and availability; optionless products have one default variant.
- Ordered products are deactivated, not hard-deleted.
- Images are local, appropriately licensed and accessible with meaningful alt text.

#### CAT-002 — Implement product discovery
**Priority:** P0 · **Release:** R1 · **Dependencies:** CAT-001, FOUND-003

Implement category pages, home entry points, search, filter, sort, pagination, shareable URL state, product detail and variant selection.

Done when:
- Search/filter/sort/page boundaries, stable tie-breaking, multiple-brand OR semantics and remaining-filter AND semantics match the PRD.
- Inactive/unknown product access and unavailable mutation targets use the approved error semantics: unknown ID → 404 NOT_FOUND; known inactive/unavailable target → 409 PRODUCT_UNAVAILABLE with no mutation.
- Variant selection updates price, SKU and availability; unavailable combinations are disabled.
- Out-of-stock, low-stock, empty and no-review states are explicit and accessible.

### M2 — R1 shopping, shipping and coupons

#### SHOP-001 — Implement cart and wishlist
**Priority:** P0 · **Release:** R1 · **Dependencies:** AUTH-001, CAT-001, DATA-001

Covers FR-031–045 and BR-018–023.

Done when:
- Cart and wishlist are customer-scoped and persistent for authenticated customers.
- Server revalidates product/variant state, price, quantity and stock on every mutation.
- Duplicate wishlist entries are prevented.
- Rejected requests do not partially mutate state; cart lock rules prevent edits while a pending order exists.

#### SHOP-002 — Implement coupon, shipping and total calculation
**Priority:** P0 · **Release:** R1 · **Dependencies:** SHOP-001, DATA-002

Covers FR-046–051 and BR-024–036, BR-075–077.

Done when:
- One shared deterministic first-failure sequence is used for coupon application and placement revalidation: normalize/lookup → active/time window → customer eligibility → minimum amount → usage limits → discount calculation/caps.
- Totals use integer minor units; shipping and coupon decisions use the exact PRD pre-coupon/pre-discount subtotals.
- WELCOME10, first-order shipping, Express shipping and the small-goods minimum-order exception match BR-075–077.
- Applying a coupon does not reserve usage; unsuccessful application leaves the cart consistent.
- UI totals are display-only; server recomputes authoritative values.

### M3 — R1 checkout, simulated payment and order lifecycle

#### ORDER-001 — Implement placement transaction TX-1
**Priority:** P0 · **Release:** R1 · **Dependencies:** SHOP-002, DATA-001, TEST-002

Covers FR-052–056, BR-068–071 and BR-074.

Done when:
- Request/state validation follows BR-074's precise deterministic order.
- A single atomic transaction creates pending order, immutable item/address snapshots, total/deadline, stock deductions and ledger entries, coupon usage, cart lock and idempotency record.
- Placement never takes payment. Failure rolls back all TX-1 effects.
- Stock cannot become negative; one pending order per customer is enforced; duplicate submissions follow the idempotency contract.
- Reservation deadline is fixed from placement and never extended by payment retries.

#### ORDER-002 — Implement payment transaction TX-2
**Priority:** P0 · **Release:** R1 · **Dependencies:** ORDER-001

Covers payment requirements, BR-069–070 and the checkout acceptance criteria.

Done when:
- Only simulated approved, declined, timed-out and error outcomes exist; no real payment processor/card data is introduced.
- Timeout delay runs before TX-2, without an open database transaction or held order lock.
- TX-2 locks and re-reads authoritative order state; cancellation, prior approval, elapsed deadline and attempt cap follow the prescribed check order.
- Declined/timed-out/error business outcomes record an attempt but retain the pending order, reservation, coupon usage and cart lock.
- Technical failure rolls back TX-2 only; approved payment confirms the order, records history and empties/unlocks the cart atomically.

#### ORDER-003 — Implement unpaid cancellation and reservation-expiry worker
**Priority:** P0 · **Release:** R1 · **Dependencies:** ORDER-001–002, FOUND-002

Covers expiry/cancellation rules and the BR-073 race matrix.

Done when:
- Worker claims due work safely and makes idempotent state transitions under database transaction rules.
- Expiry never occurs before the deadline and takes precedence over payment after the deadline.
- Inventory restoration, coupon release, status history, ledger entries and cart unlock happen at most once.
- Concurrent payment, cancellation and expiry have only the outcomes permitted by BR-073.
- Configurable timing permits deterministic tests; nightly retention cleanup defaults to 02:00 UTC and never removes unexpired records.

#### ORDER-004 — Implement customer order history/detail and result states
**Priority:** P0 · **Release:** R1 · **Dependencies:** ORDER-001–003

Covers the relevant order read and checkout-result stories.

Done when:
- Every order read/mutation checks ownership.
- UI accurately describes pending, approved, declined, timed-out, cancelled and expired states and displays the authoritative reservation deadline.
- Available actions reflect current server state and payment-attempt count.
- R1 permits unpaid-order cancellation only; paid-order cancellation is deferred to R2.
- Payment/refund status is derived from source records, not duplicate mutable state.

### M4 — R1 hardening and release evidence

#### QA-001 — Complete R1 requirement traceability and regression
**Priority:** P0 · **Release:** R1 · **Dependencies:** M1–M3

Done when:
- Each R1 Must requirement is marked Verified/Not Verified and mapped to specific tests/evidence.
- API tests cover contract, negative, boundary, authentication, ownership and error behaviour.
- Direct SQL assertions independently validate totals, snapshots, stock ledger, coupon usage, idempotency and rollback.
- Concurrency tests verify the specified stock-contention example: 20 parallel purchases competing for 5 units sell exactly 5.
- Critical UI journeys have Playwright coverage with stable selectors and observable waits.
- Actual execution commands/results are recorded; no assertion is weakened simply to pass.

#### QA-002 — Add selected BDD, Allure and CI failure evidence
**Priority:** P1 · **Release:** Cross-cutting R1, expanded in R2 · **Dependencies:** TEST-001–002

Done when:
- pytest-bdd/Gherkin covers selected business flows, such as registration/login, coupon eligibility, failed payment retaining a reservation, placement and expiry.
- BDD describes business intent; it is not a wrapper around every low-level click.
- Allure results and relevant logs/traces are available for failures with secrets masked.

#### QA-003 — Verify accessibility, responsive layouts and browser support
**Priority:** P0 · **Release:** R1 · **Dependencies:** CAT-002, SHOP-001, ORDER-004

Covers NFR-011–014.

Done when:
- Keyboard operation, visible focus, labels, contrast, alt text, announced errors, reduced-motion handling and status announcements are checked.
- No horizontal page scroll occurs from 360–1920 px; reference viewports 375×812, 768×1024 and 1280×800 are exercised.
- Latest Chromium is primary; Firefox and WebKit run secondary Playwright regression.
- Automated axe checks on home, listing, detail, cart, checkout and login have no Critical/Serious violations.
- The static design prototype is visually checked in a real browser; defects are logged rather than reopening approved design choices without cause.

#### QA-004 — Verify performance and operational readiness
**Priority:** P1 · **Release:** R1 · **Dependencies:** M1–M3

Covers NFR-001–004, NFR-010 and NFR-027.

Done when:
- Read/write p95 values are measured against the owner-approved reference environment; configured simulated delays are excluded where the NFR says so.
- Filtered listing is measured using 10,000 synthetic products.
- Startup/readiness, database reset time, request IDs and secret-safe logging are verified.
- Every unmet target remains documented with evidence and a follow-up task/defect; results are never inferred from local smoke tests.

#### DEPLOY-001 — Select and validate a public hosting provider
**Priority:** P1 · **Release:** R1 public demo · **Dependencies:** Stable M0 topology; provider choice remains deliberately deferred

Done when:
- Candidate comparison documents static frontend, API, separate worker, managed PostgreSQL, networking, secret management, health checks, persistence, deploy/rollback, cost limits and operational limitations.
- Selected host supports the worker and reservation/refund processing model; if not, a trade-off is documented for approval.
- Public deployment has test-support disabled, synthetic data, no public DB ingress and no committed secrets.
- Public-host performance is not treated as proof of the benchmark NFR targets.

### M5 — R2 administration, paid cancellation/refunds, reviews and audit

#### R2-001 — Implement catalog and inventory administration
**Priority:** P0 · **Release:** R2 · **Dependencies:** CAT-001, R1 baseline

Done when:
- Admin permissions are enforced server-side; customer sessions cannot call admin mutations.
- Catalog edits/deactivation obey schema constraints and order-history rules.
- Inventory changes write append-only movements, require valid reasons and preserve non-negative stock.
- Invalid/conflicting operations leave no partial state.

#### R2-002 — Implement administrative order operations
**Priority:** P0 · **Release:** R2 · **Dependencies:** ORDER-001–004, R2-001

Done when:
- Allowed order transitions match the PRD state matrix and use appropriate transactions/locking.
- Admin reasons are validated and state transitions cannot be bypassed.
- Actions are auditable and customer ownership protections remain intact.

#### R2-003 — Implement review eligibility and rating aggregates
**Priority:** P0 · **Release:** R2 · **Dependencies:** CAT-001, ORDER-004, DATA-001

Covers FR-077–082 and BR-058–060.

Done when:
- Only a customer with a delivered order containing the product can review it; one review per customer/product is enforced.
- Rating is 1–5 and comment length is capped at the approved 1,000 characters.
- Create/hide locks the parent product row before recalculating visible average (half-up to one decimal) and count.
- Hiding a review records admin/time metadata and audit evidence; hidden reviews are excluded from public aggregates.
- Concurrency and persistence tests verify no lost aggregate updates.

#### R2-004 — Implement paid cancellation and simulated refunds
**Priority:** P0 · **Release:** R2 · **Dependencies:** ORDER-003–004

Done when:
- Paid cancellation atomically updates order status/history, restores inventory as specified and creates at most one full pending refund.
- Worker completion of a refund is delayed as configured and idempotent.
- Concurrent cancellation/refund/payment paths cannot restore stock or create/complete a refund more than once.
- Only simulated refunds are supported; tests cover replay, worker retry, invalid state and rollback.

#### R2-005 — Implement audit-event coverage
**Priority:** P0 · **Release:** R2 · **Dependencies:** R2-001–004, DATA-001

Done when:
- Required security-sensitive and admin operations produce safe, request-correlated audit summaries.
- Passwords, hashes, JWTs, cookies, CSRF values and secrets never enter audit records.
- Normal application paths cannot update/delete audit history.
- Tests verify required events occur with successful actions and rolled-back actions leave no false success event.

#### R2-006 — Complete R2 release regression
**Priority:** P0 · **Release:** R2 · **Dependencies:** R2-001–005

Done when all R2 Must requirements are Verified, no Critical/High defects remain, all R1 regression remains green, and administration/reviews/refund/audit behaviour has cross-layer evidence.

### M6 — Optional R3

#### R3-001 — Separately scope and approve in-app notifications
**Priority:** P2 · **Release:** Optional R3 · **Dependencies:** Separate owner approval after R2

No notification implementation starts until a separate decision defines scope, stories, retention and acceptance criteria. Email/SMS/push delivery is not implicitly authorised.

## 4. Cross-layer verification strategy

Select verification layers based on feature risk; UI automation alone is never sufficient for server-side invariants.

| Layer | Required use |
|---|---|
| Unit/service (Pytest) | Pure calculations, validation precedence and state transitions |
| REST API (HTTPX + Pytest) | Status codes, schemas, errors, authentication, ownership, boundaries and idempotency |
| PostgreSQL/SQL validation | Constraints, totals/snapshots, stock/coupon ledger, uniqueness, rollback and transaction effects |
| UI (Playwright) | Critical journeys, visible state, stable selectors, keyboard/accessibility and responsive behaviours |
| Integration/concurrency | Placement/payment/cancel/expiry/refund races, stock contention and worker replay/recovery |
| BDD (pytest-bdd) | Selected business-level Gherkin scenarios, not every click |
| Allure/CI artifacts | Reproducible outcomes, failure diagnostics and retained safe evidence |
| Performance/accessibility | NFR targets on approved benchmark profile and WCAG 2.2 AA intent |

## 5. Definition of Done

A task is Done only when:
- Requirements/story IDs and acceptance criteria are linked and satisfied.
- API contracts and stable UI selectors are documented where applicable.
- Applicable unit, API, database, UI and integration tests are added and actually run; commands and results are recorded.
- Migrations work on empty and seeded databases; seed repeatability is proven when persistence changes.
- Security, ownership, error, boundary and rejected-request no-mutation paths are verified.
- Logging, request IDs, accessibility, responsiveness and CI effects are addressed for the slice.
- No secrets or real personal/payment data are introduced.
- Documentation, requirement status and traceability are updated.
- PR is reviewable. Critical/High defects block release acceptance.

## 6. Release exit criteria

### R1 — MVP
- All R1 Must requirements are Verified and trace to execution evidence.
- No open Critical/High defects.
- Migrations, repeatable seed, Docker Compose, readiness, CI quality gates and health smoke test pass.
- TX-1/TX-2, idempotency, stock contention, rejected mutation, reservation expiry and worker races have independent database/integration evidence.
- Core flows satisfy applicable accessibility, responsive and browser-support requirements.
- Performance results and any unmet targets are documented against the reference environment.
- Public deployment has its own host/security review; local reproducibility remains intact.

### R2
- All R2 Must requirements are Verified; no open Critical/High defects.
- R1 regression is green.
- Paid cancellation, full simulated refunds, administration, review eligibility/aggregates and audit events have cross-layer evidence.

### R3
- No work starts without separate owner-approved scope and acceptance criteria.

## 7. Traceability map

| Requirement group | Backlog items | Minimum verification emphasis |
|---|---|---|
| FR-001–015: identity, sessions, profile, addresses | AUTH-001–002 | API/UI/database, ownership and snapshot tests |
| FR-016–030, FR-084–089, FR-097: catalog/discovery/assets | CAT-001–002 | API contracts, UI, filter/variant boundaries and accessibility |
| FR-031–045: cart/wishlist | SHOP-001 | Ownership, availability, rejected mutation and uniqueness |
| FR-046–051, BR-075–077: coupon/shipping/thresholds | SHOP-002 | Validation precedence, boundary tests and totals |
| FR-052–076, FR-109–116, BR-068–074: orders/payment/cancel | ORDER-001–004 | TX-1/TX-2, idempotency, races, deadline and persistence |
| FR-103–108 and platform NFR/TR requirements | FOUND-001–003, DATA-001–002, TEST-001–002, QA-001–004 | Readiness, seed repeatability, CI, logging, security, accessibility/performance |
| FR-077–082: reviews | R2-003 | Eligibility, uniqueness, locking and aggregates |
| FR-090–100: inventory/admin/audit | R2-001–002, R2-005 | Authorization, ledger and audit integrity |
| FR-073–074 and paid cancellation | R2-004 | Refund idempotency, concurrency and stock restoration |
| FR-101–102: notifications | R3-001 | Out of scope until separately approved |

These groupings guide planning. Before a release is accepted, the implementation traceability matrix must map every individual requirement and relevant acceptance criterion to specific tests and evidence, not merely an epic.

## 8. Risks and deliberately deferred decisions

- Hosting provider/region is selected under DEPLOY-001 based on the approved service topology and operational constraints.
- Performance results must be measured; specified targets are not assumed to pass.
- Test-support security must be verified in a public/prod-like configuration, including disabled support endpoints and absent test credentials/clock overrides.
- Order/payment/cancel/expiry/refund races are a principal risk and require concurrency tests, not just unit tests.
- Optional R3 functionality remains out of scope until separately approved.

## Appendix A — Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-20 | Initial planning-only backlog draft based on owner-approved product/design/architecture/schema baselines. Defines dependency order, R1/R2/R3 gates and cross-layer SDET acceptance. No application code or migrations created. |
| 0.1 status update | 2026-10-21 | Owner approved the plan/backlog and it is being published as a planning baseline. Implementation remains blocked pending explicit owner assignment of AI software-engineering and QA roles and authorisation to close the implementation gate. |
