# NexaCart — Technical Architecture

| Field | Value |
|---|---|
| Document | docs/planning/TECHNICAL_ARCHITECTURE.md |
| Version | 0.9 — owner-approved architecture baseline, pending backlog approval |
| Status | **Draft under owner review; not yet approved as a complete document.** Owner-confirmed: HttpOnly JWT cookie transport with CSRF protection (AC-004), Argon2id, UUID IDs, PostgreSQL 16 with native `gen_random_uuid()`, explicit CHECK/partial-index names, nightly cleanup of expired sessions and idempotency records, row-level locking for review aggregates, GAP-02/GAP-11 defaults, and local plus public deployment. Hosting provider is deliberately deferred. Catalogue field limits not numerically specified in the PRD are proposed in the ERD and await owner review. |
| Date | 2026-10-20 |
| Repository | https://github.com/thabo81/nexacart-ecommerce-sdet |
| Primary baseline | PRD v0.7; User Stories & Flows v0.4; Design Brief & Wireframes v0.4 |
| Related documents | PROJECT_BRIEF.md; README.md; docs/testing/README.md |
| Related downstream documents | DATABASE_SCHEMA_AND_ERD.md v0.8 draft; IMPLEMENTATION_PLAN_AND_BACKLOG.md not yet created |

## 1. Purpose and decision status

This document turns the approved product and design baselines into a buildable technical design. It defines the application boundaries, data-flow and transaction rules, API conventions, authentication and security approach, background work, deployment targets, and the architecture needed to support the SDET deliverable. The database schema and delivery backlog are separate companion documents; DATABASE_SCHEMA_AND_ERD.md v0.8 is drafted for review.

No application implementation is authorised yet. Owner decisions are being recorded in the architecture baseline; the remaining hosting-provider choice can be decided later. Before feature implementation begins, finish and review the database schema/ERD and implementation backlog and record final architecture sign-off.

### 1.1 Inputs confirmed by the owner

| Topic | Confirmed direction | Source |
|---|---|---|
| Product baseline | PRD v0.7, all DEC-01–29 and CL-01–20 approved | PRD |
| Stories and design | User Stories v0.3 and Design Brief v0.3 are approved | Companion planning documents |
| Unavailable product/variant API behaviour (GAP-02) | Unknown ID → 404 NOT_FOUND; known but inactive/unavailable product or variant → 409 PRODUCT_UNAVAILABLE. The rejected request must not mutate cart/wishlist. Display the API error in the UI. | Owner decision 2026-10-20; FR-025, BR-023, SEC-009; DQ-02 |
| Coupon validation precedence (GAP-11) | Normalize/lookup → active and time-window validity → customer eligibility → minimum amount → usage limits → calculate discount and apply caps. Identical precedence at coupon application and order-placement revalidation. | Owner decision 2026-10-20; FR-048, BR-031–036, BR-075; DQ-11 |
| Deployment scope | Both local Docker Compose and a public portfolio deployment are in scope | Owner decision 2026-10-20 |
| Currency and money | ZAR; integer minor units internally | PRD BR-024 |
| Payment | Simulation only; no payment-card fields, real payment processor or money movement | PRD NG-01, SEC-017 |
| Delivery approach | Documentation-first; architecture, database design and backlog must be approved before feature implementation | Planning workflow |

### 1.2 Status vocabulary in this document

- **Confirmed** means directly specified by the approved PRD or owner decision.
- **Proposed** means the architecture recommends a mechanism where the PRD deliberately deferred the choice. Owner approval is required before it becomes the implementation baseline.
- **Open** means the choice cannot be safely claimed as approved from the current inputs.
- **Not in scope** means the option is explicitly excluded by the PRD.

## 2. Architecture goals and constraints

The design shall:

1. Preserve all approved PRD business rules and acceptance criteria without moving authoritative rules into the browser.
2. Use one reproducible local/test environment and a separately configured public portfolio environment.
3. Keep the initial system simple enough for a portfolio project while demonstrating meaningful boundaries, transaction integrity, concurrency handling, security controls, and production-style delivery practices.
4. Keep the HTTP API stateless at the process level; persist all business-critical state in PostgreSQL rather than Python globals, worker memory or browser state.
5. Make time-sensitive behaviour deterministic in local/test environments.
6. Expose stable API contracts and observable outcomes for Playwright, HTTPX, SQL assertions, pytest-bdd and Allure.
7. Avoid external runtime dependencies for product imagery, fonts, analytics and application flow, in line with TR-013.
8. Keep synthetic portfolio data and simulation disclosures clearly separated from real commerce. The deployed application is a demonstration system, not a payment-ready retail service.

### 2.1 Fixed stack

| Concern | Baseline technology | Status |
|---|---|---|
| Frontend | React + TypeScript | Confirmed |
| Backend API | Python + FastAPI | Confirmed |
| Persistence | PostgreSQL 16; native `gen_random_uuid()` for generated UUID keys | Owner-confirmed |
| ORM and schema migration | SQLAlchemy + Alembic | Confirmed |
| API style | REST/JSON under /api/v1; OpenAPI contract | Confirmed |
| Local runtime | Docker Compose | Confirmed |
| UI automation | Playwright for Python + Pytest | Confirmed |
| API automation | HTTPX + Pytest | Confirmed |
| Database assertions | Direct SQL against test database | Confirmed |
| BDD | pytest-bdd for selected business flows | Confirmed |
| Reporting | Allure | Confirmed |
| CI/CD | GitHub Actions | Confirmed |
| Code quality | Ruff, mypy, ESLint, Prettier and TypeScript compiler checks | Confirmed by NFR-017 / DEC-22 |

No microservice platform, Kubernetes cluster, message broker or caching tier is required for the first implementation. Add a new infrastructure dependency only when a specific requirement justifies its operational and testing cost.

## 3. High-level topology

### 3.1 Local development and test

Browser
→ React development server or built frontend
→ FastAPI application
→ PostgreSQL

A separate worker process uses the same backend code and PostgreSQL database to process reservation expiries and simulated refunds. Docker Compose defines the app, database and worker so local work and CI use the same service definitions. A test profile supplies the isolated test configuration and guarded test-support capabilities.

### 3.2 Public portfolio deployment

Visitor browser
→ public HTTPS frontend
→ public HTTPS FastAPI API
→ private managed PostgreSQL

A separately deployed background worker uses the same versioned backend image and the same database. The API and worker have different process commands and share domain/service code. The database is not exposed to unrestricted public ingress. The platform supplies environment variables and secrets at runtime; credentials are not built into images or committed to the repository.

The hosting provider has not been chosen in the PRD. **Proposed deployment candidate:** a managed platform able to run a static frontend, a Python web service, a background worker and managed PostgreSQL. Render may be evaluated as the first candidate, but the provider and its operational limitations remain an owner-review item rather than an already-approved decision.

### 3.3 Logical component map

