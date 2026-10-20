# NexaCart — Database Schema and ERD

| Field | Value |
|---|---|
| Document | docs/planning/DATABASE_SCHEMA_AND_ERD.md |
| Version | 0.1 — draft for owner review |
| Status | **Draft. Not implemented.** Proposed PostgreSQL model based on PRD v0.7, User Stories v0.3 and Technical Architecture v0.2. |
| Date | 2026-10-20 |
| Primary baseline | docs/planning/PRD.md v0.7 |
| Architecture | docs/planning/TECHNICAL_ARCHITECTURE.md v0.2; hosting provider deferred |
| Not yet created | docs/planning/IMPLEMENTATION_PLAN_AND_BACKLOG.md |

## 1. Purpose and design rules

This document translates approved product requirements into a proposed physical PostgreSQL schema. It is a planning artifact, not an implemented migration. Every table, constraint and index is subject to review before SQLAlchemy models and Alembic migrations are written.

- PostgreSQL is the durable source of truth. Business-critical state must not exist only in process memory.
- Store monetary amounts as integer minor units (ZAR cents), never as binary floating point.
- Store times as TIMESTAMPTZ in UTC and exchange ISO-8601 timestamps through the API.
- Primary keys use UUIDs, consistent with approved ARCH-05. UUID generation method is a schema detail; PostgreSQL UUIDv4 generation is the default proposal.
- Write schemas are strict. Clients cannot set role, ownership, stock, prices, discounts, totals, shipping fees or order/payment/refund status.
- Use deactivation rather than hard deletion for products, variants and categories referenced by orders (BR-061).
- Order line and delivery-address snapshots must not change after placement (BR-050, FR-015).
- Order history, inventory movements and audit events are append-only (BR-042, BR-052, BR-066, FR-076, FR-100).
- Use named CHECK constraints for controlled status values where this simplifies future migrations. Use JSONB for flexible specifications, canonical variant options, replay response bodies and safe audit summaries—not for relational identity or fields needing database uniqueness.
- Use Alembic migrations as the schema source of truth. Do not create the production schema implicitly during application startup.

## 2. Entity relationship diagram

This conceptual ERD shows the main persisted relationships. It is not intended to substitute for the detailed constraints below.

```mermaid
erDiagram
    USERS ||--o{ AUTH_SESSIONS : authenticates
    USERS ||--o{ ADDRESSES : owns
    USERS ||--|| CARTS : has
    USERS ||--o{ WISHLIST_ITEMS : owns
    USERS ||--o{ ORDERS : places
    USERS ||--o{ REVIEWS : writes
    USERS ||--o{ COUPON_USAGES : consumes
    USERS ||--o{ AUDIT_EVENTS : acts
    USERS ||--o{ NOTIFICATIONS : receives
    CATEGORIES o|--o{ CATEGORIES : parent_of
    CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--|{ PRODUCT_VARIANTS : has
    PRODUCTS ||--|{ PRODUCT_IMAGES : displays
    PRODUCTS ||--o{ PRODUCT_SPECIFICATIONS : describes
    PRODUCTS ||--o{ WISHLIST_ITEMS : appears_in
    PRODUCTS ||--o{ REVIEWS : receives
    PRODUCT_VARIANTS ||--o{ CART_LINES : selected_in
    CARTS ||--o{ CART_LINES : contains
    COUPONS ||--o{ COUPON_USAGES : tracks
    ORDERS ||--o{ COUPON_USAGES : counts
    ORDERS ||--|{ ORDER_ITEMS : snapshots
    ORDERS ||--|| ORDER_ADDRESS_SNAPSHOTS : preserves
    ORDERS ||--o{ ORDER_STATUS_HISTORY : records
    ORDERS ||--o{ PAYMENT_ATTEMPTS : has
    ORDERS ||--o| REFUNDS : may_create
    ORDERS ||--o{ IDEMPOTENCY_RECORDS : protects
    ORDERS ||--o{ INVENTORY_MOVEMENTS : causes
    PRODUCT_VARIANTS ||--o{ INVENTORY_MOVEMENTS : tracks
    PRODUCT_VARIANTS o|--o{ ORDER_ITEMS : purchased_as
    SHIPPING_OPTIONS ||--o{ ORDERS : snapshots
    USERS ||--o{ IDEMPOTENCY_RECORDS : scopes
```

