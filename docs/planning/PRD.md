# NexaCart — Product Requirements Document (PRD)

| Field | Value |
|---|---|
| Document | `docs/planning/PRD.md` |
| Version | 0.7 — approved baseline |
| Status | **Approved.** All decisions (DEC-01 – DEC-29) and clarifications (CL-01 – CL-20) are approved by the owner. DEC-01 – DEC-27 and CL-01 – CL-13 were approved on 2026-10-12; DEC-28, DEC-29 and CL-14 – CL-16 on 2026-10-13; CL-17 – CL-20 on 2026-10-20. No open PRD decisions or clarifications remain. |
| Date updated | 2026-10-20 |
| Baseline | `PROJECT_BRIEF.md` (initial source of truth). This PRD refines it and does not silently change it |
| Repository | https://github.com/thabo81/nexacart-ecommerce-sdet |
| Author role | Lead application engineer / technical architect |
| Companion work | SDET strategy, test design and automation are produced separately and must trace to the IDs in this document |
| Related planning documents | `USER_STORIES_AND_FLOWS.md` v0.2 approved on 2026-10-15; v0.3 is being aligned to this PRD. `DESIGN_BRIEF_AND_WIREFRAMES.md` v0.2 is approved locally; its repository update is pending. |
| Not yet created | `TECHNICAL_ARCHITECTURE.md`, `DATABASE_SCHEMA_AND_ERD.md`, `IMPLEMENTATION_PLAN_AND_BACKLOG.md` |

## Conventions

**Implementation status.** Every requirement in v0.1 is **Planned**. Nothing in this document is implemented or verified. Status values (`Planned` → `Implemented` → `Verified`) will be tracked in the traceability matrix of the backlog document. "Verified" means implemented *and* covered by passing automated acceptance checks in CI.

**Identifier scheme.** IDs are unique, stable and never renumbered; a withdrawn item is marked *Retired*, not reused.

| Prefix | Meaning | Prefix | Meaning |
|---|---|---|---|
| OBJ | Objective | SEC | Security / access-control requirement |
| NG | Non-goal | TR | SDET / testability requirement |
| FR | Functional requirement | AC | Acceptance criterion |
| NFR | Non-functional requirement | MET | Success metric |
| BR | Business rule | RSK / DEP / ASM | Risk / dependency / assumption |
| WF | Workflow | DEC / CL | Decision / clarification requiring approval (§14) |

**Change markers.** Rows tagged *(amended v0.N)* or *(new v0.N)* changed in version 0.N (a row changed in several versions carries each tag). New IDs continue the existing sequences (FR-109+, BR-068+, AC-074+, DEC-25+, CL-01+); v0.5 adds FR-116, BR-076 – BR-077, AC-117 – AC-118, DEC-29 and CL-16. Nothing was renumbered or reused. See Appendices C and D. Version 0.6 closed CL-16. Version 0.7 adds AC-119 – AC-121 and CL-17 – CL-20; no existing identifier was renumbered or reused.

**Priority** (MoSCoW): **M** Must, **S** Should, **C** Could. **Release**: R1, R2, R3 (§4.3).

**Decision tags.** `DEC-nn` marks a point where the brief is silent or ambiguous and this PRD set a default. The owner approved every default (DEC-01 – DEC-27) and every clarification (CL-01 – CL-13) on 2026-10-12, so these defaults are now requirements; any later change goes through change control and the change log. DEC-28, DEC-29 and CL-14 – CL-16 were approved on 2026-10-13; CL-17 – CL-20 were approved on 2026-10-20. No item is waiting for the owner.

**Normative language.** "Shall" = mandatory. "Should" = recommended. "May" = optional.

**Amounts.** Currency amounts are shown in rand (R) for readability and are stored/compared as integer minor units (cents) — see BR-024 and DEC-02.

---

## 1. Executive summary and product vision

NexaCart is a credible multi-category online store (computers and technology, smartphones, wearables and audio, football shirts and apparel, shoes and sneakers) with a deliberately **rule-rich, observable and deterministic** design. Customers browse, search, filter and compare variants, keep a cart and wishlist, check out with **simulated** payments, and track and cancel orders. Administrators manage catalog, inventory and orders.

The project has two coordinated parts:

1. **System under test (SUT):** React + TypeScript frontend, FastAPI backend, PostgreSQL database, delivered through Docker Compose.
2. **SDET deliverable:** risk-based test design and automated UI (Playwright), API (HTTPX), database (SQL), BDD (pytest-bdd), reporting (Allure) and CI (GitHub Actions) checks.

The product exists to demonstrate practical software quality engineering. The application is therefore designed around the areas where defects are most costly and most interesting to test: money, inventory, state machines, idempotency, concurrency and authorization. A visually complete store is a means, not the goal.

**Technology stack (unchanged from brief):** React + TypeScript; Python + FastAPI; PostgreSQL; SQLAlchemy with Alembic migrations; REST; Docker Compose; Playwright for Python + Pytest; HTTPX + Pytest; direct SQL assertions; pytest-bdd; Allure; GitHub Actions. Tooling beyond this (linters, type checkers) is proposed in NFR-017 and confirmed in the architecture document (DEC-22).

## 2. Problem statement and objectives

### 2.1 Problem statement
Demo e-commerce sites used for test-automation portfolios are typically thin: no real money rules, no concurrency hazards, no state machines, non-deterministic data, and no way to observe or reset state. Such systems cannot demonstrate risk-based testing at API, UI and database level. A realistic, testable system under test is needed that is small enough to build in phases and strict enough to make meaningful quality claims.

### 2.2 Objectives

| ID | Objective | Measured by |
|---|---|---|
| OBJ-01 | Deliver a complete browse → cart → checkout → order journey with simulated payment | AC-038, AC-104, MET-07 |
| OBJ-02 | Enforce all price, discount, shipping, stock and total calculation on the server | AC-025, AC-027, AC-032 |
| OBJ-03 | Guarantee inventory and order-state integrity, including under concurrency and failure *(amended v0.3)* | AC-045 – AC-047, AC-049, AC-034, AC-054, AC-074, AC-078, AC-082, AC-084, AC-105 – AC-107 *(amended v0.3)* |
| OBJ-04 | Enforce role-based and ownership-based access control | AC-010, AC-011, AC-061, AC-062, AC-090 |
| OBJ-05 | Make every business rule independently verifiable at API and database layers | MET-04 |
| OBJ-06 | Provide deterministic, resettable, observable test environments | TR-001 – TR-023, AC-067 – AC-069 |
| OBJ-07 | Run all automated checks repeatably in CI with useful diagnostics | MET-02, MET-05 |
| OBJ-08 | Keep planning artefacts traceable (requirement → rule → acceptance criterion → test) | MET-01, MET-09 |

## 3. Target users and roles

| Role | Description | Key characteristics |
|---|---|---|
| **Guest** | Unauthenticated visitor | Can browse, search and view products. Cannot hold a cart, wishlist or order (DEC-03) |
| **Customer** | Registered, authenticated shopper | Owns profile, addresses, cart, wishlist, orders and reviews; sees only their own private data |
| **Administrator** | Back-office operator, provisioned by seed/CLI only | Manages catalog, inventory and orders; inspects payments and audit events. Not a shopper (DEC-19) |
| **System** (non-human actor) | Payment simulator, reservation-expiry job, refund processor | Executes automated transitions; every system action is logged and testable |

The complete capability/authorization matrix is in §10.2.

## 4. Scope, non-goals and MVP boundaries

### 4.1 In scope (summary)
Accounts and authentication; addresses; catalog (5 categories, variants, search, filter, sort, pagination); cart; wishlist; shipping options; coupons; checkout with simulated payment; orders, cancellation and simulated refunds; reviews and ratings; administration; audit events; test-support capabilities for the SDET framework.

### 4.2 Non-goals