| Component | Responsibilities | Must not own |
|---|---|---|
| React application | Pages, forms, accessible interactions, route protection for user experience, display of server state, input feedback, request correlation | Authoritative price, coupon, stock, total, order-state or authorization decisions |
| API router layer | HTTP parsing, authentication dependency, request validation, status code mapping, response serialization | Multi-step business rules or transaction orchestration |
| Application/service layer | Business use cases, rule order, authorization policies, transaction boundaries, orchestration of domain services | UI layout, hosting-provider logic |
| Persistence layer | SQLAlchemy queries, row locking, conditional writes, transaction helpers and repository-style data access where useful | Duplicate business rules that differ from services |
| PostgreSQL | Durable state, foreign keys, uniqueness, check constraints, partial unique indexes and transaction serialization | External network calls or simulated delays inside open transactions |
| Background worker | Polling and safely claiming due expiry/refund work; idempotent state transitions | Independent copies of business rules; process-only job state |
| Test-support adapter | Reset, fixture creation, clock control, failure injection and internal-state inspection for local/test only | Public/demo use or production control-plane access |
| CI pipeline | Reproduce checks, enforce quality gates and retain safe diagnostics | Production credentials in ordinary pull-request jobs |

## 4. Backend architecture

### 4.1 Design style: modular monolith

**Proposed:** one FastAPI application organized by business capability, backed by one PostgreSQL database, plus a separately launched worker process from the same codebase. The modules communicate through Python service functions and database transactions; they are not independent network services.

This is preferred over microservices because the product has one small team, one seller, one currency, no external payment or carrier integration, and several operations that must be atomic across inventory, orders, cart state and coupon usage. A single deployable backend reduces integration overhead without removing the service boundaries needed for testing and later change.

### 4.2 Recommended code ownership boundaries

The eventual source layout should keep API handlers thin and domain operations testable without running the browser.

| Package or capability | Owns |
|---|---|
| core/configuration | Typed environment configuration, startup validation, application environment, secret loading and feature guards |
| core/security | Password hashing, JWT signing/verification, token-session revocation, CSRF validation and authentication dependencies |
| core/observability | Request ID middleware, structured logging, exception mapping and health/readiness checks |
| api/v1 | Versioned routers and HTTP request/response schemas |
| catalog | Category/product/variant reads, discovery filters, sort, pagination and public availability |
| accounts | Registration, login, logout, password change, profile and token revocation |
| addresses | Address ownership and immutable order-address snapshot inputs |
| cart | Cart line lifecycle, cart status, lock behaviour and server-derived cart totals |
| wishlist | Product-level membership and move-to-cart operation |
| pricing | Coupon validation, discounts, shipping and total calculation; a single authoritative calculation path |
| checkout/orders | Placement, order snapshots, status transitions, idempotency and customer cancellation |
| payments/refunds | Simulated payment attempts and simulated full refunds; no real gateway adapter |
| inventory | Stock adjustments, conditional stock changes and immutable inventory movement ledger |
| reviews | Eligibility, submission, aggregate calculation, public review display and hide behaviour |
| administration/audit | Admin-only catalog/inventory/order actions and append-only audit events |
| worker | Reservation-expiry and refund processors, using the same services and database transaction rules |
| test_support | Environment-guarded reset, seed, clock, failure injection and state inspection tools |

The schema document will decide the final module/file and table layout. This table defines responsibility boundaries, not a required one-class-per-row implementation.

### 4.3 Dependency direction

HTTP routers depend on application services. Application services depend on domain helpers and the persistence/session boundary. Domain helpers may receive explicit time/configuration dependencies for determinism. The frontend calls the HTTP API and does not import backend business logic. Worker handlers call the same application services used by API requests when the domain transition is shared.

Do not introduce a repository abstraction for every single table by default. Use repositories or query modules where they make transaction behaviour easier to understand, test or reuse. The critical requirement is a visible service/transaction boundary, not a pattern for its own sake.

### 4.4 Transaction management

Service operations define transaction boundaries explicitly. A route must not open nested or partially independent transactions around an operation whose business rules require one atomic unit. SQLAlchemy sessions should be scoped to a request or a worker task, never kept globally.

External delays, file writes and network calls must not occur while a business transaction or row lock is held. The payment timeout simulation explicitly delays before TX-2 and then re-reads the order under lock, as required by BR-069.

## 5. API architecture and contracts

### 5.1 Contract conventions

- Base path: /api/v1.
- Use resource-oriented REST routes and JSON payloads, with explicit request and response schemas.
- Use plural resource names and stable response shapes; never expose SQLAlchemy model objects directly.
- Reject unknown write fields on monetary, stock, role, status, owner, order and payment schemas (SEC-008; BR-020).
- Use ISO-8601 timestamps in UTC and integer minor-unit money values in API computations. Human-facing price strings are formatted by the UI from numeric server values.
- Every response includes X-Request-ID. Return the same identifier in the standard error envelope and structured logs.
- Use pagination fields total_items and total_pages consistently on paginated resources.
- Keep OpenAPI accurate and contract-tested (TR-008, TR-011, NFR-023–024).
- Use 201 for successful resource creation, 200 for successful reads/updates/actions returning a body, and 204 only when no response body is needed. Exact route-level mappings are to be frozen alongside schemas and acceptance tests.
- The UI displays server rejection messages in the correct field or form context; it must not choose a different business error when multiple predicates fail.

### 5.2 Route groups

The table describes logical route groups. Exact URL paths, request schemas and response examples belong in the API contract and backlog.

| Route group | Main operations | Access policy |
|---|---|---|
| Health | liveness and readiness | Public, minimal output |
| Authentication | register, login, logout, current user, change password, CSRF token | Register/login public; remaining routes authenticated |
| Catalog | categories, product listing/search/filter/sort, product detail, variants | Public reads only for visible/active catalog data |
| Cart | read, add line, update quantity, remove line, clear, apply/remove coupon, select shipping | Customer-owned cart |
| Wishlist | read, add/remove product, move item to cart | Customer-owned wishlist |
| Addresses | list/create/update/delete/set default | Customer-owned addresses |
| Shipping/pricing | shipping choices/fees and current server-calculated totals | Public or customer context as defined by the endpoint; never client-authoritative |
| Checkout/orders | place order, list own orders, order detail, cancel eligible order | Authenticated customer; ownership enforced |
| Payments | create a simulated attempt for an order | Owning customer; never accepts card information |
| Reviews | public visible reviews, submit eligible review | Public reads; authenticated eligible customers write |
| Admin catalog/inventory | product/category/variant maintenance and stock adjustments | Admin only |
| Admin orders/audit | order-state changes, payment/refund inspection, audit log, review hide | Admin only |
| Test support | reset, state setup/inspection, clock, controlled failures, expiry trigger | Only APP_ENV local or test; unavailable everywhere else |

An administrator is not a shopper, and customer endpoints never grant admin access. Public catalogue reads must not reveal inactive products or private customer data.

### 5.3 Standard error envelope

All API errors use the PRD envelope: an error object containing code, message, details and request_id. The response also carries X-Request-ID. A field error should identify the field; a business conflict should include safe, useful state such as currently available stock or the existing pending order ID where the PRD requires it. Do not include stack traces, SQL, signing secrets, internal exception text or other customers' data.

Status and code must follow the PRD error catalogue unless an owner-approved contract change is made. In particular:

| Condition | Response |
|---|---|
| Missing, malformed, expired or revoked authentication | 401 with the appropriate authentication code |
| Authenticated but forbidden capability | 403 FORBIDDEN |
| Resource unknown, or deliberately masked due to ownership | 404 NOT_FOUND |
| Business-state conflict such as unavailable item, insufficient stock, changed total or locked cart | 409 with the specific existing code |
| Schema or field validation failure | 422 VALIDATION_ERROR with field details |
| Login throttling | 429 RATE_LIMITED |
| Readiness cannot be established | 503 NOT_READY |