The cart lock is physically stored as nullable carts.locked_by_order_id → orders.id. The order does not need a foreign key back to a cart, avoiding a circular insert dependency. Reviews attach to products, not variants. Orders preserve their delivery-address values without a foreign key to the mutable address book. Payment and refund status are derived projections, not competing mutable copies of the source records.

## 3. Core table definitions

Types below are PostgreSQL-oriented. All tables also receive UUID primary keys unless a naturally unique primary key is specified, and timestamp columns as noted.

### 3.1 Identity and session security

#### users

One row per customer or administrator.

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| name | VARCHAR(100), required, trimmed and not blank |
| email | VARCHAR(254), required, trimmed/lowercase, unique case-insensitively |
| password_hash | TEXT, required adaptive hash; never returned or logged |
| phone | VARCHAR(16), nullable; validated to 7–15 digits with optional leading + |
| role | TEXT, CHECK in customer/admin; registration always creates customer |
| is_active | BOOLEAN, required, default true |
| created_at, updated_at | TIMESTAMPTZ, required |
| password_changed_at | TIMESTAMPTZ, nullable |

Constraint uq_users_email and role check implement BR-001–006. Public registration cannot set role; admin provisioning is seed/CLI only (FR-010, SEC-008).

#### auth_sessions

Durable JWT session state so logout and password-change revocation work across API replicas.

| Column | Type and rule |
|---|---|
| jti | UUID primary key and JWT ID |
| user_id | UUID FK to users.id, required |
| issued_at, expires_at | TIMESTAMPTZ; expiry must be later than issue time |
| revoked_at | TIMESTAMPTZ, nullable |
| revocation_reason | TEXT, nullable, controlled safe reason |
| csrf_token_hash | TEXT, required; store a hash, never the raw CSRF token |
| created_at | TIMESTAMPTZ, required |

Index by user_id and expiry. An authenticated request validates signature, pinned algorithm, expiry, revocation/session state and the current database role. Cookie logout revokes the session and clears the cookie. Password change revokes all older sessions and forces login with the new password (SEC-003–005, CL-17). Raw JWTs and CSRF values must not be stored or logged.

#### login_throttle_state

| Column | Type and rule |
|---|---|
| email_key | VARCHAR(254) primary key; normalized identifier |
| consecutive_failures | INTEGER, non-negative |
| locked_until | TIMESTAMPTZ, nullable |
| updated_at | TIMESTAMPTZ, required |

Use atomic updates for the account-based BR-007 lockout. Five consecutive failed attempts lock the account for 15 minutes; a successful login clears the counter. Unknown-email and wrong-password responses remain indistinguishable (BR-004). Keep this state out of response bodies and logs.

### 3.2 Catalog and assets

#### categories

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| parent_id | UUID nullable FK to categories.id |
| slug | VARCHAR(120), unique, required |
| name | VARCHAR(100), required |
| description | TEXT, nullable |
| is_active | BOOLEAN, required |
| is_small_goods | BOOLEAN, default false |
| sort_order | INTEGER, non-negative |
| created_at, updated_at | TIMESTAMPTZ, required |

A top-level category has no parent; prevent self-parenting. Enforce maximum depth of two levels in the service, because a basic row CHECK cannot validate arbitrary tree depth. Wearables and Audio is designated small-goods, with the designation inherited by its subcategories (BR-077). Prevent deactivation while active products or active subcategories remain (BR-061, FR-089).

#### products

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| category_id | UUID FK to categories.id, required |
| slug | VARCHAR(160), globally unique and immutable |
| base_sku | VARCHAR(80), unique required product code |
| name | VARCHAR(200), required |
| brand | VARCHAR(100), required |
| description | TEXT, required by the write schema |
| is_active, is_featured, is_fictional | BOOLEAN; fictional defaults true |
| rating_average | NUMERIC(3,1), 0.0–5.0 cached aggregate |
| rating_count | INTEGER, non-negative cached aggregate |
| created_at, updated_at | TIMESTAMPTZ, required |

Index by active/category and newest ordering. Products referenced by orders are deactivated/reactivated, not hard-deleted. Rating values are denormalized read projections and must be recalculated transactionally from visible reviews (BR-060, FR-081–082); review rows remain the underlying evidence.

#### product_variants

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| product_id | UUID FK to products.id, required |
| sku | VARCHAR(80), globally unique |
| options | JSONB canonical option map, e.g. colour and storage |
| options_key | TEXT canonical representation of normalized options |
| unit_price_minor | BIGINT, positive integer cents |
| stock_quantity | INTEGER, never negative |
| is_active | BOOLEAN, required |
| created_at, updated_at | TIMESTAMPTZ, required |

