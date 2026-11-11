# NexaCart Test Strategy

**Status:** Proposed QA strategy baseline  
**Applies to:** NexaCart API, database, integration, UI and selected BDD verification  
**Technology:** Pytest, HTTPX AsyncClient, FastAPI, SQLAlchemy, PostgreSQL, Playwright for Python  
**Source of truth:** Approved PRD, User Stories & Application Flows, Technical Architecture, Database Schema & ERD, and Implementation Plan & Backlog

## 1. Purpose

This document defines how NexaCart is tested. The strategy is risk-weighted and revenue-first: testing effort is concentrated on protecting order correctness, inventory, customer data ownership, transactional consistency and the integrity of the simulated-payment lifecycle.

The objective is not to maximise test count. It is to obtain high-value evidence that critical business rules hold, invalid operations are rejected safely, and database state remains correct under failure, retries and concurrency.

A feature is not considered implemented or verified merely because its tests have been designed. Test status must be supported by actual execution evidence.

## 2. Strategic principles

1. **Risk before volume.** Prioritise business impact, likelihood, exposure and detectability; do not write repetitive tests solely to increase test count.
2. **Revenue and data integrity first.** Checkout, order lifecycle, pricing, inventory, payment-state handling and access control receive the deepest coverage.
3. **Test business outcomes.** Assert status, stable error code, response contract and relevant persisted state. A successful HTTP response alone is not sufficient evidence.
4. **Use the real database for critical integration behaviour.** Tier 0 API/integration tests use PostgreSQL. Do not mock persistence to claim transaction, constraint, locking or concurrency coverage.
5. **Prove rejected operations are non-mutating.** Verify that failed requests do not partially change cart, order, stock, coupon usage, ledger, payment-attempt or session state where applicable.
6. **Test through the correct layer.** Use unit tests for pure rules, API tests for HTTP contracts and authorization, PostgreSQL tests for persistence invariants, and integration/concurrency tests for multi-component behaviour.
7. **Keep tests deterministic and isolated.** Synthetic data, controlled time, explicit cleanup and reliable database isolation are mandatory.
8. **Avoid duplication.** Test a rule at the lowest layer that gives meaningful evidence, then add a smaller number of cross-layer tests for integration risks.
9. **Trace tests to requirements.** Each test must identify its relevant PRD requirement, business rule, story or acceptance criterion.
10. **Never weaken a useful assertion to make CI pass.** Fix the product, fixture, test or environment issue and retain evidence.

## 3. Risk tiers and coverage expectations

### Tier 0 — Zero tolerance: revenue, security and data integrity

A defect in these flows can cause financial loss, incorrect orders, inventory corruption, privacy exposure or unrecoverable state.

| Business domain | Principal risks | Required verification |
|---|---|---|
| Cart and pricing | Incorrect totals, discount allocation, tax/shipping calculation, quantity limits, rounding and stale prices | Deep boundaries, invalid combinations, deterministic calculations, authoritative server totals and persisted-state checks |
| Coupons and promotions | Expired/ineligible codes, minimum spend, per-customer/global limits, duplicate use and incorrect discount caps | Validation precedence, time boundaries, usage-limit contention, no usage reservation on unsuccessful application, no partial mutation |
| Checkout / order placement (TX-1) | Duplicate submissions, partial order creation, stale cart/price/stock, inconsistent snapshots | Atomicity, idempotency, rollback, immutable item/address snapshots, stock and coupon effects, cart lock and database assertions |
| Simulated payment (TX-2) | Duplicate callbacks, replay, conflicting outcomes, attempts after deadline, technical failure | Idempotency, state-machine validation, retry/attempt caps, transaction rollback, payment history and order-state assertions |
| Inventory | Overselling, negative stock, lost updates, duplicate restoration and ledger mismatch | Concurrent purchases, row-lock/constraint behaviour, stock ledger, cancellation/expiry restoration and non-negative invariant |
| Authentication and authorization | Session misuse, IDOR, privilege escalation, account enumeration, invalid/revoked/expired sessions | Unauthenticated and cross-user access, role boundaries, token/session lifecycle, safe error behaviour and no data leakage |
| Cancellation / expiry / worker races | Payment-versus-expiry races, duplicate worker execution, repeated stock/coupon release | Deterministic time, idempotent transitions, concurrency, at-most-once effects and complete database state assertions |