The PRD remains authoritative for the placement-specific validation order in BR-074. Do not apply a generic service-level check first if it would reorder that contract.

### 5.4 GAP-02 — product/variant unavailable contract

This is an **owner-approved default** for cart/wishlist mutation and must be implemented consistently.

1. If the supplied product or variant identifier does not identify a known resource, return 404 NOT_FOUND.
2. If it identifies a known but inactive or unavailable product/variant, return 409 PRODUCT_UNAVAILABLE. This includes cases where the product, variant or its parent category is no longer eligible for sale.
3. Do not create or update a cart line, wishlist entry, or other related state after rejection.
4. The UI renders the returned message inline and preserves the rest of the user's valid state.
5. Distinguish inactive/unavailable from an active variant with insufficient stock: preserve the existing BR-018 / AC-019 contract of 409 INSUFFICIENT_STOCK for an active variant whose stock cannot satisfy the requested quantity.
6. Public product detail for an inactive or non-visible product continues to follow FR-025 / AC-020 and returns the not-found experience; the 409 rule is for a mutation that references a known-but-no-longer-eligible item.

The distinction between an unknown identifier and a known inactive resource must not leak a resource to an unauthorised caller. Ownership and visibility policies are applied before exposing details.

### 5.5 GAP-11 — coupon validation precedence

This is an **owner-approved default**. Both coupon application and order-placement revalidation shall use one shared validation function and the following first-failure sequence:

| Step | Check | Expected reason code |
|---|---|---|
| 1 | Trim and normalize the submitted code according to BR-031, then look up the coupon | Unknown code → 422 COUPON_NOT_FOUND |
| 2 | Check active status and the validity window in UTC | Inactive or not yet started → 422 COUPON_NOT_ACTIVE; expired at or after the exclusive expiry boundary → 422 COUPON_EXPIRED |
| 3 | Check eligibility for the current customer | 422 COUPON_NOT_ELIGIBLE |
| 4 | Check the pre-discount subtotal against the coupon's inclusive/exclusive minimum rule | 422 COUPON_MIN_ORDER_NOT_MET |
| 5 | Check global and per-customer usage limits | 422 COUPON_USAGE_LIMIT_REACHED |
| 6 | Calculate the discount and enforce percentage rounding, maximum-discount cap and subtotal cap | Return the calculated discount; do not create a new error code for cap application |

The error from the first failing step is the only coupon error returned. The browser displays the returned code/message; it does not rerun or reorder these checks. Order placement repeats this sequence against authoritative state inside TX-1 and only proceeds if all checks pass.

For concurrent use-limit enforcement, the placement transaction must serialize access to the relevant coupon usage state (for example, by locking the coupon usage row/counter before checking and incrementing) so that the final remaining use is awarded to at most one order. Coupon validation when applied to a cart does not reserve a use; placement revalidation remains mandatory.

## 6. PostgreSQL, persistence and business integrity

### 6.1 Database is the concurrency authority

Application checks improve messages, but the database must prevent invalid concurrent outcomes. Required database backstops from NFR-006 include, at minimum:

- Non-negative inventory stock.
- Case-insensitive unique email.
- Unique SKU and catalog identity constraints.
- Foreign keys between all owned resources and their owners.
- Unique (customer, product) wishlist and review records.
- At most one approved payment and one refund per order.
- At most one pending order per customer, enforced with an appropriate partial unique index or equivalent robust constraint.
- Unique idempotency records within the correct customer and operation scope.
- Legal numeric ranges, required fields and valid status values wherever practical as CHECK constraints.

The schema/ERD document must give each invariant its actual constraint name, table/column definition and verification query. The application should translate known constraint failures into stable API errors without leaking database details.

### 6.2 Stock reservation and order placement — TX-1

Order placement must be implemented as one transaction matching BR-068 and BR-074. The placement operation does not attempt payment.

Inside TX-1, after BR-074 request checks and under the customer's cart lock, the service shall re-read authoritative state in the exact BR-074 order. It then validates the address, cart/minimum order, product/variant availability, stock, coupon and expected total. It creates the pending order with immutable order-item and delivery-address snapshots, records the deadline, deducts stock, writes inventory ledger movements, counts coupon usage, locks the cart to the pending order and stores the idempotency result. Any failed check or failed write rolls back all effects; a successful commit returns the pending order.

To prevent overselling:
- Lock or conditionally update each relevant variant in a deterministic order, such as ascending variant ID, to reduce deadlock risk.
- Make the decrement conditional on the current row still being eligible and on stock being at least the requested quantity.
- Treat a failed conditional update as the existing 409 INSUFFICIENT_STOCK path.
- Do not first read stock, release the lock, and later write an unconditional decrement.
- Record one inventory movement per committed stock change in the same transaction.

A successful order placement must leave every line's stock deduction, order snapshot, inventory movement, coupon usage, cart lock and idempotency record committed together. There is no partially placed order.

### 6.3 Payment attempt — TX-2

Payment is a separate operation from placement. Each deliberate attempt has its own Idempotency-Key and counts toward the maximum attempt cap. The accepted outcomes are only approved, declined, timeout and processing_error.

For the timeout outcome, perform the configured simulation delay before opening TX-2 and without holding the order lock. Then acquire the order-level lock, reload the order and deadline, and apply BR-069 eligibility checks in the specified order. Do not record an attempt when the order has become non-payable or expired during the delay.

For an approved attempt, record the attempt, mark the order confirmed and paid, append order history, empty and unlock the cart, and commit together. For declined, timed-out and error outcomes, commit the attempt but keep the order pending, the stock reserved, coupon usage counted and cart locked. A technical failure rolls back TX-2 only; the TX-1 reservation remains intact.

The API must never accept PAN, CVV or card expiry. The outcome selector must be clearly described as simulated payment, and the response copy must state that nothing was charged for a non-approved outcome.

### 6.4 Cancellation, expiry and refund consistency

Customer cancellation, admin cancellation, payment and expiry for the same order serialize on the order-level row lock. Every transaction re-reads status and deadline under lock; the first valid commit wins. Inventory restoration, coupon release, status history and refund creation must occur at most once.

Use idempotent state transitions and database constraints to make duplicate worker delivery or overlapping cancellation/expiry/payment requests safe. The losing operation must not repeat stock restoration, coupon release, payment capture simulation or refund creation. The complete race outcome matrix in BR-073 is the source of truth.

Paid-order cancellation in R2 creates one full simulated refund. A worker claims a due refund and makes the deterministic state transition to refunded after the configured delay; this is a demonstration of asynchronous workflow, not a call to a payment processor. Refund creation and order cancellation must be atomic, while refund completion is a separate worker transaction.

### 6.5 Idempotency

Store idempotency state in PostgreSQL, never only in memory. Enforce the exact scope and request fingerprint from BR-070. The first successful state-changing transaction stores the response status and body alongside its business effect. A same-key/same-payload replay returns the stored result without creating duplicate effects; same key with a different payload returns 422 IDEMPOTENCY_KEY_REUSED. Rejected operations that do not change state must not leave an idempotency record.

