# NexaCart Test Standards

**Status:** Proposed test-authoring and automation standard  
**Applies to:** All automated tests in the NexaCart repository  
**Primary stack:** Python, Pytest, HTTPX AsyncClient, FastAPI, SQLAlchemy, PostgreSQL and Playwright for Python

This document defines how tests are structured and which rules an engineer or AI assistant must follow when designing, generating, reviewing or changing NexaCart tests. Read it together with TESTING_STRATEGY.md and the approved product/architecture documents.

## 1. Mandatory working protocol

Before proposing or writing tests, the contributor MUST:

1. Read the relevant approved PRD section, user story, business rule and acceptance criteria.
2. Confirm that the endpoint, feature and response contract exist in the current implementation. Planned functionality is not an implemented API.
3. Classify each scenario as Tier 0, Tier 1 or Tier 2 and state the risk being addressed.
4. Identify the expected HTTP status, stable error code, side effects and database invariants.
5. Identify the required fixtures, factories, test database and isolation approach.
6. Check existing tests and shared helpers before adding new ones; extend existing coverage instead of duplicating it.
7. Propose the test cases and any required fixture/factory work before writing code when the scope or acceptance criteria are ambiguous.

The contributor MUST NOT invent business rules, API paths, response fields, status codes or acceptance-criteria identifiers. Ask for clarification when the approved sources do not define them.

## 2. Repository test layout

The target layout is organised by test purpose and business risk, not by HTTP verb.

```text
tests/
  conftest.py                   # Shared settings and top-level fixture composition
  factories/                    # Reusable synthetic data factories
    __init__.py
    users.py
    catalogue.py
    orders.py
  helpers/                      # Focused assertion and bounded-polling helpers
    __init__.py
  unit/                         # Pure domain/service tests
  api/
    conftest.py                 # Shared API app/client/auth fixtures
    tier_0_revenue/             # Cart, pricing, coupons, checkout, payment, stock, RBAC/IDOR
    tier_1_operations/          # Catalogue, search, order history
    tier_2_support/             # Profile, addresses and other low-risk support operations
  database/                     # PostgreSQL constraints, schema and direct persistence checks
  integration/                  # Cross-component, worker and transaction workflows
  ui/                           # Playwright browser tests
  bdd/
    features/                   # Selected business-level Gherkin scenarios
```

### Directory responsibilities

- **tests/conftest.py:** shared test settings, top-level resource lifecycle and fixture configuration. Keep domain-specific fixtures out of this file.
- **tests/factories/:** reusable creation of synthetic entities and valid defaults. Factories own data construction, not HTTP assertions or test orchestration.
- **tests/helpers/:** small reusable assertions and bounded polling utilities. Avoid a generic helper framework.
- **tests/api/conftest.py:** FastAPI app lifecycle, HTTPX client construction and reusable authentication/client fixtures.
- **tests/api/tier_0_revenue/:** critical transactional and security API scenarios.
- **tests/api/tier_1_operations/:** catalogue, discovery and order-read API scenarios.
- **tests/api/tier_2_support/:** minimal profile/address/support API scenarios.
- **tests/database/:** PostgreSQL-specific constraints, migrations and direct persistence invariants.
- **tests/integration/:** workflows spanning API, database and worker boundaries, including realistic concurrency.
- **tests/ui/:** browser-visible critical journeys using Playwright.
- **tests/bdd/:** a small number of business-readable scenarios selected for stakeholder value.

The repository already has tests and test configuration. This is the target organisation, not an instruction to move or rename existing files immediately. Preserve existing tests and their history; any reorganisation must be reviewed as a separate, explicit change. Do not create empty factory modules or placeholder test suites without a real use case.

## 3. Test naming and traceability

Test functions SHOULD follow this pattern:

test_<action>_<condition>_<expected_business_outcome>

Examples:
- test_checkout_rejects_insufficient_stock_without_creating_order
- test_coupon_rejects_expired_code_without_incrementing_usage
- test_customer_cannot_read_another_customers_order
- test_duplicate_payment_callback_records_one_approval

Names MUST identify the behaviour and expected outcome. Keep them readable; do not append every response field or implementation detail merely to satisfy a formula.

Every test MUST include a concise docstring that references the actual PRD requirement, business rule, story or acceptance criterion. Use the exact identifier from the approved source. Never fabricate an AC reference.

