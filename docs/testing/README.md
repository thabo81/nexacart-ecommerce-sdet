# SDET Workflow — ChatGPT Workstream

This document defines the quality-engineering workstream. Claude's application implementation instructions are in the repository-root `CLAUDE.md`.

## Responsibilities

### Application implementation (Claude)
- Implement approved product requirements.
- Maintain FastAPI/React code, API contracts, SQLAlchemy models and database migrations.
- Document behavioural changes and actual test execution results.
- Fix application defects based on reproducible evidence.

### SDET and test engineering (ChatGPT + project owner)
- Review approved requirements for testability and risk.
- Create test conditions, test cases and acceptance-test scenarios.
- Build and review Playwright/Pytest UI tests.
- Build and review HTTPX/Pytest API tests.
- Validate persisted state through PostgreSQL queries.
- Create selected BDD scenarios with pytest-bdd.
- Analyse test failures and propose targeted fixes.
- Maintain test strategy, defect reports and CI evidence.

The project owner reviews decisions and executes commands unless a connected tool explicitly enables and verifies an action.

## Feature-by-feature workflow

For each feature:

1. **Requirements:** identify requirement IDs, acceptance criteria, business rules, assumptions and out-of-scope behaviour.
2. **Test design:** identify happy paths, negative cases, boundaries, authorization risks, state transitions and database effects.
3. **Contract review:** agree on API method/path, payloads, response schemas, status codes, error behaviour, and required UI selectors.
4. **Implementation:** Claude implements the approved feature in a small increment.
5. **Automation:** add UI/API/database/integration tests at the appropriate layers.
6. **Execution:** run tests locally and through GitHub Actions; retain actual output.
7. **Failure triage:** classify the failure as an application defect, automation defect, test-data issue, or environment/infrastructure issue.
8. **Regression:** verify the fix without weakening meaningful assertions.
9. **Evidence:** record what ran, the actual result, known limitations and any outstanding defect.

## Test design principles

- Assert outcomes and state transitions, not implementation details unnecessarily.
- Prefer stable selectors such as accessible roles/names or agreed `data-testid` attributes.
- Use explicit Playwright waits for observable conditions; avoid arbitrary sleeps.
- Keep tests independent and provide reliable data setup/cleanup.
- Use HTTPX for direct REST tests; use Playwright for browser workflows.
- Validate sensitive transaction outcomes independently in PostgreSQL.
- Cover authorization and customer ownership boundaries.
- Test failed payments, duplicate requests, stock contention, cancellation and rollback.
- Use BDD for selected business-level scenarios, not as a wrapper around every low-level click.
- Do not report a pass without execution evidence.

## Planned automation layout

```text
tests/
  api/          # REST endpoint tests
  ui/           # Playwright browser tests
  integration/  # Cross-component workflow tests
  database/     # SQL/persistence assertions where appropriate
  bdd/          # pytest-bdd features and step definitions (if needed)
pages/           # Page Objects where they reduce duplication
allure-results/  # Generated locally; ignored by git
```

The exact test structure should be confirmed in the architecture and test strategy before implementation.

## Minimum evidence per feature

- Requirement or story reference
- Test scenario(s) and expected outcomes
- Command(s) used for execution
- Actual pass/fail summary
- Failure diagnostics when relevant
- Any untested risk or known limitation

Do not mark an unimplemented feature as covered, and do not claim broad performance/security validation from a small smoke test.