Do not hold a database transaction open while waiting for a long simulated timeout. Do not reuse a payment key for a deliberate new attempt.

### 6.6 Money and time

- Store amounts as integer minor units (cents), all in ZAR. Never use binary floating-point for authoritative monetary arithmetic.
- Follow BR-025–029 for subtotal, coupon discount, shipping and total order. Implement percentage rounding as round-half-up; apply maximum-discount and subtotal caps exactly as specified.
- Calculate shipping and coupon rules on the backend. The client sends an expected total for conflict detection but cannot supply authoritative prices, discounts, fees or totals.
- Store timestamps in UTC and exchange ISO-8601 values. Use an injectable application clock for rules requiring time.
- The simulated timeout delay uses real elapsed delay rather than the controllable business clock as required by TR-006.
- The application clock may be overridden only in local/test. Public deployment always uses the real UTC clock.

### 6.7 Identifier strategy and UUID generation

**Owner-confirmed:** use UUID identifiers for generated database entities and keep the human-readable order number (`NC-YYYYMMDD-NNNNNN`) as a separate unique business identifier; it is never used as an authorization secret. The target database is PostgreSQL 16. Generated UUID primary keys and generated `auth_sessions.jti` use the native PostgreSQL `gen_random_uuid()` default. Do not add an extension solely for UUID generation.

### 6.8 Request schema and database length parity

The ERD's §3.8 string-length contract is the shared boundary for request-model validation and physical database storage. Where the PRD states a maximum, it remains authoritative. Where the PRD does not state a numeric catalogue-field maximum, the ERD labels the value as a proposed technical cap for owner review. Once those caps are accepted, the FastAPI/Pydantic models and database column/CHECK constraint must use the same lengths; CI must exercise lower/upper boundaries and reject over-length values before persistence. No request schema implementation exists yet, so parity is planned rather than already verified.

### 6.9 Review aggregate concurrency

Review creation and review hiding must serialize per product. In the same PostgreSQL transaction, each path explicitly executes `SELECT id FROM products WHERE id = :product_id FOR UPDATE` **before changing the review row**. While holding that product-row lock, insert or update review visibility, recalculate the visible-review average/count, apply the PRD round-half-up rule, and update the cached aggregate columns. Keep the lock until commit. Every write path uses the same lock ordering. This prevents two concurrent create/hide operations from overwriting a correct aggregate with a stale count or average (BR-060, FR-081–082).

## 7. Authentication, authorization and application security

Security controls below trace to SEC-001–020 and BR-001–007. The detailed implementation must not weaken any approved control.

### 7.1 Password storage

**Proposed:** use Argon2id with a maintained library and deployment-appropriate work parameters. Store only the encoded adaptive salted hash and allow parameters to be upgraded over time. The alternative bcrypt named in SEC-002 remains viable if a compatibility or deployment constraint is discovered; do not implement plain SHA-family hashes or reversible encryption for passwords.

Enforce BR-001 on the server. Never log raw passwords or include a hash in API responses, fixtures, screenshots or reports.

### 7.2 JWT access tokens and browser storage — owner-approved decision

PRD rules require a signed JWT containing sub, iat, exp and jti; a pinned signing algorithm; a 30-minute default lifetime; server-side logout revocation; password-change revocation of prior tokens; role lookup from the database on every request; and no refresh tokens.

**Owner-approved browser transport:** set the access JWT in a host-only Secure, HttpOnly cookie in the public environment, with SameSite protection and a Path restricted to the application. Use an environment-appropriate cookie configuration for local HTTP development. Do not put the raw JWT in localStorage or make it available to frontend JavaScript. Configure cross-origin fetches to include credentials only for the explicit frontend origin. When practical, deploy frontend and API under the same site to keep cookie policy simple.

This satisfies AC-004: the successful login response delivers the signed access token through the Set-Cookie header rather than a JavaScript-readable token in JSON. API tests can inspect the cookie/JWT claims and verify `exp - iat` is 30 minutes (within the approved tolerance); browser JavaScript cannot read the HttpOnly cookie. A protected endpoint must accept the cookie and return 200. The frontend never receives the raw token through application JavaScript.

For revocation, persist active token sessions or revocation state keyed by jti with expiry. Logout revokes the presented session before clearing its cookie. Password change revokes every earlier session for that customer and then requires a fresh login. Read the user's current role from PostgreSQL for each authenticated request; never trust a role claim from the JWT as authoritative.

### 7.3 CSRF, CORS and origins

HttpOnly cookies require a CSRF defence. **Owner-approved approach:** require a server-validated CSRF token in a custom header for state-changing requests, validate the Origin against the same explicit allowlist used for the browser deployment, and apply SameSite cookie protection as defence in depth. Safe read-only methods do not use state-changing semantics.

CORS shall allow only configured frontend origins. Never combine wildcard origins with credentialed requests. Configure methods and headers narrowly, including X-Request-ID and the CSRF header where used. Local origins belong only in local configuration; public origins belong in the deployed environment configuration.

### 7.4 Authorization

Every non-public API operation enforces authentication, role and ownership on the server. Object identifiers must not permit a customer to access or modify another customer's data. Apply deliberate 404 masking for another customer's private resources where required by SEC-006. Admin routes have explicit function-level authorization and strict schemas. Neither frontend route guards nor hidden controls are considered security.

Registration always creates a customer role. There is no public admin creation/elevation route. Provision the administrator using a guarded management/seed operation outside the public registration path.

### 7.5 Other controls

- Pin the JWT algorithm and reject unsigned, tampered, expired, wrong-secret and revoked tokens.
- Apply login throttling per normalized account according to BR-007, and configurable registration rate limiting. Persist state in PostgreSQL or a deliberately selected shared rate-limit store; do not rely on per-process dictionaries in a multi-process deployment.
- Validate every request server-side with strict schemas; limit request body sizes and pagination/filter ranges.
- Use parameterized ORM/database operations only.
- Output-encode user-submitted names, address content and reviews; never render user text as raw HTML.
- Apply standard security headers including content-type protection, referrer policy, frame protections and a baseline CSP compatible with the frontend.
- Never log Authorization headers, cookies, CSRF tokens, passwords, secrets, or raw environment values.
- Store secrets only in platform environment/secret settings or CI secret storage. Provide .env.example with names and safe dummy values only.
- Run dependency/security scanning and secret scanning in CI; production dependency updates must be reviewed and locked.
- No real customer data, payment-card data or runtime third-party font/image requests.

### 7.6 Production environment guardrails

The application shall refuse to start if test-support functions are enabled outside APP_ENV local or test. Test-support routes must return 404 outside those environments, even to an administrator. Production configuration must not contain the test clock override, controlled failure injection, database reset command credentials or test seed passwords. Do not assume that hiding routes from OpenAPI is sufficient protection.

## 8. Background execution and nightly cleanup

### 8.1 Responsibilities

The worker has three responsibilities, all backed by PostgreSQL state and safe to retry:

1. Expire a pending order at its fixed reservation deadline, restoring stock and coupon usage exactly once, appending history and unlocking the cart while retaining lines.
2. Complete a due simulated refund in R2 after the configured delay.
3. Run nightly maintenance to remove expired authentication-session records and expired idempotency replay records.