Use meaningful pytest markers consistently with the repository configuration, such as unit, api, integration, database, ui and bdd. Do not add new marker names without updating the project configuration.

## 4. Test anatomy: Arrange, Act, Assert

Tests MUST use Arrange-Act-Assert (AAA) and keep low-level setup out of test functions.

### Arrange
- Use factories and fixtures to create synthetic state.
- Declare the business-relevant preconditions clearly.
- Do not manually insert ORM rows or assemble large nested setup payloads inside test functions.
- Keep the scenario-specific values visible in the test so its intent is understandable.

### Act
- Perform the action through the layer under test.
- API integration tests use the shared HTTPX AsyncClient fixture.
- Do not call internal service functions when the purpose is to verify the public API contract.

### Assert
Assert the business outcome, not just that the request completed:
- expected HTTP status;
- stable application error code and relevant response contract;
- relevant response values;
- database state before/after where the operation changes persistent state;
- no partial mutation after a rejected operation;
- relevant audit, ledger, history, idempotency or attempt records.

Example shape (illustrative only; use the actual endpoint and error contract from the implemented feature):

```python
@pytest.mark.asyncio
async def test_checkout_rejects_insufficient_stock_without_creating_order(
    authenticated_client: AsyncClient,
    product_factory: ProductFactory,
    db_session: AsyncSession,
) -> None:
    """PRD Ref: use the approved checkout AC identifier here."""
    # Arrange
    product = await product_factory(stock_quantity=0)
    payload = build_checkout_payload(product_id=product.id, quantity=1)

    # Act
    response = await authenticated_client.post(
        "/api/v1/orders/checkout",
        json=payload,
    )

    # Assert
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INSUFFICIENT_STOCK"
    assert await order_count_for_customer(db_session, customer_id=...)
    # Assert the actual expected count/state; rejected checkout must not create an order.
```

The example demonstrates structure only. The error envelope already documented for NexaCart uses the top-level error object (error.code), not FastAPI's default detail.code shape. Follow the actual contract and update this example if the approved contract changes.

## 5. HTTPX AsyncClient and FastAPI lifespan

- API integration tests MUST use HTTPX AsyncClient with ASGITransport, unless a documented technical limitation requires an approved alternative.
- FastAPI startup and shutdown lifespan MUST be executed for tests that depend on application lifespan resources.
- Use an explicit ASGI lifespan manager/context around the application and client. Do not assume ASGITransport automatically runs lifespan handlers.
- Keep one consistent app configuration per test environment; inject test settings through the application factory.
- Do not start Uvicorn for in-process API tests.
- Ensure the client is closed and lifespan shutdown runs even when a test fails.
- Keep test-only settings separate from development and production configuration.
- Do not expose test-only routes, credentials or clock overrides in production-like environments; verify they return 404 or are otherwise unavailable according to the approved security contract.

Before adopting a specific lifespan helper or adding a dependency, check the current dependency lock/configuration and obtain approval for material dependency changes.

## 6. PostgreSQL and database isolation

Tier 0 API/integration tests MUST use a real PostgreSQL database. SQLite, mocked repositories or mocked database sessions are not substitutes for PostgreSQL transaction, locking, constraint or concurrency evidence.

### Standard transaction isolation

For ordinary tests that can share one connection:
- connect to the dedicated test database;
- begin an outer transaction for the test;
- bind the test SQLAlchemy session to that connection using the approved SQLAlchemy 2.x transaction-joining strategy;
- use nested transactions/savepoints so application-level session commits do not commit the outer test transaction;
- roll back the outer transaction during teardown;
- verify that the application request dependency uses the test-bound session/connection rather than creating an unrelated engine session.

The SQLAlchemy option join_transaction_mode="create_savepoint" is the preferred session-joining mechanism when the outer connection transaction is already active and the installed SQLAlchemy version supports it. Validate this against the actual application session dependency and driver behaviour before implementation.

### Important concurrency exception

A single outer transaction and one shared connection are NOT sufficient for realistic multi-connection concurrency tests. Tests for stock contention, row locks, worker claims or competing transactions MUST use independent database connections and an isolated disposable test database or another explicitly approved cleanup strategy. They must clean up reliably without relying on one test transaction to contain all concurrent work.

### Database safety