**Tier 0 coverage minimum:** happy path, negative path, boundary conditions, validation precedence, ownership/security checks, persistence invariants, rollback behaviour, retry/idempotency and relevant concurrency. Not every scenario needs every test layer; the selected layers must collectively provide the evidence.

NexaCart-specific high-risk examples include:
- TX-1 must atomically create the pending order and snapshots, deduct stock, record ledger effects, apply coupon usage, lock the cart and persist the idempotency record.
- A TX-1 failure must leave none of those partial effects behind.
- TX-2 must re-read and validate authoritative order state under the approved transaction/locking rules.
- Expiry/cancellation must restore inventory and release applicable reservations at most once.
- The backlog's stock-contention example requires a concurrency test in which 20 purchases compete for 5 units and exactly 5 units are sold, with no negative stock.

These are requirement targets, not claims that the corresponding application features are already implemented.

### Tier 1 — Core operations

These flows support discovery and normal customer activity. Failures matter, but generally have lower direct transactional risk than Tier 0.

| Business domain | Principal risks | Required verification |
|---|---|---|
| Product catalogue and detail | Inactive/unavailable products, incorrect variant, price or stock display | Happy path plus key not-found/unavailable cases, variant selection and server-authoritative values |
| Search, filtering, sorting and pagination | Incorrect result sets, invalid boundaries, unstable ordering and filter interaction | Contract and boundary tests, deterministic ordering, empty results and invalid parameters |
| Order history and detail | Cross-customer disclosure, incorrect state or snapshot display | Ownership checks, valid/unknown IDs, correct status and immutable order details |

**Tier 1 coverage minimum:** representative happy path and the primary negative, boundary and ownership cases. Expand only where the PRD or observed risk justifies it.

### Tier 2 — Low-risk support operations

Examples include profile details, static category presentation and address-book operations that do not themselves trigger a high-risk transaction.

**Tier 2 coverage minimum:** concise smoke coverage for the principal supported behaviour, input validation and applicable ownership protection. Add deeper tests only when a specific business rule, security risk or defect history warrants it.

Tier 2 classification never removes baseline security requirements. For example, a customer must not read or edit another customer's profile or address.

## 4. Test layers and their responsibilities

| Test layer | Primary responsibility | Appropriate evidence |
|---|---|---|
| Unit / domain | Pure calculations, validation ordering, value objects and state-transition rules | Exact expected values, boundaries and deterministic outcomes |
| API integration (HTTPX) | HTTP contract, authentication, authorization, validation and business error behaviour | Status, response schema, error code, headers and database side effects |
| Database | PostgreSQL constraints, relationships, uniqueness, ledger and migration behaviour | Direct SQL/ORM state, constraint rejection, rollback and referential integrity |
| Cross-component integration | API, services, database and worker interactions | Atomicity, lifecycle transitions, retry/recovery and transaction boundaries |
| Concurrency | Simultaneous requests or worker claims against shared state | No overselling, duplicate effects, lost updates or invalid state transitions |
| UI (Playwright) | Critical customer journeys and visible state | Observable user outcomes, stable selectors, navigation and accessible feedback |
| BDD (pytest-bdd) | Selected business-readable end-to-end examples | Traceable Gherkin scenarios for meaningful business workflows |
| CI / reporting | Repeatability and failure diagnosis | Reproducible commands, test results and safe failure artifacts |

UI tests do not replace API or database assertions for server-side invariants. BDD is reserved for selected business flows; it is not a wrapper around every click or every API test.

## 5. Test prioritisation

For each feature, apply this order:

1. Identify the approved requirement, business rule and acceptance criteria.
2. Identify assets and trust boundaries: customer identity, cart, order, payment state, inventory, coupon usage and persisted records.
3. Assess impact and failure modes, including partial failure, retries, concurrency and malicious access.
4. Assign Tier 0, Tier 1 or Tier 2 based on business impact.
5. Select the smallest set of test layers that gives credible evidence.
6. Design the happy path, high-value negative paths, boundaries and invariants.
7. Add concurrency and time-control scenarios where the underlying behaviour is race- or time-sensitive.
8. Map each test to requirement identifiers and record execution evidence.

Prioritise tests that detect:
- incorrect money, quantity, stock or order state;
- cross-customer or cross-role access;
- duplicate or partially committed business effects;
- failure to roll back;
- incorrect validation precedence;
- race conditions and non-idempotent retries;
- leakage of secrets, credentials or sensitive submitted values.

Do not prioritise repetitive assertions that every field returns HTTP 200 when they do not establish a distinct contract or risk.

## 6. Negative-path and invariant strategy