### 8.2 Execution model

Use a separate worker process using the same backend image and service functions. Poll due reservation/refund work at a configurable short interval. Claim/order/refund work using row locks and `FOR UPDATE SKIP LOCKED`, or an equivalent database-backed claim method, then perform the state transition within a transaction. A crashed/restarted worker must safely retry.

The nightly maintenance job runs at **02:00 UTC by default**, configured via `MAINTENANCE_CLEANUP_UTC`; this is an operational default, not a product-rule deadline. It deletes only rows whose expiry timestamp is at or before the actual UTC time, in bounded batches. Cleanup SQL and transactions must be restart-safe and idempotent. If multiple worker instances are used, they must coordinate the scheduled run or safely divide work so concurrent runs cannot corrupt state.

Do not use an in-process scheduler as the only mechanism when the web service may have multiple workers or restart. Do not add Celery, Redis or a broker to the initial design unless implementation evidence proves PostgreSQL polling insufficient.

### 8.3 Reservation expiry semantics

The deadline is fixed at placement and is never extended by payment retries. Once now is at or beyond the deadline, expiry takes precedence over payment. A payment request may apply the expiry transition itself under BR-069 if it observes an elapsed reservation before the worker has done so. Both paths use the same transition service and transaction guarantees. Duplicate worker runs become no-ops after the order leaves pending state.

Time-based behaviour remains testable through the local/test clock and a deterministic expiry-trigger command/interface. The public worker uses the actual UTC clock and does not expose test clock endpoints.

### 8.4 Nightly retention cleanup

At each scheduled run:
- delete `auth_sessions` rows only where `expires_at <= now()`. Do not remove a revoked but unexpired session, because its revocation record is needed to reject the still-live JWT. Once the token has expired, authentication rejects it independently of the deleted session row;
- delete `idempotency_records` rows only where `expires_at <= now()`. The record must survive at least the full 24-hour retention in BR-070. Do not delete valid/unexpired rows to reduce table size;
- run in bounded batches, use supporting expiry indexes, log counts/duration/job result and request/correlation context, but never log session tokens, CSRF values or stored response secrets;
- ensure the optional FK from a retained payment-attempt row to an idempotency record uses `ON DELETE SET NULL`, so cleanup cannot fail because historic attempt audit data remains;
- commit each batch safely; an interruption must leave the remaining expired rows eligible for the next run.

No cleanup task may delete orders, payment attempts, refunds, inventory movements, order history, audit events or coupon-usage history. The maintenance task is not an account-deletion mechanism.

### 8.5 Operational behaviour

The worker shall:
- emit structured logs and request/correlation identifiers for each processed item;
- log resource IDs, affected-row counts, cleanup duration and transition results, but not secrets or unnecessary personal content;
- isolate a failed item so it does not permanently block later due work;
- use bounded retries and report repeatedly failing work without silently dropping it;
- rely on database state rather than process memory for claims and progress;
- start only after database connectivity is available, and tolerate temporary database restarts.

Polling interval, batch size, retry policy and nightly run time are configuration. They must not change business semantics or allow reservation/refund timing to drift beyond acceptance-test tolerances.

## 9. Environments and configuration

### 9.1 Environment matrix

| Concern | Local development | CI/test | Public portfolio |
|---|---|---|---|
| APP_ENV | local | test | production |
| Services | Docker Compose; optional frontend dev server | Compose test profile, isolated DB, app and worker | Hosted frontend, hosted API, separate worker and managed PostgreSQL |
| Database | Disposable local PostgreSQL volume | Fresh isolated DB per run/job; resettable seed | Private persistent managed database |
| Secrets | Untracked local .env | Ephemeral test-only values and CI secrets where required | Platform secret/environment settings |
| Seed data | Synthetic baseline; repeatable seed | Deterministic fixtures with stable IDs | Synthetic catalogue only; no public test credentials or test users with known passwords |
| Test support | Enabled | Enabled | Disabled; routes return 404 |
| Clock override | Allowed | Allowed | Disabled |
| Failure injection | Allowed | Allowed | Disabled |
| Browser origin | Local origin allowlist | CI browser origin/port | Exact deployed frontend origin(s) only |
| Test intensity | Developer-selected | Unit/API/DB/UI/accessibility/concurrency suites | Read-only health/catalog smoke checks by default; no destructive full regression |
| Logs/artifacts | Local diagnostics | Safe CI logs, Allure and Playwright artifacts | Runtime structured logs with secrets redacted |

### 9.2 Reference performance-test environment

The PRD's NFR-001–004 targets shall be evaluated in a documented Docker Compose reference environment, not inferred from the public host. **Proposed benchmark profile for owner review:**

| Resource | Reference baseline |
|---|---|
| Host OS / architecture | Linux x86_64 |
| CPU | 4 vCPU available to the Docker host |
| Memory | 8 GiB RAM available to the Docker host |
| Storage | SSD-backed storage with at least 20 GiB free before the test |
| Containers | API, worker, frontend and PostgreSQL run on the same Compose host; do not run unrelated CPU-heavy workloads during the measurement |
| Database | PostgreSQL 16; record the exact pinned image tag/digest and minor version in the run artefact |
| Data | Standard deterministic seed for NFR-001–003; 10,000-product generated dataset and required indexes for NFR-004 |
| Measurement | Single-user request load for PRD p95 targets; separate startup/readiness and UI content-timing measurements |

Every benchmark report shall record CPU/architecture, available RAM, storage type, OS/kernel, Docker Engine/Compose versions, exact database image/version, dataset size, build SHA and measured result. Comparisons are valid only when the same profile and workload are used. If the available host cannot provide this profile, label the result as a non-reference diagnostic run instead of claiming an NFR pass. Public-host performance observations are tracked separately and do not replace the Compose baseline.

This resource profile is a proposed engineering benchmark convention, not an approved product requirement; owner sign-off is pending.

### 9.3 Environment variable groups

The eventual .env.example and deployment runbook shall document the exact names. At minimum, configuration must cover:

- Application: APP_ENV, app version/build SHA, log level, public frontend URL and API base URL.
- Persistence: database connection string, connection pool limits and migration command configuration.
- Security: JWT signing secret, token TTL, password hash parameters, allowed frontend origins, cookie settings and registration/login rate limits.
- Business timing: reservation TTL, payment attempt cap, simulated timeout delay, refund delay, and other existing configurable PRD timing rules.
- Test-only controls: clock override, test-support enablement, deterministic failure injection and test seed passwords, accepted only in local/test.
- Worker: polling interval, batch size, retry limits, worker-enabled command and `MAINTENANCE_CLEANUP_UTC` (default `02:00`, UTC).
- Asset/build configuration: local asset base path, frontend API base URL, and any non-secret public runtime configuration.

Validate configuration at startup. Production-like startup must fail clearly if required secrets, origins or database settings are missing or invalid. Never provide real production-like defaults for credentials or signing secrets.

### 9.4 Migrations and seed policy