- Never point destructive test fixtures at development or production databases.
- Require explicit test-database configuration and validate the database identity/name before destructive setup.
- Keep migration/reset operations guarded and measurable.
- Do not let one test's committed data leak into another test.
- Restore environment variables and connection state changed during fixture setup.
- Verify cleanup even after exceptions and failed assertions.

The project target for a full database reset is under 30 seconds. Treat this as a measured performance target, not an assumed result. Record the command, environment and measured duration.

## 7. Fixtures and factories

Fixtures manage lifecycle and shared dependencies. Factories create domain data. Keep those responsibilities separate.

### Planned reusable fixtures

| Fixture | Responsibility |
|---|---|
| settings / test_settings | Consistent test configuration without mutating unrelated environment state |
| app | Application created through the production create_app factory with test settings and controlled dependencies |
| lifespan_app | Starts and shuts down the ASGI lifespan for the test app |
| api_client | Unauthenticated HTTPX AsyncClient |
| authenticated_client | HTTPX AsyncClient authenticated as a synthetic customer |
| admin_client | HTTPX AsyncClient authenticated as a synthetic administrator, only when admin behaviour exists |
| db_connection / db_session | PostgreSQL connection/session with the approved isolation strategy |
| migrated_test_database | Explicitly guarded disposable database prepared with Alembic migrations |
| browser / context / page | Playwright browser resources with consistent configuration and deterministic cleanup |
| frozen_clock / controlled_clock | Deterministic time control, only after the project clock strategy is selected |

Fixture names are proposed contracts. Implement only those required by an approved test slice. Do not create a fixture that silently bypasses the behaviour the test is intended to verify.

### Planned factories

| Factory | Responsibility |
|---|---|
| user_factory | Create synthetic customer/admin identities with unique identifiers and valid defaults |
| product_factory | Create products and variants with controlled price, status and stock |
| coupon_factory | Create coupons with explicit eligibility, time window and usage limits |
| cart_factory | Create customer-owned carts and items through supported persistence/domain setup |
| order_factory | Create orders in explicit valid states for lifecycle and ownership tests |
| payment_attempt_factory | Create simulated payment-attempt records where the schema and feature support them |

Factories MUST:
- generate unique values for unique fields;
- expose meaningful overrides for boundary scenarios;
- return created objects/identifiers needed by the test;
- use the same database/session isolation as the test;
- provide reliable cleanup through transaction rollback or explicit cleanup;
- avoid hidden side effects and unrelated default data;
- never use production data or real payment credentials.

Add factories incrementally as real test scenarios need them. Do not build a speculative factory framework for features that do not yet exist.

## 8. Authentication and test performance

- Do not hash a password with an expensive production password-hashing algorithm repeatedly in every test setup.
- Reuse a precomputed hash for a known synthetic test password, or use an explicitly approved test-only credential/token mechanism.
- NexaCart's approved architecture specifies Argon2id; do not assume bcrypt or silently change the password-hashing algorithm.
- Any fast path MUST remain test-environment-only and MUST NOT bypass the authorization rule being tested.
- Authentication tests must exercise real credential/session validation when that is the subject of the test.
- Tests for IDOR, role enforcement and ownership MUST use distinct principals and verify that one principal cannot access another principal's data.
- Never commit real secrets, tokens or reusable production credentials.

A test-token helper may be used for tests that are not testing login/token issuance, but it must create a token accepted by the actual test authentication middleware and must preserve the intended user identity and permissions.

## 9. Synthetic data, determinism and parallel execution

- Never use static unique values such as a shared test email address.
- Generate unique identifiers per test using UUIDs or an approved factory strategy.
- Use deterministic explicit values for business boundaries; randomness must not determine whether a test passes.
- Keep factory defaults minimal and override relevant values in the scenario.
- Ensure tests can run independently and in a different order.
- When pytest-xdist is enabled, isolate data by worker/database/schema or another proven mechanism. Unique strings alone do not isolate shared mutable database state.
- Do not rely on data left by seed scripts unless the test explicitly verifies the seed contract.

## 10. Time and asynchronous work

- Never use arbitrary fixed sleeps to wait for application behaviour.
- Do not use direct asyncio.sleep calls as a substitute for observing completion.
- For asynchronous workers or webhook processing, use a bounded polling helper that checks an observable condition, has a clear deadline and reports the last observed state on timeout. A short polling interval inside such a helper is acceptable; it is not a fixed wait used as an assertion.
- Use one approved time-control mechanism for expiry, coupon windows and reservation deadlines. Prefer an injectable application clock if the application architecture supports it.
- Do not freeze time globally in a way that breaks event-loop scheduling or unrelated tests.
- Ensure test-only clock control is unavailable in production-like configurations.