| ID | Non-goal |
|---|---|
| NG-01 | Real payment processing, real card data, real money movement |
| NG-02 | Email verification, OTP, magic links, **email-based password reset** (conflicts with the brief's no-email/OTP rule), MFA, social login |
| NG-03 | Guest checkout and anonymous server-side carts (DEC-03) |
| NG-04 | Multi-currency, tax engine, VAT invoices |
| NG-05 | Multiple warehouses, backorders, pre-orders, stock transfers |
| NG-06 | Returns/RMA, partial cancellation, partial refunds (only full cancellation and full refund) |
| NG-07 | Real carrier integration, tracking numbers, delivery-date promises beyond static estimates |
| NG-08 | Marketplace/multi-vendor, gift cards, loyalty points, recommendations/AI features |
| NG-09 | Coupon administration UI/API (coupons are seeded; DEC-08, DEC-19) |
| NG-10 | Product image upload, external image URLs, CDN (images come from a managed local asset set; FR-097) |
| NG-11 | Account deletion/data-subject tooling, user management UI, role changes |
| NG-12 | Native mobile apps, SSR/SEO optimisation, i18n/localisation, real-time inventory push |
| NG-13 | Email/SMS/push notifications (in-app only, optional, R3) |
| NG-14 | Configurable PC builder and component-compatibility validation (custom PCs are listed as complete products; possible later enhancement) |
| NG-15 | Scraping or copying commercial retail imagery or content |

### 4.3 Release plan and MVP boundary (DEC-01)

The brief defines six delivery phases but no MVP boundary. Approved mapping (DEC-01):

| Release | Brief phases | Contents | Exit criterion |
|---|---|---|---|
| **R1 — MVP** | 1 – 4 | Foundation, accounts, addresses, catalog + discovery, cart, wishlist, shipping, coupons, simulated payment, order placement/history/detail, inventory consistency, reservation expiry, cancellation of **unpaid** orders (paid-order cancellation is not available until R2; DEC-26), read-only display of seeded rating aggregates (CL-01), single-pending-order and cart-lock rules (DEC-25), health/seed/test-support, error envelope | All R1 **M** requirements Verified; no open Critical/High defects |
| **R2** | 5 | Cancellation of **paid** orders with inventory restoration and simulated refunds, administration, reviews, audit events | All R2 **M** requirements Verified; no open Critical/High defects |
| **R3 — Optional** | 5 (optional items) | In-app notifications; later enhancements (e.g., PC builder) only after separate approval | Separate approval and scope |

Phase 6 (framework maturity: fixtures, BDD, Allure, artifacts, CI) is **cross-cutting**: each release ships its own automated coverage, and framework maturity increases release by release. The SDET framework baseline (project skeleton, CI pipeline, health-check smoke test) begins in Phase 2 as in the brief.

## 5. Product catalog and category requirements

### 5.1 Categories

All five top-level categories shall contain a realistic mix of budget, mid-range and premium products (indicative price bands in R, DEC-16).

| Category | Subcategories | Variant dimensions | Typical specification attributes | Indicative tiers (budget / mid / premium) |
|---|---|---|---|---|
| **Computers and Technology** | Desktop PCs; Gaming PCs; Custom-built PCs (complete products); Laptops; Monitors; Keyboards and Mice; Gaming Accessories; PC Components (GPU, CPU, Memory, Storage) | Configuration (RAM/storage), colour | CPU, GPU, RAM, storage, screen size, resolution, refresh rate, connectivity, warranty | < 10,000 / 10,000–30,000 / > 30,000 |
| **Smartphones** | iPhone-style, Samsung Galaxy-style, Xiaomi, Google Pixel-style, Entry-level | Storage capacity, colour (model = separate product) | Screen size, battery mAh, camera MP, OS, network (4G/5G) | < 4,000 / 4,000–15,000 / > 15,000 |
| **Wearables and Audio** | Earbuds; Headphones and Gaming Headsets; Bluetooth Speakers; Smartwatches; Fitness Bands | Colour, case size (watches) | Battery life, connectivity, noise cancelling, water resistance | < 1,000 / 1,000–4,000 / > 4,000 |
| **Football Shirts and Apparel** | Club Shirts; National Team Shirts; Training Tops and Sportswear | Size, kit style (home/away/third), season, colour | Season, kit type, fabric, fit | < 600 / 600–1,500 / > 1,500 |
| **Shoes and Sneakers** | Running; Casual Sneakers; Training; Sports Shoes | Size (UK sizing labels), colour, style | Upper material, sole, fit | < 1,200 / 1,200–2,500 / > 2,500 |

Brand coverage follows the brief (e.g., Apple, Samsung, Xiaomi, Google; Nike, Adidas, Jordan, Puma; named clubs/national teams). Brand names are used nominatively only (BR-017). Wearables and Audio is designated a small-goods category (DEC-29, BR-077).

### 5.2 Logical product data

| Entity | Required fields (logical; physical design belongs to the ERD document) |
|---|---|
| **Category** | id, slug, name, parent (max 2 levels), is_active, sort order, small-goods designation (BR-077; inherited by subcategories) *(amended v0.5)* |
| **Product** | id, slug, base SKU/product code, name, brand, category (leaf), description, specifications (key–value), images (1–8; one primary; alt text mandatory), is_active, is_featured, is_fictional flag, created_at, updated_at |
| **Variant** (purchasable unit) | id, variant SKU (unique), option set (e.g., storage=256GB, colour=Black; unique per product), unit price (> 0, minor units), stock (≥ 0), is_active. Products without options have exactly one default variant (DEC-06) |
| **Derived** | from-price (lowest active variant price), availability state, rating average and count |

### 5.3 Image and licensing policy
- Only original/generated assets, properly licensed images, or assets whose terms have been reviewed. No scraping of retail websites.
- Deterministic UI tests require **stable local images** served by the application (no runtime third-party image or font requests — TR-013).
- Brand references shall not imply sponsorship or affiliation. Football shirts are explicitly **fictional/unofficial demo listings**; the storefront shows a site-wide demo notice and a per-product notice (BR-017, AC-022).

### 5.4 Baseline seed catalog (DEC-16)
The standard seed shall provide ≥ 5 categories, ≥ 2 subcategories each, ≥ 12 products per category (≥ 60 total), ≥ 3 products in each price tier per category, and ≥ 50% of products with multiple variants. It shall also include named, stable **fixture products** for edge cases:

| Fixture purpose | Required characteristic |
|---|---|
| Out of stock | All active variants stock = 0 |
| Single remaining unit | Stock = 1 |
| Low-stock threshold | Stock = 5 (boundary) and 6 |
| Inactive product | `is_active = false` |
| Multi-variant partial availability | One variant out of stock, another in stock |
| Single-variant product | Exactly one default variant |
| No reviews / many reviews | 0 reviews; ≥ 5 reviews with known average |
| Price boundaries | Prices at R999.99, R1,000.00, R500.00, R250.00, R249.99, R800.00 and R800.01 (coupon, shipping and minimum-order thresholds) *(amended v0.5)* |
| Small-goods minimum | Low-priced Wearables and Audio products such that four units total under R250.00, plus a non-small product priced under R250.00 *(new v0.5)* |
| Long name / special characters | Name near maximum length and containing `&`, quotes and non-ASCII characters |

## 6. Functional requirements

All requirements are **Planned**. "Refs" lists the governing rules/decisions.

### 6.1 Accounts and authentication

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-001 | Visitors shall register with name, email and password. The account is created with role `customer`. No email verification, OTP or confirmation step exists. Success returns 201 with the new user representation (id, name, email, role, created_at) and **no token or session**; the UI then signs the user in through the standard login operation (DEC-27). *(amended v0.2)* | M | R1 | BR-001–003, BR-006, DEC-04, DEC-27 |
| FR-002 | Email uniqueness is case-insensitive; duplicate registration returns 409 `EMAIL_ALREADY_REGISTERED`. | M | R1 | BR-002 |
| FR-003 | Users shall log in with email and password and receive a signed access token. Failure responses shall not reveal whether the email exists. | M | R1 | BR-004, BR-005, SEC-003 |
| FR-004 | Logout shall invalidate the presented token server-side so it can no longer authenticate. | M | R1 | BR-005, SEC-005 |
| FR-005 | Missing, malformed, expired or revoked tokens return 401 (`UNAUTHENTICATED` / `TOKEN_EXPIRED`). Five minutes before an access token expires, the UI shall display and announce “Your session is about to expire.” This warning does not refresh, renew or extend the token (CL-20). When the token expires, the UI redirects to login and returns the user to the intended destination after success. *(amended v0.7)* | M | R1 | BR-005, CL-20 |
| FR-006 | The UI shall guard protected routes (cart, wishlist, checkout, account, orders, admin) and redirect unauthenticated users to login. | M | R1 | DEC-03, CL-08 |
| FR-007 | Customers shall view and update their profile (name, optional phone). Email is read-only in the MVP. | M | R1 | BR-003, DEC-04 |
| FR-008 | Customers shall change password by supplying the current password; the new password shall satisfy policy, differ from the current one, and invalidate previously issued tokens. On success, the UI shall confirm the change and require the customer to log in again using the new password (CL-17). *(amended v0.7)* | M | R1 | BR-001, BR-005, CL-17 |
| FR-009 | Repeated failed logins shall be throttled per account. | S | R1 | BR-007, DEC-05 |
| FR-010 | Admin accounts shall be provisioned only via seed/CLI; no public endpoint or UI path can create or elevate an administrator. | M | R1 | BR-006, SEC-008 |

### 6.2 Addresses

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-011 | Customers shall create, list, update and delete saved delivery addresses. | M | R1 | BR-008 |
| FR-012 | Exactly one address is the default when at least one exists; the first address becomes default automatically. | M | R1 | BR-009 |
| FR-013 | Address fields shall be validated server-side and client-side. | M | R1 | BR-008 |
| FR-014 | Addresses are visible and modifiable only by their owner. | M | R1 | BR-064 |
| FR-015 | Editing or deleting an address shall not alter the delivery address stored on existing orders. | M | R1 | BR-050 |

### 6.3 Product discovery

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-016 | Users shall browse the category tree (categories and subcategories) and view category pages listing products. A parent category page includes the products of its subcategories (CL-07). *(amended v0.2)* | M | R1 | BR-011, CL-07 |
| FR-017 | Product listings shall be paginated and return per item: id, slug, name, brand, from-price, primary image, rating average/count (in R1 sourced from seeded review data, read-only; CL-01) and availability state. *(amended v0.2)* | M | R1 | BR-010, BR-016, CL-01 |
| FR-018 | Users shall search by product name or brand. | M | R1 | BR-014, DEC-15 |
| FR-019 | Users shall filter by category/subcategory, brand (multi-select), price range, and availability (in-stock only). Different filters combine with AND; multiple brands combine with OR. | M | R1 | BR-010, BR-012 |
| FR-020 | Users shall sort by price ascending/descending, rating, and newest, with deterministic tie-breaking. | M | R1 | BR-015 |
| FR-021 | Pagination parameters shall be validated; a page beyond the last returns an empty item list with correct metadata. | M | R1 | BR-016 |
| FR-022 | Product detail shall show name, brand, description, specifications, image gallery, variant selector, price, availability and rating summary. | M | R1 | BR-010, BR-012, CL-01 |
| FR-023 | Selecting variant options shall update displayed price, SKU and availability. Unavailable option combinations are visibly disabled. | M | R1 | BR-010, BR-012 |
| FR-024 | Out-of-stock products remain listed with an "Out of stock" indication and a disabled add-to-cart control; low stock (1–5 units) is indicated. | M | R1 | BR-012 |
| FR-025 | Inactive products are excluded from listings and search and return 404 on direct access. | M | R1 | BR-011 |
| FR-026 | Empty search/filter results shall show an empty state with a way to reset filters. | M | R1 | — |
| FR-027 | Search, filter, sort and page state shall be reflected in the URL so views are shareable and reproducible. | S | R1 | TR-020 |
| FR-028 | Fictional/unofficial listing and demo-store notices shall be displayed per BR-017. | M | R1 | BR-017 |
| FR-029 | Every product image shall have alt text; a placeholder is shown if an image is missing. | M | R1 | NFR-011 |
| FR-030 | The home page shall show category entry points and featured products. | S | R1 | — |

### 6.4 Shopping cart

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-031 | Each customer has one active server-side cart that persists across sessions, logout and login. | M | R1 | BR-064 |
| FR-032 | Customers shall add a variant with a quantity; adding an existing variant merges into the existing line. | M | R1 | BR-018, BR-021 |
| FR-033 | Customers shall update a line quantity (1 – maximum). | M | R1 | BR-018 |
| FR-034 | Customers shall remove a line or clear the cart. | M | R1 | — |
| FR-035 | The server shall validate quantity (positive integer, within line limit) and stock on every add/update. | M | R1 | BR-018, BR-037 |
| FR-036 | The cart shall display server-calculated subtotal, eligible discount, delivery cost (including any free first-order Standard shipping, BR-076) and total for the selected coupon and shipping option. *(amended v0.5)* | M | R1 | BR-025–029 |
| FR-037 | On every cart read, the server shall flag lines: `price_changed` (informational: it does not block checkout; the customer acknowledges it by submitting the new expected total, BR-022) and the blocking flags `unavailable`, `out_of_stock` and `insufficient_stock`, which block checkout until the line is corrected or removed. A cart-level blocking flag `below_minimum_order` applies when BR-077 is not met. *(amended v0.2)* *(amended v0.5)* | M | R1 | BR-019, BR-022 |
| FR-038 | A guest using "Add to cart" or "Add to wishlist" shall be sent to login and, after success, the intended action shall be completed. | M | R1 | DEC-03 |
| FR-039 | Client-supplied monetary values (unit price, discount, shipping fee, totals) shall be rejected; only server values are authoritative. | M | R1 | BR-020, SEC-008 |
| FR-040 | The header shall show the current cart item count. | S | R1 | — |

### 6.5 Wishlist

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-041 | Customers shall add a product to their wishlist; duplicates return 409 `WISHLIST_DUPLICATE`. | M | R1 | BR-023 |
| FR-042 | Customers shall remove a product from their wishlist. | M | R1 | BR-023 |
| FR-043 | The wishlist shall list items with current price and availability; unavailable items remain with an "unavailable" flag. | M | R1 | BR-023 |
| FR-044 | "Move to cart" shall add the item to the cart (requiring variant selection when multiple variants exist) and remove it from the wishlist only if the cart addition succeeded (atomic). | M | R1 | BR-023 |
| FR-045 | The wishlist persists per customer and is visible only to its owner. | M | R1 | BR-064 |

### 6.6 Coupons and shipping

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-046 | Customers shall apply a coupon code to the cart/checkout; the response returns the discount or a specific rejection reason code. | M | R1 | BR-030–036, BR-075 |
| FR-047 | Customers shall remove an applied coupon. | M | R1 | BR-030 |
| FR-048 | All coupon validation (existence, active, window, customer eligibility, minimum order, usage limits, caps) is enforced server-side and re-checked at order placement. *(amended v0.4)* | M | R1 | BR-031–036, BR-075 |
| FR-049 | The system shall expose available shipping options with the fee that applies to the caller's current cart (including free first-order Standard shipping, BR-076) and a static delivery estimate, from configuration. *(amended v0.5)* | M | R1 | BR-028, FR-107, CL-06 |
| FR-050 | Shipping fee, including first-order free Standard shipping eligibility (BR-076), shall be calculated server-side. *(amended v0.5)* | M | R1 | BR-028, BR-076, DEC-29, CL-16 |
| FR-051 | Coupons are provided by seed data in this version (percentage and fixed-value types). | M | R1 | NG-09, DEC-08 |

### 6.7 Checkout and simulated payment

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-052 | Checkout requires authentication, a non-empty cart without blocking flags, a saved address and a shipping option; violations return the status and error codes defined in BR-074 (e.g., 409 `CART_EMPTY`, 409 `PRODUCT_UNAVAILABLE`, 409 `INSUFFICIENT_STOCK`, 422 `VALIDATION_ERROR` for a missing address). The checks run in the order defined in BR-074. *(amended v0.2)* *(amended v0.3)* | M | R1 | BR-019, DEC-17, BR-074, FR-115 |
| FR-053 | The review step shall show items, address, shipping, coupon and the server-calculated total. | M | R1 | BR-025–029 |
| FR-054 | Placing an order shall re-validate cart, prices, stock, coupon and totals; if the total differs from the customer's displayed expected total, return 409 `PRICE_CHANGED` with fresh totals and create no order. The checks run in the BR-074 order: stock (step 9), coupon (step 10) and expected total (step 11), after the pending-order, address and cart checks. *(amended v0.2)* *(amended v0.3)* | M | R1 | BR-022, BR-036 |
| FR-055 | Order placement shall be one atomic transaction (TX-1) covering order header, items, address snapshot, stock deduction, inventory ledger entries, coupon usage, the cart lock and the idempotency record; any failure rolls back everything, and the transaction commits before any payment attempt. *(amended v0.2)* | M | R1 | BR-035, BR-038, NFR-005, BR-068 |
| FR-056 | Order placement shall be idempotent via an `Idempotency-Key` scoped per customer and operation: retries or concurrent duplicates with the same key and payload never create a second order or second stock deduction; a **different** key while a pending order exists is rejected by FR-111 (after the key, replay and schema checks of BR-074). *(amended v0.2)* *(amended v0.3)* | M | R1 | BR-048, DEC-11, BR-070 |
| FR-057 | The customer shall choose one simulated payment outcome — `approved`, `declined`, `timeout`, `processing_error` — via a clearly labelled "Simulated payment" control. Outcomes are returned in the response body as business outcomes, not transport errors. The payment operation accepts only these four values (anything else → 422) and is separate from order placement (FR-110). *(amended v0.2)* | M | R1 | BR-047, DEC-10, BR-069 |
| FR-058 | `approved`: payment attempt approved; order becomes `confirmed`; the stock deduction made at placement stands; the cart is emptied and unlocked (BR-072). *(amended v0.2)* | M | R1 | BR-045, BR-047, BR-072 |
| FR-059 | `declined`: attempt recorded as declined; order is **not** confirmed and stays `pending`; customer may retry or cancel. Stock deduction and coupon usage from placement remain in force and the cart stays locked (BR-069). *(amended v0.2)* | M | R1 | BR-045, BR-047 |
| FR-060 | `timeout`: the simulated delay is taken before the payment transaction and without holding the order lock. After the delay, if the order is still payable and unexpired, the attempt is recorded as `timed_out`; no payment is treated as captured; the order stays `pending`; the customer may retry or cancel. If the order was cancelled or its reservation expired during the delay, FR-114 applies and no attempt is recorded. Reservation effects from placement remain in force (BR-069). *(amended v0.2)* *(amended v0.3)* | M | R1 | BR-047, BR-069 |
| FR-061 | `processing_error`: attempt recorded as `error`; order not confirmed; stays `pending`; retry/cancel allowed. Reservation effects from placement remain in force (BR-069). *(amended v0.2)* | M | R1 | BR-047 |
| FR-062 | Payment retries on a pending order are allowed up to the attempt cap (counting every committed attempt); each retry is a new payment operation with a new `Idempotency-Key`; beyond the cap return 409 `PAYMENT_ATTEMPTS_EXHAUSTED`. *(amended v0.2)* | M | R1 | BR-049, BR-070 |
| FR-063 | Payment requests shall be idempotent; an order can never have more than one approved payment; paying an already-paid order returns 409 `ORDER_ALREADY_PAID`. Paying a cancelled or expired order returns 409 `ORDER_NOT_PAYABLE` (FR-114). *(amended v0.2)* | M | R1 | BR-046, BR-048, BR-070 |
| FR-064 | A pending order's stock hold expires after the reservation window; expiry cancels the order, releases stock and coupon usage exactly once, and unlocks the cart with its lines retained (BR-072). Once the deadline has elapsed, expiry takes precedence over payment (BR-069, BR-073). *(amended v0.2)* *(amended v0.3)* | M | R1 | BR-041, BR-040, BR-054, BR-072, BR-073, CL-05 |
| FR-065 | After approval the customer sees an order confirmation page with order number, items, address, totals and statuses. After a non-approved outcome they see a payment-failed page with retry and cancel actions. | M | R1 | — |
| FR-066 | No real card data shall be requested, transmitted, stored or logged (no PAN, CVV or expiry fields anywhere). | M | R1 | NG-01, SEC-017 |
| FR-067 | Every payment attempt shall be stored (order, attempt number, outcome, amount, timestamp, idempotency key). | M | R1 | BR-044, BR-046 |

### 6.8 Orders, cancellation and refunds

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-068 | Customers shall view a paginated history of their own orders, newest first. | M | R1 | BR-064 |
| FR-069 | Order detail shall show item snapshots, address snapshot, totals breakdown, order status, payment status, refund status and status history. | M | R1 | BR-050, BR-052 |
| FR-070 | Each order has a unique human-readable order number. | M | R1 | BR-051 |
| FR-071 | Order status changes shall obey the transition matrix; invalid transitions return 409 `INVALID_STATUS_TRANSITION`. | M | R1 | BR-043 |
| FR-072 | Customers shall cancel their own **unpaid pending** orders (including from the payment-failed page), releasing stock and coupon usage, without being required to provide a cancellation reason (CL-19). Cancelling a `confirmed` order is not available before R2 (DEC-26). *(amended v0.7)* | M | R1 | BR-053, BR-054, DEC-26, CL-19 |
| FR-073 | Customers shall cancel their own **confirmed** (paid) orders without being required to provide a cancellation reason (CL-19); stock is restored and a full simulated refund is created. *(amended v0.7)* | M | R2 | BR-053, BR-055, CL-19 |
| FR-074 | Refunds shall progress `refund_pending` → `refunded` via the simulated refund processor, with a configurable delay (zero in test environments). | M | R2 | BR-056, DEC-13 |
| FR-075 | Cancellation of unpaid pending orders (by the customer or the expiry job) shall be idempotent and concurrency-safe: stock is restored and coupon usage released exactly once; repeating a cancellation returns 409 `ORDER_NOT_CANCELLABLE` with no side effects. The paid-order counterpart is FR-109 (R2). *(amended v0.2)* | M | R1 | BR-040, BR-054 |
| FR-076 | Every status change shall append an entry (from, to, actor, timestamp, reason) to the order status history. | M | R1 | BR-052 |

### 6.9 Reviews and ratings

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-077 | Eligible customers shall submit a rating (1–5) and optional comment for a product. | M | R2 | BR-058, BR-059 |
| FR-078 | Eligibility requires a `delivered` order containing the product; otherwise 403 `REVIEW_NOT_ELIGIBLE`. | M | R2 | BR-058 |
| FR-079 | Rating boundaries and comment length are validated server-side. | M | R2 | BR-059 |
| FR-080 | One review per customer per product; duplicates return 409 `REVIEW_DUPLICATE`. | M | R2 | BR-059 |
| FR-081 | Product pages shall show the review list and the aggregate rating, which feeds the rating sort and listing display; the aggregate is recomputed when reviews are created or hidden. Read-only display of seeded aggregates is available from R1 (CL-01). *(amended v0.2)* | M | R2 | BR-060, CL-01 |
| FR-082 | Administrators may hide a review; hidden reviews are excluded from lists and aggregates. | C | R2 | BR-060 |

### 6.10 Administration

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-083 | The admin area and all admin endpoints are accessible only to role `admin`. | M | R2 | BR-065, SEC-007, CL-08 |
| FR-084 | Admins shall create products with at least one variant. | M | R2 | BR-010, BR-013, CL-02, CL-03 |
| FR-085 | Admins shall update product details (not id, slug or SKU). | M | R2 | BR-013, CL-02 |
| FR-086 | Admins shall deactivate and reactivate products; hard deletion of ordered products is prevented. | M | R2 | BR-061 |
| FR-087 | Admins shall inspect any product including inactive ones, with variants and stock. | M | R2 | — |
| FR-088 | Admins shall add, update and deactivate variants. | M | R2 | BR-061, CL-02, CL-03 |
| FR-089 | Admins shall create, update and deactivate categories and subcategories. The small-goods designation of a category (BR-077) is part of category management. *(amended v0.5)* | M | R2 | BR-061, CL-02 |
| FR-090 | Admins shall adjust inventory (delta or absolute) with a mandatory reason; results below zero are rejected. | M | R2 | BR-062, BR-042, CL-03 |
| FR-091 | Admins shall list and filter orders (status, date range, order number, customer email). | M | R2 | CL-04 |
| FR-092 | Admins shall inspect order detail including payment attempts, refund, status history and ledger movements. | M | R2 | — |
| FR-093 | Admins shall move orders along permitted forward transitions only. | M | R2 | BR-057 |
| FR-094 | Admins may cancel orders in `pending`, `confirmed` and `processing`, with a reason. | M | R2 | BR-053–055, CL-09 |
| FR-095 | Admin inputs are validated with the same rules as customer-facing inputs. | M | R2 | BR-010 |
| FR-096 | Product price/active-state changes affect carts (flagged) but never existing orders. | M | R2 | BR-063 |
| FR-097 | Product images are selected from the managed local asset set; arbitrary upload and external URLs are not supported. | S | R2 | NG-10 |

### 6.11 Audit events and notifications

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-098 | The system shall record audit events for designated sensitive actions (BR-066). | S | R2 | DEC-20 |
| FR-099 | Admins shall view and filter audit events by actor, action, entity and date. | S | R2 | — |
| FR-100 | Audit events are append-only; no application operation updates or deletes them. | S | R2 | BR-066 |
| FR-101 | The system shall create in-app notifications for order and payment status changes. | C | R3 | BR-067 |
| FR-102 | Customers shall view and mark their own notifications as read. | C | R3 | BR-064, BR-067 |

### 6.12 Platform

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-103 | The API shall expose liveness (`/health/live`) and readiness (`/health/ready`, reflecting DB connectivity) endpoints. | M | R1 | NFR-010 |
| FR-104 | A deterministic seed/reset capability shall restore the baseline dataset (idempotent). | M | R1 | NFR-008, TR-003 |
| FR-105 | Guarded test-support interfaces shall be available only in `local`/`test` environments. | M | R1 | TR-004, SEC-018, DEC-21 |
| FR-106 | The API shall publish an accurate OpenAPI 3.x document and interactive docs. | M | R1 | NFR-024 |
| FR-107 | Business parameters (§8.2) shall be configuration, not hard-coded constants. | M | R1 | §8.2 |
| FR-108 | All errors use one envelope with a stable machine-readable code and request ID (Appendix A). | M | R1 | TR-011 |

### 6.13 Release reconciliation and checkout/cart lifecycle (new in v0.2)

| ID | Requirement | Pri | Rel | Refs |
|---|---|---|---|---|
| FR-109 | Cancellation of paid (`confirmed`) orders shall be idempotent and concurrency-safe: stock is restored exactly once and at most one refund is created; repeating a cancellation returns 409 `ORDER_NOT_CANCELLABLE` with no side effects. Paid-order counterpart of FR-075. | M | R2 | BR-040, BR-055, BR-056 |
| FR-110 | Order placement (create the pending order and reserve stock) and payment attempt shall be two separate API operations with separate transactions and separate idempotency scopes. The UI performs them in sequence when the customer selects Place order. | M | R1 | BR-068, BR-069, BR-070, DEC-10, DEC-11 |
| FR-111 | A customer shall have at most one pending order. A further placement that is not a replay and passes the key, replay and schema checks returns 409 `CHECKOUT_ALREADY_PENDING` (details: the existing order id) whatever its new `Idempotency-Key` or payload content, ahead of the address, cart, stock, coupon and total checks (BR-074 step 5); a replay of the original key and payload returns the stored response; concurrent placements create exactly one order. *(amended v0.3)* | M | R1 | BR-071, DEC-25 |
| FR-112 | While a pending order exists the cart is locked to it: cart mutations return 409 `CART_LOCKED`; cart reads succeed and show a locked indicator and the pending order id; the cart and checkout entry show a pending-order banner offering "Pay now" and "Cancel order". The payment page and order detail display "Reserved until [time]" using the order's reservation deadline, and order detail offers a "Pay now" route (CL-18). *(amended v0.7)* | M | R1 | BR-071, DEC-25, CL-18 |
| FR-113 | Cart behaviour after outcomes: approval empties and unlocks the cart; cancellation or reservation expiry unlocks it and retains its lines and selections for re-validation. | M | R1 | BR-072, DEC-25 |
| FR-114 | Paying an order that is cancelled or expired returns 409 `ORDER_NOT_PAYABLE` and records no payment attempt. If the reservation deadline has elapsed, expiry takes precedence over payment: the payment operation applies the expiry transition first. Payment, cancellation and expiry on the same order are serialised so that exactly one outcome wins, and the simulated payment delay never blocks or overrides cancellation or expiry. *(amended v0.3)* | M | R1 | BR-049, BR-069, BR-073 |
| FR-115 | Order placement shall evaluate its preconditions in the 12-step order defined in BR-074 and return the specified status and error code for each failure. An existing pending order is reported (step 5) before address, cart, stock, coupon and total checks; idempotency replay and key-reuse resolution (step 3) precede schema validation (step 4). A rejected request creates no order, inventory movement, coupon usage or idempotency record. *(amended v0.3)* | M | R1 | BR-074 |
| FR-116 | The system shall enforce the minimum order rule: the pre-coupon (pre-discount) subtotal must be at least R250.00 unless the cart contains four or more units of products from small-goods categories (Wearables and Audio), counting quantities across all such lines. The exception waives only this restriction and grants no shipping benefit. The cart shows the rule and a blocking `below_minimum_order` flag; when neither the minimum nor the exception is satisfied, placement returns 409 `ORDER_BELOW_MINIMUM`. *(new v0.5)* *(amended v0.6)* | M | R1 | BR-077, DEC-29 |

## 7. Non-functional requirements

Targets are measured in the Docker Compose reference environment with the standard seed; exact reference hardware is defined in the architecture document.

| ID | Requirement | Pri |
|---|---|---|
| NFR-001 | Read API endpoints (listing, detail, cart, order history): p95 ≤ 300 ms at single-user load | S |
| NFR-002 | Write endpoints (cart update, order placement, payment): p95 ≤ 800 ms excluding the configured simulated delay | S |
| NFR-003 | Product listing page shows meaningful content within 2.5 s on the reference environment | S |
| NFR-004 | With a generated 10,000-product dataset, filtered listing p95 ≤ 800 ms (indexes defined for filter/sort columns) | C |
| NFR-005 | Multi-row business operations (place order, cancel, refund, inventory adjust, move to cart) are ACID transactions | M |
| NFR-006 | The database enforces invariants as a backstop to application logic: stock ≥ 0, unique email, unique SKU, at most one approved payment per order, at most one refund per order, unique (customer, product) wishlist and review, foreign keys, at most one `pending` order per customer (BR-071), unique idempotency key per scope (BR-070) *(amended v0.2)* | M |
| NFR-007 | Schema changes use versioned migrations (Alembic) that apply cleanly to an empty and to a seeded database | M |
| NFR-008 | Seeding is idempotent and repeatable; running it twice yields the identical baseline | M |
| NFR-009 | Business invariants hold under concurrent requests (e.g., 20 parallel purchases of 5 remaining units sell exactly 5); no business-critical state is held only in process memory | M |
| NFR-010 | `docker compose up` yields a ready system within 120 s; readiness reflects database connectivity | M |
| NFR-011 | Core flows meet WCAG 2.2 AA intent: keyboard operable, visible focus, labelled controls, sufficient contrast, meaningful alt text, announced errors | M |
| NFR-012 | No critical or serious automated accessibility violations (axe) on home, listing, detail, cart, checkout, login | S |
| NFR-013 | Responsive from 360 px to 1920 px with no horizontal page scroll; reference test viewports 375×812, 768×1024, 1280×800 | M |
| NFR-014 | Browser support: latest Chromium (primary); Firefox and WebKit via Playwright (secondary) (DEC-23) | M |
| NFR-015 | Structured (JSON) logs with timestamp, level, request ID and route; passwords, tokens and secrets are never logged | M |
| NFR-016 | Every response carries `X-Request-ID`, repeated in error envelopes | M |
| NFR-017 | Quality gates in CI: backend lint/format and type check; frontend lint, format and type check (ruff, mypy, ESLint, Prettier, `tsc`; DEC-22) | M |
| NFR-018 | Business rules live in a backend service layer, not in routers or UI components; UI mirrors rules only for convenience, never as the sole enforcement | M |
| NFR-019 | Configuration via environment variables; no secrets in the repository; `.env.example` provided | M |
| NFR-020 | All services run in containers with pinned image versions; one-command local bring-up | M |
| NFR-021 | Timestamps stored in UTC and exchanged as ISO-8601; money as integer minor units | M |
| NFR-022 | Only synthetic data; no real personal data in seeds, fixtures, logs or CI artifacts | M |
| NFR-023 | REST/JSON API under `/api/v1`; consistent pagination and error envelopes | M |
| NFR-024 | The OpenAPI document matches actual behaviour (verified by contract checks in CI) | M |
| NFR-025 | The API process is stateless and horizontally scalable (scaling is not load-tested) | S |
| NFR-026 | Each release updates requirement status and the traceability matrix | M |
| NFR-027 | Resetting the test database to baseline takes ≤ 30 s | S |

## 8. Business rules

### 8.1 Rules

**Identity and input**

| ID | Rule |
|---|---|
| BR-001 | Password: 8–128 characters, at least one letter and one digit, not equal to the email address. Stored only as an adaptive salted hash (SEC-002). |
| BR-002 | Email: trimmed, lowercased for comparison, valid format, ≤ 254 characters; unique case-insensitively. |
| BR-003 | Name 1–100 characters (trimmed, not blank). Phone optional: 7–15 digits with optional leading `+`. |
| BR-004 | Login failure for unknown email and wrong password is indistinguishable (same status, code, message): 401 `INVALID_CREDENTIALS`. |
| BR-005 | Access token lifetime 30 minutes (configurable). Logout revokes the presented token; changing password invalidates all tokens issued earlier. No refresh tokens in the MVP (DEC-04). |
| BR-006 | Exactly one role per user: `customer` or `admin`. Role can never be set or changed by client input. |
| BR-007 | After 5 consecutive failed logins for an account, further attempts return 429 `RATE_LIMITED` for 15 minutes (even with the correct password); success resets the counter. Values are configurable. |

**Addresses**

| ID | Rule |
|---|---|
| BR-008 | Max 10 saved addresses per customer (11th → 409 `ADDRESS_LIMIT_REACHED`). Required: recipient name (1–100), phone, line 1 (1–150), city (1–80), province (1–80), postal code (4 digits for the default delivery country). Line 2 optional (≤ 150). Delivery country is a single configured value (DEC-17). |
| BR-009 | Exactly one default address when ≥ 1 exists; setting a new default unsets the previous one; deleting the default promotes the most recently created remaining address. |

**Catalog**

| ID | Rule |
|---|---|
| BR-010 | Variant unit price is a positive integer in minor units and is authoritative. Product from-price = lowest active variant price. Price filter and price sort use from-price (DEC-06). |
| BR-011 | A product is visible to guests/customers only if the product and its category are active and it has ≥ 1 active variant. |
| BR-012 | Availability per variant: `out_of_stock` if stock = 0; `low_stock` if 1 ≤ stock ≤ 5 (configurable); else `in_stock`. A product is out of stock only if all active variants are. The "in stock" filter matches products with ≥ 1 active variant with stock > 0. |
| BR-013 | Product id, slug and SKUs are immutable after creation. |
| BR-014 | Search input is trimmed, internal whitespace collapsed, 2–100 characters; matching is case-insensitive substring on name or brand. No typo tolerance or relevance ranking in the MVP (DEC-15). |
| BR-015 | Sort definitions: `price_asc`/`price_desc` by from-price, ties by id ascending; `rating_desc` by average descending, then review count descending, then id; unrated products last; `newest` by created_at descending, then id. Default sort is `newest`. |
| BR-016 | Pagination: `page` ≥ 1; `page_size` 1–48, default 12; responses include `total_items` and `total_pages`. Invalid values → 422. |
| BR-017 | All MVP listings are fictional demo listings. Brand and club names are used nominatively; the UI shall state that listings are fictional/unofficial and that no sponsorship or affiliation is implied. |

**Cart and wishlist**

| ID | Rule |
|---|---|
| BR-018 | Line quantity is an integer 1–10 (configurable) and ≤ the variant's current stock; max 20 distinct lines per cart. Over-limit → 422; over-stock → 409 `INSUFFICIENT_STOCK` (details include available units). |
| BR-019 | The cart does not reserve stock. Prices, availability and product status are re-validated on every cart read and at checkout. |
| BR-020 | Clients cannot supply authoritative values. Request schemas are strict: unexpected monetary, status or stock fields → 422. |
| BR-021 | Adding an existing variant sums quantities; the merged quantity is subject to BR-018. |
| BR-022 | Displayed prices are always current. If the expected total submitted at order placement differs from the server calculation → 409 `PRICE_CHANGED` and no order is created. |
| BR-023 | Wishlist is unique per (customer, product), product-level; only active products can be added. Moving to cart requires an explicit variant when the product has several; the wishlist entry is removed only if the cart addition succeeds. Out-of-stock items stay in the wishlist, flagged. |

**Money, totals and shipping**

| ID | Rule |
|---|---|
| BR-024 | Single currency, amounts stored as integer minor units, displayed with 2 decimals. Prices are tax-inclusive; there is no separate tax line (DEC-02). |
| BR-025 | Calculation order: (1) subtotal = Σ unit price × quantity; (2) coupon discount; (3) discounted subtotal = subtotal − discount; (4) shipping fee; (5) total = discounted subtotal + shipping fee. |
| BR-026 | Percentage discount = round-half-up(subtotal × percent ÷ 100) to the minor unit, then capped by the coupon's maximum discount, then capped at the subtotal. |
| BR-027 | Fixed-value discount = min(coupon value, subtotal). |
| BR-028 | Shipping options (seed, DEC-07, DEC-29): Standard R60.00 and Express R120.00. Express is always charged. Standard is free **only** for a qualifying first order (BR-076); every other Standard order pays R60.00, including any order of R1,000.00 or more — the earlier "free at R1,000.00" rule is withdrawn. Coupons never discount shipping. *(amended v0.5)* |
| BR-029 | Invariant on every order: total = subtotal − discount + shipping fee; each stored amount is a non-negative integer; line totals sum to the subtotal. |
| BR-076 | **First-order free Standard shipping.** First-order status is decided from the customer's previous orders: orders with status `cancelled` are not counted, and the order currently being placed is not counted. The order being placed is the customer's first order when no previous order exists with any other status (`pending`, `confirmed`, `processing`, `shipped` or `delivered`); a customer whose earlier orders were all cancelled is therefore still a first-time buyer. Standard shipping is free only when it is the customer's first order and the pre-coupon (pre-discount) subtotal is at least R250.00 and below R1,000.00 (R250.00 inclusive, R1,000.00 exclusive). Every other Standard order pays R60.00: returning customers at any subtotal, and first-time buyers at R1,000.00 or more or below R250.00. Express is always R120.00. Coupons never affect eligibility because the band uses the pre-coupon subtotal; a customer using `WELCOME10` is returning by definition (BR-075) and pays R60.00 Standard. The small-goods exception of BR-077 waives only the minimum-order restriction and grants no shipping benefit. First-order status is evaluated at placement and reflected in the cart totals (DEC-29, CL-16). *(new v0.5)* *(amended v0.6)* |
| BR-077 | **Minimum order and small goods.** The pre-coupon (pre-discount) subtotal of an order must be at least R250.00 unless the cart contains four or more units of products in small-goods categories, counting quantities across all such lines (three units do not qualify). A category is small-goods by designation; Wearables and Audio, with all its subcategories, is designated (DEC-29). The check ignores coupons. The small-goods exception waives only the minimum-order restriction: it does not grant free shipping, and Standard shipping remains R60.00 (BR-076). When neither the minimum nor the exception is satisfied, the cart shows the blocking cart-level flag `below_minimum_order` and placement returns 409 `ORDER_BELOW_MINIMUM` at BR-074 step 7. *(new v0.5)* *(amended v0.6)* |

**Coupons**

| ID | Rule |
|---|---|
| BR-030 | At most one coupon per order (no stacking); it applies to the goods subtotal only. |
| BR-031 | Codes are trimmed, case-insensitive, stored upper-case, 3–20 characters from `A–Z 0–9 _ -`. |
| BR-032 | Valid only if active and `starts_at` ≤ now < `expires_at` (UTC; expiry exclusive). |
| BR-033 | Minimum order amount is evaluated against the pre-discount subtotal. The comparison is inclusive (subtotal ≥ minimum) unless the coupon declares an exclusive minimum (subtotal > minimum); `SAVE100` does (DEC-28). *(amended v0.4)* |
| BR-034 | Optional global usage limit and per-customer usage limit; exceeded → 422 `COUPON_USAGE_LIMIT_REACHED`. |
| BR-035 | Usage is counted when the order is placed; it is released if the order is cancelled before payment approval (including expiry); it is **not** released when a paid order is cancelled (DEC-08). Under concurrency the last remaining use goes to exactly one order. |
| BR-036 | The coupon, including customer eligibility (BR-075), is re-validated at order placement; if no longer valid or eligible, no order is created and the specific reason code is returned. *(amended v0.4)* |
| BR-075 | **Coupon eligibility.** A coupon may carry a customer-eligibility condition, evaluated when the coupon is applied and re-evaluated at placement (BR-036). `WELCOME10` is for returning customers only: the customer must own at least one order that has reached `shipped` or `delivered` (cancelled and not-yet-shipped orders do not count; only the customer's own orders are considered). An ineligible customer receives 422 `COUPON_NOT_ELIGIBLE`. `SAVE100` and `ONCE1` have no eligibility condition; `SAVE100` is order-value-based only (DEC-28). Because this condition needs an earlier non-cancelled order that has shipped, a customer using `WELCOME10` is a returning customer for shipping purposes (BR-076): Standard shipping is R60.00 and the free first-order offer never applies to them. *(new v0.4)* *(amended v0.6)* |

**Inventory**

| ID | Rule |
|---|---|
| BR-037 | Stock is never negative (application check plus database constraint). |
| BR-038 | Stock is deducted at order placement by atomic conditional update for all lines in one transaction; any failure rolls back all lines, the order and coupon usage. |
| BR-039 | Concurrent placements never sell more units than available; losers receive 409 `INSUFFICIENT_STOCK`. |
| BR-040 | Stock is restored exactly once when an order is cancelled from `pending`, `confirmed` or `processing`, in the ordered quantity per variant (even if the variant is now inactive). |
| BR-041 | A pending order holds its stock for the reservation window (30 minutes, configurable). On expiry the order is auto-cancelled per BR-054 (DEC-09). The window is fixed from placement and is not extended by payment attempts. Once the deadline has elapsed the order is expirable and expiry takes precedence over any payment (BR-069, BR-073). *(amended v0.2)* *(amended v0.3)* |
| BR-042 | Every stock change writes an inventory movement (variant, delta, reason, reference, actor, timestamp). Reasons include `order_placed`, `order_cancelled`, `reservation_expired`, `admin_adjustment`, `initial_stock` (CL-03). For every variant, current stock = initial stock + Σ movements. |

**Orders and payments**

| ID | Rule |
|---|---|
| BR-043 | Order statuses: `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`. Allowed transitions are exactly those in the matrix below (DEC-12). |
| BR-044 | Payment attempt statuses: `approved`, `declined`, `timed_out`, `error`. Order payment status: `unpaid` (no attempts), `paid` (an approved attempt exists), `failed` (≥ 1 attempt, none approved). |
| BR-045 | An order may be `confirmed`, `processing`, `shipped` or `delivered` only if it has an approved payment. Unpaid orders are only `pending` or `cancelled`. A non-approved outcome never confirms an order. |
| BR-046 | At most one approved payment per order; its amount equals the order total. |
| BR-047 | Outcome mapping — `approved`: attempt approved, order → `confirmed`. `declined`: attempt declined, order stays `pending`. `timeout`: attempt `timed_out` after the configured delay (recorded only if the order is still payable and unexpired after the delay, BR-069), nothing captured, order stays `pending`. `processing_error`: attempt `error`, order stays `pending`. Each outcome is committed as defined in BR-069. *(amended v0.2)* *(amended v0.3)* |
| BR-048 | Order placement and payment require an `Idempotency-Key`. Same key + identical payload (within 24 h) returns the stored result with no new order, payment or stock change; same key + different payload → 422 `IDEMPOTENCY_KEY_REUSED`; missing key → 422 `IDEMPOTENCY_KEY_REQUIRED` (DEC-11). Scope, replay, conflict and storage rules: BR-070. *(amended v0.2)* |
| BR-049 | Max 3 payment attempts per order (configurable), counting every committed attempt regardless of outcome; further attempts → 409 `PAYMENT_ATTEMPTS_EXHAUSTED`. Paying an already-paid order → 409 `ORDER_ALREADY_PAID`; paying a cancelled (including expired) order → 409 `ORDER_NOT_PAYABLE`. *(amended v0.2)* |
| BR-050 | Order items and delivery address are immutable snapshots (name, variant description, SKU, unit price, quantity, image reference); later catalog or address changes never alter them. |
| BR-051 | Order number format `NC-YYYYMMDD-NNNNNN`, unique; not used for authorization. |
| BR-052 | Order status history is append-only (from, to, actor, reason, timestamp). |

**Order transition matrix (BR-043)**

| From | To | Trigger | Actor |
|---|---|---|---|
| `pending` | `confirmed` | Approved payment | System |
| `pending` | `cancelled` | Cancel / reservation expiry | Customer, Admin, System |
| `confirmed` | `processing` | Fulfilment started | Admin |
| `confirmed` | `cancelled` | Cancel | Customer, Admin |
| `processing` | `shipped` | Dispatched | Admin |
| `processing` | `cancelled` | Cancel | Admin only |
| `shipped` | `delivered` | Delivered | Admin |
| `shipped`, `delivered`, `cancelled` | — | Terminal for cancellation; `cancelled` is fully terminal | — |

**Cancellation and refunds**

| ID | Rule |
|---|---|
| BR-053 | Customers may cancel own orders only in `pending` and `confirmed`; admins also in `processing`. `shipped`, `delivered` and `cancelled` are never cancellable → 409 `ORDER_NOT_CANCELLABLE`. Release note: until the paid-order branch ships in R2 (FR-073), a `confirmed` order is treated as not cancellable by customers (409 `ORDER_NOT_CANCELLABLE`, DEC-26). *(amended v0.2)* |
| BR-054 | Cancelling an unpaid order: stock restored (BR-040), coupon usage released (BR-035), refund status `not_applicable`. |
| BR-055 | Cancelling a paid order: stock restored; a full refund (goods + shipping) is created; coupon usage is not released. |
| BR-056 | Refund statuses: `not_applicable`, `refund_pending`, `refunded`. At most one refund per order; amount equals the amount paid; only orders with an approved payment can be refunded. |
| BR-057 | Admin status updates are forward-only, one step at a time: `confirmed→processing→shipped→delivered`. Admins cannot move an order to `confirmed` (only an approved payment can) and cannot skip or reverse. |

**Reviews**

| ID | Rule |
|---|---|
| BR-058 | A customer may review a product only if they own a `delivered` order containing any variant of it. |
| BR-059 | Rating is an integer 1–5; comment optional, ≤ 1,000 characters, always rendered as escaped text; one review per (customer, product); no edit/delete in the MVP (DEC-14). |
| BR-060 | Rating average = mean of visible reviews rounded half-up to 1 decimal; count of visible reviews; recomputed on create/hide. |

**Administration**

| ID | Rule |
|---|---|
| BR-061 | Products, variants and categories referenced by orders are deactivated, never hard-deleted. A category with active products or active subcategories cannot be deactivated → 409 `CATEGORY_NOT_EMPTY`. |
| BR-062 | Admin inventory changes require a reason (1–200 chars) and must leave stock ≥ 0. |
| BR-063 | Product price or active-state changes affect carts (flagged per FR-037) and future orders only, never existing orders. |

**Access control and audit**

| ID | Rule |
|---|---|
| BR-064 | Customer-owned resources (cart, wishlist, addresses, orders, reviews, notifications) are accessible only to their owner; a non-owner receives 404 (DEC-18). |
| BR-065 | Admin endpoints: unauthenticated → 401; authenticated non-admin → 403. Admin accounts cannot use customer shopping operations (addresses, cart, wishlist, checkout and payment, own-order operations, reviews) → 403 (DEC-19). *(amended v0.2)* |
| BR-066 | Audit events (R2) are recorded for: product create/update/deactivate/reactivate, price change, variant change, category change, inventory adjustment, order status change, admin order cancellation, review hiding, admin login. Each stores actor, role, action, entity type/id, before/after summary, timestamp, request ID; events are append-only. |
| BR-067 | In-app notifications (R3) are created for order confirmed, payment failed, order status change, order cancelled and refund completed; each belongs to exactly one customer. |

### 8.2 Configurable parameters (FR-107)

| Key (illustrative) | Default | Rule |
|---|---|---|
| `TOKEN_TTL_MINUTES` | 30 | BR-005 |
| `LOGIN_MAX_FAILURES` / `LOGIN_LOCK_MINUTES` | 5 / 15 | BR-007 |
| `MAX_ADDRESSES` | 10 | BR-008 |
| `MAX_QTY_PER_LINE` / `MAX_CART_LINES` | 10 / 20 | BR-018 |
| `LOW_STOCK_THRESHOLD` | 5 | BR-012 |
| `PAGE_SIZE_DEFAULT` / `PAGE_SIZE_MAX` | 12 / 48 | BR-016 |
| `SHIPPING_STANDARD_FEE` / `SHIPPING_EXPRESS_FEE` | R60.00 / R120.00 | BR-028 |
| `FIRST_ORDER_FREE_SHIPPING_MIN` | R250.00 (inclusive) | BR-076 |
| `FIRST_ORDER_FREE_SHIPPING_BELOW` | R1,000.00 (exclusive) | BR-076 |
| `MIN_ORDER_AMOUNT` | R250.00 | BR-077 |
| `SMALL_GOODS_MIN_UNITS` | 4 | BR-077 |
| `RESERVATION_TTL_MINUTES` | 30 | BR-041 |
| `MAX_PAYMENT_ATTEMPTS` | 3 | BR-049 |
| `PAYMENT_SIM_TIMEOUT_MS` | 5,000 (test env: 500) | BR-047 |
| `REFUND_DELAY_SECONDS` | 5 (test env: 0) | FR-074 |
| `IDEMPOTENCY_RETENTION_HOURS` | 24 | BR-048 |

### 8.3 Reference seed coupons (DEC-08, DEC-28)

| Code | Type / value | Minimum order | Maximum discount | Limits | Validity |
|---|---|---|---|---|---|
| `WELCOME10` | 10% | R500.00 (inclusive) | R200.00 | 1 per customer; **returning customers only** (BR-075) *(amended v0.4)* | Active, far-future expiry |
| `SAVE100` | Fixed R100.00 | Subtotal **above** R800.00 (exclusive); order value only *(amended v0.4)* | — | 3 per customer, 100 global | Active |
| `ONCE1` | **Percentage 5%** *(amended v0.4, v0.5)* | — | R50.00 | 1 global, 1 per customer; any customer | Active |
| `EXPIRED5` | 5% | — | — | — | Expired (2020) |
| `INACTIVE15` | 15% | — | — | — | Inactive |

### 8.4 Checkout, payment and cart lifecycle (new in v0.2)

These rules make the operation boundaries, transaction commitments, idempotency scope and cart behaviour explicit. They refine BR-035 – BR-049 and implement DEC-10, DEC-11 and DEC-25. Technology-specific mechanisms (locking, job scheduling) belong to the architecture document; the observable outcomes below are binding.

| ID | Rule |
|---|---|
| BR-068 | **Placement operation (TX-1).** Order placement is its own operation. After the request-level checks (BR-074 steps 1–4) and, under the customer's cart lock, the state checks (steps 5–11), one database transaction creates the `pending` order (payment status `unpaid`) with immutable item and address snapshots, totals and a payment deadline (placement time + reservation window); deducts stock for all lines with `order_placed` ledger entries (the atomic conditional deduction is the stock check of step 9); counts coupon usage; locks the cart to the order (BR-071); and stores the idempotency record (BR-070). The transaction (step 12) commits **before** any payment is attempted and only when every earlier check succeeded. Any failure rolls back all of it. Success returns 201 with the pending order; placement never takes payment. *(amended v0.3)* |
| BR-069 | **Payment operation (TX-2).** A payment attempt is its own operation on an existing order. (1) Authenticate, validate the idempotency key, resolve replay and key reuse (scoped to the order, BR-070), validate the payload (`simulated_outcome` in the allowed set) and check ownership (else 404). (2) For outcome `timeout`, the simulated delay elapses **before** the transaction, with no database transaction open and without holding the order lock, so reads, cancellation and expiry on the order are not blocked. (3) Begin TX-2, acquire the order-level lock and re-read the authoritative order and reservation state inside the transaction. (4) Check eligibility in this order: status `cancelled` → 409 `ORDER_NOT_PAYABLE`; an approved payment exists or the order is past `pending` → 409 `ORDER_ALREADY_PAID`; reservation deadline elapsed on a `pending` order → apply the expiry transition (BR-041, BR-054: cancel, restore stock, release coupon usage, `reservation_expired` ledger entries, status history, unlock the cart), commit those expiry effects and return 409 `ORDER_NOT_PAYABLE`; attempt cap reached → 409 `PAYMENT_ATTEMPTS_EXHAUSTED`. A request that fails step 4 records **no** payment attempt and no idempotency record, and the attempt count is unchanged. (5) If the order is payable and unexpired, the attempt and its idempotency record are recorded in the same transaction; `approved` also sets the order `confirmed` and payment status `paid`, empties and unlocks the cart and appends status history. `declined`, `timed_out` and `error` are valid business outcomes: their attempt record commits (2xx) and never alters the effects committed by TX-1 — the order stays `pending`, stock stays deducted, coupon usage stays counted and the cart stays locked. A technical failure of the payment operation rolls back only that operation: the order stays `pending` and payable (until its deadline) with its reservation intact. The reservation deadline is fixed from placement and is not extended by attempts. *(amended v0.3)* |
| BR-070 | **Idempotency scope.** A key is 8–64 characters from `A–Z a–z 0–9 _ -` (DEC-11) and is unique per (customer, scope), where scope is `place_order` for placement and `pay_order` + order id for payment; the same key string in another scope or for another customer is independent. A request fingerprint is its canonical payload (placement: `address_id`, `expected_total`; payment: `simulated_outcome`). Same scope + key + fingerprint within 24 h returns the stored response (same status and body) with no state change, even if the order has since changed state; same key + different fingerprint → 422 `IDEMPOTENCY_KEY_REUSED`; missing or malformed key → 422 `IDEMPOTENCY_KEY_REQUIRED`. A record is written only inside the transaction that commits the protected state change, so requests rejected before any state change (validation errors, 404, 409) store nothing and the same key may be retried once the cause is fixed. A deliberate retry (another payment attempt, or checkout after cancellation) must use a new key. Replay lookup and key-reuse resolution (BR-074 step 3) precede schema validation and every state check; a legitimate replay is never rejected because its order is still pending or has since changed state. *(amended v0.3)* |
| BR-071 | **One pending order per customer; cart lock.** A customer can have at most one `pending` order at a time (database-enforced). While it exists the cart is locked to it: add, update, remove, clear, coupon/shipping change and move-to-cart return 409 `CART_LOCKED` (details: order id); cart reads succeed with a locked indicator. A further placement that is not a replay and passes BR-074 steps 1–4 (authentication, key format, replay/key-reuse resolution, schema) returns 409 `CHECKOUT_ALREADY_PENDING` (details: existing order id) at step 5 — before address, cart, stock, coupon and total checks — whatever its new key or payload content, and creates nothing. A replay of the same key and payload (BR-070) returns the original response even while the order is still pending. Under concurrent placements by one customer exactly one succeeds; each loser receives the same 409. The customer resolves a pending order by paying it, cancelling it, or letting the reservation expire (DEC-25). *(amended v0.3)* |
| BR-072 | **Cart lifecycle after outcomes** follows the Cart lifecycle table below. The cart persists the selected coupon code and shipping option (default Standard); placement snapshots them into the order. |
| BR-073 | **Serialisation and race outcomes.** Payment (TX-2), customer cancellation, admin cancellation and reservation expiry on one order are serialised by an order-level lock; each operation re-reads the order inside its transaction and the first to commit wins. The Race outcomes table below defines every pairing. Stock restoration, coupon release, status transitions and refund creation happen at most once per order. The losing operation records no payment attempt and has no side effects of its own (an expiry applied by a payment operation under BR-069 step 4 is the expiry transition itself, not a side effect of the payment). *(amended v0.3)* |
| BR-074 | **Placement validation order and error contract.** Checks run in the order of the Placement table below and the first failure is returned. Steps 1–4 are request-level. Steps 5–11 are evaluated against authoritative state under the customer's cart lock, so the state observed is the state committed; the stock check of step 9 is the atomic conditional deduction inside TX-1, and a lost race returns the same `INSUFFICIENT_STOCK`. Step 12 (commit of TX-1) is reached only when steps 1–11 all pass. Precedence: a schema-valid, non-replay request is rejected for an existing pending order (step 5) before any address, cart, stock, coupon or total check; payload-schema errors (step 4) and idempotency conflicts (steps 2–3) are reported at their earlier stages. A rejected request creates no order, stock movement, coupon usage or idempotency record (BR-070). Because the cart always carries a shipping option, a missing shipping option is not a separate failure. *(amended v0.3)* |

**Cart lifecycle (BR-072)**

| Event | Cart lines | Cart lock | Coupon / shipping selection | Stock and coupon usage |
|---|---|---|---|---|
| Order placed (`pending`) | Retained, read-only | Locked to the order | Retained | Stock deducted; coupon usage counted |
| Payment `declined` / `timed_out` / `error` | Unchanged | Remains locked | Unchanged | Unchanged (still held) |
| Payment `approved` (`confirmed`) | **Emptied** | Unlocked | **Cleared** | Deduction stands; usage stays counted |
| Customer (or admin, R2) cancels the unpaid order | Retained unchanged; re-validated on next read | Unlocked | Retained | Stock restored; coupon usage released |
| Reservation expires | As for cancellation | Unlocked | Retained | As for cancellation |
| Paid order cancelled (R2) | Not affected (any new cart contents are untouched) | Not affected | Not affected | Stock restored; usage stays counted; refund created |

**Placement preconditions (BR-074)**

| # | Check | Failure response / result |
|---|---|---|
| 1 | Authentication and role | 401 `UNAUTHENTICATED` / `TOKEN_EXPIRED`; admin account → 403 `FORBIDDEN` |
| 2 | `Idempotency-Key` present and well-formed | 422 `IDEMPOTENCY_KEY_REQUIRED` |
| 3 | Replay and key-reuse resolution (BR-070) | Stored response replayed (original status and body); 422 `IDEMPOTENCY_KEY_REUSED` if the payload differs |
| 4 | Payload schema: `address_id` present, `expected_total` a non-negative integer, no unknown fields | 422 `VALIDATION_ERROR` (details name the field, e.g. `address_id`) |
| 5 | Customer has no existing pending order | 409 `CHECKOUT_ALREADY_PENDING` (details: existing order id) |
| 6 | Address exists and belongs to the caller | 404 `NOT_FOUND` |
| 7 | Cart not empty, then minimum order met (BR-077) | 409 `CART_EMPTY`; 409 `ORDER_BELOW_MINIMUM` *(amended v0.5)* |
| 8 | No line whose product or variant is unavailable | 409 `PRODUCT_UNAVAILABLE` (details: line ids) |
| 9 | Stock sufficient for every line (atomic deduction inside TX-1) | 409 `INSUFFICIENT_STOCK` (details: line id, requested, available) |
| 10 | Coupon, if any, valid, eligible and within usage limits (BR-031 – BR-035, BR-075) *(amended v0.4)* | 422 `COUPON_*` reason code |
| 11 | `expected_total` equals the server total | 409 `PRICE_CHANGED` (details: fresh totals) |
| 12 | Commit TX-1 (order, stock deduction, ledger, coupon usage, cart lock, idempotency record) | 201 with the pending order |

**Race outcomes (BR-073, new in v0.3)**

| Operation that commits first | Competing operation | Required outcome |
|---|---|---|
| Customer or admin cancellation | Payment, including one in its simulated delay | Payment returns 409 `ORDER_NOT_PAYABLE`; no attempt row; no second restoration or release |
| Expiry (job, or applied by a payment under BR-069 step 4) | Payment | 409 `ORDER_NOT_PAYABLE`; no attempt row; stock restored and coupon released once |
| Deadline elapsed but expiry not yet applied | Payment | Expiry takes precedence: applied first, then 409 `ORDER_NOT_PAYABLE` |
| Payment approval | Expiry job | Job no-ops (the order is no longer `pending`) |
| Payment approval | Customer or admin cancellation | R1: cancellation returns 409 `ORDER_NOT_CANCELLABLE`, no effects (DEC-26). R2: evaluated as a paid-order cancellation under BR-055 — per CL-10 |
| Cancellation | Expiry | First to commit wins; the other no-ops or returns 409; one restoration only |
| Non-approved payment attempt | Another payment attempt | Both may commit up to the attempt cap with sequential attempt numbers; at most one approved |
| Approved payment | Another payment | 409 `ORDER_ALREADY_PAID`; exactly one approved payment |

## 9. Main workflows

Diagrams belong to the next document; these define behaviour. "Alt" = alternative or exception path.

**WF-01 Registration, login and return to intent.** 1) Visitor opens Register, submits name/email/password. 2) System validates (BR-001–003) and creates a customer; the API returns 201 with the user and no token (FR-001, DEC-27). 3) The UI immediately signs the user in through the standard login operation. 4) User lands on the page they came from or the home page. *Alt:* duplicate email → inline error; weak password → field errors; automatic sign-in fails → login page with a "registration successful" notice; unauthenticated access to a protected page → login → return to that page (FR-005, FR-038).

