# Seed data and local assets (DATA-002)

Deterministic, synthetic, **local/test only**. Planned behaviour is distinguished from verified behaviour in the DATA-002 completion report; this file documents how the mechanism works.

## Commands

All commands run from the repository root as `python -m app.seed <command>` (inside Docker, where the compose service already sets `APP_ENV`: `docker compose run --rm -e SEED_PASSWORD_ADMIN -e SEED_PASSWORD_CUSTOMER -e SEED_PASSWORD_HISTORY -e SEED_PASSWORD_REVIEWER api python -m app.seed <command>`, forwarding your shell values; this Docker invocation has **not** been executed by the author and should be confirmed on first use).

| Command | Purpose |
|---|---|
| `seed` | Insert any missing seed rows in one transaction. Idempotent; never updates or deletes existing rows. |
| `reset --confirm` | Remove seed-owned and `qa_`-prefixed test data inside the boundary below, then re-seed. Separate from `seed`; requires `--confirm`. |
| `verify [--snapshot]` | Read-only baseline report; checks that every planned seed-owned row exists by deterministic primary key and validates data invariants. Returns non-zero for missing/duplicate planned rows or invariant failures. `--snapshot` adds per-table row counts and SHA-256 digests for before/after comparison. |
| `assets [--check]` | Regenerate (or verify) the local SVG assets and provenance manifest. |
| `fixtures` | Print the fixture catalogue as a Markdown table. |

Prerequisite: apply migrations first (`alembic upgrade head`). Seed never creates schema.

## Environment variables

| Variable | Notes |
|---|---|
| `APP_ENV` | **Must be explicitly `local` or `test`.** Anything else, or unset, is refused before any database access. |
| `DATABASE_URL` | Host must be `localhost`, `127.0.0.1`, `::1`, `db`, `db-test` or `host.docker.internal`; remote hosts are refused. Never printed. |
| `SEED_PASSWORD_ADMIN`, `SEED_PASSWORD_CUSTOMER`, `SEED_PASSWORD_HISTORY`, `SEED_PASSWORD_REVIEWER` | Local/test passwords (12-128 chars, not starting `change-me`). Read from the environment or an untracked `.env`. Needed only when an account is **created** (first seed, or reset). `SEED_PASSWORD_REVIEWER` is shared by the five reviewer accounts. |

No password is stored in source. `.env.example` holds commented placeholders only. Hashes are Argon2id (`argon2-cffi`). Plaintext passwords and hashes are never printed. A second `seed` run does not need the passwords and does not touch any stored hash.

## Seeded accounts (passwords: yours, from the variables above)

| Email | Role | Purpose |
|---|---|---|
| `admin@nexacart.test` | admin | Administrator; created only by this mechanism (never via public registration). |
| `customer@nexacart.test` | customer | First-time buyer: saved address, empty cart, no orders, not eligible for `WELCOME10`. |
| `history@nexacart.test` | customer | Returning customer: one order in each status (pending, confirmed, processing, shipped, delivered, cancelled); eligible for `WELCOME10`. |
| `reviewer@nexacart.test`, `reviewer2`-`reviewer5@nexacart.test` | customer | Review contributors, each with one delivered order for the products they reviewed. |

Notes for test authors:

* `history@` has a **pending** order, so its cart is locked to that order and it cannot start another order until the pending order is paid or cancelled.
* The pending order's `reservation_deadline` is deliberately 2099-12-31 so a future expiry worker never alters the baseline.
* No `coupon_usages` rows are seeded, so every coupon limit starts at zero use.
* Seeded orders use numbers `NC-YYYYMMDD-9NNNNN`; a future order-number generator should avoid the `9xxxxx` range or accept the collision risk.

## Shipping and coupons

| Shipping | Fee (minor) | Estimate |
|---|---:|---|
| `standard` | 6000 | 3-5 business days |
| `express` | 12000 | 1-2 business days |

| Coupon | Type | Value | Minimum | Limits / state |
|---|---|---|---|---|
| `WELCOME10` | percentage | 1000 bp | 50000 inclusive | max discount 20000; 1/customer; `returning_customer` |
| `SAVE100` | fixed | 10000 | 80000 exclusive | 3/customer; 100 global |
| `ONCE1` | percentage | 500 bp | 0 | max discount 5000; 1 global; 1/customer |
| `EXPIRED5` | percentage | 500 bp | 0 | expired 2020-12-31 |
| `INACTIVE15` | percentage | 1500 bp | 0 | `is_active = false` |