- Alembic owns every schema change. Do not rely on automatic table creation during normal application startup.
- Test migrations from an empty database and from the prior released schema.
- Run production migrations as an explicit, single release step before compatible application processes are promoted. Do not let every web/worker instance race to migrate at startup.
- Seed operations shall be idempotent and repeatable in local/test.
- The public portfolio may be seeded with synthetic product/category/coupon data. Do not publish known local/test account passwords or test-support secrets. Provision any administrator deliberately with a secure out-of-band operation.
- Back up persistent public database state before risky schema operations, and document a tested restore procedure. This is a demo system, but database recovery still needs a basic operational plan.

## 10. Public portfolio deployment

### 10.1 Deployment recommendation

**Proposed:** use a managed deployment platform with four separately configured runtime resources: static frontend, FastAPI web service, background worker and managed PostgreSQL. Render is a candidate to evaluate because the topology is compatible with conventional static/web/worker/database hosting; the final provider is still an owner-review decision. Confirm current region availability, database persistence, health checks, worker support, TLS, logs, service sleep/availability, backup capability and cost at the time of selection rather than relying on this document for vendor-specific guarantees.

Keep the deployment reproducible and container-based where supported. Use a pinned, known-good base image and build the frontend into static assets. The worker uses the same application release/image as the API so database logic cannot drift by version.

### 10.2 Release sequence

1. Build and test the release in GitHub Actions.
2. Build versioned frontend/backend artifacts with the source commit SHA.
3. Provision/update environment configuration and secrets through the hosting platform.
4. Apply the Alembic migration as a controlled one-off step.
5. Deploy the backend API and worker using the same release version.
6. Deploy the frontend configured to call the correct API origin.
7. Wait for liveness and readiness checks.
8. Run non-destructive public smoke checks: readiness, OpenAPI/schema availability, catalogue list/detail, pagination and important public content/disclaimer. Where auth is checked, use an intentionally provisioned disposable account and avoid placing orders or modifying stock unless a separate safe demo-test plan is explicitly approved.
9. Record the release SHA, smoke results and deployment URL in the release notes.

A failed readiness or smoke check blocks promotion or triggers the documented rollback path. Migration changes must be backward-compatible with the immediately prior app version during rollout, or use an explicitly planned maintenance window if compatibility cannot be preserved.

### 10.3 Public-environment restrictions

- HTTPS only; redirect HTTP to HTTPS at the platform edge.
- Database ingress restricted to application/worker access where the provider supports private networking.
- Exact frontend CORS allowlist; no permissive wildcard.
- No public test-support endpoints, reset operations, clock controls or failure injection.
- No seeded, well-known admin password. Admin access is owner-provisioned.
- Catalog images, icons and fonts are locally bundled/original/licensed; no runtime third-party dependency.
- Clear demo and simulated-payment notices remain visible.
- Public regression must not reset the database, change global stock, use fixture IDs to mutate common data, or run concurrency tests against shared demo records.
- Apply resource limits, logging and database connection-pool limits appropriate to the selected platform.

### 10.4 Public vs local testing

The complete acceptance suite runs against the isolated Compose test environment where state can be reset and faults/time can be controlled. The public deployment is not a substitute for the reproducible test environment.

Public automated checks should normally be read-only. A write test requires a separate agreed design using an isolated disposable account, data cleanup and strict no-shared-stock rules; test-support endpoints remain disabled in production. Never run reservation-expiry, refund, inventory-concurrency or reset tests against the shared public portfolio instance.

### 10.5 Operational caveats to verify before launch

The provider decision must confirm:
- Persistent PostgreSQL storage and backup/restore capability.
- API and worker support with independent start commands and coordinated release versions.
- HTTPS and custom/subdomain configuration for frontend/API origins.
- Whether platform health checks can distinguish liveness from database-backed readiness.
- Sleep/cold-start characteristics and how they affect portfolio availability and smoke tests.
- Log retention and redaction options.
- Service/database limits and expected cost for the chosen plan.

These checks are deployment acceptance criteria, not assumptions about provider plans.

## 11. Frontend architecture

### 11.1 Principles

The frontend is a responsive React + TypeScript single-page application following the approved design brief. Organize code by feature/domain rather than one large page directory. A page assembles components; a shared API client handles base URL, credential inclusion, request IDs, CSRF headers, JSON parsing and standardized errors. Feature hooks/services coordinate requests; reusable components own presentation and interaction semantics.

Recommended frontend areas: app/routing and session state; shared API client; catalog/search/filter; product details/variants; authentication/profile; addresses; cart/wishlist; checkout and simulated payment; order history/detail; admin; reviews; shared design system/accessibility utilities.

### 11.2 Authoritative vs presentation state

The server is authoritative for all price, discount, shipping, stock, coupon eligibility, minimum order, order state, payment/refund state and authorization decisions. Frontend-calculated totals are display estimates only, and checkout always uses server totals. If a submitted expected total differs, present the 409 PRICE_CHANGED response and the fresh server total without creating an order.

Display the API message for unavailable/inactive products and coupon failures; do not derive a different error precedence in the UI. Keep the pending-order deadline/banner and Pay now/Cancel order routes aligned to CL-18. The five-minute session warning follows CL-20 and does not refresh or extend the token.

### 11.3 Accessibility and deterministic UI testing

Implement semantic HTML, labelled controls, accessible names, visible focus, keyboard operation, announced validation/errors and reduced-motion behaviour. Core pages target WCAG 2.2 AA intent and use axe scans per NFR-011–012. Keep stable data-testid values using the approved area-element kebab-case pattern; also preserve role and label semantics so tests prefer role/label locators.

Ship all required fonts and imagery locally. Tests must not depend on live image/font/CDN services. Loading, empty, unavailable, validation and error states must be explicit rather than inferred from timing or colour alone.

## 12. SDET and verification architecture

### 12.1 Test layers

| Layer | Primary tools | Main proof obligations |
|---|---|---|
| Backend unit/service tests | Pytest | Rule boundaries, validation precedence, monetary arithmetic, state transitions, token handling and deterministic clock |
| API/integration tests | HTTPX + Pytest | Request/response contract, HTTP codes, authorization/ownership, idempotency, error envelope, coupon precedence, order lifecycle and rate limiting |
| Database tests | Pytest + read-only/direct SQL assertions; SQLAlchemy sessions for setup | Constraints, stock ledger reconciliation, immutable snapshots, unique pending order, idempotency uniqueness, and absence of partial state |
| UI journey tests | Playwright for Python | Core registration/login, browse, variant choice, cart, checkout/payment, reservation banner, orders, profile and admin journeys |
| Accessibility tests | Playwright + axe integration | Critical public/customer routes, keyboard/focus/names, automated violation gate |
| BDD | pytest-bdd | Selected business examples for checkout, coupon precedence, cancellation/refund and inventory |
| Contract checks | OpenAPI schema/HTTP assertions | Documented schemas, error envelope and actual response behaviour remain aligned |
| Concurrency tests | HTTPX clients/workers against PostgreSQL | No oversell; no duplicate order/payment/refund; serial race outcomes follow BR-073 |
| End-to-end CI reporting | Allure, Playwright traces/screenshots on failure | Reproducible diagnostics without secret leakage |

A rule that can be proven more reliably at service/API/database level must not rely solely on a UI test. UI tests assert the user-facing rendering and journey, API tests prove rules and authorization, and database assertions independently prove durable consistency.

### 12.2 Deterministic fixture strategy