**WF-02 Browse, search, filter, view.** 1) User opens a category or search box. 2) Applies filters/sort; URL updates (FR-027). 3) Opens a product, selects variant options. 4) Sees price, availability, notices. *Alt:* no results → empty state; inactive product link → not-found page; page beyond last → empty state.

**WF-03 Cart.** 1) Customer adds a variant with a quantity. 2) Cart shows server-calculated lines and totals. 3) Customer changes quantity or removes a line. 4) Optionally applies a coupon and selects shipping. *Alt:* quantity above stock → error with available units; blocking lines (unavailable, out of stock, insufficient stock) must be resolved before checkout, while a changed price is flagged and acknowledged by submitting the new total; a pending order locks the cart (409 `CART_LOCKED`) and the UI offers Pay now / Cancel order; guest → login first, then action completes. A cart below the R250.00 minimum order, without four or more Wearables and Audio units, cannot be checked out (BR-077).

**WF-04 Wishlist.** 1) Customer adds a product. 2) Opens wishlist. 3) "Move to cart" (selects variant if required). *Alt:* duplicate add → 409 handled gracefully; out-of-stock → move disabled, item stays.

**WF-05 Addresses.** 1) Customer adds an address (first becomes default). 2) Edits, sets default, deletes. *Alt:* 11th address blocked; validation errors per field.

**WF-06 Checkout — approved payment.** 1) Customer opens checkout from the cart (lines valid, cart unlocked). 2) Selects or creates an address; the cart's shipping option and coupon apply; reviews the server-calculated total. 3) Selects the simulated outcome "Approved" and clicks Place order. 4) **PlaceOrder** (own idempotency key): one transaction creates the `pending` order, deducts stock, counts coupon usage and locks the cart, and commits (201). 5) **PayOrder** (own key): the approved attempt is recorded, the order becomes `confirmed`, the cart is emptied and unlocked. 6) Confirmation page shows the order details.

**WF-07 Checkout — payment failure, retry, expiry.** 1) Steps 1–4 of WF-06 with outcome Declined, Timeout or Processing error. 2) The attempt is recorded; the order remains `pending` with stock and coupon usage still held and the cart locked; the payment-failed page shows the outcome and a pending-order banner. 3) Customer retries (a new PayOrder with a new key; up to 3 attempts in total) with a new outcome, or cancels (FR-072). *Alt:* attempts exhausted → only cancel offered; no action within 30 minutes → system cancels, releases stock and coupon usage and unlocks the cart with its lines retained; trying to place another order while one is pending → 409 `CHECKOUT_ALREADY_PENDING` and the UI returns the customer to the pending order. If the order is cancelled or its reservation expires while a payment is in flight (for example during the simulated timeout delay), the payment returns 409 `ORDER_NOT_PAYABLE`, no attempt is recorded and the UI shows the order as cancelled or expired (BR-069, BR-073).

