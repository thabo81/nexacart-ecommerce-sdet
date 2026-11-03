# NexaCart — Master Project Brief

**Status:** Draft planning baseline  
**Project type:** Full-stack multi-category e-commerce application plus SDET automation framework  
**Repository:** https://github.com/thabo81/nexacart-ecommerce-sdet

This document is the master product brief and records the original product vision, scope and high-level expectations. The formal PRD and other approved planning documents refine its requirements. This brief remains labelled a draft planning baseline; implementation status is maintained separately in §11 and in the repository README. If a requirement is ambiguous, record the question and propose a default; do not silently invent a high-impact business rule.

## 1. Product vision

Build a credible online store that lets customers browse products across several categories, compare price ranges and product variants, manage a cart and wishlist, check out using simulated payments, and track orders. Alongside it, build a maintainable SDET automation framework that verifies the application across browser, API and database layers.

The project has two distinct but coordinated parts:

1. **System under test:** the e-commerce application, backend APIs and data model.
2. **SDET deliverable:** risk-based test design, automated UI/API/integration/database checks, BDD for selected business flows, reports and CI/CD.

The purpose is to demonstrate practical software quality engineering, not merely to present a visually complete store.

## 2. Target users and roles

- **Guest:** browse and search the product catalog; begin shopping; must authenticate before protected actions according to approved rules.
- **Customer:** manage account details and addresses; manage cart and wishlist; place and view orders; review eligible products.
- **Administrator:** manage products, categories, inventory and order status through protected admin functionality.

Role permissions and ownership checks must be defined explicitly. Customers must not be able to read or modify other customers' private records or use administrative operations.

## 3. Product catalog

All major categories should contain a realistic mix of budget, mid-range and premium products. Products should have stable identifiers and fields appropriate to their category, including name, brand, category, SKU, description, price, stock, image, and optional attributes/variants.

### Computers and technology
- Desktop PCs, gaming PCs and custom-built PCs
- Laptops and monitors
- Keyboards, mice and gaming accessories
- Components such as GPUs, CPUs, memory and storage

Initial custom PC items can be listed as complete products. Configurable component selection and compatibility validation may be a later enhancement.

### Smartphones
- Apple iPhones
- Samsung Galaxy phones
- Xiaomi smartphones
- Google Pixel phones
- Affordable entry-level devices

Useful variants include storage capacity, colour and model.

### Wearables and audio
- Samsung Galaxy Buds
- Apple AirPods
- Headphones and gaming headsets
- Bluetooth speakers
- Smartwatches and fitness bands

### Football shirts and apparel
- Liverpool, Manchester United, Real Madrid, Barcelona and other club shirts
- National team shirts, training tops and sportswear
- Size, season/style and availability variants where applicable

Clearly distinguish fictional listings from officially licensed merchandise.

### Shoes and sneakers
- Nike, Adidas, Jordan and Puma footwear
- Running shoes, casual sneakers, training shoes and sports shoes
- Size, colour, style and stock variants

### Image policy
Use original/generated assets, properly licensed imagery, or assets whose usage terms have been reviewed. Use stable local test images where deterministic UI tests need predictable results. Do not scrape commercial retail websites. Brand references must not imply sponsorship or affiliation.

## 4. Planned customer functionality

### Accounts and authentication
- Registration, login and logout
- Profile and password management
- Delivery address management
- Appropriate session/token expiry and authentication failure handling

Do not add email verification or OTP unless explicitly approved as a new requirement.

### Product discovery
- Browse categories and subcategories
- Search by product or brand
- Filter by category, price, brand and availability
- Sort by price, rating and newest
- Product details, specifications and gallery
- Pagination and out-of-stock handling

### Shopping cart
- Add/remove items and update quantities
- Display subtotal, eligible discount, delivery cost and total
- Validate quantities and stock on the server
- Handle price or availability changes before checkout

### Wishlist
- Add and remove products
- Prevent duplicates according to the agreed model
- Move an item to the cart
- Persist the wishlist for the correct customer