Required constraints: unique (product_id, options_key), unique SKU, positive price and non-negative stock. The same normalization routine must sort and normalize option names/values before producing options_key. Do not rely on arbitrary JSON text formatting for uniqueness. A product without options has exactly one default variant. Product/variant SKU and identity fields are immutable (BR-010–013, NFR-006).

#### product_images

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| product_id | UUID FK to products.id |
| asset_key | VARCHAR(240), key to a managed local/original/licensed asset; no arbitrary external URL |
| alt_text | VARCHAR(250), required and non-blank |
| is_primary | BOOLEAN, required |
| sort_order | INTEGER, non-negative |
| created_at | TIMESTAMPTZ, required |

A partial unique index permits at most one primary image per product. The service enforces one primary and 1–8 images for a complete product. Use a managed placeholder if an intended asset is missing; no runtime third-party image requests (PRD §5.2, FR-029, FR-097).

#### product_specifications

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| product_id | UUID FK to products.id |
| name | VARCHAR(100), required |
| value | VARCHAR(500), required |
| sort_order | INTEGER, non-negative |

Unique (product_id, normalized name). Keeping key/value specifications separate avoids mixing display attributes with identity and pricing.

### 3.3 Addresses, cart and wishlist

#### addresses

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| customer_id | UUID FK to users.id |
| recipient_name | VARCHAR(100), required |
| phone | VARCHAR(16), required |
| line1 | VARCHAR(150), required |
| line2 | VARCHAR(150), nullable |
| city | VARCHAR(80), required |
| province | VARCHAR(80), required |
| postal_code | VARCHAR(4), required four-digit postal code for the configured South African delivery country |
| country_code | CHAR(2), single configured delivery country |
| is_default | BOOLEAN, required |
| created_at, updated_at | TIMESTAMPTZ, required |

Index by customer and creation time. A partial unique index allows at most one default address per customer. The address service guarantees exactly one default whenever the collection is non-empty, auto-selects the first address and promotes the most recently created remaining address when the default is deleted. The maximum of ten addresses is enforced in a transaction (BR-008–009). Order snapshots deliberately do not reference the address row.

#### carts

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| customer_id | UUID FK to users.id, unique; one cart per customer |
| applied_coupon_id | UUID nullable FK to coupons.id; selection only, no usage reservation |
| shipping_option_id | UUID FK to shipping_options.id, default Standard |
| locked_by_order_id | UUID nullable FK to orders.id; pending order that holds the lock |
| created_at, updated_at | TIMESTAMPTZ, required |

Carts survive logout/login; the cart does not reserve stock. Lock the cart row during mutation/placement. While an order is pending, mutation requests return CART_LOCKED. After payment approval, clear cart lines and selections and unlock; after unpaid cancellation/expiry, retain and revalidate lines/selections and unlock (BR-019, BR-071–072, FR-031, FR-112–113). Use a unique partial index on non-null locked_by_order_id.

#### cart_lines

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| cart_id | UUID FK to carts.id |
| variant_id | UUID FK to product_variants.id |
| quantity | INTEGER 1–10 |
| last_acknowledged_unit_price_minor | BIGINT, informational price-change reference only |
| created_at, updated_at | TIMESTAMPTZ, required |

Unique (cart_id, variant_id), and quantity CHECK. Limit each cart to 20 distinct lines. Validate current stock within the cart transaction. The stored acknowledged/reference price supports the informational price_changed flag; it is never authoritative for pricing. Checkout always recalculates using current server values and compares the submitted expected total (BR-018–022, FR-037).

#### wishlist_items

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| customer_id | UUID FK to users.id |
| product_id | UUID FK to products.id |
| created_at | TIMESTAMPTZ, required |

Unique (customer_id, product_id). New adds require an active product; existing wishlist entries can persist and show an unavailable flag after product deactivation/stock change. Moving to cart removes the wishlist row only if cart insertion succeeds, within one atomic operation (BR-023, FR-041–045).

### 3.4 Coupons and shipping

#### coupons

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| code | VARCHAR(20), uppercase normalized, unique |
| discount_type | TEXT, CHECK percentage/fixed |
| percentage_basis_points | INTEGER nullable; percentage without binary floating point |
| fixed_discount_minor | BIGINT nullable |
| maximum_discount_minor | BIGINT nullable |
| minimum_order_minor | BIGINT, non-negative pre-discount minimum |
| minimum_is_exclusive | BOOLEAN, selects > versus >= comparison |
| starts_at, expires_at | TIMESTAMPTZ; interval [starts_at, expires_at) |
| is_active | BOOLEAN, required |
| global_usage_limit | INTEGER nullable |
| per_customer_usage_limit | INTEGER nullable |
| eligibility_rule | TEXT, CHECK all_customers/returning_customer |
| created_at, updated_at | TIMESTAMPTZ, required |