**WF-08 Order history and cancellation.** 1) Customer opens Orders, then an order. 2) "Cancel order" is offered for `pending` orders (R1) and for `confirmed` orders (R2, DEC-26); otherwise hidden/disabled. 3) After confirmation of the dialog, system cancels, restores stock; for a paid order creates a full refund (`refund_pending` → `refunded`). *Alt:* order progressed meanwhile → 409 `ORDER_NOT_CANCELLABLE` with refreshed state.

**WF-09 Review.** 1) Customer opens a product from a delivered order. 2) Submits rating and optional comment. 3) Product aggregate updates. *Alt:* not eligible, duplicate, invalid rating.

**WF-10 Admin catalog and inventory.** 1) Admin logs in, opens product management. 2) Creates or edits product/variants/categories. 3) Adjusts stock with a reason. 4) Deactivates a product. *Alt:* negative stock rejected; category with active products cannot be deactivated; ordered products cannot be deleted.

**WF-11 Admin fulfilment.** 1) Admin filters orders by status. 2) Opens an order, inspects payment attempts and refund. 3) Advances `confirmed → processing → shipped → delivered`. 4) Or cancels with a reason. *Alt:* skipping/reversing states rejected.

**WF-12 Audit inspection.** 1) Admin opens audit log. 2) Filters by actor/action/entity/date. 3) Verifies that sensitive actions appear exactly once.

## 10. Security and access-control requirements

### 10.1 Requirements

| ID | Requirement |
|---|---|
| SEC-001 | Authentication and authorization are enforced server-side on every non-public endpoint. Public: catalog read, registration, login, health, OpenAPI. |
| SEC-002 | Passwords are hashed with an adaptive, salted algorithm (Argon2id or bcrypt — chosen in architecture) and never logged or returned. |
| SEC-003 | Access tokens are signed JWTs with `sub`, `iat`, `exp`, `jti`; signing secret ≥ 256 bits from the environment. |
| SEC-004 | The signing algorithm is pinned; `alg=none`, tampered, wrong-secret and unsigned tokens are rejected (401). The user's role is read from the database on each request, not trusted from the token. |
| SEC-005 | Logout and password change revoke tokens (BR-005). |
| SEC-006 | Object-level authorization on every customer-owned resource (BR-064); no existence leaks between customers. |
| SEC-007 | Function-level authorization on all admin operations (BR-065), covering UI routes and API. |
| SEC-008 | Mass-assignment protection via strict schemas: clients cannot set role, price, totals, discount, shipping fee, stock, order/payment/refund status or ownership. |
| SEC-009 | Input validation on all endpoints; user-generated text (names, addresses, reviews) is output-encoded, never rendered as raw HTML. |
| SEC-010 | Database access uses parameterised queries/ORM only; no string-built SQL. |
| SEC-011 | CORS uses an explicit origin allowlist; wildcard origins are never combined with credentials. |
| SEC-012 | Standard security headers (`X-Content-Type-Options`, `Referrer-Policy`, frame protection, a baseline CSP). |
| SEC-013 | Token storage and CSRF handling are defined in the architecture document; if cookies are used, CSRF protection is mandatory. |
| SEC-014 | Rate limiting on login (BR-007) and registration (configurable, relaxed in `test`). |
| SEC-015 | No stack traces, SQL or secrets in error responses; sensitive data never in URLs or logs. |
| SEC-016 | Secrets only via environment/CI secrets; secret scanning in CI (should). |
| SEC-017 | No payment-card data in UI, API schemas, database columns, logs or fixtures. |
| SEC-018 | Test-support interfaces (reset, seed, clock, state setup) are disabled by default, enabled only when `APP_ENV` is `local` or `test`, return 404 otherwise, and the application refuses to start with them enabled in a production-like environment. |
| SEC-019 | Dependency vulnerability scanning in CI (should). |
| SEC-020 | Registration reveals email existence (409). This is an accepted trade-off while email verification is out of scope (ASM-10); login responses remain non-enumerating. |

### 10.2 Capability / authorization matrix

Cell values are the expected outcome. `own` = only the caller's records. Unauthenticated access to protected operations → 401.

| Capability | Guest | Customer | Administrator |
|---|---|---|---|
| Browse, search, view product, view public reviews | Allowed | Allowed | Allowed |
| Register / login | Allowed | — | — |
| Own profile, password, logout | 401 | own | own |
| Addresses, cart, wishlist, checkout, own orders, cancel own order | 401 | own | 403 |
| Submit review | 401 | Eligible only | 403 |
| Another customer's private record (by id) | 401 | 404 | Order/payment/refund read only, via admin endpoints |
| Admin product/variant/category/inventory management | 401 | 403 | Allowed |
| Admin order list/detail/status/cancel, payment and refund inspection | 401 | 403 | Allowed |
| Audit log | 401 | 403 | Allowed (read-only) |
| Own notifications (R3) | 401 | own | 403 |
| Test-support interfaces | 404 outside `local`/`test` | 404 outside `local`/`test` | 404 outside `local`/`test` |

## 11. SDET and testability requirements

| ID | Requirement |
|---|---|
| TR-001 | Interactive and key data elements carry stable `data-testid` attributes in a documented `area-element` kebab-case convention (e.g., `cart-line-quantity`, `checkout-place-order`); IDs never depend on layout or generated values. |
| TR-002 | Controls also expose correct roles, accessible names and labels so Playwright role/label locators work; `data-testid` is a supplement, not a replacement. |
| TR-003 | A deterministic baseline seed with fixed identifiers and the §5.4 fixtures. Seeded accounts (illustrative; finalised later): `admin@nexacart.test`; `customer@nexacart.test` (address, empty cart; a first-time buyer, so eligible for free first-order Standard shipping; not eligible for `WELCOME10`); `history@nexacart.test` (a returning customer with orders in every status, including `shipped` and `delivered`; eligible for `WELCOME10`; pays Standard shipping); `reviewer@nexacart.test` (delivered orders). Passwords exist only in local/test seed configuration. *(amended v0.4)* *(amended v0.5)* |
| TR-004 | Guarded test-support capabilities (CLI and/or endpoints; architecture decides): reset to baseline, create users/products/orders in a requested state, set stock, inject a controlled technical failure into a named step (e.g., payment recording) to verify transaction boundaries, trigger reservation expiry deterministically (CL-05), and read internal state (DEC-21). *(amended v0.2)* |
| TR-005 | Controllable time in `test`/`local` (set/advance the application clock) to exercise token expiry, coupon expiry, reservation expiry and throttling lock windows without real waiting. |
| TR-006 | Configurable payment-simulator delay/timeout and refund delay; defaults in §8.2; test values lower. The simulated delay is measured independently of the application clock (it is not skipped when the clock is advanced), so the clock can be advanced while a payment request is in flight (AC-105). *(amended v0.3)* |
| TR-007 | PostgreSQL is reachable by the test suite with a documented connection (read-only role recommended for assertions); table/column names are stable and documented in the ERD document. |
| TR-008 | Accurate OpenAPI with request/response examples enabling schema/contract tests. |
| TR-009 | The application must not force serial test execution: tests create their own users and data; no business-critical global mutable state except explicitly designated fixtures. |
| TR-010 | Business state is observable through the API (order status, payment status, refund status, status history, per-variant stock for admins) so UI/API tests can assert outcomes; database tests independently verify consistency. |
| TR-011 | One error envelope and a stable error-code catalogue (Appendix A). |
| TR-012 | Diagnostics: request IDs correlate UI, API and logs; animations/transitions are reducible (honour `prefers-reduced-motion`; a test flag disables them); loading and error states are explicit and detectable. |
| TR-013 | No runtime dependency on third-party networks (fonts, images, analytics, CDNs) so UI tests are deterministic and offline-capable. |
| TR-014 | Compose profiles for `dev` and `test`; CI uses the same images/definitions as local runs. |
| TR-015 | Health/readiness endpoints allow tests and CI to wait for readiness. |
| TR-016 | Test-created records carry an identifiable prefix (e.g., `qa_`) so cleanup is safe and never touches the seed baseline. |
| TR-017 | PRD IDs are stable so tests can be tagged with FR/BR/AC IDs (e.g., pytest markers); the backlog document carries the requirement → test traceability matrix. |
| TR-018 | Time-based limits (token TTL, reservation TTL, throttling, payment delay) are configurable per environment (§8.2). |
| TR-019 | Concurrency-critical invariants rely on the database (conditional updates, constraints, row locks), so multi-process/parallel test harnesses observe correct behaviour. |
| TR-020 | Deterministic ordering and pagination (explicit tie-breakers), fixed local images, no random content ordering. |
| TR-021 | Evidence for defect triage: structured logs, request/response correlation and database state allow separating application defects, automation defects, test-data issues and environment failures. |
| TR-022 | Selected workflows suited to BDD (checkout, coupons, cancellation/refund, inventory) have unambiguous rules and observable outcomes; Gherkin authoring belongs to the SDET track. |
| TR-023 | Valid assertions are never removed or weakened to obtain a green build; requirement changes occur through PRD change control with the change log. |

**Planned test-layer split** (strategy owned by the SDET track): UI covers user journeys and presentation; API covers rules, boundaries, authorization, idempotency and contracts; database checks cover consistency, constraints, ledger reconciliation and concurrency outcomes. Rules that can be proven at API/DB level shall not rely on UI-only tests.

## 12. Acceptance criteria and success metrics

Layers: **U** = UI (Playwright), **A** = API (HTTPX), **D** = database (SQL). **Rel** = the release in which the criterion first applies (the highest release among the functional requirements it verifies; criteria with no functional requirement default to R1). R2/R3 criteria are not part of the R1 gate. v0.2 added AC-074 – AC-104, v0.3 added AC-105 – AC-114 v0.4 added AC-115 – AC-116, v0.5 added AC-117 – AC-118 and v0.7 adds AC-119 – AC-121; no existing AC was renumbered. All criteria are Planned.

### 12.1 Acceptance criteria

**Accounts and security**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-001 | R1 | FR-001, BR-001–003 | Given a new valid email/password, when registering via the API, then 201 Created with the user representation (id, name, email, role `customer`, created_at), **no token and no session cookie**, and no password or hash in the body; one `users` row with role `customer` exists and the stored password is a hash, not plaintext; calling a protected endpoint afterwards without logging in → 401; no verification or OTP step exists. UI sign-in after registration: AC-088. *(amended v0.2)* | U A D |
| AC-002 | R1 | FR-002, BR-002 | Given `a@x.test` exists, when registering `A@X.TEST`, then 409 `EMAIL_ALREADY_REGISTERED`; exactly one row for that normalised email. | A D |
| AC-003 | R1 | BR-001 | Passwords of 7 chars, 129 chars, letters-only, digits-only, equal-to-email → 422 with field errors; 8 chars and 128 chars with letter+digit → accepted. | A U |
| AC-004 | R1 | FR-003, BR-005 | Valid login returns a token whose `exp − iat` = 30 min (±5 s); a protected endpoint then returns 200. | A |
| AC-005 | R1 | FR-003, BR-004 | Login with unknown email and with wrong password return identical status, code and message. | A |
| AC-006 | R1 | FR-004 | After logout, the same token on a protected endpoint → 401; UI redirects to login. | A U |
| AC-007 | R1 | FR-005 | With `TOKEN_TTL` shortened and the clock advanced, an expired token → 401 `TOKEN_EXPIRED`; the UI redirects to `/login` and returns to the original page after login. | A U |
| AC-008 | R1 | FR-009, BR-007 | After 5 consecutive failures the 6th attempt (correct password) → 429 `RATE_LIMITED`; after the lock window succeeds; a success resets the counter. | A |
| AC-009 | R1 | FR-008, CL-17 | Wrong current password → 422 `INVALID_CURRENT_PASSWORD`; success invalidates old tokens (→ 401), the UI confirms the change and redirects to login, and the new password logs in. A new password equal to the current one, or one violating BR-001, → 422. *(amended v0.7)* | A U |
| AC-010 | R1 | FR-010, BR-006, SEC-008 | Registration/profile payloads containing `role: admin` → 422; no admin created or elevated. | A D |
| AC-011 | R1 | SEC-004 | Token with `alg=none`, wrong signature or modified claims → 401. | A |

**Addresses**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-012 | R1 | BR-008 | The 11th address → 409 `ADDRESS_LIMIT_REACHED`; row count stays 10; postal code `123` and `12345` rejected, `1234` accepted. | A D |
| AC-013 | R1 | FR-012, BR-009 | After adding a second address as default, exactly one `is_default = true`; deleting the default promotes the most recent remaining address. The first address created becomes the default automatically. *(amended v0.3)* | A D |
| AC-014 | R1 | FR-015, BR-050 | After editing or deleting an address used by an order, order detail still shows the original address. | A U D |

**Catalog**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-015 | R1 | FR-017, FR-021, BR-016 | On the standard seed, `page_size=12` returns 12 items with correct `total_items`; `page_size=49` or `page=0` → 422; a page beyond the last → 200 with empty items. Item representation (FR-017) is verified in AC-109. *(amended v0.3)* | A U |
| AC-016 | R1 | FR-018, FR-026, BR-014 | `q=adidas` (any case) returns only products whose name or brand contains it, matching an SQL query; `q=a` → 422; no match → UI empty state with reset control. | A U D |
| AC-017 | R1 | FR-019 | Category + brand (two brands) + price range + in-stock combined returns only items satisfying all conditions; result count equals the SQL count. | A U D |
| AC-018 | R1 | FR-020, BR-015 | `price_asc` is non-decreasing with id tie-break; `rating_desc` places unrated products last; `newest` is `created_at` descending. `price_desc` is non-increasing with the same id tie-break. *(amended v0.3)* | A U |
| AC-019 | R1 | FR-024, BR-012 | Out-of-stock product: UI shows "Out of stock" and disables add-to-cart; API add → 409 `INSUFFICIENT_STOCK`. Stock = 5 shows low-stock, stock = 6 does not. | A U |
| AC-020 | R1 | FR-025, BR-011 | An inactive product is absent from listings and search; detail by id/slug → 404; UI shows not-found page. | A U |
| AC-021 | R1 | FR-023 | Choosing variant options updates displayed price, SKU and availability to match the variant row. Option combinations with no active variant, or whose matching variants are all out of stock, are rendered disabled/unavailable. *(amended v0.3)* | U D |
| AC-022 | R1 | FR-027, FR-028, BR-017 | Reloading a filtered URL reproduces the same results; each football-shirt page and the site footer show the fictional/unofficial notice; no third-party image/font requests occur (network log). | U |

**Cart and wishlist**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-023 | R1 | FR-032, BR-021 | Adding the same variant with quantity 2, then 3 → one line of quantity 5; adding 6 more → 422 (line limit 10). | A U D |
| AC-024 | R1 | FR-035, BR-018 | Quantity 0, −1, 11, 1.5, `"abc"` → 422; quantity above stock → 409 `INSUFFICIENT_STOCK` with available units; cart unchanged. | A |
| AC-025 | R1 | FR-036, FR-039, BR-020 | Cart totals equal values computed from DB prices; a request containing `unit_price`, `total` or `discount` → 422. | A |
| AC-026 | R1 | FR-031 | Cart contents survive logout/login and a new browser context. | U A |
| AC-027 | R1 | FR-037, FR-054, BR-022 | After a price change, the cart shows the new price with a "price changed" flag; placing an order with the stale expected total → 409 `PRICE_CHANGED`; no order row or stock change. | A U D |
| AC-028 | R1 | FR-038 | As a guest, add-to-cart → login → the item is in the cart after authentication. | U |
| AC-029 | R1 | FR-045, BR-064 | Customer B requesting or modifying customer A's cart line or wishlist entry → 404; data unchanged. | A |
| AC-030 | R1 | FR-041, BR-023 | First wishlist add → 201; the same product again → 409 `WISHLIST_DUPLICATE`; one row. | A U D |
| AC-031 | R1 | FR-044 | Move-to-cart on a multi-variant product without variant → 422; with variant → cart line created and wishlist row removed; for an out-of-stock item the move fails and the wishlist row remains. | A U D |

**Totals, shipping and coupons**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-032 | R1 | FR-036, FR-050, FR-053, BR-024–029 | Totals equal the worked examples T-01–T-17 below, computed from integer minor units. *(amended v0.4)* *(amended v0.5)* | A U |
| AC-033 | R1 | FR-046, FR-048, BR-030–034, BR-075 | Expired → `COUPON_EXPIRED`; unknown → `COUPON_NOT_FOUND`; inactive → `COUPON_NOT_ACTIVE`; below minimum → `COUPON_MIN_ORDER_NOT_MET`; over usage limit → `COUPON_USAGE_LIMIT_REACHED`; `" welcome10 "` accepted; a second coupon replaces rather than stacks. A customer who is not eligible for `WELCOME10` → `COUPON_NOT_ELIGIBLE` (BR-075; AC-115). *(amended v0.4)* | A |
| AC-034 | R1 | FR-048, BR-034, BR-035, BR-036, BR-039 | Coupon concurrency, independent of the one-pending-order rule. Given two **distinct** customers C1 and C2, each with their own valid cart (separate lines, sufficient stock, and every other `ONCE1` condition satisfied), no pending order for either, and `ONCE1` (global limit 1, per-customer limit 1) with zero committed uses: when both place an order concurrently with different `Idempotency-Key`s, exactly one placement returns 201 and the other returns 422 `COUPON_USAGE_LIMIT_REACHED` (not `CHECKOUT_ALREADY_PENDING`). The database shows exactly one committed use of `ONCE1` (usage count 1, one usage row for the winner); exactly one order across the two customers, with its items, address snapshot and `order_placed` ledger entries; stock changed only for the winner's variants; the loser has no order, no stock movement, no ledger rows, no coupon usage and no idempotency record, and the loser's cart is unlocked and unchanged. Repeated 20 times with the winner varying. *(amended v0.3)* | A D |
| AC-035 | R1 | BR-035 | Cancelling a pending unpaid order that carries a coupon releases its usage exactly once (global and per-customer counters each decrease by 1) and the coupon can be used again. The paid-order case (usage stays counted) is verified in AC-052 (R2). *(amended v0.2)* | A D |
| AC-036 | R1 | FR-049, FR-050, BR-028, BR-076 | Standard shipping fee by customer and subtotal: a first-time buyer with a pre-coupon subtotal of R249.99 (a cart of four small-goods units) → R60.00; R250.00 → R0.00; R999.99 → R0.00; R1,000.00 → R60.00; a returning customer pays R60.00 at every subtotal; Express is always R120.00. Each option returned by the shipping-options endpoint carries the fee that applies to the caller's cart and a static delivery estimate (wording per CL-06). *(amended v0.3)* *(amended v0.5)* *(amended v0.6)* | A U |

**Worked totals (AC-032)** — amounts in rand; Standard shipping unless stated. "Returning" = the customer has an earlier non-cancelled order; "First" = a first-time buyer (BR-076). Cases using `WELCOME10` are run as an eligible customer, who is by definition returning (BR-075).

| Case | Customer | Subtotal | Coupon | Discount | After discount | Shipping | Total |
|---|---|---|---|---|---|---|---|
| T-01 | Returning | 2,000.00 | WELCOME10 | 200.00 | 1,800.00 | 60.00 | 1,860.00 |
| T-02 | Returning | 3,000.00 | WELCOME10 | 200.00 (10% = 300, capped) | 2,800.00 | 60.00 | 2,860.00 |
| T-03 | Returning | 900.00 | WELCOME10 | 90.00 | 810.00 | 60.00 | 870.00 |
| T-04 | Returning | 450.00 | WELCOME10 | Rejected `COUPON_MIN_ORDER_NOT_MET` (min 500.00) | 450.00 | 60.00 | 510.00 (no coupon) |
| T-05 | Returning | 500.00 | WELCOME10 | 50.00 (minimum boundary, inclusive) | 450.00 | 60.00 | 510.00 |
| T-06 | First | 1,050.00 | SAVE100 | 100.00 | 950.00 | 60.00 (1,050.00 is not under 1,000.00, so no free shipping) | 1,010.00 |
| T-07 | Returning | 1,234.55 | WELCOME10 | 123.46 (123.455 rounded half-up) | 1,111.09 | 60.00 | 1,171.09 |
| T-08 | First | 1,000.00 | — | 0.00 | 1,000.00 | 60.00 (upper bound exclusive) | 1,060.00 |
| T-09 | First | 999.99 | — | 0.00 | 999.99 | 0.00 (first-order band) | 999.99 |
| T-10 | First (Express) | 1,500.00 | — | 0.00 | 1,500.00 | 120.00 | 1,620.00 |
| T-11 | Returning | 800.00 | SAVE100 | Rejected `COUPON_MIN_ORDER_NOT_MET` (the minimum is exclusive: the subtotal must be above 800.00) | 800.00 | 60.00 | 860.00 (no coupon) |
| T-12 | Returning | 800.01 | SAVE100 | 100.00 | 700.01 | 60.00 | 760.01 |
| T-13 | First | 250.00 | — | 0.00 | 250.00 | 0.00 (first-order band, lower bound inclusive) | 250.00 |
| T-14 | First | 249.99 (four Wearables and Audio units) | — | 0.00 | 249.99 | 60.00 (below the free band; the small-goods exception waives only the minimum) | 309.99 |
| T-15 | First | 249.99 (three Wearables and Audio units) | — | Rejected `ORDER_BELOW_MINIMUM` | — | — | — |
| T-16 | First | 900.00 | SAVE100 | 100.00 | 800.00 | 0.00 (the band uses the pre-discount subtotal) | 800.00 |
| T-17 | Returning | 250.00 | — | 0.00 | 250.00 | 60.00 | 310.00 |

**Checkout, payment and inventory**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-037 | R1 | FR-052, FR-115, BR-074 | Given an empty cart (never filled, or emptied) and no pending order, when placing an order, then 409 `CART_EMPTY`; no order, stock change, ledger row, coupon usage or idempotency record is created; the UI shows the empty-cart state and offers no checkout. (Flagged lines: AC-076; missing address: AC-077.) *(amended v0.2)* *(amended v0.3)* | A U D |
| AC-038 | R1 | FR-057, FR-058, FR-065, FR-067, BR-045, BR-068 | Approved outcome: order `confirmed`; one `approved` payment equal to order total; each variant's stock reduced by the ordered quantity; coupon usage counted; cart emptied and unlocked (AC-080); order items = cart lines; total = Σ items − discount + shipping. The confirmation page shows the order number, items, delivery-address snapshot, totals and statuses. *(amended v0.3)* | U A D |
| AC-039 | R1 | FR-057, FR-059, FR-065, FR-067, BR-044, BR-047, BR-069 | Declined: no `confirmed` order exists; order `pending`, payment status `failed`, attempt `declined`; stock still held; retry offered. The cart stays locked; the transaction boundary is verified in AC-082 and the response contract in AC-086. The payment-failed page shows the outcome with retry and cancel actions. *(amended v0.2)* *(amended v0.3)* | U A D |
| AC-040 | R1 | FR-057, FR-060, FR-067 | Timeout: after the configured delay the attempt is `timed_out`; no approved payment; order `pending`; UI shows a timeout message with retry/cancel. This is the control case in which the order is still payable and unexpired after the delay; cancellation or expiry during the delay is AC-105 / AC-106. *(amended v0.3)* | U A D |
| AC-041 | R1 | FR-057, FR-061, FR-067 | Processing error: attempt `error`; order not confirmed; after cancel, stock fully restored. | U A D |
| AC-042 | R1 | FR-056, BR-048, BR-070 | The same `Idempotency-Key` and payload sent twice, and five times concurrently → exactly one order, one stock deduction, identical responses; same key with a different payload → 422 `IDEMPOTENCY_KEY_REUSED`; missing key → 422. A different key while the first order is pending is covered by AC-078; key scope by AC-083. A replay of the same key and payload is returned unchanged (original status and body) while the order is still pending, after it was paid, and after it was cancelled — a legitimate replay is never rejected as `CHECKOUT_ALREADY_PENDING` or `CART_EMPTY`. *(amended v0.2)* *(amended v0.3)* | A D |
| AC-043 | R1 | FR-063, BR-046 | Repeating an approved payment with the same key creates one approved payment; a new key on a paid order → 409 `ORDER_ALREADY_PAID`; DB shows one approved payment. | A D |
| AC-044 | R1 | FR-062, BR-049 | After 3 non-approved attempts, the 4th → 409 `PAYMENT_ATTEMPTS_EXHAUSTED`; cancel still allowed. | A U |
| AC-045 | R1 | FR-055, BR-038, BR-068 | A two-line cart where line 2 lacks stock → 409; line 1's stock unchanged; no order, items, ledger rows, coupon usage or idempotency record persisted, and the cart stays unlocked. *(amended v0.2)* | A D |
| AC-046 | R1 | FR-064, BR-041 | With the reservation TTL shortened and clock advanced, an unpaid order auto-cancels; stock is restored exactly once; coupon usage released; ledger contains a `reservation_expired` entry. The cart is unlocked with its lines retained (AC-081). Expiry is applied within 60 s of the TTL, or immediately through the test-support trigger (CL-05). *(amended v0.2)* | A D |
| AC-047 | R1 | BR-037, BR-039, NFR-009 | Stock = 5; 20 concurrent single-unit placements by distinct customers → exactly 5 succeed, 15 get 409; final stock 0; no negative values at any time. | A D |
| AC-048 | R1 | FR-066, SEC-017 | Checkout UI has no card number/CVV/expiry inputs; API rejects unknown card fields; no card-like columns exist in the schema. | U A D |
| AC-049 | R1 | BR-042 | For every variant, current stock = initial stock + Σ inventory movements after any sequence of placements and cancellations. | D |