Use the standard seed and named fixture characteristics from PRD §5.4/TR-003. Seeding is idempotent. Tests that write data create their own identifiable records and clean up only their own data; no parallel test may depend on a globally mutable fixture. Use isolated database state per test run where feasible, and separate test databases for parallel workers if schema/state isolation requires it.

Test accounts and passwords belong only in test configuration. Do not copy them into public deployment variables or public documentation. Read-only DB credentials are recommended for assertion code wherever the selected test topology permits separation from setup/admin credentials.

### 12.3 Required high-risk suites

At minimum, the architecture and backlog must allocate explicit test coverage for:
- BR-074 exact order-placement validation precedence.
- GAP-02 known-inactive vs unknown product/variant responses, with no mutation.
- GAP-11 identical coupon validation order at application and placement, including multiple simultaneous invalid conditions.
- Atomic TX-1 rollback across stock, order, coupon usage, cart lock and idempotency record.
- Same-key/same-payload idempotent replay and same-key/different-payload rejection.
- Single pending order and cart lock under concurrent placement attempts.
- Stock boundary and parallel purchase tests, including no negative stock.
- Payment timeout racing cancellation and reservation expiry; no attempt recorded when the reservation has expired.
- Exactly-once restoration/release and one refund under duplicate or racing operations.
- Password change invalidation, logout revocation, expiry warning and expired-token redirect.
- Customer-to-customer ownership isolation and admin-only actions.
- Test-support endpoint denial in production configuration.
- Responsive, keyboard, semantic locator and axe accessibility checks for key pages.

### 12.4 Continuous integration

A pull request workflow should:
1. Run backend lint/format and type checks, and frontend lint/format and TypeScript checks.
2. Build containers and verify configuration/startup validation.
3. Apply Alembic migrations to a fresh PostgreSQL database and seed it.
4. Run service, API, database, contract and required concurrency suites.
5. Run primary Chromium UI journeys and accessibility gates; run Firefox and WebKit according to the browser matrix in the approved backlog.
6. Publish Allure results and failure-only Playwright traces/screenshots as workflow artifacts, with retention appropriate for debugging.
7. Run secret/dependency checks.
8. Fail on weakened/removed assertions or unapproved changes to test references.

Use the same Compose service definitions and pinned versions locally and in CI. Public-deployment smoke checks are a separate, low-risk workflow and must not be used to claim the complete acceptance suite passed.

## 13. Observability, operations and failure handling

### 13.1 Logging and request correlation

Emit structured JSON logs with timestamp, level, application/build version, request ID, method/route, response status, elapsed time and safe domain identifiers where useful. Every HTTP response includes X-Request-ID. If the client supplies an accepted request ID, validate and bound it; otherwise generate one. Return it in the error envelope.

Redact credentials, JWTs, cookie contents, CSRF tokens and secret configuration. Do not log whole request bodies by default; payment-related routes must never log simulated or real card fields because no card fields should exist.

### 13.2 Health and readiness

Expose a minimal liveness endpoint to indicate the process is running, and a readiness endpoint that verifies required dependency connectivity, especially PostgreSQL. When the app is not ready, readiness returns 503 NOT_READY and avoids revealing internal details. The platform and CI should wait for readiness before running traffic or tests.

### 13.3 Failure behaviour

- Database unavailable at startup: fail readiness and retry only according to the process/platform policy; do not accept writes without persistence.
- Business validation or conflict: stable error envelope and no partial mutation.
- Unexpected exception: rollback the active transaction, log safe diagnostic detail with request ID, and return a generic error body.
- Worker interruption: the next worker run safely re-evaluates due work from database state.
- Migration failure: stop release promotion and follow documented rollback/repair instructions; do not let all app instances repeatedly run migration attempts.
- Frontend/API origin mismatch: deployment smoke fails; do not fix by switching CORS to wildcard.

### 13.4 Basic operations runbook

The release and operations notes must include commands or platform steps for local startup, database migration, deterministic seeding, test-support usage, app/worker startup, health checks, reading correlated logs, backup/restore, and recovery from a failed migration/deployment. Sensitive commands or credentials must not be embedded in public documentation.

## 14. Proposed technical decision register

The table distinguishes owner-confirmed requirements, proposed technical limits, and host-specific settings that are deliberately deferred. Owner-specified mechanics below are reflected in both architecture and ERD drafts.

| ID | Decision | Recommendation/status | Rationale / approval note |
|---|---|---|---|
| ARCH-01 | Overall service topology | Proposed: modular monolith, one API codebase, one PostgreSQL database, separate worker process | Small project and cross-domain atomic operations; avoids microservice overhead |
| ARCH-02 | Password hashing | Owner-approved: Argon2id | One of the algorithms permitted by SEC-002; strong adaptive password hashing |
| ARCH-03 | Browser token storage | Owner-approved: HttpOnly Secure cookie with JWT, explicit CSRF defence, server-side jti session revocation | Keeps the JWT unavailable to frontend JavaScript; AC-004 is verified by inspecting Set-Cookie and testing authenticated requests |
| ARCH-04 | Background execution | Owner-approved: PostgreSQL-polled worker using row locks/skip-locked claiming and idempotent transitions | Durable and testable; avoids new broker infrastructure |
| ARCH-05 | Internal identifiers | Owner-approved recommendation: UUID entity IDs; separate PRD-formatted order number | Opaque public references and separate human-facing order number; schema/version details are specified in the ERD |
| ARCH-06 | Public deployment | Owner-approved scope: public portfolio deployment plus local Compose; hosting provider remains open. Proposed candidate: managed static frontend, API, worker and PostgreSQL; evaluate Render | Keeps runtime shape simple and gives a clear operational review checklist |
| ARCH-07 | GAP-02 unavailable-item semantics | Owner-approved | 404 for unknown ID; 409 PRODUCT_UNAVAILABLE for known inactive/unavailable mutation target; no mutation |
| ARCH-08 | GAP-11 coupon precedence | Owner-approved | One first-failure order shared by apply and placement revalidation |
| ARCH-09 | Test-support boundary | Confirmed by SEC-018: enabled only local/test and disabled/404 in public/prod-like environments | Prevents destructive control-plane actions from being reachable in public deployment |
| ARCH-10 | Transaction and race policy | Confirmed by PRD BR-068–074 / NFR-005–009; specific row/constraint implementation to be fixed in ERD | Preserve all-or-nothing writes and first-valid-commit race outcomes |
| ARCH-11 | Database engine/version | Owner-specified: PostgreSQL 16, latest available minor in major version 16 | Stable version baseline for local Compose, CI and deployment |
| ARCH-12 | UUID generation | Owner-specified: native PostgreSQL `gen_random_uuid()` defaults for generated UUID keys | No extension added just for UUID generation |
| ARCH-13 | String limits and named schema objects | PRD-defined lengths are fixed; ERD proposes canonical caps where PRD is silent. All CHECK constraints and partial indexes have explicit names | Request schemas and bounded database fields must agree; CI will test boundary parity |
| ARCH-14 | Nightly retention cleanup | Owner-specified nightly deletion of expired `auth_sessions` and `idempotency_records`; proposed default 02:00 UTC, configurable, and never before expiry | Preserve live-token revocation and 24-hour replay guarantees |
| ARCH-15 | Review aggregate concurrency | Owner-specified: `SELECT ... FOR UPDATE` on the parent product row before review create/hide mutations and aggregate recomputation | Serializes per-product aggregate updates |
| ARCH-16 | Public hosting provider | Deliberately deferred until after architecture/schema model review | Provider does not alter relational model; hosting validation is a later deployment task |
| ARCH-17 | Performance reference environment | Proposed: Linux x86_64, 4 vCPU, 8 GiB RAM, SSD-backed storage with 20 GiB free, Compose services colocated; same profile and workload for comparisons | Makes NFR-001–004 reproducible; owner sign-off remains pending |