Active coupons run 2026-01-01 to 2099-12-31 UTC. Definitions live only in `app/seed/commerce.py`; DATA-002 implements no coupon or shipping logic.

## Fixture catalogue

Stable slugs and SKUs (`fx-` slugs are fixtures). Prices are integer minor units; stock is the baseline value visible to tests. Regenerate with `python -m app.seed fixtures`.

| Fixture | Product slug | Base SKU | Active | Variants (price minor : stock) |
|---|---|---|---|---|
| long-name | `fx-long-name-workstation` | `NC-CMP-008` | True | default 6499900:6 |
| no-reviews | `fx-no-reviews-aria-13-laptop` | `NC-CMP-012` | True | {'colour': 'Silver'} 899900:20 |
| inactive | `fx-inactive-viewline-22-monitor` | `NC-CMP-016` | False | default 179900:15 |
| single-variant | `fx-single-variant-keystone-keyboard` | `NC-CMP-017` | True | default 129900:35 |
| low-stock-boundary | `fx-low-stock-boundary-volt-mouse` | `NC-CMP-018` | True | {'colour': 'Black'} 89900:5; {'colour': 'White'} 89900:6 |
| out-of-stock | `fx-out-of-stock-nova-lite-5` | `NC-PHN-013` | True | {'storage': '64GB'} 179900:0; {'storage': '128GB'} 199900:0 |
| small-goods | `fx-small-goods-ear-tips-set` | `NC-WAR-004` | True | default 3999:80 |
| small-goods | `fx-small-goods-earbuds-pouch` | `NC-WAR-005` | True | {'colour': 'Black'} 2999:80; {'colour': 'Grey'} 2999:60 |
| small-goods | `fx-small-goods-wired-earphones` | `NC-WAR-006` | True | default 5999:80 |
| many-reviews | `fx-many-reviews-sonic-studio-headphones` | `NC-WAR-007` | True | {'colour': 'Black'} 349900:40; {'colour': 'Sand'} 349900:30 |
| partial-availability | `fx-partial-availability-nimbus-anc-headphones` | `NC-WAR-010` | True | {'colour': 'Black'} 379900:8; {'colour': 'Silver'} 379900:0 |
| small-goods | `fx-small-goods-band-spare-strap` | `NC-WAR-018` | True | {'colour': 'Black'} 4999:80; {'colour': 'Blue'} 4999:60 |
| small-goods | `fx-small-goods-band-screen-protectors` | `NC-WAR-019` | True | default 2999:80 |
| price-999.99 | `fx-price-999-99-liverpool-away-shirt` | `NC-FBL-005` | True | {'size': 'S'} 99999:12; {'size': 'M'} 99999:13; {'size': 'L'} 99999:14; {'size': 'XL'} 99999:15 |
| price-1000.00 | `fx-price-1000-00-manchester-united-third-shirt` | `NC-FBL-006` | True | {'size': 'S'} 100000:12; {'size': 'M'} 100000:13; {'size': 'L'} 100000:14; {'size': 'XL'} 100000:15 |
| price-800.00 | `fx-price-800-00-france-away-shirt` | `NC-FBL-012` | True | {'size': 'S'} 80000:12; {'size': 'M'} 80000:13; {'size': 'L'} 80000:14; {'size': 'XL'} 80000:15 |
| price-800.01 | `fx-price-800-01-spain-home-shirt` | `NC-FBL-013` | True | {'size': 'S'} 80001:12; {'size': 'M'} 80001:13; {'size': 'L'} 80001:14; {'size': 'XL'} 80001:15 |
| price-500.00 | `fx-price-500-00-matchday-training-tee` | `NC-FBL-014` | True | {'size': 'S'} 50000:12; {'size': 'M'} 50000:13; {'size': 'L'} 50000:14; {'size': 'XL'} 50000:15 |
| price-250.00 | `fx-price-250-00-training-socks-3-pack` | `NC-FBL-015` | True | {'size': 'M'} 25000:70; {'size': 'L'} 25000:60 |
| price-249.99 | `fx-price-249-99-matchday-fan-scarf` | `NC-FBL-016` | True | {'colour': 'Red'} 24999:55; {'colour': 'Blue'} 24999:45 |
| non-small-goods | `fx-non-small-goods-club-beanie` | `NC-FBL-017` | True | default 14900:90 |
| single-unit | `fx-single-unit-puma-caven-classic` | `NC-SHO-009` | True | default 89900:1 |