**Orders, cancellation and refunds**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-050 | R1 | FR-068, FR-069, BR-064 | Order history lists only own orders, newest first, paginated; another customer's order id → 404. | A U |
| AC-051 | R1 | FR-069, BR-050 | After changing a product's price/name or deactivating it, past order detail remains unchanged. | A D |
| AC-052 | R2 | FR-073, FR-074, BR-055, BR-056 | Cancelling a `confirmed` order: status `cancelled`; stock restored by ordered quantity; one refund equal to the paid amount; refund status `refund_pending` then `refunded` (delay 0 in test); status-history and ledger entries written. Coupon usage remains counted (BR-055). From R2 this supersedes AC-075. *(amended v0.2)* | U A D |
| AC-053 | R1 | BR-053 | Cancelling `shipped`, `delivered` or `cancelled` orders → 409 `ORDER_NOT_CANCELLABLE`; no stock, refund or status change. In R1, `shipped` and `delivered` orders are created through test-support state setup because admin transitions arrive in R2. *(amended v0.2)* | A D |
| AC-054 | R1 | FR-072, FR-075, BR-040, BR-054 | Given a `pending` unpaid order, when two cancellation requests run concurrently (customer/customer, or customer/reservation-expiry job), then exactly one succeeds and the other returns 409 `ORDER_NOT_CANCELLABLE` (or the expiry job no-ops); stock is restored exactly once (+ordered quantity per variant); coupon usage is released once; exactly one restoring ledger entry exists per variant; no refund row exists (refund status `not_applicable`). The paid-order counterpart is AC-074 (R2). *(amended v0.2)* | A D |
| AC-055 | R1 | FR-072, BR-054 | Cancelling a pending unpaid order: stock and coupon usage released; refund status `not_applicable`; no refund row. | U A D |
| AC-056 | R2 | FR-071, FR-093, BR-043, BR-057 | Admin `confirmed→processing→shipped→delivered` succeeds; skipping (`confirmed→shipped`), reversing, admin `pending→confirmed`, and any change from `cancelled` → 409 `INVALID_STATUS_TRANSITION`. | A U |
| AC-057 | R1 | BR-045 | At all times, no order in `confirmed`/`processing`/`shipped`/`delivered` lacks an approved payment equal to its total; no order has more than one approved payment. | D |

**Reviews**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-058 | R2 | FR-077, FR-078, BR-058 | A customer without a delivered order for the product → 403 `REVIEW_NOT_ELIGIBLE`; with one → 201. | A U |
| AC-059 | R2 | FR-079, FR-080, BR-059 | Ratings 0, 6, 3.5, `"x"` → 422; 1 and 5 → accepted; a second review of the same product → 409 `REVIEW_DUPLICATE`; comment of 1,001 chars → 422; `<script>` text is shown escaped. | A U D |
| AC-060 | R2 | FR-081, BR-060 | Ratings 5 and 4 → average 4.5; ratings 5, 4, 4 → 4.3; hiding a review recomputes the aggregate. The product page lists each visible review's rating and comment. *(amended v0.3)* | A D |

**Administration, authorization and audit**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-061 | R2 | FR-083, BR-065, SEC-007 | For **every** admin route: no token → 401; customer token → 403; admin token → success (parametrised from the OpenAPI document). In the UI, a signed-in customer opening an admin route sees the forbidden page (CL-08). Admin accounts on shopping endpoints are covered by AC-090 (R1). *(amended v0.2)* | A U |
| AC-062 | R1 | FR-014, BR-064, SEC-006 | For every customer-owned resource type, access by another customer → 404 with no data leakage. Resource types delivered later (reviews in R2, notifications in R3) join this check on release. *(amended v0.2)* | A |
| AC-063 | R2 | FR-086, FR-096, BR-061, BR-063 | Deactivating a product removes it from catalog/search, flags it in carts, and leaves existing orders intact; hard-deleting an ordered product is impossible. Reactivation and the cross-checks are verified in AC-112. *(amended v0.3)* | A U D |
| AC-064 | R2 | FR-090, BR-042, BR-062, CL-11 | Inventory adjustment in both modes (FR-090). Request shape per CL-11: exactly one of `delta` (non-zero integer) or `set_to` (non-negative integer), plus a mandatory `reason` (1–200 characters). (a) **Delta mode:** from stock 10, `delta` +5 with a reason → stock 15 and exactly one ledger movement with delta +5; then `delta` −3 → stock 12 and exactly one movement with delta −3. (b) **Absolute mode:** from stock 12, `set_to` 20 → stock 20 and exactly one movement with delta +8; from 20, `set_to` 0 → stock 0 and exactly one movement with delta −20. For every successful adjustment the movement stores the variant, the delta, the reason code `admin_adjustment` with the admin-supplied reason text, the acting admin's id and the adjustment reference (CL-11), and the AC-049 reconciliation (stock = initial stock + Σ movements) still holds. (c) **Rejections:** `set_to` of −1; a `delta` that would take stock below zero (e.g., −13 from 12); a payload with both or neither of `delta`/`set_to`; a non-integer value; a missing, blank or over-length (> 200) reason → 422 `VALIDATION_ERROR` (CL-11), each leaving stock unchanged and adding no ledger movement and no audit event. (d) A customer token → 403. *(amended v0.3)* | A D |
| AC-065 | R2 | FR-089, BR-061 | Deactivating a category with active products → 409 `CATEGORY_NOT_EMPTY`. | A |
| AC-066 | R2 | FR-098, FR-100, BR-066 | Each designated admin action creates exactly one audit event with actor, action, entity, summary, timestamp; no update/delete operation exists for audit events. | A D |

**Platform, quality attributes**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-067 | R1 | FR-103 | `/health/live` → 200 when the process is up; `/health/ready` → 200 only with DB connectivity, 503 otherwise. | A |
| AC-068 | R1 | FR-051, FR-104, NFR-008 | Resetting twice yields identical baseline row counts and checksums for categories, products, variants, coupons and users. | D |
| AC-069 | R1 | FR-105, SEC-018 | With `APP_ENV` outside `local`/`test`, test-support endpoints → 404 and cannot be enabled by request. | A |
| AC-070 | R1 | FR-108, NFR-016 | Every error response matches the envelope schema (`code`, `message`, `details`, `request_id`), with `X-Request-ID` header present; validation errors list field paths. | A |
| AC-071 | R1 | FR-106, NFR-024 | Responses of implemented endpoints validate against the published OpenAPI schemas. | A |
| AC-072 | R1 | NFR-011–013 | At 375×812, 768×1024 and 1280×800 the core flows complete with no horizontal page scroll; zero critical/serious axe violations on the six core pages; all forms operable by keyboard. | U |
| AC-073 | R3 | FR-101, FR-102, BR-067 | Order/payment status changes create exactly one notification for the owning customer; others cannot read it (404); mark-as-read persists. | A U D |

**Release reconciliation and checkout/cart lifecycle (new in v0.2)**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-074 | R2 | FR-109, BR-040, BR-055, BR-056 | Given a `confirmed` (paid) order, when two cancellation requests run concurrently (customer/customer or customer/admin), then exactly one succeeds and the other returns 409 `ORDER_NOT_CANCELLABLE`; stock is restored exactly once (+ordered quantity per variant); exactly one refund row equal to the paid amount exists; exactly one restoring ledger entry exists per variant; coupon usage stays counted. Paid-order counterpart of AC-054. | A D |
| AC-075 | R1 | FR-072, BR-053 | Before paid-order cancellation ships (R1): cancelling a `confirmed` order → 409 `ORDER_NOT_CANCELLABLE`; no stock, coupon, refund or status change; the UI offers "Cancel order" only on `pending` orders. Superseded by AC-052 when FR-073 is released (R2; DEC-26). | A U D |
| AC-076 | R1 | FR-037, FR-052, FR-115, BR-019, BR-074 | Given no pending order and blocking cart lines, when placing an order: (a) a line whose product or variant became inactive → 409 `PRODUCT_UNAVAILABLE` (details list the line ids); (b) a line with quantity above current stock, or stock 0 → 409 `INSUFFICIENT_STOCK` (details: line id, requested, available). In both cases no order, stock change, coupon usage or idempotency record is created; the cart read shows the flag (`unavailable`, `out_of_stock`, `insufficient_stock`); the UI disables "Place order" until the line is corrected or removed. A price-changed line alone is not blocking (AC-027). *(amended v0.3)* | A U D |
| AC-077 | R1 | FR-052, FR-115, BR-064, BR-074 | Given a valid cart and no pending order, when placing an order: (a) `address_id` missing or null → 422 `VALIDATION_ERROR` with field `address_id` (schema validation, which also applies while an order is pending); (b) an `address_id` that belongs to another customer or does not exist → 404 `NOT_FOUND` (this check follows the pending-order check; see AC-078 and AC-114). No order is created in either case. In the UI "Place order" stays disabled until an address is selected, and a customer with no saved address is prompted to add one inline. *(amended v0.3)* | A U D |
| AC-078 | R1 | FR-056, FR-111, FR-115, BR-070, BR-071, BR-074 | Given a customer with a `pending` order: (a) a new placement with a different `Idempotency-Key` and the same payload → 409 `CHECKOUT_ALREADY_PENDING` (details: existing order id); (b) a different key and a different but schema-valid payload — including an `address_id` the customer does not own, or cart, stock or coupon state that would otherwise fail — → 409 `CHECKOUT_ALREADY_PENDING` (the pending check takes precedence over BR-074 steps 6–11); (c) a malformed payload with a new key → 422 `VALIDATION_ERROR` (schema validation precedes the pending check); (d) the original key with a different payload → 422 `IDEMPOTENCY_KEY_REUSED`; (e) a missing or malformed key → 422 `IDEMPOTENCY_KEY_REQUIRED`. In every case the customer still has exactly one order, stock was deducted once, and the rejected request added no order, inventory movement, coupon usage or idempotency record. With 5 concurrent placements using 5 distinct keys on a fresh valid cart → exactly one 201 and four 409 `CHECKOUT_ALREADY_PENDING`; the DB shows one `pending` order and one stock deduction. *(amended v0.3)* | A D |
| AC-079 | R1 | FR-112, BR-071 | While the customer has a `pending` order, add, update, remove, clear, coupon apply/remove, shipping change and move-to-cart → 409 `CART_LOCKED` (details: pending order id) with the cart unchanged; a cart read succeeds with `locked = true`; the UI shows a pending-order banner with "Pay now" and "Cancel order". Wishlist add/remove remain allowed. | A U |
| AC-080 | R1 | FR-058, FR-113, BR-072 | After approved payment: the cart has zero lines, is unlocked, and its coupon and shipping selections are cleared; the customer can add items and start a new checkout; later cart changes do not alter the confirmed order. | A U D |
| AC-081 | R1 | FR-064, FR-072, FR-113, BR-072 | After customer cancellation or reservation expiry of an unpaid order: cart lines are unchanged (same variants and quantities), the cart is unlocked and its coupon and shipping selections are retained; lines are re-validated on the next read (FR-037 flags); a new placement with a new key creates a new order; stock is restored and coupon usage released. | A U D |
| AC-082 | R1 | FR-059, FR-060, FR-061, FR-110, BR-069 | For each non-approved outcome (declined, timeout, error), after the payment operation returns: the order, its items, the stock deduction, the `order_placed` ledger entries and the coupon usage from placement all remain; a committed attempt row exists; the cart stays locked. With a controlled technical failure injected into the payment-recording step (TR-004), the payment operation fails without changing the order, stock, ledger, coupon usage or attempt count, and the order stays `pending` and payable. | A D |
| AC-083 | R1 | FR-056, FR-063, BR-048, BR-070 | Idempotency scope: (a) the same key and payload from two different customers → two independent orders; (b) the same key string used for placement and for payment is independent; (c) a payment key is scoped to its order: same key + same outcome replays the stored result (status and body) with no new attempt and an unchanged attempt count; same key + different outcome → 422 `IDEMPOTENCY_KEY_REUSED`; (d) a deliberate retry with a new key creates attempt 2; (e) a request rejected before any state change (e.g., 409 `INSUFFICIENT_STOCK`) stores no record, so the same key succeeds once the cause is fixed; (f) after 24 h (clock advanced) the same key is treated as new; (g) a malformed key (7 or 65 characters, illegal characters) → 422 `IDEMPOTENCY_KEY_REQUIRED`. | A D |
| AC-084 | R1 | FR-064, FR-114, BR-069, BR-073 | Payment versus cancellation and expiry (FR-064, FR-114). (a) Payment on an order already cancelled by the customer or by expiry → 409 `ORDER_NOT_PAYABLE`; no payment-attempt row is created and the attempt count is unchanged. (b) Payment on a `pending` order whose deadline has elapsed (clock advanced; expiry job not yet run) → expiry takes precedence: the order becomes `cancelled`, stock is restored once, coupon usage released once, a `reservation_expired` ledger entry and a status-history entry are written, the cart is unlocked, the response is 409 `ORDER_NOT_PAYABLE` and no attempt row exists — for each of the four outcomes. (c) The expiry job later ignores the order (no second restoration, release or entry). (d) Approval racing with reservation expiry, and approval racing with customer cancellation, repeated 20 times each: exactly one outcome wins — either `confirmed` with one approved payment and stock deducted, or `cancelled` with stock restored once — never both, and the BR-045/BR-046 invariants hold. (e) Delay scenarios are AC-105 and AC-106; the approval-wins case is AC-107. *(amended v0.3)* | A D |
| AC-085 | R1 | FR-071, BR-043, BR-045 | R1 transition enforcement: paying a `cancelled` order → 409 `ORDER_NOT_PAYABLE`; paying a `confirmed` order → 409 `ORDER_ALREADY_PAID`; cancelling a `cancelled` order → 409 `ORDER_NOT_CANCELLABLE`; no customer endpoint accepts a status field (→ 422, SEC-008) and the OpenAPI document exposes no operation that sets an arbitrary status; in the database every (from, to) pair in the status history belongs to the BR-043 matrix. | A D |
| AC-086 | R1 | FR-057, BR-047 | The checkout UI shows a clearly labelled "Simulated payment" control with exactly four options (approved, declined, timeout, processing error); the payment API accepts only those four `simulated_outcome` values (any other → 422); every outcome, including declined, timeout and error, returns a 2xx response whose body carries the attempt status (`approved`, `declined`, `timed_out`, `error`). | U A |
| AC-087 | R1 | FR-048, FR-054, BR-036 | Given a coupon that was valid when applied, when it becomes invalid before placement (expired via clock advance, usage limit consumed by another customer, or deactivated), then placement → 422 with the specific `COUPON_*` code; no order, stock deduction, coupon usage or idempotency record is created and the cart stays unlocked. | A D |

**Registration and access (new in v0.2)**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-088 | R1 | FR-001, FR-003 | After successful registration the UI signs the user in through the standard login operation and shows the authenticated state on the page they came from (or home); if that sign-in call fails, the UI shows the login page with a "registration successful, please log in" notice; no verification or OTP screen appears at any point. | U A |
| AC-089 | R1 | FR-006, FR-007, BR-003 | (a) A guest opening /cart, /wishlist, /checkout, /account or /orders is redirected to login and returned there after login; (b) a profile update with a valid name/phone → 200 and persisted; a blank name, a 101-character name or phone `12ab` → 422; a payload containing `email` → 422 (email is read-only). | U A D |
| AC-090 | R1 | FR-010, BR-065 | An admin token on address, cart, wishlist, place-order, pay-order and own-order endpoints → 403 `FORBIDDEN` with no data change. (Admin-route authorization is AC-061, R2.) | A |

**Coverage additions (new in v0.2)**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-091 | R1 | FR-011, FR-013, FR-014, BR-008 | Address CRUD: create → 201 and listed; update persists; delete removes; every required field blank or over length → 422 with the field path; another customer's address read/update/delete → 404. | A U D |
| AC-092 | R1 | FR-016, FR-022, FR-029, CL-07 | (a) The category tree shows the 5 top-level categories with their subcategories, and a parent category lists the products of its subcategories (CL-07); (b) product detail shows name, brand, description, specifications, gallery (≥ 1 image), price, availability and rating summary; (c) every image has non-empty alt text and a product without an image shows the placeholder. | U A D |
| AC-093 | R1 | FR-033, FR-034, BR-018 | Cart edit: quantity 2 → 4 persists; the maximum (10) is accepted when stock allows; 0 → 422 (removal is a separate operation); removing a line removes only that line; clearing empties the cart; totals are recalculated after each change. | A U D |
| AC-094 | R1 | FR-042, FR-043, FR-045, BR-023 | Wishlist: removing deletes the entry (removing a non-existent entry → 404); the list shows current price and availability; out-of-stock and deactivated products remain, flagged; the wishlist survives logout and login. | A U D |
| AC-095 | R1 | FR-047, BR-030, BR-035 | Removing an applied coupon restores no-coupon totals (e.g., T-01 without coupon: discount 0.00, shipping 60.00, total 2,060.00); applying a coupon to a cart never counts usage (only placement does). *(amended v0.5)* | A D |
| AC-096 | R1 | FR-070, BR-051 | Order numbers match `NC-YYYYMMDD-NNNNNN` (UTC placement date), are unique across 50 concurrent placements by distinct customers, and appear on the confirmation page and in order history. | A U D |
| AC-097 | R1 | FR-076, BR-052 | Every status change (placement, approval, cancellation, expiry; admin transitions in R2) appends exactly one history entry with from, to, actor type, reason where required and UTC timestamp; entries are time-ordered and no API modifies or deletes them. | A D |
| AC-098 | R1 | FR-107 | With `MIN_ORDER_AMOUNT`, `MAX_QTY_PER_LINE` and `LOW_STOCK_THRESHOLD` overridden through environment configuration, behaviour changes accordingly without code changes; defaults match §8.2 when unset. *(amended v0.5)* | A |
| AC-099 | R2 | FR-084, FR-085, FR-087, BR-010, BR-013, CL-02 | Admin creates a product with ≥ 1 variant → 201 and visible per BR-011; creation without a variant → 422; update of name/description/specifications persists; a payload changing `id`, `slug` or any SKU → 422; admin detail returns inactive products with variants and stock. Duplicate SKU or slug is rejected (status and code per CL-02). | A U D |
| AC-100 | R2 | FR-088, FR-089, BR-061, CL-02, CL-03 | Variants: add (initial stock recorded in the ledger per CL-03), update price (positive integer), deactivate (excluded from availability); stock changes only through inventory adjustment. Categories: create, rename, deactivate; a third nesting level → 422; a duplicate variant option set or category slug is rejected (CL-02). | A U D |
| AC-101 | R2 | FR-091, FR-092, CL-04 | The admin order list filtered by status, date range, order number and customer email returns exactly the rows an equivalent SQL query returns (semantics per CL-04); order detail shows items, address snapshot, payment attempts, refund, status history and ledger movements; a customer token → 403. | A U D |
| AC-102 | R2 | FR-094, BR-053, BR-054, BR-055, CL-09 | Admin cancellation with a reason (1–200 characters) is allowed in `pending`, `confirmed` and `processing`, with effects per BR-054/BR-055 (stock restored once; refund only for paid orders); a missing reason → 422; `shipped`, `delivered` and `cancelled` → 409 `ORDER_NOT_CANCELLABLE`. | A U D |
| AC-103 | R2 | FR-095, BR-010, BR-062 | Admin validation parity: price 0, negative or non-integer → 422; blank or over-length name → 422; stock set below zero → 422 — the same rules and error codes as the customer-facing equivalents. | A |
| AC-104 | R1 | FR-001, FR-018, FR-032, FR-046, FR-052, FR-058, FR-065, FR-068 | Core journey (OBJ-01, MET-07): on the standard seed a new customer registers (auto sign-in), searches, selects a variant, adds to cart, ensures the cart subtotal is above R800.00 and applies `SAVE100`, adds an address, keeps Standard shipping, selects Approved and places the order. The confirmation shows an order number and the server-calculated total; the order appears in history; the DB shows order `confirmed`, one approved payment equal to the total, stock reduced, coupon usage 1, and the cart empty and unlocked; the journey runs within 90 s. *(amended v0.4)* | U A D |