### Coupons and delivery
- Percentage and fixed-value coupons
- Minimum order amount, expiry, usage limits and maximum discount
- Shipping options and explicit fee/free-shipping rules
- Server-side calculation of all totals

Exact coupon and shipping rules are defined in the owner-approved PRD and its referenced business rules. Implement those approved rules; any proposed change requires explicit owner review.

### Checkout and payments
- Review cart and address
- Choose delivery option
- Apply a coupon
- Review server-calculated order total
- Select a simulated payment outcome
- Confirm the order and display order details

Payment outcomes to simulate: approved, declined, timeout and processing error. No real payment gateway, real card data or actual money transfer is in scope.

### Orders and cancellation
- Order history and order details
- Defined order states: pending, confirmed, processing, shipped, delivered and cancelled, subject to the approved lifecycle
- Cancellation only when allowed by the order state
- Simulated refund statuses for eligible paid orders
- Correct inventory restoration according to the approved cancellation rules

### Reviews and ratings
- Eligible customers can submit a rating/review
- Validate rating boundaries, ownership and duplicate submissions according to approved rules

### Administration
- Create, update, deactivate and inspect products
- Manage categories and variants
- Update inventory
- View orders and update permitted statuses
- Inspect payment statuses and relevant audit events
- Enforce role-based authorization

### Notifications and audit events
Optional after the MVP: store in-app notifications for order/payment changes and audit events for designated sensitive actions. These must have explicit scope before implementation.

## 5. Core business risks and rules

The formal PRD must assign stable IDs and acceptance criteria. Initial risk areas include:

- Clients cannot set authoritative prices, discounts, stock or order totals.
- Requested quantity must be positive and cannot exceed available stock.
- Inventory must never become negative, including with concurrent requests.
- A declined, timed-out or errored payment must not create a falsely confirmed order.
- Repeated checkout/payment requests must not create duplicate orders or process a payment twice.
- Coupon rules must be validated on the server.
- Cancellation is allowed only for eligible order states.
- Eligible cancellation restores inventory and triggers the correct simulated refund state.
- Customer data is scoped to the authenticated customer.
- Administrative endpoints require the correct role.
- Persistent records must remain consistent when transactions fail or roll back.

## 6. Approved technology stack

### Application
- Frontend: React + TypeScript
- Backend: Python + FastAPI
- Database: PostgreSQL
- ORM and migrations: SQLAlchemy and Alembic
- API style: REST
- Local environment: Docker Compose

### Test automation
- UI: Playwright for Python + Pytest
- API: HTTPX + Pytest
- Database validation: direct SQL/query assertions against PostgreSQL
- BDD: pytest-bdd/Gherkin for selected business workflows
- Reporting: Allure
- CI/CD: GitHub Actions
- Diagnostics: Playwright traces, screenshots, browser logs, request/response evidence
- Test data: reusable fixtures and factories with safe setup/cleanup

Application code and tests may share one repository, but responsibilities and directories must be separated. The owner-approved Technical Architecture v0.9 is the authoritative technical baseline for the selected stack and system boundaries.

## 7. SDET coverage expectations

### UI
- Register/login and protected access
- Product search/filter/sort/details
- Cart add/update/remove and totals
- Coupon and checkout flow
- Successful and failed simulated payments
- Order history and eligible cancellation
- Customer/admin permissions
- Responsive layout and core accessibility behaviour

### API
- Positive/negative/boundary testing
- Schema and response contract checks
- Authentication and authorization
- Invalid input and error responses
- Duplicate requests and idempotency where required
- Product, cart, checkout, payment, order and inventory behaviour

### Database/integration
- Order header/items consistency
- Payment status persistence
- Inventory deduction/restoration
- Coupon usage
- User ownership relationships
- Transaction rollback and concurrency-sensitive operations
- Audit events where in scope