## 11. Playwright standards

- Reuse browser, context and page fixtures with reliable teardown.
- Use the configured base URL and explicit browser configuration.
- Prefer role, label and other user-facing locators; use stable test IDs where semantic locators are unsuitable.
- Wait for observable UI state or a specific network/application condition.
- Never use arbitrary fixed sleeps.
- Keep UI tests focused on user-visible behaviour. Verify server-side invariants in API/database tests.
- Capture traces, screenshots and logs on failure only where CI configuration supports safe retention and secret redaction.
- Do not expose authentication cookies, tokens or personal data in artifacts.

## 12. Assertions and error contracts

- Assert the exact expected status and stable business error code for negative paths.
- Follow NexaCart's standard error envelope and status/code catalogue; do not assume FastAPI's default validation/error shape.
- Do not assert unstable message wording unless the message itself is part of an approved contract.
- For money, use integer minor units and exact equality where the domain contract requires exact totals.
- For state-changing operations, assert both the response and relevant persisted state.
- For rejected requests, explicitly assert the protected state did not change.
- Prefer focused assertions over a large collection of repetitive field-by-field checks.
- Avoid broad snapshots that obscure which business invariant failed.

## 13. Test case selection: avoid bloat

For each business rule, select representative tests that prove distinct behaviours.

Prioritise:
1. valid business outcome;
2. high-impact invalid input and negative response;
3. lower/upper boundary and immediately adjacent values;
4. validation precedence where multiple rules can fail;
5. database invariants and rollback;
6. ownership/role enforcement;
7. idempotency, retries and concurrency where relevant.

Do not create one test per field merely to assert HTTP 200. Do not multiply every input partition by every user role, payment state and product type unless the interaction represents a real risk. Use parameterisation for genuinely equivalent cases and separate tests when the expected business outcome or invariant differs.

## 14. Code quality and review

Generated or modified tests MUST:
- be typed consistently with the project's Python conventions;
- follow PEP 8 and the configured Ruff/mypy rules;
- use descriptive names and concise docstrings;
- avoid duplicated setup and assertions;
- avoid hidden global state and order dependencies;
- preserve existing useful assertions;
- use only dependencies already present or explicitly approved;
- include no secrets or real customer/payment data.

Before finalising a test change, review:
- Does it test an approved requirement?
- Is the tier correct?
- Does it test the correct layer?
- Does it use the shared fixture/factory?
- Is the database real where required?
- Does isolation survive endpoint-level commits?
- Does the test verify persisted state and non-mutation?
- Is concurrency genuinely multi-connection where necessary?
- Is time deterministic?
- Can it run repeatedly and in parallel under the supported CI configuration?
- Does it add distinct risk coverage rather than duplicate an existing test?

## 15. AI and contributor guardrails

Any AI assistant or contributor MUST follow these standards and the repository's root CLAUDE.md.

- The repository owner owns QA test design, test authorship, execution, evidence and acceptance.
- Do not create, modify, delete, skip, weaken or reformat files under tests/ unless the owner explicitly authorises that specific test change.
- Do not claim a test passed unless it was actually executed and the command/result are available.
- Do not state that a fixture, endpoint, factory, test database or CI job exists without verifying it in the current repository.
- Distinguish clearly between proposed design, implemented code and verified behaviour.
- Report changed files, commands run, actual results, limitations and remaining risks.
- When a requirement is ambiguous or conflicts with the approved PRD/architecture, stop and ask the owner rather than inventing a rule.

## 16. Definition of Done for a test slice

A test slice is ready for review when:
- requirement and acceptance-criteria references are valid;
- scenarios are risk-classified and non-duplicative;
- fixtures/factories are reusable and correctly scoped;
- async application lifespan is handled correctly;
- PostgreSQL isolation and teardown are proven;
- Tier 0 invariants are asserted directly against persisted state;
- relevant negative paths prove no partial mutation;
- time/concurrency behaviour is deterministic and realistic;
- tests pass repeatedly under the supported local/CI command;
- failures provide useful diagnostics without leaking secrets;
- documentation and traceability are updated.

A green test run is evidence for the executed scope only; it is not proof that unimplemented features or untested requirements are complete.