Review fixtures (documented, reproducible): `fx-many-reviews-sonic-studio-headphones` has 5 ratings [5,5,4,4,3] -> 4.2 (count 5). `samsung-galaxy-buds-fe` has [5,4,4,4] -> 4.25 -> **4.3** (half-up boundary, count 4). `pebble-mini-bluetooth-speaker` [5,4] -> 4.5; `adidas-duramo-sl` [3] -> 3.0; `puma-smash-v2` [4,4,4] -> 4.0 (count 3); `xiaomi-smart-band-8` [4,4] -> 4.0 (count 2, ties on average with the previous); `nike-air-force-1-07` [5] -> 5.0. Every other product, including `fx-no-reviews-aria-13-laptop`, has zero reviews and a 0.0/0 aggregate. Aggregates are computed from the review rows, never entered independently.

Small goods: `fx-small-goods-*` (Wearables and Audio) cost at most R59.99, so four units total under R250 (e.g. 4 x R59.99 = R239.96) with 60-80 units in stock. `fx-non-small-goods-club-beanie` (R149.00, Football Shirts and Apparel) is the non-small-goods control; `fx-price-249-99-matchday-fan-scarf` is a second one.

## Baseline

5 top-level categories, 25 subcategories, 93 products (Computers 24, Smartphones 15, Wearables 19, Football 19, Shoes 16), 224 variants (68 products, 73%, have several variants), 103 product images, 2 shipping options, 5 coupons, 8 accounts, 11 orders (6 delivered, 1 each pending/confirmed/processing/shipped/cancelled), 18 reviews, 254 inventory movements, 0 coupon usages.

Inventory ledger: every variant has one `initial_stock` movement with a deterministic key `seed:initial_stock:<variant sku>`; `stock_quantity` equals the sum of the variant's movements. Seeded orders add `order_placed` movements (and an `order_cancelled` restoration for the cancelled order). Because the schema forbids zero-delta movements, each zero-stock variant is seeded as `initial_stock +10` followed by an `admin_adjustment -10` (key `seed:seed_adjustment:<sku>`, actor = seed admin, with a reason text), leaving a documented, auditable balance of 0.

## Idempotency model

Every seed-owned row has a UUIDv5 id derived from a fixed namespace and a natural key (`app/seed/ids.py`), and all timestamps derive from a fixed epoch (2026-01-01 UTC). `seed` inserts with `ON CONFLICT DO NOTHING`, so an unchanged database is never rewritten. If a seed natural key (email, slug, SKU, coupon or shipping code) already exists under a different id, the seed refuses to proceed rather than silently skipping.

## Reset boundary and safety

`reset --confirm` runs in one transaction and only deletes:

* the 8 seed users and any user whose email starts with `qa_`, plus everything those users own (orders and dependants, carts, wishlist, addresses, sessions, reviews, idempotency records, audit events they acted in);
* the seed catalogue (and any category/product slug starting `qa-`) with variants, images and specifications; the five seed coupons and codes starting `QA_`; the two seed shipping options;
* inventory movements of in-scope variants/orders/actors. Movements are append-only in normal operation; this explicit local/test reset is the only authorised exception.

It never issues `DROP`/`TRUNCATE` and never touches other rows. It aborts with nothing changed if (a) an in-scope order, movement or review references a variant/product outside the seed/`qa` catalogue, or (b) any other row references an in-scope record (foreign-key refusal). Public reset endpoints do not exist. Reset re-creates the seed accounts, so they receive freshly salted Argon2id hashes (credentials return to the values in your environment).

Test authors should therefore create test records with the `qa_` email prefix and `qa-` slug / `QA_` coupon-code prefixes (TR-016) so reset can clean them.

## Assets

Local original SVG files live in `app/assets/` (key `products/<slug>-main|-alt` -> `app/assets/<key>.svg`, plus `placeholders/product`). They are generated by `app/seed/assets.py`, contain no brand artwork or crests, and use no external URLs, CDNs or fonts. Provenance: `app/assets/provenance.json` and [ASSET_PROVENANCE.md](ASSET_PROVENANCE.md). Static serving of these files is part of the later catalogue work; the directory location is an assumption for owner confirmation.

## Known limitations

* The repository has no declared licence; asset licence text says so (owner to confirm).
* `seed` does not repair a partially modified baseline (use `reset`).
* DATA-002 seeds no `idempotency_records`, `auth_sessions`, `audit_events`, refunds or coupon usages.