**Race conditions, contracts and clause-level strengthening (new in v0.3)**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-105 | R1 | FR-060, FR-064, FR-114, BR-069, BR-073 | Expiry during the simulated delay. Given a `pending` order carrying a coupon whose reservation deadline is shortly ahead, when a payment with outcome `timeout` is started and the clock is advanced past the deadline during the simulated delay (TR-005, TR-006), then after the delay: the payment returns 409 `ORDER_NOT_PAYABLE`; **no payment-attempt row** exists for the call and the attempt count is unchanged; the order is `cancelled` through the expiry transition (applied by the payment operation under the order lock, or already applied by the expiry job); stock is restored exactly once; coupon usage is released exactly once; exactly one `reservation_expired` ledger entry per variant and exactly one `pending → cancelled` status-history entry exist; the cart is unlocked with its lines retained; no approved payment exists; an expiry-job run afterwards finds nothing to do (no second restoration, release or history entry). *(new v0.3)* | A D |
| AC-106 | R1 | FR-060, FR-072, FR-075, FR-114, BR-069, BR-073 | Cancellation during the simulated delay. Given a `pending` order carrying a coupon and a `timeout` payment in its simulated delay, when the customer cancels the order during the delay, then the cancellation completes without waiting for the delay (the payment holds no order lock); stock is restored once and coupon usage released once; after the delay the payment returns 409 `ORDER_NOT_PAYABLE`; no payment-attempt row is created and the attempt count is unchanged; exactly one cancellation status-history entry exists; no approved payment exists; no second restoration, release or transition occurs; the cart is unlocked with its lines retained. *(new v0.3)* | A D |
| AC-107 | R1 | FR-058, FR-064, FR-072, FR-114, BR-045, BR-046, BR-073 | Approval wins the race. When an `approved` payment and a reservation expiry, or an `approved` payment and a customer cancellation, are submitted concurrently (20 repetitions each) and the approval commits first: the order is `confirmed` with exactly one approved payment equal to the total; stock stays deducted (no restoring ledger entry); coupon usage stays counted; the cart is emptied and unlocked; the expiry job no-ops; the losing cancellation returns 409 `ORDER_NOT_CANCELLABLE` (R1, DEC-26) with no effects — no second outcome, restoration or status transition. When cancellation or expiry commits first, the outcome is instead that of AC-084 (cancelled, stock restored once, payment 409 `ORDER_NOT_PAYABLE`, no attempt). Every order ends in exactly one of these two consistent states. *(new v0.3)* | A D |
| AC-108 | R2 | FR-073, FR-109, BR-055, BR-056, BR-073, CL-10 | Approval versus customer cancellation in R2. Where a customer cancellation is evaluated after an approval has committed, the outcome follows the resolution of CL-10 (approved default: processed as a paid-order cancellation). Whatever the resolution, the invariants hold: at most one approved payment; stock restored at most once; at most one refund, equal to the paid amount; exactly one final order status; stock = initial + Σ movements (AC-049); no cancelled paid order without a refund row. *(new v0.3)* | A D |
| AC-109 | R1 | FR-017, FR-025, BR-010, BR-011, BR-012, BR-016, BR-060, CL-01, CL-13 | Product-listing contract. On the standard seed, each item returned by the listing API contains `id`, `slug`, `name`, `brand`; `from_price` (integer minor units); a primary image (URL and alt text); `rating_average` and `review_count`; and an `availability` state; the envelope carries `page`, `page_size`, `total_items` and `total_pages`. For a sample of ≥ 12 products including the §5.4 fixtures, values equal the authoritative database: `from_price` = the lowest price among the product's **active** variants (a cheaper inactive variant is ignored); `availability` follows BR-012 and CL-13 (fixtures with stock 0, 1, 5 and 6 and the partially available multi-variant product); `rating_average` = mean of the visible seeded reviews rounded half-up to 1 decimal and `review_count` = their count, with unrated products showing no average and count 0 (R1 ratings are read-only seeded data per CL-01; review creation is not an R1 requirement); exactly one primary image per product. Inactive products, products in inactive categories and products with no active variant are absent and excluded from `total_items` (BR-011); `total_items` equals the SQL count and `total_pages` = ceil(`total_items` ÷ `page_size`). The UI product card shows name, brand, a "From" price, the image with alt text, the rating with count (or a no-reviews indication) and the availability badge. Pagination boundaries are as in AC-015. *(new v0.3)* | A U D |
| AC-110 | R1 | FR-068, FR-069, FR-076, BR-029, BR-050, BR-052, BR-056, BR-064 | Customer order detail. Given a customer with (i) a `confirmed` order placed by a customer eligible for `WELCOME10`, with that coupon and Express shipping, (ii) a `pending` order after a declined payment, and (iii) a `cancelled` unpaid order, the order-detail API and page return values that match the persisted order and snapshot rows: order number and placement timestamp; per item the product name, variant description, SKU, unit price, quantity and line total; the delivery-address snapshot (all BR-008 fields); `subtotal`, `discount`, `shipping_fee` and `total`, with total = subtotal − discount + shipping_fee (BR-029) and discount and shipping equal to the server calculation at placement; `status`; `payment_status` (`paid` for (i), `failed` for (ii), and `unpaid` or `failed` for (iii) according to the attempts recorded); `refund_status` = `not_applicable` for all three (no refund exists in R1); and `status_history` in chronological order whose entries (from, to, actor type, UTC timestamp) equal the history rows, e.g. `pending → confirmed` for (i) and `pending → cancelled` for (iii). After the product's price, name, SKU and image change and after the delivery address is edited or deleted, the detail is unchanged (BR-050; AC-014, AC-051). Another customer's order id → 404 (AC-050). *(new v0.3)* *(amended v0.4)* | A U D |
| AC-111 | R2 | FR-069, FR-073, FR-074, BR-055, BR-056 | Order detail with refund (R2). After a `confirmed` order is cancelled by the customer, the order detail shows `status` `cancelled`, `payment_status` `paid`, and `refund_status` `refund_pending` and then `refunded` (delay 0 in test); the item and address snapshots and the subtotal, discount, shipping fee and total are unchanged; the status history is chronological and ends with the cancellation entry; the refund row's amount in the database equals the paid amount and the order total; an order with no refund still shows `not_applicable`; another customer's order → 404. *(new v0.3)* | A U D |
| AC-112 | R2 | FR-037, FR-086, FR-096, BR-011, BR-061, BR-063 | Product deactivation and reactivation. Given an active product with known stock, a line in a customer's cart, a wishlist entry and a past order: (a) **Deactivate** → the product is absent from listings, search and category counts (matching the BR-011 visibility query), its detail returns 404, its cart line shows the blocking flag `unavailable` and placement returns 409 `PRODUCT_UNAVAILABLE` (FR-037, BR-063), its wishlist entry is flagged unavailable, and the past order's snapshots (name, variant description, SKU, unit price, quantity, image reference) are unchanged. (b) **Reactivate** → the product is visible again in listings, search and detail when its category is active and it has ≥ 1 active variant (BR-011); the cart line's flag clears on the next read; the past order is still unchanged. (c) With the category inactive, or with every variant inactive, reactivating the product leaves it hidden. (d) Neither action changes any variant's stock quantity or writes inventory movements. (e) Existing orders and their totals are never modified. Hard deletion of an ordered product remains impossible (AC-063). *(new v0.3)* | A U D |
| AC-113 | R1 | FR-062, FR-063, FR-065, FR-067, BR-044, BR-046, BR-049, BR-070, CL-12 | Payment-attempt record. Given a `pending` order with total T: (a) attempt 1 with outcome `declined` and key K1 commits a row with `order_id` = the order, `attempt_number` = 1, `status` = `declined`, `amount` = T (equal to the order total), `created_at` a UTC timestamp within the request window, and `idempotency_key` = K1; (b) a deliberate retry with a new key K2 and outcome `approved` commits attempt 2 (`attempt_number` = 2, key K2, status `approved`, amount T); attempt numbers per order are unique and sequential (1, 2) and each row carries its own key; (c) replaying K1 or K2 with the same outcome returns the stored response and creates no row (count stays 2); (d) a payment operation that fails before committing its attempt — rejected with 409/422, or failed by an injected technical error (TR-004) — leaves no partial or null-field row and does not increment the attempt count, and the next committed attempt receives the next number without a gap; (e) with 5 concurrent `declined` attempts under distinct keys and a cap of 3, exactly 3 attempts commit with numbers 1, 2 and 3 and 2 requests return 409 `PAYMENT_ATTEMPTS_EXHAUSTED`; (f) `timed_out` and `error` attempts each commit all six attributes (timestamp taken at commit). The payment response exposes `order_id`, `attempt_number`, `status`, `amount` and `created_at`; the idempotency key is verified in the database (exposure per CL-12). The UI payment-failed page shows the outcome of the latest attempt with retry and cancel actions. *(new v0.3)* | U A D |
| AC-114 | R1 | FR-111, FR-115, BR-070, BR-071, BR-074 | Placement precedence. Using fixtures that violate several preconditions at once, the first failing step of the BR-074 order is reported and nothing is created (no order, stock movement, coupon usage or idempotency record): (a) no key → `IDEMPOTENCY_KEY_REQUIRED` even if the payload is also malformed (step 2 before 4); (b) an already-used key with a different payload that is also malformed → `IDEMPOTENCY_KEY_REUSED` (3 before 4); (c) a malformed payload while a pending order exists → `VALIDATION_ERROR` (4 before 5); (d) a schema-valid new request with a foreign `address_id` while a pending order exists → `CHECKOUT_ALREADY_PENDING` (5 before 6); (e) a foreign `address_id` with an empty cart and no pending order → `NOT_FOUND` (6 before 7); (f) an empty cart → `CART_EMPTY`, a below-minimum cart → `ORDER_BELOW_MINIMUM` (step 7, after the empty check), and a cart with both an unavailable line and an insufficient-stock line → `PRODUCT_UNAVAILABLE` (8 before 9); (g) insufficient stock together with an expired coupon → `INSUFFICIENT_STOCK` (9 before 10); (h) an invalid coupon together with a stale `expected_total` → the `COUPON_*` code (10 before 11); (i) all checks passing → 201, and because the rejections above stored no idempotency record, the same key succeeds once its cause is fixed. A replay of an earlier successful placement is returned unchanged (original status and body) whether its order is pending, paid or cancelled. *(new v0.3)* *(amended v0.5)* | A D |

**Coupon eligibility and minimum boundaries (new in v0.4)**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-115 | R1 | FR-046, FR-048, BR-036, BR-075 | Coupon eligibility (`WELCOME10`). (a) A brand-new customer, and a customer whose only orders are `pending`, `confirmed`, `processing` or `cancelled`, applying `WELCOME10` → 422 `COUPON_NOT_ELIGIBLE` with no discount; placing an order with that coupon selected is rejected with the same code at BR-074 step 10, creating no order, stock change, coupon usage or idempotency record. (b) A customer with an order that has reached `shipped`, and a customer with a `delivered` order, can apply it and receive the BR-026 discount. (c) Eligibility uses only the customer's own orders: another customer's shipped order does not qualify them. (d) `SAVE100` and `ONCE1` carry no eligibility condition: a brand-new customer can apply them, subject to their other conditions. In R1 the eligible customer is the seeded customer with shipped and delivered orders (TR-003); eligibility earned through real fulfilment is exercised from R2, when admins can ship orders. *(new v0.4)* | A D |
| AC-116 | R1 | FR-046, FR-048, BR-033 | Minimum-order boundaries. `SAVE100` requires a subtotal above R800.00 (exclusive): R799.99 and R800.00 → 422 `COUPON_MIN_ORDER_NOT_MET` (T-11); R800.01 → accepted with discount R100.00 (T-12); it depends on order value only, with no customer-history condition. `WELCOME10`'s R500.00 minimum stays inclusive: R499.99 → rejected, R500.00 → accepted (T-04, T-05). *(new v0.4)* | A U |


**Shipping and minimum-order criteria (new in v0.5)**

| ID | Rel | Verifies | Criterion | Layers |
|---|---|---|---|---|
| AC-117 | R1 | FR-049, FR-050, FR-116, BR-028, BR-029, BR-075, BR-076, BR-077 | First-order free shipping. (a) A first-time buyer placing a Standard order with a pre-coupon subtotal from R250.00 up to under R1,000.00 pays R0.00 shipping (T-13, T-09); R1,000.00 or more pays R60.00 (T-06, T-08); Express is R120.00 in every case (T-10). (b) The band uses the pre-coupon subtotal: a R900.00 cart with `SAVE100` (discounted to R800.00) still ships free for a first-time buyer (T-16). (c) A returning customer pays R60.00 Standard at every subtotal (T-17). (d) First-order status is decided from the customer's previous orders, excluding `cancelled` orders and the order currently being placed: a customer whose only earlier orders are `cancelled` (including an unpaid order cancelled or expired) is still a first-time buyer, while an earlier `pending`, `confirmed`, `processing`, `shipped` or `delivered` order makes the next order a returning order. (e) A customer using `WELCOME10` is returning by definition and pays R60.00 Standard, including at subtotals from R250.00 to R999.99 (T-01 – T-03, T-05, T-07). (f) The small-goods exception grants no free shipping: a first-time buyer's R249.99 cart of four small-goods units pays R60.00 (T-14). (g) The shipping fee shown in the cart equals the fee stored on the placed order. *(new v0.5)* *(amended v0.6)* | A U D |
| AC-118 | R1 | FR-116, BR-077 | Minimum order and small goods. (a) A cart whose pre-coupon subtotal is below R250.00 and that holds fewer than four small-goods units shows the `below_minimum_order` flag, the UI disables "Place order", and placement returns 409 `ORDER_BELOW_MINIMUM` with nothing created (T-15); three units do not qualify. (b) A cart of four Wearables and Audio units at R249.99 is accepted (T-14); units are counted across all small-goods lines (two units of one product plus two of another qualify); three small units plus other items below R250.00 is rejected. (c) R250.00 with no small-goods items is accepted (T-13). (d) The check ignores coupons: a R260.00 cart with `ONCE1` (discounted to R247.00) is accepted. (e) A subcategory of Wearables and Audio counts as small goods; four units of a product in another category totalling below R250.00 are rejected. (f) The exception waives only the minimum: Standard shipping stays R60.00 (T-14). *(new v0.5)* *(amended v0.6)* | A U |
| AC-119 | R1 | FR-005, BR-005, CL-20 | With an authenticated session and five minutes remaining before access-token expiry, the UI displays and announces “Your session is about to expire.” The warning does not obtain a replacement token or alter the token's expiry. Once the token expires, a protected request returns 401 `TOKEN_EXPIRED`; the UI redirects to login and restores the intended destination after successful login. | A U |
| AC-120 | R1 | FR-112, BR-041, CL-18 | While a pending order's reservation remains active, the payment page and order detail display “Reserved until [time]” using the reservation deadline; order detail offers “Pay now”; the cart and checkout entry display the pending-order banner with “Pay now” and “Cancel order.” The deadline is placement time plus the configured 30-minute reservation window and is never extended by retries. An expired order cannot be paid. | A U D |
| AC-121 | R1 | FR-072, FR-073, FR-094, CL-09, CL-19 | Customer cancellation of an eligible unpaid pending order (R1) or confirmed paid order (R2) does not require or request a reason. The cancellation can be completed without a reason value. Administrator cancellation (R2) still requires a 1–200 character reason; omitting it returns 422. | A U |

### 12.2 Success metrics

| ID | Metric | Target |
|---|---|---|
| MET-01 | Requirement → acceptance criterion → automated test traceability for **M** requirements of the release (requirement → AC mapping is 100% as of v0.2; see Appendix D) | 100% at release gate |
| MET-02 | Automated suite flake rate on the main branch (rolling 20 CI runs) | ≤ 2% |
| MET-03 | Open Critical/High application defects at release gate | 0 (Medium triaged and recorded) |
| MET-04 | Business rules (BR-001 – BR-077 in the release) with ≥ 1 automated check at the lowest practical layer; money/inventory/payment/order-state rules (BR-024–057) also database-verified *(amended v0.4)* *(amended v0.5)* | 100% / 100% |
| MET-05 | CI duration: pull-request pipeline / full suite | ≤ 15 min / ≤ 40 min |
| MET-06 | Time from clean clone to running system with documented commands | ≤ 10 min |
| MET-07 | Core journey (register → add to cart → coupon → checkout approved → order visible) passes end-to-end in a UI test | Passes deterministically, ≤ 90 s |
| MET-08 | Critical/serious accessibility violations on core pages | 0 |
| MET-09 | Requirement statuses (Planned/Implemented/Verified) reflect reality at every release gate | 100% accurate |
| MET-10 | Backend service-layer line coverage (informational; not a substitute for rule coverage) | ≥ 80% |

## 13. Risks, dependencies and assumptions

### 13.1 Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| RSK-01 | Race conditions in stock, coupon usage, payment and cancellation | High | Conditional updates, constraints, ledger (BR-037–042), concurrency ACs |
| RSK-02 | Scope creep (catalog breadth, PC builder, extra features) | High | MoSCoW, release plan, non-goals, change control |
| RSK-03 | Ambiguous business rules cause rework | High | Decision register (§14) approved before downstream documents |
| RSK-04 | Image/trademark/licensing problems | Medium | §5.3 policy, fictional listings, generated/licensed assets only |
| RSK-05 | Flaky UI tests from async behaviour, animations, external assets | Medium | TR-001, TR-012, TR-013, TR-020 |
| RSK-06 | Time-dependent behaviour (expiry, TTL, throttling) is hard to test | Medium | TR-005, TR-018 |
| RSK-07 | Reservation expiry and refund processing need background execution | Medium | Keep mechanism simple; deterministic trigger/clock in test (architecture decides) |
| RSK-08 | Divergence between application and SDET tracks | Medium | One PRD, stable IDs, change log, traceability matrix |
| RSK-09 | Test-support interfaces exposed in a non-test environment | High | SEC-018, AC-069 |
| RSK-10 | Single-developer capacity | Medium | Small increments, phased releases, defined MVP |
| RSK-11 | Seed data volume and upkeep | Low | Structured seed files and generators; fixtures defined in §5.4 |
| RSK-12 | CI/local environment drift | Medium | Compose parity (TR-014), pinned versions |
| RSK-13 | Simulated payment mistaken for production-grade payment handling | Low | Explicit demo disclosure; NG-01 |
| RSK-14 | The one-pending-order and cart-lock rules (DEC-25) could strand or confuse customers who abandon a payment | Medium | Pending-order banner with Pay/Cancel (FR-112), 30-minute expiry (BR-041), deterministic expiry in tests (CL-05, TR-005) |

### 13.2 Dependencies

| ID | Dependency |
|---|---|
| DEP-01 | Approval of this PRD and its decision register before the next planning documents |
| DEP-02 | GitHub repository and GitHub Actions availability |
| DEP-03 | Docker/Docker Compose on developer machines and CI runners |
| DEP-04 | Licensed/original image assets (§5.3) |
| DEP-05 | SDET strategy and automation track (separate) consuming the IDs in this PRD |
| DEP-06 | Architecture document confirming mechanisms deferred here (token storage, hashing algorithm, background execution, test-support design, identifier strategy) |

### 13.3 Assumptions

| ID | Assumption |
|---|---|
| ASM-01 | One storefront, one seller, one warehouse, one currency, English only |
| ASM-02 | Web only (responsive); no native apps |
| ASM-03 | All data is synthetic; there are no real customers, personal data or payments |
| ASM-04 | No backorders: stock is a finite integer per variant |
| ASM-05 | Delivery fulfilment is simulated; shipping options are static configuration |
| ASM-06 | Emails are never sent; no email infrastructure exists |
| ASM-07 | Admin accounts are seeded; there is no admin sign-up |
| ASM-08 | The MVP serves modest load; correctness under concurrency matters more than throughput |
| ASM-09 | The proposed stack in `PROJECT_BRIEF.md` is unchanged |
| ASM-10 | Registration revealing an existing email is acceptable while verification is out of scope |
| ASM-11 | Default delivery country and currency are single configured values (DEC-02, DEC-17) |

## 14. Decision register and clarifications

Each decision shows the **approved default** used throughout this PRD (approved by the owner on 2026-10-12 with "approve all"). "Needed by" is the earliest downstream document that depends on it.

**Status: DEC-01 – DEC-27 and CL-01 – CL-13 approved on 2026-10-12; DEC-28, DEC-29 and CL-14 – CL-16 approved on 2026-10-13; CL-17 – CL-20 approved on 2026-10-20; no item is pending.** Items tagged *(amended v0.2)* changed in v0.2 and items tagged *(amended v0.3)* or *(new v0.3)* changed in v0.3. DEC-25 – DEC-27 and CL-01 – CL-09 were added in v0.2; CL-10 – CL-13 were added in v0.3; DEC-28, CL-14 and CL-15 were added in v0.4; DEC-29 and CL-16 were added in v0.5 and CL-16 was approved in v0.6; CL-17 – CL-20 were added and approved in v0.7.

### 14.1 Decision register

| ID | Decision / ambiguity in the brief | Approved default | Alternatives (not adopted) | Needed by |
|---|---|---|---|---|
| DEC-01 | MVP boundary not defined | R1 = phases 1–4 (including cancellation of *unpaid* orders); R2 = paid cancellation/refunds, admin, reviews, audit; R3 = optional notifications; R1 shows seeded read-only rating aggregates (CL-01) and customer cancellation of `confirmed` orders is not available until R2 (DEC-26) *(amended v0.2)* | Move paid cancellation/refunds into R1 | Backlog |
| DEC-02 | Currency, tax and money representation unspecified | Single currency ZAR (R), tax-inclusive prices, no tax line, integer minor units | USD or other; separate VAT line | ERD |
| DEC-03 | "Guest: begin shopping" vs "authenticate before protected actions" | Guests browse/search only; add-to-cart/wishlist triggers login, then completes the action; no guest cart/checkout | Guest cart merged into customer cart on login | Stories |
| DEC-04 | Session/token design | 30-min signed access token, no refresh token; server-side revocation on logout/password change; email immutable; **no forgot-password** (needs email — excluded by the no-email/OTP rule); silent refresh was considered on 2026-10-13 and not adopted: the 30-minute, no-refresh rule stands *(amended v0.4)* | Refresh tokens; admin-assisted password reset | Architecture |
| DEC-05 | Password/lockout values | 8–128 chars, ≥ 1 letter + 1 digit; lock 15 min after 5 failures (Should) | Stricter/looser policy; no lockout | Stories |
| DEC-06 | Variant, SKU and price model | Price, SKU and stock live on the variant; product has a base code; from-price = lowest active variant; wishlist is product-level | Product-level price with variant deltas | ERD |
| DEC-07 | Totals order and shipping rules ("explicit fee/free-shipping rules") | Discount before shipping; Standard R60 (free when discounted subtotal ≥ R1,000), Express R120 never free; coupons exclude shipping; no tax; v0.5: the free-shipping rule and the minimum order are replaced by DEC-29 *(amended v0.5)* | Free-shipping on pre-discount subtotal; flat/other fees | Stories |
| DEC-08 | Coupon rules and administration | Seed coupons §8.3; one per order; case-insensitive; usage counted at placement, released on unpaid cancellation, **not** on paid cancellation; no coupon admin UI; v0.4: customer eligibility, the exclusive SAVE100 minimum and the percentage ONCE1 per DEC-28 *(amended v0.4)* | Restore usage on every cancellation; add coupon admin | Stories |
| DEC-09 | Inventory model and stock hold | No cart reservation; stock deducted at order placement; 30-min hold for pending orders then auto-cancel; low stock ≤ 5 | Deduct only on payment approval (oversell risk); reserve at cart | ERD |
| DEC-10 | What a failed/timed-out payment does to the order; who picks the outcome | Order stays `pending` with failed payment; ≤ 3 attempts; outcome chosen via a labelled "Simulated payment" control; outcomes returned as 2xx business results; no card fields; placement (creates the pending order and reserves stock) and payment are separate operations committed independently, so a failed payment never rolls back the reservation; after the reservation deadline expiry takes precedence over payment, and a payment that finds the order cancelled or expired records no attempt (BR-069, BR-073) *(amended v0.2)* *(amended v0.3)* | Failure auto-cancels order; HTTP 4xx/5xx for failures | Stories |
| DEC-11 | Idempotency mechanism | Required `Idempotency-Key` header on placement and payment; 24 h retention; key scoped per customer and operation (payment keys per order); records stored only with committed state changes (BR-070) *(amended v0.2)* | Server-side dedupe only; optional key | Architecture |
| DEC-12 | Order lifecycle and cancellation eligibility | Matrix in §8.1: customer cancels `pending`/`confirmed`; admin also `processing`; no returns after shipping | Allow customer cancel in `processing` | Stories |
| DEC-13 | Refund model | Full refund only (goods + shipping); `refund_pending` → `refunded` through simulator with configurable delay | Partial refunds; instant `refunded` only | ERD |
| DEC-14 | Review eligibility and rules | Delivered purchase required; rating 1–5; one per product; no edit/delete; admin hide (Could) | Allow edit/delete; allow reviews without purchase | Stories |
| DEC-15 | Search and discovery behaviour | Case-insensitive substring on name/brand; no fuzzy search; sort definitions per BR-015; default sort `newest`; page size 12 (max 48) | PostgreSQL full-text search; different page sizes | Architecture |
| DEC-16 | Seed volume and price tiers | ≥ 60 products, tier bands §5.1, fixtures §5.4, all listings fictional | Larger/smaller dataset | Backlog |
| DEC-17 | Address rules and delivery area | Max 10 addresses; single configured delivery country (default South Africa) with 4-digit postal code; saved address required at checkout; order address is a snapshot | Multiple countries; checkout-only one-off address | ERD |
| DEC-18 | HTTP result for another customer's resource | 404 for ownership violations; 403 for role violations | Use 403 for both | Architecture |
| DEC-19 | Admin scope | Admins cannot shop (403 on addresses, cart, wishlist, checkout/payment, own-order operations and reviews; aligned with BR-065 and §10.2) *(amended v0.2)*; no hard deletes; no user management, coupon management or image upload | Admin as superset of customer; add coupon management | Stories |
| DEC-20 | Audit/notification scope ("explicit scope before implementation") | Audit events R2 for the actions in BR-066; in-app notifications R3 (Could) with events in BR-067 | Audit in R3; drop notifications | Backlog |
| DEC-21 | Test-support capabilities | Guarded reset/seed/state-setup/clock control in `local`/`test` only (CLI and/or endpoints) | CLI-only; DB-only reset | Architecture |
| DEC-22 | Tooling beyond the brief's stack | ruff + mypy, ESLint + Prettier + `tsc`, Alembic, axe for accessibility checks (no change to the agreed stack) | Other linters/formatters | Architecture |
| DEC-23 | Browser/device support | Chromium primary; Firefox and WebKit as secondary (e.g., scheduled) runs; viewports 375×812, 768×1024, 1280×800 | Chromium only | Backlog |
| DEC-24 | Identifier strategy (UUID vs integer) and fixed seed IDs | Deferred to the ERD; PRD requires stable, seed-fixed identifiers | — | ERD |
| DEC-25 | Duplicate-checkout prevention and cart behaviour while an order is pending *(new v0.2)* | At most one `pending` order per customer; the cart is locked to it (409 `CART_LOCKED`); further placement → 409 `CHECKOUT_ALREADY_PENDING`; approval empties the cart; cancellation/expiry unlocks it and keeps its lines (BR-071, BR-072); the pending-order check precedes the address, cart, stock, coupon and total checks (BR-074 step 5) *(amended v0.3)* | Allow several pending orders; clear the cart at placement (never restored); allow cart edits while pending | Stories |
| DEC-26 | R1 behaviour for a customer cancelling a `confirmed` order, since paid-order cancellation ships in R2 *(new v0.2)* | Not cancellable in R1 (409 `ORDER_NOT_CANCELLABLE`, action hidden in the UI); FR-073 enables it in R2 | Pull paid-order cancellation and refunds into R1 (contradicts the DEC-01 default) | Backlog |
| DEC-27 | Registration contract and sign-in *(new v0.2)* | API returns 201 + user representation, **no token or session**; the UI then signs in through the normal login operation and falls back to the login page if that fails | Registration returns an access token; require an explicit login | Stories |
| DEC-28 | Coupon eligibility and conditions *(new v0.4; approved 2026-10-13)* | `WELCOME10` is for returning customers only: the customer must own an order that has reached `shipped` or `delivered`; ineligible → 422 `COUPON_NOT_ELIGIBLE`; R1 tests use the seeded customer with shipped orders. `SAVE100`: the R800 minimum stays but becomes exclusive (subtotal above R800.00), order value only. `ONCE1`: any customer, percentage type (value: CL-15), global limit 1 and per-customer limit 1 unchanged, no separate email check (email is unique per account) | `WELCOME10` for new customers; inclusive R800 minimum; drop the global limit on `ONCE1` | Stories |
| DEC-29 | Shipping fees, first-order offer and minimum order *(new v0.5; approved 2026-10-13)* | Standard R60 and Express R120. Standard is free only for a customer's first order (earliest non-cancelled) with a pre-discount subtotal from R250.00 up to under R1,000.00; orders of R1,000.00 or more pay the fee (the "free at R1,000" rule is withdrawn). An order under R250.00 is accepted only with more than three units of small goods, where small goods = the Wearables and Audio category; the minimum uses the pre-discount subtotal; the consequences listed in CL-16 are confirmed *(amended v0.6)* | Keep free shipping at R1,000 and above; flag small products per product | Stories |