For every state-changing Tier 0 operation, identify:
- the valid preconditions;
- invalid, stale, expired or conflicting inputs;
- the expected HTTP status and stable business error code;
- the expected state before the request;
- the expected state after rejection;
- whether the operation is safe to retry;
- whether concurrent requests can observe or create conflicting state.

Where applicable, verify invariants such as:
- inventory quantity never becomes negative;
- stock deductions and restorations are represented consistently in the inventory ledger;
- one idempotency key does not create multiple business effects;
- one customer cannot access another customer's cart, order or address;
- failed transactions leave no partial order, coupon, stock or cart effects;
- immutable order snapshots do not change when catalogue or address records later change;
- coupon usage and reservation release happen no more than the business rules permit;
- order, payment-attempt and lifecycle history remain consistent.

Use direct PostgreSQL assertions for persisted invariants. Do not infer database correctness from the response body alone.

## 7. Boundary-value and equivalence-partition design

Apply ISTQB techniques deliberately rather than mechanically.

- **Equivalence Partitioning (EP):** identify groups expected to behave equivalently, such as valid/invalid coupon states, available/unavailable stock, authorised/unauthorised users and supported/unsupported payment outcomes.
- **Boundary Value Analysis (BVA):** test values at, immediately below and immediately above meaningful limits, such as minimum order value, maximum quantity, coupon usage cap, reservation deadline and pagination limits.
- Use two-value or three-value BVA according to the risk and the precision of the requirement.
- For money, use integer minor units and test rounding/allocation rules specified by the PRD. Do not use approximate floating-point assertions for monetary invariants.
- Combine partitions only when the interaction is itself meaningful; avoid an unbounded Cartesian product.

## 8. Concurrency and idempotency strategy

Concurrency is a first-class Tier 0 concern, not an optional performance test.

Design tests around the actual transaction and locking model. Use independent database connections and genuinely concurrent requests when testing database races. A single connection or one outer test transaction cannot establish realistic multi-connection locking behaviour.

Prioritise:
- competing checkouts for limited stock;
- repeated checkout submissions with the same idempotency key;
- duplicate or replayed simulated payment callbacks;
- payment racing cancellation or expiry;
- multiple worker claims for the same due order;
- concurrent coupon usage at a customer or global limit;
- concurrent inventory restoration attempts.

Assert final database state and the number of business effects, not merely the status returned by each request. Use bounded waits and observable completion conditions for asynchronous work.

## 9. Time-dependent behaviour

Time-dependent rules include coupon windows, session/token expiry, reservation deadlines, scheduled cleanup and worker processing.

Use an explicit, deterministic clock-control strategy. Prefer an injectable application clock where supported by the architecture; otherwise use one approved time-control library consistently. Do not mix uncontrolled wall-clock assumptions into tests.

Test exact boundary instants and the immediately-before/immediately-after cases. Ensure test-only clock overrides cannot be enabled in production-like environments.

## 10. Test data and environment

- Use synthetic data only. Never use production customer data, real payment data or real credentials.
- Create data through reusable factories rather than inline database-row construction in test functions.
- Unique values must be generated per test so parallel workers do not collide.
- Use a dedicated PostgreSQL test database, isolated from development and production data.
- Make destructive reset operations explicit, guarded and measurable.
- Keep tests independent: one test must not depend on execution order or data created by another test.
- Do not assume an endpoint or feature exists because it appears in a planned requirement. Confirm implementation and contract before writing executable tests.

## 11. Coverage and completion evidence

A feature's test design is complete when:
- its requirements and acceptance criteria are identified;
- risk tier and rationale are recorded;
- material happy, negative and boundary paths are covered;
- applicable invariants are asserted;
- relevant security, ownership and retry cases are addressed;
- concurrency/time cases are included where justified;
- test data and isolation are reusable;
- test execution results are recorded truthfully.

A feature is QA-accepted only after the agreed tests have actually run and evidence has been reviewed. Record skipped, blocked, flaky and unverified cases explicitly.

## 12. Project alignment and change control

This strategy supplements, and does not override, the approved NexaCart PRD, user stories, technical architecture, database schema or implementation backlog. If a generic testing rule conflicts with an approved business requirement or architectural decision, stop and raise the conflict for owner resolution.

The repository owner owns test design, test implementation, execution and QA acceptance. Any AI or contributor must follow the repository's CLAUDE.md boundaries and must not modify files under tests/ without explicit owner authorisation for that specific change.