Enforce consistency between discount_type and its value columns, non-negative values/caps, positive limits when present, unique code and starts_at < expires_at. Coupons are seeded and are not managed via public admin UI (NG-09). Seed values live in seed data rather than duplicated application constants.

**Owner-approved coupon validation order (GAP-11):** normalize/lookup → active and validity window → customer eligibility → minimum amount → usage limits → calculate discount/caps. The same shared validator is used when applying a coupon and revalidating at placement. The first failing check determines the one returned code. Applying a coupon does not reserve a use.

#### coupon_usages

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| coupon_id | UUID FK to coupons.id |
| customer_id | UUID FK to users.id |
| order_id | UUID FK to orders.id, unique |
| usage_state | TEXT, CHECK reserved/consumed/released |
| reserved_at | TIMESTAMPTZ, required |
| finalized_at | TIMESTAMPTZ, nullable |

Create during TX-1 when usage is counted. On unpaid cancellation/expiry, reserved becomes released. On successful payment, reserved becomes consumed. Paid-order cancellation does not release consumed usage (BR-035). Counts for global and per-customer limits include reserved and consumed records. Lock the relevant coupon/usage state before checking limits, so concurrent placement cannot overrun the final use. Only one coupon is allowed per order.

#### shipping_options

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| code | VARCHAR(30), unique, stable code such as standard or express |
| display_name | VARCHAR(80), required |
| base_fee_minor | BIGINT, non-negative |
| delivery_estimate | VARCHAR(100), static configured estimate |
| is_active | BOOLEAN, required |
| sort_order | INTEGER, non-negative |

Seed Standard at 6000 cents and Express at 12000 cents. The pricing service calculates the applied Standard fee according to BR-076; Express is always charged. Free Standard shipping applies only to an eligible first order with pre-coupon subtotal at least R250.00 and below R1,000.00. Coupon discounts never affect shipping eligibility. Store the actual applied fee and selected shipping option details in the order snapshot.

### 3.5 Orders, payment and refunds

#### orders

The order header is created as pending in TX-1. Payment is a separate TX-2 operation.

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| order_number | VARCHAR(24), unique human-readable NC-YYYYMMDD-NNNNNN; never authorization |
| customer_id | UUID FK to users.id |
| status | TEXT CHECK pending/confirmed/processing/shipped/delivered/cancelled |
| subtotal_minor, discount_minor, shipping_fee_minor, total_minor | BIGINT, non-negative cents |
| coupon_code_snapshot | VARCHAR(20), nullable |
| shipping_option_code_snapshot | VARCHAR(30) |
| shipping_option_name_snapshot | VARCHAR(80) |
| reservation_deadline | TIMESTAMPTZ, fixed from placement and never extended by retries |
| placed_at | TIMESTAMPTZ, required |
| cancelled_at | TIMESTAMPTZ, nullable |
| created_at, updated_at | TIMESTAMPTZ, required |

Unique order number; index (customer_id, placed_at DESC) and (status, reservation_deadline). A partial unique index uq_one_pending_order_per_customer on customer_id WHERE status = pending enforces at most one pending order per customer (BR-071, NFR-006). Amount checks enforce total = subtotal − discount + shipping fee. TX-1 commits order header, items, address snapshot, stock movements, coupon usage, cart lock and idempotency record together.

**Derived status projections:** payment_status is derived from attempts: no attempts = unpaid; any approved attempt = paid; attempts exist but none approved = failed. refund_status is not_applicable if no refund exists, otherwise it comes from the refund row. Use a SQL view/query helper for these projections instead of storing a second competing mutable status.

#### order_items

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| order_id | UUID FK to orders.id |
| product_id | UUID FK to products.id; restrict delete |
| variant_id | UUID FK to product_variants.id; restrict delete |
| product_name_snapshot | VARCHAR(200), required |
| variant_description_snapshot | TEXT, required |
| sku_snapshot | VARCHAR(80), required |
| image_asset_key_snapshot | VARCHAR(240), required local asset key |
| unit_price_minor | BIGINT, non-negative |
| quantity | INTEGER, positive |
| line_total_minor | BIGINT, equals unit_price_minor × quantity |
| created_at | TIMESTAMPTZ, required |