### 14.2 Clarifications (new in v0.2)

Gaps found while auditing requirement coverage (CL-01 – CL-09 in v0.2, CL-10 – CL-13 in v0.3, CL-14 – CL-15 in v0.4, CL-16 in v0.5, and CL-17 – CL-20 in v0.7). Each approved clarification states its default, and dependent criteria reference the CL ID. CL-01 – CL-13 were approved on 2026-10-12; CL-14 – CL-16 on 2026-10-13; CL-17 – CL-20 on 2026-10-20.

| ID | Requirement(s) | Gap | Approved default | Needed by |
|---|---|---|---|---|
| CL-01 | FR-017, FR-020, FR-022, FR-081 | R1 requires rating display and rating sort, but review submission is R2 | R1 shows aggregates from seeded reviews (read-only); the review list and recomputation arrive with FR-081 in R2 | ERD |
| CL-02 | FR-084, FR-085, FR-088, FR-089 | No error contract for duplicate SKU, slug, variant option set or category slug | 409 `DUPLICATE_RESOURCE` | Architecture |
| CL-03 | FR-084, FR-088, FR-090 | How initial stock and variant edits interact with the inventory ledger (BR-042) | Initial stock is recorded as an `initial_stock` movement; stock changes only through inventory adjustment (FR-090) | ERD |
| CL-04 | FR-091 | Admin order list: default sort, pagination and date semantics unspecified | Newest first; BR-016 pagination; inclusive UTC dates; email = case-insensitive partial match; order number exact | Stories |
| CL-05 | FR-064 | Timing of reservation-expiry processing unspecified (affects testability) | The deadline is placement time + the reservation window. Expiry is applied by a periodic job within 60 s of the deadline; in addition, any operation that holds the order lock and finds a `pending` order past its deadline applies the expiry transition first, so a payment is never accepted after the deadline (payment then returns 409 `ORDER_NOT_PAYABLE` with no attempt recorded, BR-069 step 4). Reads do not mutate state, so an overdue order may read `pending` for up to 60 s. Test-support can trigger expiry deterministically *(amended v0.3)* | Architecture |
| CL-06 | FR-049 | Source and wording of delivery estimates | Static configuration strings: Standard "3–5 business days", Express "1–2 business days" | Stories |
| CL-07 | FR-016 | Whether a parent category lists the products of its subcategories | Yes, all descendants | Stories |
| CL-08 | FR-006, FR-083 | UI behaviour when a signed-in customer opens an admin route | Forbidden page (not a redirect); the API returns 403 | Stories |
| CL-09 | FR-094 | Length limits for the admin cancellation reason | Same as BR-062: 1–200 characters | Stories |
| CL-10 | FR-073, BR-053, BR-073 | In R2, a customer cancellation that reaches an order after payment approval has already committed (it was meant for a pending order): cancel the now-paid order, or reject? *(new v0.3)* | Process it as a paid-order cancellation under BR-055 (stock restored once, one refund); no expected-status precondition on the cancel request. Alternative: require the client to send the status it saw and return a new 409 code on mismatch. R1 is unaffected (409 `ORDER_NOT_CANCELLABLE`, DEC-26) | Stories |
| CL-11 | FR-090, BR-042, BR-062 | Inventory-adjustment contract: request shape, ledger representation of absolute adjustments, adjustment reference, zero-delta handling and error status for a negative result *(new v0.3)* | Exactly one of `delta` (non-zero integer) or `set_to` (non-negative integer) plus `reason` (1–200 characters); absolute mode computes delta = `set_to` − stock under a row lock and writes one movement with that delta; movement reason code `admin_adjustment` plus the admin's reason text; reference = the adjustment request id; a zero-delta request → 422; a negative result → 422 `VALIDATION_ERROR` | ERD |
| CL-12 | FR-067, FR-069, FR-092 | Which payment-attempt fields are exposed to which API consumers *(new v0.3)* | Customer payment response: `order_id`, `attempt_number`, `status`, `amount`, `created_at`; the idempotency key is stored but not returned to customers; admin payment inspection (FR-092, R2) shows all fields including the key | Architecture |
| CL-13 | FR-017, BR-012 | Product-level availability when active variants differ (BR-012 defines variant states and only the all-out-of-stock product state) *(new v0.3)* | `in_stock` if any active variant is `in_stock`; otherwise `low_stock` if any is `low_stock`; otherwise `out_of_stock` | Stories |
| CL-14 | BR-028, FR-050 | Owner statement (2026-10-13), recorded as written: "your first order if its between exactly under 1000 and 250 . we dont ship products under that price {we ship more than three if its small products , this rule only applies to small products only}". It is not specific enough to implement. It seems to describe a first-order shipping offer plus a minimum shippable order value of R250 with a quantity exception for small products, but "first order", "small products", the scope of the R250 minimum and the effect on the approved R1,000 free-shipping rule are undefined *(new v0.4)* | **Approved 2026-10-13.** Owner answers: small products are marked by category and the category is Wearables and Audio; a first order (earliest non-cancelled) with a subtotal from R250 up to under R1,000 ships Standard free; Standard R60 and Express R120 on orders above R1,000; an order under R250 is blocked unless it has more than three small-goods units; the minimum is checked on the pre-discount subtotal. Implemented as DEC-29, BR-028, BR-076 and BR-077; consequences the owner did not state: CL-16 | Stories |
| CL-15 | BR-026, §8.3 | `ONCE1` is now a percentage coupon (DEC-28) but no percentage or maximum discount was given *(new v0.4)* | **Approved 2026-10-13:** 5%, maximum discount R50.00, no minimum order | Stories |
| CL-16 | BR-028, BR-076, BR-077 | Consequences of the owner's CL-14 answers that the owner did not state *(new v0.5)* | **Approved 2026-10-13.** Owner confirmed: Standard R60 and Express R120, Express always R120; free Standard shipping only for a customer's first non-cancelled order with a pre-coupon subtotal of R250 or more and under R1,000; returning customers always pay R60 Standard and first-time customers at R1,000 or more also pay R60; the minimum order uses the pre-coupon subtotal and needs four or more small-goods units to be waived; the exception waives only the minimum and grants no free shipping; coupons never change eligibility (a R900 first order with `SAVE100` still ships free); `WELCOME10` users are returning and pay R60 Standard; first-order status excludes cancelled orders and the order being placed | Stories |
| CL-17 | FR-008, BR-005 | The PRD required token invalidation after a password change but did not define the customer-facing outcome *(new v0.7)* | **Approved 2026-10-20.** A successful password change revokes all previously issued tokens; the UI confirms the change and redirects the customer to login; the customer must authenticate again with the new password. | Stories / Architecture |
| CL-18 | FR-112, BR-041 | The PRD did not define how the reservation deadline and route back to a pending order are displayed *(new v0.7)* | **Approved 2026-10-20.** While a reservation is active, the payment page and order detail display “Reserved until [time]”; the cart and checkout entry show a pending-order banner with “Pay now” and “Cancel order”; order detail offers a “Pay now” route. The reservation remains placement time plus the existing 30-minute window; the display does not extend it. | Stories / Architecture |
| CL-19 | FR-072, FR-073, FR-094, CL-09 | Customer cancellation reason requirements were unspecified; administrator reason is already defined by FR-094 and CL-09 *(new v0.7)* | **Approved 2026-10-20.** Customers do not need to provide a reason when cancelling eligible unpaid pending (R1) or confirmed paid (R2) orders. Administrator cancellation still requires a 1–200 character reason. | Stories |
| CL-20 | FR-005, BR-005 | The PRD did not define whether the UI warns before token expiry *(new v0.7)* | **Approved 2026-10-20.** Five minutes before access-token expiry, the UI displays and announces “Your session is about to expire.” This is informational only and does not refresh, renew or extend the token. On expiry, existing FR-005 redirect-to-login and return-to-destination behaviour applies. | Stories / Architecture / SDET tests |

## 15. Definition of done

**Planning document (this PRD).** All decisions DEC-01–DEC-29 and all clarifications CL-01–CL-20 are approved by the owner (DEC-01–DEC-27 and CL-01–CL-13 on 2026-10-12; DEC-28, DEC-29 and CL-14–CL-16 on 2026-10-13; CL-17–CL-20 on 2026-10-20; no item is pending); IDs unique and consistent; every **M** requirement has at least one acceptance criterion (Appendix D); no further planning document is started before that approval; no real payment, email verification or OTP introduced; stack unchanged; owner has approved the version.

**Requirement / feature.** A requirement is **Verified** only when: (1) code reviewed and merged; (2) database migration included, reversible where feasible, and applied cleanly; (3) business rules implemented in the service layer; (4) acceptance criteria automated at the planned layers (UI/API/DB) with meaningful assertions, none weakened to pass; (5) OpenAPI and error catalogue updated; (6) lint, formatting and type checks pass; (7) CI is green with reports, traces and screenshots retained for failures; (8) no open Critical/High defects against it; (9) seed/fixtures updated; (10) status updated in the traceability matrix.

**Release.** All **M** requirements of the release Verified; MET-01 – MET-05 and MET-08 met; clean-clone setup verified (MET-06); known defects and deferred items documented; planning documents reconciled with the delivered behaviour.

---

## Appendix A — Error envelope and code catalogue

```json
{ "error": { "code": "INSUFFICIENT_STOCK", "message": "Only 2 units available.",
             "details": [ { "field": "quantity", "available": 2 } ], "request_id": "…" } }
```

| HTTP | Codes |
|---|---|
| 401 | `UNAUTHENTICATED`, `TOKEN_EXPIRED`, `INVALID_CREDENTIALS` |
| 403 | `FORBIDDEN`, `REVIEW_NOT_ELIGIBLE` |
| 404 | `NOT_FOUND` (also used for non-owned resources) |
| 409 | `EMAIL_ALREADY_REGISTERED`, `INSUFFICIENT_STOCK`, `PRICE_CHANGED`, `PRODUCT_UNAVAILABLE`, `CART_EMPTY`, `WISHLIST_DUPLICATE`, `REVIEW_DUPLICATE`, `ADDRESS_LIMIT_REACHED`, `ORDER_NOT_CANCELLABLE`, `INVALID_STATUS_TRANSITION`, `ORDER_ALREADY_PAID`, `PAYMENT_ATTEMPTS_EXHAUSTED`, `CATEGORY_NOT_EMPTY`, `ORDER_NOT_PAYABLE`, `CHECKOUT_ALREADY_PENDING`, `CART_LOCKED`, `DUPLICATE_RESOURCE` (CL-02), `ORDER_BELOW_MINIMUM` |
| 422 | `VALIDATION_ERROR`, `INVALID_CURRENT_PASSWORD`, `COUPON_NOT_FOUND`, `COUPON_NOT_ACTIVE`, `COUPON_EXPIRED`, `COUPON_MIN_ORDER_NOT_MET`, `COUPON_USAGE_LIMIT_REACHED`, `COUPON_NOT_ELIGIBLE`, `IDEMPOTENCY_KEY_REQUIRED`, `IDEMPOTENCY_KEY_REUSED` |
| 429 | `RATE_LIMITED` |
| 503 | `NOT_READY` (readiness endpoint) |

Exact status-code mapping may be refined in the architecture document; codes are stable once approved. The order-placement contract (which code for which precondition, and in which order) is BR-074. New in v0.2: `ORDER_NOT_PAYABLE`, `CHECKOUT_ALREADY_PENDING`, `CART_LOCKED`, `DUPLICATE_RESOURCE`. v0.3 clarifies usage without adding codes: `CHECKOUT_ALREADY_PENDING` is returned at BR-074 step 5 (after the idempotency and schema checks, before address, cart, stock, coupon and total checks); `ORDER_NOT_PAYABLE` is also returned when a payment finds the reservation deadline elapsed (expiry is applied first) or the order cancelled during a simulated delay, with no attempt recorded; `VALIDATION_ERROR` also covers invalid inventory adjustments (CL-11). New in v0.4: `COUPON_NOT_ELIGIBLE` (422, BR-075). New in v0.5: `ORDER_BELOW_MINIMUM` (409, BR-077).

## Appendix B — Traceability of the brief's core risks (§5 of `PROJECT_BRIEF.md`)

| Brief risk | Requirements and rules | Acceptance criteria |
|---|---|---|
| Clients cannot set authoritative prices, discounts, stock or totals | FR-039, FR-054, BR-020, BR-022, SEC-008 | AC-025, AC-027 |
| Quantity positive and ≤ stock | FR-035, BR-018, BR-037 | AC-024 |
| Inventory never negative, including concurrency | BR-037–039, NFR-006, NFR-009 | AC-047, AC-049 |
| Failed/timed-out/error payment never confirms an order | FR-059–061, FR-114, BR-045, BR-047, BR-069, BR-073 | AC-039–041, AC-057, AC-082, AC-084, AC-105 – AC-107 |
| Repeated checkout/payment never duplicates | FR-056, FR-063, FR-067, FR-110, FR-111, FR-115, BR-046, BR-048, BR-068 – BR-071, BR-074 | AC-042, AC-043, AC-078, AC-083, AC-113, AC-114 |
| Coupon rules validated on the server | FR-048, BR-030–036, BR-075 | AC-032–035, AC-087, AC-115, AC-116 |
| Cancellation only in eligible states | FR-072, FR-073, BR-053 | AC-053, AC-075 |
| Eligible cancellation restores stock and triggers refund state | FR-072–075, FR-109, BR-040, BR-054–056 | AC-052, AC-054, AC-055, AC-074 |
| Customer data scoped to the customer | FR-014, FR-045, BR-064, SEC-006 | AC-029, AC-050, AC-062 |
| Admin endpoints require the correct role | FR-083, BR-065, SEC-007 | AC-061, AC-090 |
| Records stay consistent on failure/rollback | FR-055, BR-038, BR-068, BR-069, BR-073, NFR-005 | AC-045, AC-082, AC-105 – AC-107 |

## Appendix C — Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-10 | Initial draft for review; no decisions approved yet |
| 0.2 | 2026-10-11 | Release reconciliation (FR-075/AC-054 split; FR-109, AC-074, AC-075, DEC-26); checkout and cart lifecycle (FR-110 – FR-115, BR-068 – BR-074, §8.4, DEC-25); corrected OBJ-04 and re-verified all objective references; added AC-074 – AC-104 closing every Must-level coverage gap (Appendix D); split AC-037 into AC-037/AC-076/AC-077 with explicit status and error codes; reconciled registration (FR-001, WF-01, AC-001, AC-088, DEC-27); added Rel column to acceptance criteria; clarified FR-037 and BR-065/DEC-19; added clarifications CL-01 – CL-09, new error codes and RSK-14. No existing ID renumbered or removed; no decision approved |
| 0.3 | 2026-10-12 | Correction A: DoD (§15) now covers DEC-01 – DEC-27 and CL-01 – CL-13. Correction B: single 12-step placement validation order (BR-074) with the pending-order check at step 5 before address, cart, stock, coupon and total checks; amended FR-052, FR-054, FR-056, FR-111, FR-115, BR-068, BR-070, BR-071, AC-037, AC-042, AC-076 – AC-078; new AC-114. Correction C: payment, cancellation and expiry contract during the simulated delay (BR-069, BR-073 and its Race outcomes table, BR-041, BR-047, FR-060, FR-064, FR-114, CL-05, TR-006, WF-07); AC-084 rewritten; new AC-105 – AC-108; CL-10. Correction D: AC-034 rewritten for two distinct customers. Correction E: new AC-109 (FR-017), AC-110/AC-111 (FR-069), AC-112 (FR-086), AC-113 (FR-067); AC-064 (FR-090) rewritten for both modes; new CL-11 – CL-13; clause-level assertions added to AC-009, AC-013, AC-018, AC-021, AC-036, AC-038, AC-039, AC-060. Appendix B and D recomputed. No existing ID renumbered or removed; no decision or clarification approved; no requirement marked Implemented or Verified |
| 0.3 (approval record) | 2026-10-12 | Owner approved all decisions DEC-01 – DEC-27 and clarifications CL-01 – CL-13 ("approve all"). Status changed from Not approved to Approved; wording that described items as proposed or pending was updated. No requirement, rule, acceptance criterion or identifier changed; the document version stays 0.3 |
| 0.3 (confirmation record) | 2026-10-12 | Owner explicitly confirmed the BR-028 shipping fees (Standard R60.00, Express R120.00) under DEC-07. No requirement, rule, acceptance criterion or identifier changed; the document version stays 0.3 |
| 0.3 (confirmation record) | 2026-10-12 | Owner explicitly confirmed the order-handling values: 30-minute stock hold (BR-041), up to 3 payment attempts (BR-049), maximum 10 units per cart line (BR-018). No requirement, rule, acceptance criterion or identifier changed; the document version stays 0.3 |
| 0.4 | 2026-10-13 | Owner answers applied. Coupons (DEC-28, approved): `WELCOME10` restricted to returning customers (BR-075, new code `COUPON_NOT_ELIGIBLE`, AC-115); `SAVE100` minimum R800 made exclusive (BR-033, T-11, T-12, AC-116); `ONCE1` becomes a percentage coupon with limits unchanged (value: CL-15); seeded-customer eligibility in TR-003; AC-032, AC-033, AC-104, AC-110 adjusted. DEC-04 unchanged: silent refresh considered and not adopted. New CL-14 (shipping and minimum-order statement) and CL-15 (`ONCE1` percentage) are pending; the approved shipping rule (BR-028) is unchanged. No existing ID renumbered or removed |
| 0.4 (confirmation record) | 2026-10-13 | Owner answers: small products are identified by category (CL-14 item e; the categories are not yet named); the `ONCE1` percentage is 5% (CL-15; the R50.00 cap and no minimum await confirmation). Seed table §8.3 updated. No identifier, requirement, rule or acceptance criterion changed; the document version stays 0.4 |
| 0.5 | 2026-10-13 | Owner answers on shipping and minimum order applied (DEC-29, approved): Standard R60 / Express R120; Standard free only for a first order (earliest non-cancelled) with a pre-discount subtotal from R250 up to under R1,000, so the earlier "free at R1,000" rule is withdrawn (BR-028, new BR-076, FR-049, FR-050); minimum order of R250 unless more than three small-goods units, small goods = Wearables and Audio (new BR-077, FR-116, `ORDER_BELOW_MINIMUM`, category designation in §5.2, fixtures, config keys); worked totals rebuilt (T-01 – T-17, customer column); AC-032, AC-036, AC-095, AC-098, AC-114 adjusted; new AC-117, AC-118. CL-14 and CL-15 resolved (`ONCE1` = 5%, cap R50.00, no minimum); new CL-16 (derived shipping consequences) pending. No existing ID renumbered or removed |
| 0.6 | 2026-10-13 | Owner confirmed all five CL-16 points and three further statements; CL-16 closed (approved) and the PRD is the approved baseline with no open items. Documented explicitly: the small-goods exception waives only the minimum order and grants no free shipping (BR-077, BR-076, FR-116, T-14); `WELCOME10` customers are returning and pay R60.00 Standard (BR-075, BR-076, AC-117); first-order status excludes cancelled orders and the order being placed (BR-076, AC-117); both the minimum and the free-shipping band use the pre-coupon subtotal (BR-076, BR-077). AC-036, AC-117 and AC-118 reworded. No new IDs; no existing ID renumbered or removed; version label changed to 0.6 (approved baseline) |
| 0.7 | 2026-10-20 | Owner-approved clarifications CL-17–CL-20: require login after password change; show reservation deadline and Pay Now route for pending orders; customer cancellation reasons are not required while administrator reasons remain required; display and announce “Your session is about to expire” five minutes before token expiry without extending the session. FR-005, FR-008, FR-072, FR-073, FR-112 and AC-009 amended; AC-119–AC-121 added; no existing identifier renumbered or removed. |

## Appendix D — Traceability audit and consistency review (v0.6)

Recomputed in v0.6 from the actual requirement and acceptance-criterion tables of this document (ID resolution, uniqueness, coverage and release consistency were re-verified by script; clause-level review is manual).

### D.1 Objective → acceptance-criterion check

| Objective | Referenced acceptance criteria | Subject of each criterion | Result |
|---|---|---|---|
| OBJ-01 | AC-038, AC-104, MET-07 | AC-038: approved checkout; AC-104: end-to-end journey | Correct |
| OBJ-02 | AC-025, AC-027, AC-032 | AC-025: server-side money; AC-027: stale price; AC-032: worked totals | Correct |
| OBJ-03 | AC-045 – AC-047, AC-049, AC-034, AC-054, AC-074, AC-078, AC-082, AC-084, AC-105 – AC-107 | AC-034: coupon concurrency (two customers); AC-045: rollback; AC-047: oversell concurrency; AC-049: ledger reconciliation; AC-054: unpaid cancellation concurrency; AC-074: paid cancellation concurrency; AC-078: duplicate checkout / precedence; AC-082: payment-failure transaction boundary; AC-084: payment vs cancel/expiry; AC-105: expiry during delay; AC-107: approval wins | Correct; extended in v0.3 (AC-034, AC-105 – AC-107) |
| OBJ-04 | AC-010, AC-011, AC-061, AC-062, AC-090 | AC-010: no role escalation; AC-011: token tampering; AC-061: admin-route authorization; AC-062: ownership isolation; AC-090: admin cannot shop | Correct (corrected in v0.2) |
| OBJ-05 | MET-04 | Metric references only | Correct |
| OBJ-06 | TR-001 – TR-023, AC-067 – AC-069 | AC-067: health; AC-069: test-hook guard | Correct |
| OBJ-07 | MET-02, MET-05 | Metric references only | Correct |
| OBJ-08 | MET-01, MET-09 | Metric references only | Correct |

### D.2 Must-level functional requirement → acceptance-criterion matrix

