# SDET Workflow — Owner-Led Testing with ChatGPT Assistance

This document defines the NexaCart quality-engineering workflow. Claude's application implementation instructions are in the repository-root `CLAUDE.md`. The project owner is responsible for writing and maintaining the test suite; ChatGPT assists the owner but does not take over test ownership.

## Responsibilities

### Project owner — test owner and author

The project owner is accountable for the test suite and is responsible for:

- Writing, maintaining and committing test scripts and test assets.
- Deciding test scope, priorities, coverage and acceptance of results.
- Reviewing and adapting all ChatGPT-generated test ideas, code, fixtures and test data before using them.
- Running tests in the intended environment, inspecting actual results and retaining evidence.
- Confirming whether a failure is a product defect, automation defect, test-data issue or environment/infrastructure issue.
- Deciding when test coverage and evidence are sufficient for acceptance.

### ChatGPT — testing assistant

ChatGPT is an assistant to the project owner. Use it to help with:

- **Test-case brainstorming:** derive happy paths, negative cases, boundaries, state transitions, permissions, failure modes and regression scenarios from approved requirements.
- **Test design and traceability:** map proposed test cases to PRD requirements, acceptance criteria, business rules and risk.
- **Script generation:** draft or improve Pytest, HTTPX, Playwright, SQL/database and selected pytest-bdd tests in the repository's existing style.
- **Test data and fixtures:** propose deterministic synthetic data, boundary values, fixture setup/cleanup and independent test-state strategies.
- **Debugging:** explain stack traces and assertion failures, identify likely causes, suggest targeted experiments and distinguish possible test, application, data and environment problems.
- **Test review:** check assertions, coverage gaps, flaky waits, selector stability, test independence, setup/teardown, security and maintainability.
- **Documentation and reporting:** help prepare test plans, defect reports, traceability records, regression summaries and test-evidence notes.

ChatGPT's output is a proposal, not an automatic change to the repository. The owner reviews, adapts, executes and accepts it. ChatGPT must not claim a test passed unless actual execution evidence is available and verified. Do not present suggested scripts or reasoning as execution results.

### Application implementation — Claude

- Implement approved product requirements in small increments.
- Maintain FastAPI/React code, API contracts, SQLAlchemy models and database migrations.
- Document behavioural changes and report tests actually run.
- Investigate and fix application defects using reproducible evidence.
- Keep implementation aligned with the approved PRD, architecture, schema and backlog.

Claude owns application implementation. The project owner owns test authorship and final test acceptance. ChatGPT supports the owner with QA and automation tasks.

## Feature-by-feature workflow

1. **Requirements and risk:** the owner and ChatGPT identify requirement IDs, acceptance criteria, business rules, risks, assumptions and out-of-scope behaviour.
2. **Test design:** ChatGPT helps brainstorm test conditions and expected outcomes. The owner selects the required coverage and owns the final test design.
3. **Test authoring:** the owner writes and maintains the test scripts. ChatGPT may draft scripts, assertions, data and fixtures for the owner to review and adapt.
4. **Contract review:** confirm API method/path, payloads, response schemas, status codes, error behaviour and required UI selectors against the approved contract.
5. **Implementation:** Claude implements the approved feature in a small increment, without silently changing requirements or weakening tests.
6. **Execution:** the owner runs relevant tests locally and through GitHub Actions when available, and retains actual output. ChatGPT can help formulate commands and interpret their results.
7. **Failure triage:** the owner establishes the evidence; ChatGPT helps analyse whether the failure is likely an application defect, automation defect, test-data issue or environment/infrastructure issue.
8. **Fix and regression:** Claude fixes confirmed application defects; the owner updates automation when needed and reruns the relevant regression. Meaningful assertions must not be weakened merely to obtain a passing build.
9. **Evidence and acceptance:** the owner records what ran, the actual result, remaining risks and known limitations, then decides whether the feature's verification is sufficient.

## Test design principles

- Assert observable outcomes and state transitions rather than implementation details unnecessarily.
- Prefer stable selectors such as accessible roles/names or agreed `data-testid` attributes.
- Use explicit Playwright waits for observable conditions; avoid arbitrary sleeps.
- Keep tests independent and provide reliable data setup and cleanup.
- Use HTTPX for direct REST tests and Playwright for browser workflows.
- Validate sensitive transaction outcomes independently in PostgreSQL.
- Cover authorization and customer-ownership boundaries.
- Test failed payments, duplicate requests, stock contention, cancellation and rollback where relevant to the approved scope.
- Use BDD for selected business-level scenarios, not as a wrapper around every low-level click.
- Use synthetic test data only. Never place secrets, tokens, production customer data or real payment data in fixtures, logs or artifacts.
- Review generated code before committing it. Prefer readable names, focused assertions and comments where they explain non-obvious intent or setup.
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

Use the current repository layout and approved testing strategy as the source of truth; do not introduce a parallel structure without a reason.

## How to ask ChatGPT for help

Provide the requirement IDs and acceptance criteria, relevant endpoint or UI contract, existing test conventions, relevant code, synthetic input/output examples and exact failure output. State the requested help clearly (for example: brainstorm boundary cases, draft a Pytest test, create test data, review a fixture, or debug a failure).

For generated scripts, ask for the purpose of each test, the expected result, required setup/cleanup and any assumptions. Compare the draft with the actual project before adopting it. Run commands yourself unless a connected tool explicitly enables and verifies execution, and keep the real output for the evidence record.

## Minimum evidence per feature

- Requirement or story reference.
- Test scenarios and expected outcomes.
- Test scripts used and any important test-data assumptions.
- Commands used for execution.
- Actual pass/fail/skip summary.
- Failure diagnostics when relevant.
- Untested risks, environment limitations and known defects.

Do not mark an unimplemented feature as covered, and do not claim broad performance or security validation from a small smoke test.