Unique (order_id, variant_id) because identical variant cart lines merge. Store snapshots to preserve order history after catalog changes. Do not update snapshot fields after placement (BR-050, BR-068).

#### order_address_snapshots

One immutable delivery address per order, without an FK to the editable addresses table.

| Column | Type and rule |
|---|---|
| order_id | UUID primary key and FK to orders.id |
| recipient_name | VARCHAR(100) |
| phone | VARCHAR(16) |
| line1, line2 | VARCHAR(150); line2 nullable |
| city, province | VARCHAR(80) |
| postal_code | VARCHAR(4) |
| country_code | CHAR(2) |
| created_at | TIMESTAMPTZ |

Insert exactly once during TX-1. Later edits/deletion of a saved address do not affect this snapshot (FR-015).

#### order_status_history

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| order_id | UUID FK to orders.id |
| from_status | TEXT nullable only for initial event |
| to_status | TEXT, valid order status |
| actor_type | TEXT CHECK customer/admin/system |
| actor_user_id | UUID nullable FK to users.id |
| reason | VARCHAR(200), nullable |
| request_id | VARCHAR(100), nullable |
| occurred_at | TIMESTAMPTZ, required |

Index by (order_id, occurred_at). Append the initial pending event and every permitted status transition in the same transaction as the order update. Admin cancellation requires a 1–200 character reason; customer cancellation requires none (CL-19). No normal operation updates or deletes history rows (BR-052, FR-076).

#### payment_attempts

Every committed simulated attempt is recorded; no card details exist.

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| order_id | UUID FK to orders.id |
| attempt_number | INTEGER, positive, sequential per order |
| outcome | TEXT CHECK approved/declined/timed_out/error |
| amount_minor | BIGINT, equals the order total |
| idempotency_key | VARCHAR(64), required |
| idempotency_record_id | UUID FK to idempotency_records.id, unique |
| occurred_at | TIMESTAMPTZ, required |

Constraints: unique (order_id, attempt_number), unique (order_id, idempotency_key), at most one approved attempt per order via a partial unique index. The service enforces attempt cap and amount equality. A payment request rejected because the order is cancelled/expired, already paid or over the attempt limit creates no attempt and no idempotency record (BR-046–049, BR-069). The timeout delay occurs before TX-2 and does not hold a database lock.

#### refunds

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| order_id | UUID FK to orders.id, unique |
| amount_minor | BIGINT, equals amount paid/order total |
| status | TEXT CHECK refund_pending/refunded |
| created_at | TIMESTAMPTZ, required |
| completed_at | TIMESTAMPTZ, nullable |
| reason | VARCHAR(200), nullable |

Only an order with an approved payment may have one full simulated refund. Create the refund atomically with paid-order cancellation in R2; complete it later in an idempotent worker transaction. No refund row is created for unpaid cancellation. Do not connect a real payment processor (NG-01, BR-055–056, FR-073–074, FR-109).

### 3.6 Idempotency and inventory ledger

#### idempotency_records

Durable replay response storage for the 24-hour idempotency contract.

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| customer_id | UUID FK to users.id |
| scope | VARCHAR(100), place_order or pay_order:<order UUID> |
| key_value | VARCHAR(64), validate allowed 8–64 characters |
| request_fingerprint | CHAR(64), SHA-256 of canonical permitted payload |
| response_status | SMALLINT, original HTTP status |
| response_body | JSONB, original safe response body |
| order_id | UUID nullable FK to orders.id |
| created_at, expires_at | TIMESTAMPTZ; expires_at at least 24 hours after creation |

Unique (customer_id, scope, key_value); index expires_at for cleanup. Same key/same fingerprint within retention replays the stored status/body without side effects. Same key/different fingerprint returns 422 IDEMPOTENCY_KEY_REUSED. A rejected operation that commits no state change leaves no record. Never purge an unexpired record (BR-048, BR-070).

#### inventory_movements

Append-only stock ledger. For every variant, current stock must equal the sum of committed movement deltas, including the initial-stock movement (BR-042).

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| variant_id | UUID FK to product_variants.id |
| delta_quantity | INTEGER, non-zero signed change |
| reason_code | TEXT CHECK initial_stock/order_placed/order_cancelled/reservation_expired/admin_adjustment |
| reference_type | TEXT controlled type such as seed/order_item/admin_adjustment |
| reference_id | UUID nullable related record |
| operation_key | VARCHAR(160), stable unique deduplication key |
| actor_user_id | UUID nullable FK to users.id; null for system/seed |
| reason_text | VARCHAR(200), required 1–200 chars for admin adjustment |
| occurred_at | TIMESTAMPTZ, required |