Tests must assert meaningful outcomes. Do not remove or weaken valid assertions to obtain a green build. Separate application defects, automation defects, test-data issues and environment failures using evidence.

## 8. CI/CD expectations

GitHub Actions should progressively run formatting/linting and type checks where configured, backend/API tests, database/integration checks, frontend checks, and Playwright UI tests. PostgreSQL and application services should be provisioned in a repeatable test environment. Upload useful reports/traces/screenshots when failure diagnostics are needed. A successful application start alone does not mean CI passed.

## 9. Delivery phases

1. Requirements and test architecture: PRD, user stories/flows, UI design, architecture, ERD and backlog.
2. Foundation: repository conventions, environments, database connectivity, health endpoint and initial checks.
3. Core shopping: catalog, images, search/filter/sort, authentication, cart and wishlist.
4. Transactions: addresses, shipping, coupons, simulated payments, orders and inventory consistency.
5. Advanced features: cancellation/refunds, admin functionality, reviews, notifications/audit events as approved.
6. Framework maturity: robust fixtures, BDD, Allure, failure artifacts, Docker test environments, CI and test documentation.

Work in small, reviewable increments. Define acceptance criteria and tests before implementing each major workflow when feasible.

## 10. Required planning documents

- `PRD.md` — requirements, non-goals, business rules, risks and measurable acceptance criteria
- `USER_STORIES_AND_FLOWS.md` — epics, stories, acceptance criteria and workflow diagrams
- `DESIGN_BRIEF_AND_WIREFRAMES.md` — visual identity, responsive layout, pages and wireframes
- `TECHNICAL_ARCHITECTURE.md` — components, boundaries, APIs, environments and operational concerns
- `DATABASE_SCHEMA_AND_ERD.md` — entities, columns, keys, constraints, relationships and ERD
- `IMPLEMENTATION_PLAN_AND_BACKLOG.md` — prioritized work items, dependencies and phased delivery

These documents establish the product and engineering planning baseline for implementation. Maintain cross-document traceability and record unresolved decisions rather than silently choosing high-impact defaults. Changes to approved requirements or architecture require explicit owner review.

## 11. Implementation status and delivery coordination

**Status date:** 2026-11-03

The Project Brief remains the product-planning baseline described above. The following status records engineering delivery; it does not change or supersede the approved product requirements.

| Milestone | Scope | Status |
|---|---|---|
| FOUND-001 | Repository structure and application foundation | Complete — merged into `main` (PR #4) |
| FOUND-002 | Docker Compose services and readiness checks | Complete — merged into `main` (PR #5) |
| FOUND-003 | API conventions, request IDs, error handling and diagnostics | Complete — merged into `main` (PR #6) |
| DATA-001 | PostgreSQL 16 schema, SQLAlchemy models and initial Alembic migration for 25 non-R3 tables | Complete — merged into `main` (PR #7) |
| DATA-002 | Deterministic synthetic seed data and local assets | Next planned implementation milestone |
| TEST-001 | Initial GitHub Actions quality gates and readiness smoke test | Outstanding |
| TEST-002 | Deterministic SDET fixtures | Outstanding |

The merged milestones establish engineering and persistence foundations. They do **not** mean that the core customer-facing e-commerce workflows have been implemented or accepted. Catalogue browsing, authentication, cart, wishlist, coupons, checkout, orders and related business workflows remain subject to their individual backlog items, implementation and QA acceptance. R2 work and optional R3 notifications remain governed by their approved release scope.

**Responsibility assignment**

- **Claude:** application and backend engineering, API and persistence implementation, migrations, seed implementation and application defect fixes.
- **Repository owner:** QA ownership, test design, writing and maintaining automated tests, test execution, evidence and acceptance.
- **ChatGPT:** independent QA planning, test review, coverage analysis, failure analysis and implementation review; not the owner of feature implementation or QA sign-off.

Claude works locally because its environment has no GitHub write credentials. The repository owner publishes branches, opens pull requests and merges approved changes.