## 15. Remaining architecture review items

The owner has confirmed the PostgreSQL 16/UUID mechanism, cookie/CSRF auth approach, Argon2id, GAP-02/GAP-11 defaults, nightly-cleanup requirement, and product-row locking protocol. The following items still require owner review before merging the architecture/database documents:

1. **Overall architecture approach:** approve or adjust the proposed modular-monolith structure in ARCH-01 (§3–4), with one FastAPI application, one PostgreSQL database and a separate worker process.
2. **Catalogue field lengths:** confirm the proposed maxima in ERD §3.8 for fields where the PRD does not state numeric limits. PRD-defined limits are fixed. No implemented FastAPI/Pydantic request schemas currently exist, so true length parity can be verified only after implementation and CI boundary tests.
3. **Performance reference profile:** approve or adjust the proposed Linux/x86_64, 4-vCPU, 8-GiB, SSD-backed benchmark profile in §9.2. The PRD delegates definition of the reference environment to this document.
4. **Nightly run time:** the nightly cleanup itself is owner-specified; 02:00 UTC is a configurable proposed default in §8.2. Accept this default or specify another preferred UTC time.
5. **Document-level sign-off:** review the complete architecture and database drafts, including the named constraint/index registry and ERD relationships, before they are merged into `main`.

**Not a blocker:** public hosting provider and region can be selected later, as requested. Operational limits that depend on the chosen host will be set during deployment planning.

The cookie/CSRF transport, Argon2id, UUID identifiers, PostgreSQL 16 with native `gen_random_uuid()`, nightly cleanup, review-row locking, GAP-02 response behaviour, GAP-11 validation precedence, and dual local/public environment scope are owner-confirmed. There are no outstanding product-rule decisions for GAP-02 or GAP-11.

## 16. Architecture acceptance checklist

Before this document is marked approved, review that:
- [ ] Every core component and service boundary aligns with PRD v0.7 and User Stories v0.3.
- [x] Owner dispositions are recorded for the owner-specified technical mechanisms in §14; proposed field limits in ERD §3.8 are still awaiting confirmation.
- [x] The cookie/CSRF decision is settled and AC-004 remains testable through Set-Cookie and protected-endpoint checks.
- [x] Public hosting provider is explicitly deferred and does not block the relational model; production guardrails remain specified.
- [ ] Owner approves or adjusts the proposed modular-monolith architecture in ARCH-01.
- [ ] Owner confirms proposed catalogue-field length caps in ERD §3.8 before merge.
- [ ] Owner approves or adjusts the proposed reference performance environment in §9.2.
- [ ] Owner accepts the configurable 02:00 UTC nightly cleanup default or specifies another time.
- [ ] GAP-02 and GAP-11 rules are consistently represented in APIs and future tests.
- [ ] TX-1, TX-2, cancellation, expiry, idempotency and refund races preserve the PRD transaction boundaries.
- [ ] Test-support, seed credentials and clock overrides cannot be enabled in public deployment.
- [ ] The ERD can encode the required uniqueness, status, stock, idempotency and foreign-key constraints.
- [ ] The SDET strategy covers UI, API, database, contracts, concurrency, accessibility and CI evidence.
- [ ] The PRD, stories, design brief and planning README metadata are aligned.

## Appendix A — Traceability map

| Architecture area | Primary PRD references |
|---|---|
| Component boundaries and business service layer | NFR-018; FR-109–116 as applicable |
| REST and error contract | NFR-023–024; TR-008, TR-011; Appendix A |
| Product availability API | FR-025; BR-011–012, BR-018, BR-023; AC-019–021; GAP-02 / DQ-02 |
| Coupon rules | FR-046–048; BR-030–036, BR-075; AC-043–044 as applicable; GAP-11 / DQ-11 |
| Transaction integrity | FR-054–056; BR-038–042; BR-068–074; NFR-005–009 |
| Authentication/security | FR-001–010; BR-001–007; SEC-001–020 |
| Background processing | FR-064 and refund requirements; BR-041, BR-054, BR-069, BR-073; TR-004–006, TR-018; RSK-07 |
| Frontend semantics/accessibility | NFR-011–014; TR-001–003, TR-012–013, TR-020 |
| Test environment and CI | TR-001–023; NFR-017, NFR-019–027; MET and AC sections |
| Deployment and operational controls | NFR-010, NFR-015–016, NFR-019–022, NFR-025; SEC-011, SEC-016, SEC-018–019 |
| Public demo restrictions | NG-01, NG-02, NG-10, NG-13; SEC-016–018; ASM-03, ASM-06–09 |

## Appendix B — Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-20 | Initial architecture draft based on approved PRD v0.7, User Stories v0.3 and Design Brief v0.3. Records owner decisions for GAP-02, GAP-11 and dual local/public deployment scope. No application code implemented. |
| 0.2 | 2026-10-20 | Recorded owner approval of HttpOnly JWT cookie transport with CSRF protection, Argon2id, UUID entity IDs and a PostgreSQL-polled background worker. AC-004 verification is specified. Hosting provider and operational deployment settings remain deferred. |
| 0.3 | 2026-10-20 | Added owner-specified PostgreSQL 16/`gen_random_uuid()`, named CHECK and partial-index registry requirement, nightly expiry cleanup and `SELECT ... FOR UPDATE` review aggregate serialization. Aligned the architecture to Database Schema v0.2. Catalogue string caps absent from PRD are identified for owner confirmation. |
| 0.4 | 2026-10-20 | Aligned architecture metadata to Database Schema v0.3, and clarified that 02:00 UTC is a proposed configurable nightly-cleanup default, while the nightly cleanup requirement itself is owner-approved. Hosting provider remains deferred; proposed catalogue field caps await confirmation. |
| 0.5 | 2026-10-20 | Updated baseline references to owner-approved User Stories v0.4 and Design Brief v0.4, which now reflect the approved GAP-02/GAP-11 defaults. No backend implementation or migrations were created. |
| 0.6 | 2026-10-20 | Added the proposed reference performance-test profile required to measure NFR-001–004, and aligned architecture metadata to Database Schema v0.5. Hosting provider remains deferred; catalogue string caps and the benchmark profile await owner sign-off. |
| 0.7 | 2026-10-20 | Aligned schema reference metadata to Database Schema v0.7 after named constraint/index registry and table-description reconciliation. No application code or migration is present. Hosting provider remains deferred; proposed catalogue-field caps and performance reference profile await owner sign-off. |
| 0.8 | 2026-10-20 | Aligned metadata to Database Schema v0.8 after completing the explicit coupon-usage check registry. Expanded the owner-review list to call out the proposed modular-monolith approach, catalogue field caps, benchmark reference profile and configurable nightly run time. No application code or migrations exist. |