Unique operation_key; index (variant_id, occurred_at) and reference fields. Write stock balance changes and movements in the same transaction. Seed an initial_stock movement for every variant. Any correction is a new audited adjustment, never an edit to ledger history. The database prevents negative stock; a conditional update and row locking prevent overselling (BR-037–042).

#### audit_events

Append-only sensitive-action history required in R2 (BR-066).

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| actor_user_id | UUID nullable FK to users.id |
| actor_role | TEXT role snapshot |
| action | VARCHAR(100), controlled action |
| entity_type | VARCHAR(80) |
| entity_id | UUID nullable |
| before_summary, after_summary | JSONB nullable, safe minimal summaries |
| request_id | VARCHAR(100), required |
| occurred_at | TIMESTAMPTZ, required |

Indexes by timestamp, actor, action and entity. Never store passwords, hashes, JWTs, cookies, CSRF values or secret configuration in event summaries. Deny normal application updates/deletes.

### 3.7 Reviews and optional notifications

#### reviews

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| customer_id | UUID FK to users.id |
| product_id | UUID FK to products.id |
| verified_order_id | UUID FK to orders.id, evidence reference |
| rating | SMALLINT CHECK 1–5 |
| comment | VARCHAR(1000), nullable |
| is_hidden | BOOLEAN default false |
| hidden_by_user_id | UUID nullable FK to users.id |
| hidden_at | TIMESTAMPTZ nullable |
| created_at | TIMESTAMPTZ, required |

Unique (customer_id, product_id); index by product and newest-first date. At submission, the service verifies the order belongs to the customer, is delivered, and contains any variant of the reviewed product. A simple FK cannot prove this cross-table eligibility rule. Customer review edit/delete is not in MVP. Admin hiding updates visibility, recalculates visible rating average/count, and is audit logged (BR-058–060, FR-077–082).

#### notifications (R3 only)

| Column | Type and rule |
|---|---|
| id | UUID primary key |
| customer_id | UUID FK to users.id |
| notification_type | TEXT approved event type |
| payload | JSONB minimal display data; no secrets |
| created_at | TIMESTAMPTZ |
| read_at | TIMESTAMPTZ nullable |

Index (customer_id, created_at DESC). R3 notifications are optional and require separate release approval (FR-101–102, BR-067); do not implement them as part of R1.

## 4. Derived read models

Use views/query helpers instead of duplicating mutable state unless measurement proves a cache necessary.

| Projection | Source / rule |
|---|---|
| Order payment status | No attempts = unpaid; any approved attempt = paid; attempts with no approval = failed |
| Order refund status | No refund = not_applicable; otherwise refund row status |
| Product availability | Active product/category and active variants; per-variant state derived from stock |
| Product from-price | Lowest active variant price |
| Rating aggregate | Visible review average rounded half-up to one decimal and visible count |
| Cart line flags | Current variant/product state, available stock and acknowledged price reference; checkout still revalidates |
| Cart minimum-order flag | Pre-coupon subtotal and unit quantities from small-goods categories |
| Coupon usage limits | Count reserved and consumed coupon_usages by coupon and customer |
| WELCOME10 eligibility | Customer has at least one order reaching shipped/delivered; cancelled/unshipped orders do not qualify |
| Inventory reconciliation | Stored stock_quantity compared with sum of movement deltas |

## 5. Critical constraints and indexes

All names should be explicit and stable for error translation and SQL assertions.