**Mapping coverage (recomputed in v0.6):** 105 Must-level functional requirements; **105 map to at least one acceptance criterion; 0 are unmapped.** (v0.1: 33 of 97 unmapped; v0.2 – v0.5: 0 of 104–105 unmapped.)

**Mapping is not the same as clause-level assertion.** A requirement can be linked to a criterion that asserts only part of what it says. The "Assertion depth" column records the result of the manual clause-by-clause review (v0.3, extended to the coupon changes in v0.4 and the shipping changes in v0.5 and the clarifications of v0.6): requirements marked *Strengthened* had clauses with no explicit assertion (FR-017, FR-067, FR-069, FR-086, FR-090) or an under-specified contract (FR-111, FR-114, FR-115); *Clause gap closed* marks smaller clauses now asserted; the rest were read against their criteria and no unasserted clause was found. That last statement is a reviewer judgement, not a mechanical proof. Where behaviour is unresolved, the criterion asserts only the supported part and cites a DEC/CL item.

| FR | Rel | Acceptance criteria | Assertion depth | Open item |
|---|---|---|---|---|
| FR-001 | R1 | AC-001, AC-088, AC-104 | Mapped; no clause gap found | DEC-27 |
| FR-002 | R1 | AC-002 | Mapped; no clause gap found | — |
| FR-003 | R1 | AC-004, AC-005, AC-088 | Mapped; no clause gap found | — |
| FR-004 | R1 | AC-006 | Mapped; no clause gap found | — |
| FR-005 | R1 | AC-007, AC-119 | Strengthened in v0.7: AC-119 | CL-20 |
| FR-006 | R1 | AC-089 | Mapped; no clause gap found | CL-08 |
| FR-007 | R1 | AC-089 | Mapped; no clause gap found | — |
| FR-008 | R1 | AC-009 | Clause gap closed in v0.3: AC-009 | — |
| FR-010 | R1 | AC-010, AC-090 | Mapped; no clause gap found | — |
| FR-011 | R1 | AC-091 | Mapped; no clause gap found | — |
| FR-012 | R1 | AC-013 | Clause gap closed in v0.3: AC-013 | — |
| FR-013 | R1 | AC-091 | Mapped; no clause gap found | — |
| FR-014 | R1 | AC-062, AC-091 | Mapped; no clause gap found | — |
| FR-015 | R1 | AC-014 | Mapped; no clause gap found | — |
| FR-016 | R1 | AC-092 | Mapped; no clause gap found | CL-07 |
| FR-017 | R1 | AC-015, AC-109 | Strengthened in v0.3: AC-109 | CL-01, CL-13 |
| FR-018 | R1 | AC-016, AC-104 | Mapped; no clause gap found | — |
| FR-019 | R1 | AC-017 | Mapped; no clause gap found | — |
| FR-020 | R1 | AC-018 | Clause gap closed in v0.3: AC-018 | CL-01 |
| FR-021 | R1 | AC-015 | Mapped; no clause gap found | — |
| FR-022 | R1 | AC-092 | Mapped; no clause gap found | CL-01 |
| FR-023 | R1 | AC-021 | Clause gap closed in v0.3: AC-021 | — |
| FR-024 | R1 | AC-019 | Mapped; no clause gap found | — |
| FR-025 | R1 | AC-020, AC-109 | Mapped; no clause gap found | — |
| FR-026 | R1 | AC-016 | Mapped; no clause gap found | — |
| FR-028 | R1 | AC-022 | Mapped; no clause gap found | — |
| FR-029 | R1 | AC-092 | Mapped; no clause gap found | — |
| FR-031 | R1 | AC-026 | Mapped; no clause gap found | — |
| FR-032 | R1 | AC-023, AC-104 | Mapped; no clause gap found | — |
| FR-033 | R1 | AC-093 | Mapped; no clause gap found | — |
| FR-034 | R1 | AC-093 | Mapped; no clause gap found | — |
| FR-035 | R1 | AC-024 | Mapped; no clause gap found | — |
| FR-036 | R1 | AC-025, AC-032 | Mapped; no clause gap found | — |
| FR-037 | R1 | AC-027, AC-076, AC-112 | Mapped; no clause gap found | — |
| FR-038 | R1 | AC-028 | Mapped; no clause gap found | — |
| FR-039 | R1 | AC-025 | Mapped; no clause gap found | — |
| FR-041 | R1 | AC-030 | Mapped; no clause gap found | — |
| FR-042 | R1 | AC-094 | Mapped; no clause gap found | — |
| FR-043 | R1 | AC-094 | Mapped; no clause gap found | — |
| FR-044 | R1 | AC-031 | Mapped; no clause gap found | — |
| FR-045 | R1 | AC-029, AC-094 | Mapped; no clause gap found | — |
| FR-046 | R1 | AC-033, AC-104, AC-115, AC-116 | Clause gap closed in v0.3: AC-115, AC-116 | — |
| FR-047 | R1 | AC-095 | Mapped; no clause gap found | — |
| FR-048 | R1 | AC-033, AC-034, AC-087, AC-115, AC-116 | Clause gap closed in v0.3: AC-034, AC-115 | — |
| FR-049 | R1 | AC-036, AC-117 | Clause gap closed in v0.3: AC-036, AC-117 | CL-06 |
| FR-050 | R1 | AC-032, AC-036, AC-117 | Clause gap closed in v0.3: AC-036, AC-117 | DEC-29, CL-16 (approved) |
| FR-051 | R1 | AC-068 | Mapped; no clause gap found | — |
| FR-052 | R1 | AC-037, AC-076, AC-077, AC-104 | Mapped; no clause gap found | — |
| FR-053 | R1 | AC-032 | Mapped; no clause gap found | — |
| FR-054 | R1 | AC-027, AC-087 | Mapped; no clause gap found | — |
| FR-055 | R1 | AC-045 | Mapped; no clause gap found | — |
| FR-056 | R1 | AC-042, AC-078, AC-083 | Clause gap closed in v0.3: AC-042 | — |
| FR-057 | R1 | AC-038, AC-039, AC-040, AC-041, AC-086 | Mapped; no clause gap found | — |
| FR-058 | R1 | AC-038, AC-080, AC-104, AC-107 | Mapped; no clause gap found | — |
| FR-059 | R1 | AC-039, AC-082 | Mapped; no clause gap found | — |
| FR-060 | R1 | AC-040, AC-082, AC-105, AC-106 | Clause gap closed in v0.3: AC-105, AC-106 | — |
| FR-061 | R1 | AC-041, AC-082 | Mapped; no clause gap found | — |
| FR-062 | R1 | AC-044, AC-113 | Mapped; no clause gap found | — |
| FR-063 | R1 | AC-043, AC-083, AC-113 | Mapped; no clause gap found | — |
| FR-064 | R1 | AC-046, AC-081, AC-084, AC-105, AC-107 | Clause gap closed in v0.3: AC-084, AC-105 | CL-05 |
| FR-065 | R1 | AC-038, AC-039, AC-104, AC-113 | Clause gap closed in v0.3: AC-038, AC-039 | — |
| FR-066 | R1 | AC-048 | Mapped; no clause gap found | — |
| FR-067 | R1 | AC-038, AC-039, AC-040, AC-041, AC-113 | Strengthened in v0.3: AC-113 | CL-12 |
| FR-068 | R1 | AC-050, AC-104, AC-110 | Mapped; no clause gap found | — |
| FR-069 | R1 | AC-050, AC-051, AC-110, AC-111 | Strengthened in v0.3: AC-110, AC-111 | CL-12 |
| FR-070 | R1 | AC-096 | Mapped; no clause gap found | — |
| FR-071 | R1 | AC-056, AC-085 | Mapped; no clause gap found | — |
| FR-072 | R1 | AC-054, AC-055, AC-075, AC-081, AC-106, AC-107, AC-121 | Strengthened in v0.7: AC-121 | DEC-26, CL-19 |
| FR-073 | R2 | AC-052, AC-108, AC-111, AC-121 | Strengthened in v0.7: AC-121 | DEC-26, CL-10, CL-19 |
| FR-074 | R2 | AC-052, AC-111 | Mapped; no clause gap found | — |
| FR-075 | R1 | AC-054, AC-106 | Mapped; no clause gap found | — |
| FR-076 | R1 | AC-097, AC-110 | Mapped; no clause gap found | — |
| FR-077 | R2 | AC-058 | Mapped; no clause gap found | — |
| FR-078 | R2 | AC-058 | Mapped; no clause gap found | — |
| FR-079 | R2 | AC-059 | Mapped; no clause gap found | — |
| FR-080 | R2 | AC-059 | Mapped; no clause gap found | — |
| FR-081 | R2 | AC-060 | Clause gap closed in v0.3: AC-060 | CL-01 |
| FR-083 | R2 | AC-061 | Mapped; no clause gap found | CL-08 |
| FR-084 | R2 | AC-099 | Mapped; no clause gap found | CL-02, CL-03 |
| FR-085 | R2 | AC-099 | Mapped; no clause gap found | CL-02 |
| FR-086 | R2 | AC-063, AC-112 | Strengthened in v0.3: AC-112 (and AC-063) | — |
| FR-087 | R2 | AC-099 | Mapped; no clause gap found | — |
| FR-088 | R2 | AC-100 | Mapped; no clause gap found | CL-02, CL-03 |
| FR-089 | R2 | AC-065, AC-100 | Mapped; no clause gap found | CL-02 |
| FR-090 | R2 | AC-064 | Strengthened in v0.3: AC-064 (both modes) | CL-03, CL-11 |
| FR-091 | R2 | AC-101 | Mapped; no clause gap found | CL-04 |
| FR-092 | R2 | AC-101 | Mapped; no clause gap found | — |
| FR-093 | R2 | AC-056 | Mapped; no clause gap found | — |
| FR-094 | R2 | AC-102, AC-121 | Strengthened in v0.7: AC-121 | CL-09, CL-19 |
| FR-095 | R2 | AC-103 | Mapped; no clause gap found | — |
| FR-096 | R2 | AC-063, AC-112 | Mapped; no clause gap found | — |
| FR-103 | R1 | AC-067 | Mapped; no clause gap found | — |
| FR-104 | R1 | AC-068 | Mapped; no clause gap found | — |
| FR-105 | R1 | AC-069 | Mapped; no clause gap found | — |
| FR-106 | R1 | AC-071 | Mapped; no clause gap found | — |
| FR-107 | R1 | AC-098 | Mapped; no clause gap found | — |
| FR-108 | R1 | AC-070 | Mapped; no clause gap found | — |
| FR-109 | R2 | AC-074, AC-108 | Mapped; no clause gap found | CL-10 |
| FR-110 | R1 | AC-082 | Mapped; no clause gap found | — |
| FR-111 | R1 | AC-078, AC-114 | Strengthened in v0.3: AC-078, AC-114 | DEC-25 |
| FR-112 | R1 | AC-079, AC-120 | Strengthened in v0.7: AC-120 | DEC-25, CL-18 |
| FR-113 | R1 | AC-080, AC-081 | Mapped; no clause gap found | DEC-25 |
| FR-114 | R1 | AC-084, AC-105, AC-106, AC-107 | Strengthened in v0.3: AC-084, AC-105 – AC-107 | — |
| FR-115 | R1 | AC-037, AC-076, AC-077, AC-078, AC-114 | Strengthened in v0.3: AC-114 | — |
| FR-116 | R1 | AC-117, AC-118 | Clause gap closed in v0.3: AC-118 | DEC-29 |

### D.3 Business-rule coverage

All 77 business rules (BR-001 – BR-077) are referenced by at least one acceptance criterion. As with D.2, this shows mapping, not that every sentence of every rule is separately asserted; the multi-part rules BR-069, BR-073 and BR-074 are exercised by AC-082, AC-084, AC-105 – AC-107 and AC-114.

### D.4 Release-consistency checks

| Check | Result |
|---|---|
| Acceptance criteria by release | R1: 98; R2: 19; R3: 1; total 118 |
| Criteria verifying a functional requirement of a later release than their own Rel | 0 |
| R1 Must requirements without any R1 criterion | 0 |
| Paid-order split | R1: cancellation of unpaid pending orders (FR-072, FR-075, AC-054, AC-055, AC-075); R2: paid cancellation and refunds (FR-073, FR-074, FR-109, AC-052, AC-074, AC-108, AC-111) |

### D.5 Consistency findings and resolutions

**Findings resolved in v0.2**

| # | Finding | Resolution |
|---|---|---|
| F-01 | OBJ-04 cited review criteria (AC-059/AC-060) instead of access-control criteria | OBJ-04 → AC-010, AC-011, AC-061, AC-062, AC-090; all other objectives re-checked (D.1) |
| F-02 | FR-075 (R1) and AC-054 mixed unpaid cancellation with refunds, which are R2 | FR-075/AC-054 limited to unpaid pending orders (R1); new FR-109/AC-074 for paid orders (R2); AC-035 narrowed to the unpaid case and its paid half moved into AC-052; stock-restoration and concurrency checks preserved in both |
| F-03 | BR-053 let customers cancel `confirmed` orders although FR-073 is R2 | Release notes on BR-053 and FR-072; AC-075 for R1; DEC-26 added |
| F-04 | FR-037 treated a price change as blocking, while BR-022 resolves it through `expected_total` | `price_changed` is informational; blocking flags are `unavailable`, `out_of_stock`, `insufficient_stock`; AC-027 and AC-076 distinguish them |
| F-05 | AC-037 combined three failures with unspecified codes ("409 or 422") | Split into AC-037 (empty cart, 409 `CART_EMPTY`), AC-076 (409 `PRODUCT_UNAVAILABLE` / `INSUFFICIENT_STOCK`), AC-077 (422 `VALIDATION_ERROR` / 404 `NOT_FOUND`); contract in BR-074 and Appendix A |
| F-06 | WF-01 said registration signs the user in; FR-001/AC-001 were silent | FR-001, WF-01, AC-001 and AC-088 aligned: 201 + user, no token; UI signs in via login; DEC-27 |
| F-07 | WF-06 described placement and payment as one atomic step; transaction boundaries, retries and idempotency scope were undefined | Two operations with separate transactions and scopes (FR-110, BR-068 – BR-070); WF-06/WF-07 rewritten; AC-082, AC-083 |
| F-08 | A different idempotency key could create a second order from the same cart | One pending order per customer, cart lock, `CHECKOUT_ALREADY_PENDING` (FR-111/FR-112, BR-071, AC-078, AC-079, DEC-25) |
| F-09 | Cart behaviour after approval, cancellation and expiry was only partly stated | BR-072 lifecycle table; FR-113; AC-080, AC-081; FR-058/FR-064 amended |
| F-10 | FR-017/FR-020/FR-022 (R1) need ratings while review submission is R2 | CL-01 (seeded read-only aggregates in R1); FR-081 and DEC-01 amended |
| F-11 | AC-056 verified R1 requirement FR-071 only through R2 admin transitions | AC-085 added for R1 enforcement; AC-056 is R2 |
| F-12 | AC-061 bundled an R1-testable check (admin cannot shop) into an R2 criterion | Moved to AC-090 (R1); AC-061 is R2 |
| F-13 | BR-065/DEC-19 omitted addresses and own-order operations that the §10.2 matrix denies to admins | BR-065 and DEC-19 aligned with §10.2 |
| F-14 | Reservation expiry timing was untestable | CL-05 (60 s bound, always before payment evaluation, deterministic trigger); AC-046 amended |
| F-15 | Payment against a cancelled/expired order had no error code | `ORDER_NOT_PAYABLE` (FR-114, BR-049, BR-073, AC-084, AC-085) |
| F-16 | 33 Must FRs and 9 BRs lacked acceptance criteria | D.2/D.3: 100% mapped; AC-074 – AC-104 added |
| F-17 | Error catalogue lacked codes for the new cases | Appendix A updated (4 codes) |
| F-18 | Acceptance criteria carried no release attribution | Rel column added to all ACs |

**Findings resolved in v0.3**

| # | Finding | Resolution |
|---|---|---|
| F-19 | BR-071 said any further placement returns `CHECKOUT_ALREADY_PENDING` "whatever its key or payload", but BR-074 validated schema and address before checking for a pending order | Single 12-step order in BR-074: key and replay first, schema, then the pending-order check (step 5), then address, cart, stock, coupon, total; BR-071, BR-068, BR-070, FR-052, FR-054, FR-056, FR-111, FR-115, Appendix A aligned |
| F-20 | AC-037, AC-076 and AC-077 did not state a no-pending-order precondition; AC-078 did not assert the precedence over address and other checks | Preconditions added; AC-078 extended; new AC-114 exercises each adjacent pair of steps; AC-042 asserts legitimate replay while pending/paid/cancelled |
| F-21 | BR-069 held no lock during the simulated delay but did not define cancellation or expiry arriving during it | BR-069 sequenced (delay, then lock and re-read, then eligibility); BR-073 rewritten with a Race outcomes table; FR-060, FR-064, FR-114 amended; AC-084 rewritten; new AC-105, AC-106, AC-107 |
| F-22 | CL-05 (expiry within 60 s) could be read as leaving a window in which payment is accepted after the deadline | CL-05 amended: the deadline is authoritative; any lock-holding operation applies expiry first; BR-041, BR-069 step 4 and AC-084(b) enforce it |
| F-23 | R2 behaviour of a customer cancellation that loses a race to payment approval is undefined (cancel the paid order, or reject) | New CL-10 (pending); R1 behaviour fixed by DEC-26; AC-108 asserts invariants only |
| F-24 | AC-034 did not require distinct customers, so the one-pending-order rule could mask the coupon behaviour | AC-034 rewritten: two distinct customers, separate carts, unused global limit; loser returns 422 `COUPON_USAGE_LIMIT_REACHED`; database assertions on usage, order, stock and ledger |
| F-25 | Mapping hid clause gaps for FR-017, FR-067, FR-069, FR-086 and FR-090 | New AC-109, AC-110, AC-111, AC-112, AC-113; AC-064 rewritten for delta and absolute modes; Appendix D now separates mapping from assertion depth |
| F-26 | Smaller clause gaps: FR-008 (new = current password), FR-012 (first address default), FR-020 (`price_desc`), FR-023 (disabled options), FR-049 (fee and estimate), FR-065 (confirmation content), FR-081 (review list) | Assertions added to AC-009, AC-013, AC-018, AC-021, AC-036, AC-038, AC-039, AC-060 |
| F-27 | §15 Definition of Done stopped at DEC-24 | Now DEC-01 – DEC-27 and CL-01 – CL-13; approval required before further planning documents; no stale DEC-24 limit remains elsewhere |
| F-28 | Unspecified contracts surfaced while strengthening criteria: product-level availability, inventory-adjustment shape and ledger representation, payment-attempt exposure | New CL-13, CL-11, CL-12 (all pending) instead of invented behaviour |
| F-29 | The v0.3 instruction refers to the "approved" R1 seeded-rating behaviour of CL-01, but every CL remains pending | CL-01 stayed pending in v0.3 and AC-109 called the behaviour "proposed"; CL-01 was approved on 2026-10-12 and AC-109 now cites it as approved |

**Findings resolved in v0.4**

| # | Finding | Resolution |
|---|---|---|
| F-30 | `WELCOME10` restricted to returning customers (shipped order) would be unusable by any new customer in R1, because admins can only ship orders in R2; this would break the core-journey test and the worked totals | Seeded customer with shipped and delivered orders is eligible (TR-003); AC-104 now uses `SAVE100`; WELCOME10 cases of AC-032 run as the eligible customer; AC-110 adjusted; BR-075, AC-115, DEC-28 |
| F-31 | The owner's `SAVE100` minimum ("more than R800") contradicts the inclusive default of BR-033 | BR-033 allows a per-coupon exclusive minimum; `SAVE100` declares it; T-11, T-12 and AC-116 test R799.99, R800.00 and R800.01; `WELCOME10` stays inclusive |
| F-32 | `ONCE1` became a percentage coupon but no value or cap was given | CL-15 (pending); seed row marked pending; AC-034 unaffected because the global and per-customer limits are unchanged |
| F-33 | The owner's shipping and minimum-order statement is not specific enough to implement (first order, small products, scope of the R250 minimum, interaction with the R1,000 rule) | Recorded as written in CL-14 with a suggested reading; BR-028, FR-050 and the totals acceptance criteria are unchanged; no rule invented |
| F-34 | Silent token refresh was requested and then withdrawn ("keep the old rule") | DEC-04 unchanged and annotated; BR-005, SEC-003 and AC-004/AC-006/AC-007 unchanged |
| F-35 | `COUPON_NOT_ELIGIBLE` had no place in the error contract | Added to Appendix A and BR-074 step 10; BR-036 re-validates eligibility at placement |

**Findings resolved in v0.5**

| # | Finding | Resolution |
|---|---|---|
| F-36 | The owner's shipping answers withdraw the approved "Standard free at R1,000 or more" rule: Standard is now free only for a qualifying first order from R250 up to under R1,000, and orders of R1,000 or more pay R60 | BR-028 rewritten; new BR-076; FR-049, FR-050, FR-036, DEC-07 amended; DEC-29 and CL-14 approved; AC-036 rewritten; worked totals rebuilt with a customer column (T-01, T-02, T-07, T-08, T-09 changed; T-13 – T-17 added) |
| F-37 | The small-goods rule needs a catalog designation that the data model and fixtures lacked | Category small-goods designation (§5.2, inherited by subcategories; Wearables and Audio designated), FR-089, BR-077, fixtures in §5.4 |
| F-38 | No error code or placement step existed for an order below the minimum | `ORDER_BELOW_MINIMUM` (409) in Appendix A; BR-074 step 7 extended without renumbering; FR-037 cart flag `below_minimum_order`; AC-114 amended; AC-118 |
| F-39 | Several consequences of the owner's answers were not stated by the owner (Standard-only offer, returning customers pay below R1,000, pre-discount band, first order below R250) | Recorded as CL-16 instead of being presented as approved requirements; approved by the owner on 2026-10-13 and closed in v0.6 |
| F-40 | AC-095 and AC-098 still cited the old free-shipping values and the removed `FREE_SHIPPING_THRESHOLD` key | AC-095 now expects shipping 60.00 and total 2,060.00; AC-098 uses `MIN_ORDER_AMOUNT`; §8.2 lists the four new configuration keys |
| F-41 | `WELCOME10` customers are returning by definition, so the worked totals for them must include the Standard fee | T-01, T-02, T-03, T-04, T-05, T-07 are marked Returning and use R60.00 shipping |

**Findings resolved in v0.6**

| # | Finding | Resolution |
|---|---|---|
| F-42 | CL-16 (five derived shipping consequences) was still pending, leaving the PRD without an approved baseline | Owner confirmed all five points; CL-16 approved; status, §14, §15 and Appendix C updated; no open items remain |
| F-43 | The effect of the small-goods exception on shipping was implicit | BR-076, BR-077, FR-116, T-14 and AC-117/AC-118 state that the exception waives only the minimum order and grants no free shipping |
| F-44 | The treatment of `WELCOME10` customers for shipping was only a note under the worked totals | BR-075 and BR-076 state that `WELCOME10` customers are returning and pay R60.00 Standard; AC-117 asserts it |
| F-45 | First-order status was defined as "no earlier non-cancelled order" without saying how the order being placed is treated | BR-076 and AC-117 exclude cancelled orders and the order currently being placed, and list the statuses that count |
| F-46 | Rules used both "pre-discount" and "pre-coupon" for the same subtotal; AC-036 did not say the R249.99 cart is a four-unit small-goods cart | BR-076, BR-077, FR-116 and AC-036 use "pre-coupon (pre-discount)" consistently; AC-036 clarified |

No open items remain: all decisions (DEC-01 – DEC-29) and clarifications (CL-01 – CL-16) are approved.

### D.6 Targeted traceability check (v0.7)

This targeted check covers the v0.7 clarification changes only; it does not replace the earlier full v0.6 audit.

| Clarification | Requirement and story trace | Acceptance criterion |
|---|---|---|
| CL-17 | FR-008 → US-008 | AC-009 |
| CL-18 | FR-112 → US-043, US-044, US-051 | AC-120 |
| CL-19 | FR-072, FR-073, FR-094 → US-053, US-054, US-074 | AC-121 |
| CL-20 | FR-005, BR-005 → US-005, UI-28 | AC-119 |