| Name / rule | Physical invariant | Source |
|---|---|---|
| uq_users_email | Unique normalized email | BR-002 |
| ck_users_role | customer/admin only | BR-006 |
| uq_categories_slug | Unique category slug | Catalog identity |
| uq_products_slug, uq_products_base_sku, uq_variants_sku | Unique catalog identities | BR-013 |
| uq_variant_product_options | Unique (product_id, options_key) | Variant uniqueness |
| ck_variant_price_positive | unit_price_minor > 0 | BR-010 |
| ck_variant_stock_nonnegative | stock_quantity >= 0 | BR-037 |
| uq_product_images_primary | At most one primary image per product; partial unique index | PRD §5.2 |
| uq_cart_customer | One cart per customer | FR-031 |
| uq_cart_line_variant | Unique (cart_id, variant_id) | BR-021 |
| ck_cart_line_quantity | 1–10 | BR-018 |
| uq_wishlist_customer_product | Unique (customer_id, product_id) | BR-023 |
| uq_coupon_code | Unique normalized code | BR-031 |
| ck_coupon_validity_window | starts_at < expires_at | BR-032 |
| uq_coupon_usage_order | One coupon usage per order | BR-030 |
| ck_order_money_nonnegative | Amount columns are non-negative | BR-029 |
| ck_order_total_arithmetic | total = subtotal − discount + shipping fee | BR-029 |
| uq_order_number | Unique order number | BR-051 |
| uq_one_pending_order_per_customer | Partial unique index where status = pending | BR-071, NFR-006 |
| uq_order_variant_line | Unique (order_id, variant_id) | Cart merge rule |
| uq_payment_attempt_number | Unique (order_id, attempt_number) | FR-067 |
| uq_payment_idempotency_key | Unique (order_id, idempotency_key) | BR-070 |
| uq_one_approved_payment_per_order | Partial unique index for approved attempt | BR-046, NFR-006 |
| uq_refund_order | Unique order ID | BR-056, NFR-006 |
| uq_idempotency_scope_key | Unique (customer_id, scope, key_value) | BR-070 |
| uq_inventory_operation_key | Unique operation_key | BR-038–042 |
| uq_review_customer_product | Unique (customer_id, product_id) | BR-059, NFR-006 |
| Append-only operations | No ordinary UPDATE/DELETE on history, ledger and audit records | BR-042, BR-052, BR-066 |

The database alone cannot enforce every cross-row rule with a simple CHECK. Use service validation in a transaction for max ten addresses/one default when non-empty, max twenty cart lines, category depth, product visibility across category and variants, small-goods threshold, coupon eligibility/limits, review evidence ownership, payment/refund amount equality, legal order transitions, and the rule that payment/cancellation/expiry can have only one winning transition.

## 6. Transaction mapping

### TX-1 — order placement

Under the customer's cart lock, execute the exact state-check sequence in BR-074. If valid, create orders, order_items, order_address_snapshots, inventory_movements, coupon_usages when needed, cart lock, initial order_status_history and idempotency_records, while decrementing each variant's stock conditionally. Commit all effects together. A failure leaves no order, movement, usage, lock or idempotency row. Placement does not create a payment attempt.

Lock variants in deterministic ID order or use conditional updates that require sufficient stock. Never read stock, release the lock and then write an unconditional decrement. Any losing concurrent purchase receives INSUFFICIENT_STOCK and creates no partial state.

### TX-2 — payment

For a timeout outcome, wait before opening the transaction. Then lock/re-read the order and apply the BR-069 precedence. A non-payable/expired order receives ORDER_NOT_PAYABLE and creates no attempt. Within TX-2, write the idempotency record and payment_attempt; for approval also confirm the order, append status history, clear cart lines/selections and unlock it. Declined/timed_out/error attempts commit, but the pending order keeps its reservation and cart lock.

### Cancellation and reservation expiry

Serialize payment, cancellation and expiry using the order-level lock. For unpaid cancellation/expiry, change order status, append history, restore stock once, write matching inventory movements, release reserved coupon usage, and unlock the cart in one transaction. For paid cancellation in R2, restore stock and create one full refund; do not release consumed coupon usage. Repeated worker execution must be safe and idempotent (BR-053–056, BR-069–074).

### Inventory adjustment

Validate reason, lock the variant and conditionally apply the balance change. Reject a negative result. Write variant balance, movement and audit event in one transaction.

### Review creation/hide

Validate the delivered-order evidence and duplicate rule, write the review or hide state, recalculate visible aggregate values and append the applicable admin audit event transactionally.

## 7. Retention and deletion policy

| Data | Policy |
|---|---|
| Users | No public account-deletion flow in MVP; restrict deletion while referenced |
| Addresses | Customers may delete; order snapshots remain |
| Products/categories/variants | Deactivate instead of deleting if referenced by order history |
| Orders/items/address snapshots | Retain durable business history; no delete endpoint |
| Payment attempts/refunds | Change only through approved state transitions; never delete to mask failure |
| Coupon usage | Keep released rows for audit and correct usage semantics |
| Inventory movements, order history, audit events | Append-only |
| Idempotency records | At least 24 hours; purge only expired records via controlled cleanup |
| Auth sessions | Retain until expiry/revocation cleanup is safe; revocation never depends on process memory |
| Notifications | Customer-owned, R3 only |

## 8. Seed and reset requirements

The idempotent seed/reset implementation (FR-104, TR-003, TR-016) must satisfy PRD §5.4:

- Five top-level categories; at least two subcategories each; at least twelve products per top-level category (minimum sixty total); at least three products in each price tier per category.
- At least 50% of products have multiple variants. Include fixed fixtures for zero stock, one remaining unit, stock 5 and 6, inactive product, partially available variants, single default variant, no reviews and multiple known reviews.
- Include coupon/shipping/minimum order boundaries: R999.99, R1,000.00, R500.00, R250.00, R249.99, R800.00 and R800.01, plus qualifying small-goods cases.
- Include seed coupons and customer/order-state fixtures for first-order shipping and WELCOME10 eligibility.
- Write an initial_stock inventory movement for each seeded variant.
- Seed user accounts and passwords only in local/test configuration. Never publish known test passwords or put them in the public deployment.
- Use only synthetic catalogue data and managed original/licensed local assets.

Running seed twice must not duplicate inventory movements, coupon usage, orders, reviews or audit records. A test reset may rebuild the isolated test database; never expose reset of shared public data.

## 9. Migration and database verification

### Migration rules

1. All schema changes are versioned in Alembic.
2. Test migrations from an empty database and from the previous schema version.
3. Use explicit migration steps for partial indexes, constraints and data backfills.
4. Run migrations as a controlled release step; do not let each web/worker instance race at startup.
5. Document rollback limits and recovery steps rather than assuming every migration can safely downgrade.
6. Keep test seed passwords and environment secrets out of migration files.

### SQL assertions required by the backlog

- Unique normalized email and SKUs; valid role/status checks and foreign keys.
- Stock never negative and stock balance equals ledger delta sum.
- At most one pending order per customer, including concurrent attempts.
- TX-1 rollback leaves no order, item, snapshot, movement, coupon usage, cart lock or idempotency state.
- TX-2 failure leaves correct state; at most one approved payment and one refund per order.
- Correct coupon reserved/consumed/released counts under cancellation/expiry and concurrency.
- Same-key replay has no duplicate effects; same key with different payload conflicts.
- Address and catalogue edits do not alter order snapshots.
- Review uniqueness, eligibility evidence, and aggregate equality with visible reviews.
- Order status history, inventory movement ledger and audit events are append-only.
- Fresh install, migration upgrade and repeatable seed all pass.
- Test-support routes/controls are unavailable in production configuration.

## 10. Remaining schema review items

These are physical implementation details, not open product rules:

1. Confirm exact UUID generation function and supported PostgreSQL version during migration design.
2. Confirm final string lengths against the validated request schemas and design limits.
3. Define operational cleanup schedules for expired sessions and idempotency records.
4. Finalize the locking strategy for review aggregate recalculation.
5. Finalize explicit CHECK/partial-index names and migration ordering.
6. Choose the public host later; the host does not change the relational model.

## Appendix A — Traceability

| Tables / constraints | Primary requirements |
|---|---|
| users, auth_sessions, login_throttle_state | FR-001–010; BR-001–007; SEC-002–005, SEC-014 |
| addresses, order_address_snapshots | FR-011–015; BR-008–009, BR-050 |
| categories, products, product_variants, product_images, product_specifications | FR-016–030, FR-084–089, FR-097; BR-010–017, BR-061 |
| carts, cart_lines | FR-031–040, FR-052–056, FR-111–116; BR-018–022, BR-068–074 |
| wishlist_items | FR-041–045; BR-023, BR-064 |
| coupons, coupon_usages, shipping_options | FR-046–051; BR-025–036, BR-075–077 |
| orders, order_items, order_status_history | FR-052–076, FR-109–115; BR-038–056, BR-068–074 |
| payment_attempts, idempotency_records | FR-056–067, FR-110, FR-114–115; BR-046–049, BR-068–070 |
| inventory_movements | FR-090, FR-092; BR-037–042, BR-068–073 |
| refunds | FR-073–074, FR-092, FR-109; BR-053–056 |
| reviews | FR-077–082; BR-058–060 |
| audit_events | FR-098–100; BR-066 |
| notifications | FR-101–102; BR-067; R3 only |
| Health/test support | FR-103–106; TR-004–010, TR-014–019; SEC-018 |

## Appendix B — Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-20 | Initial proposed PostgreSQL schema and ERD based on approved PRD v0.7, User Stories v0.3 and Technical Architecture v0.2. No migration or application code implemented. |
