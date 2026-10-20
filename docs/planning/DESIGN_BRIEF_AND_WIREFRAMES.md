# NexaCart — Design Brief and Wireframes

| Field | Value |
|---|---|
| Document | `docs/planning/DESIGN_BRIEF_AND_WIREFRAMES.md` |
| Version | 0.3 — owner-approved design baseline, aligned with PRD v0.7 and User Stories v0.3 |
| Status | **Approved by the owner on 2026-10-20.** Approval covers Gallery (A), the N-and-dot logo concept, and the full design baseline after the v0.3 reconciliation below. DQ-01 – DQ-26 have approved design dispositions; DQ-20 is aligned with PRD clarification CL-20. GAP-02 and GAP-11 remain architecture follow-ups. No application code has been written. The prototype has not been visually verified in a real browser (§1.6). |
| Date | 2026-10-20 |
| Primary sources | `docs/planning/PRD.md` v0.7 (approved baseline) and `docs/planning/USER_STORIES_AND_FLOWS.md` v0.3 (approved baseline) |
| Context sources | `docs/planning/PROJECT_BRIEF.md`, `docs/planning/README.md`, `docs/testing/README.md`, `CLAUDE.md`, `README.md` |
| Visual exploration assets | `docs/planning/design/prototypes/home-direction-picker.html`, `docs/planning/design/brand/nexacart-logo-concepts.svg` |
| Downstream planning status | `TECHNICAL_ARCHITECTURE.md` v0.2 records owner-approved core mechanisms and is under final review; hosting-provider selection is deferred. `DATABASE_SCHEMA_AND_ERD.md` v0.1 is drafted for review; `IMPLEMENTATION_PLAN_AND_BACKLOG.md` has not yet been created. |

## 1. Purpose, scope and conventions

### 1.1 Purpose
This brief defines how NexaCart should look, feel and behave on screen, precisely enough for a frontend engineer to reproduce the intended hierarchy, layout, navigation and states without guessing, and for an SDET to find every control and state. It turns the approved requirements into a visual direction, a brand identity, design tokens, an information architecture, annotated wireframes for every screen, a component inventory, interaction states, responsive and accessibility rules, motion guidance and asset rules.

### 1.2 Scope
- **In scope:** the customer storefront and account area (R1), product reviews and the administration screens (R2), and the rules that apply across them. Optional R3 notifications are noted but **not designed** (DQ-24).
- **Out of scope:** application code, final pixel-level artwork, final photography, copy beyond the microcopy proposals in §14, the technical architecture, the database design and the delivery backlog.
- **Authority:** the PRD wins over this brief and over the user stories. Where the two documents disagree the discrepancy is recorded in §14.5 and not silently resolved. This brief never changes a business rule.

### 1.3 Approved requirements versus design decisions
Everything that comes from the PRD or the user stories is cited with its identifier. Elements marked **[P]** began as proposals and now reflect approved design defaults; the marker is retained for traceability and is not an indication that owner approval is still pending. A design default does not override a PRD business rule. GAP-01, GAP-06 and GAP-10 are resolved by PRD v0.7 clarifications CL-17 to CL-19. GAP-02 and GAP-11 remain architecture follow-ups; the other observations have approved design dispositions documented in §14.2.

**Status update (2026-10-20):** the owner confirmed approval of the visual direction (Gallery A), logo concept and complete corrected design baseline. The four cross-document behaviours that were formerly noted in §14.7 are now recorded in PRD v0.7 as CL-17 to CL-20 and reflected in User Stories v0.3. Those clarifications, not the old proposals, are the normative source for architecture and test design.

### 1.4 Conventions

| Item | Convention |
|---|---|
| Identifiers | `DP-nn` design principle, `SCR-nn` screen (wireframe), `CMP-nn` component, `ST-nn` state fragment, `AX-nn` accessibility rule, `MO-nn` motion rule, `AS-nn` asset rule, `DQ-nn` design question. PRD, story and observation IDs (FR, BR, AC, DEC, CL, NFR, SEC, TR, US, UI, GAP) are quoted exactly. |
| Release labels | R1 MVP, R2, R3 as in PRD §4.3. A screen or element not available in R1 says so. |
| Wireframe notation | Boxes show regions. `[ Label ]` is a button, `[ ........ ]` a text field, `( )` and `(o)` an unselected and a selected radio, `[ ]` and `[x]` a checkbox, `{image}` an image slot, `v` a select or disclosure, `(n)` a numbered callout explained in the table under the wireframe, `[P]` an element that began as a proposal and is now approved (see §14). Wireframes show structure only; wording in them is illustrative. |
| Viewports | Desktop wireframes represent about 1280 px, mobile wireframes about 375 px. The supported range is 360 to 1920 px (NFR-013; §9). |
| Amounts | Rand, two decimals. Sample figures in wireframes obey the approved rules (for example a first-time buyer with a pre-coupon subtotal of R898.00 gets free Standard delivery; BR-076). |
| Status | Every screen is **Planned**. Nothing here is implemented. |

### 1.5 Specialist skills: availability and use
Availability was checked in this environment before use. A skill is described as used only to the extent it was.

| Skill | Available | How it was used | Limits and overrides |
|---|---|---|---|
| `minimalist-ui` | Yes | Primary candidate. Provided the editorial-minimalist rules: restrained palette, typographic contrast, flat surfaces, hairline borders, one solid primary action. | Its warm bone palette was replaced by a cool-neutral one because `design-taste-frontend` rejects cream defaults and because product photography across five categories needs a neutral canvas. Its placeholder-photo and icon-CDN suggestions were **not** followed: the NexaCart asset policy forbids third-party runtime images and fonts (AS-01). |
| `design-taste-frontend` | Yes | Dials, layout discipline, typography and colour rules, and its list of generic-template tells, applied to the home page, listings and product card (the storefront). | It targets landing pages and storefronts, not dashboards or multi-step tools, so it was **not** applied to checkout, account or admin. Its "generate images first, then fetch stock images" order was not used: no image-generation tool exists here and stock sources conflict with AS-01, so image slots are labelled placeholders. |
| `prototype` | Yes | Three genuinely different directions built as one self-contained HTML file with a picker (§2.3). | The skill refers to a shared `PICKER.md` that is **not present** in this environment, so the picker is a small purpose-built toolbar (keys 1, 2, 3 or arrows), not the skill's canonical chrome. |
| `brandkit` | Yes | Brand strategy, logo reasoning (one idea, simple geometry) and kit structure (§3). | It is built for image generation, which is unavailable. It produced no raster brand board; a vector logo concept sheet was drawn by hand instead (`nexacart-logo-concepts.svg`). |
| `impeccable` | Partly | Its `SKILL.md` is present and its principles were applied: surfaces are treated by what the visitor must do (persuade on home and listings, operate on cart, checkout, account and admin). | Its launcher script and reference files (including the craft floor and critique references) are **missing**, so context loading and its formal critique pass did not run. The design critique in §1.6 was done manually. |
| `mobile-native` | Yes | Mobile baseline: 16 px inputs, 44 px targets, safe areas, `dvh`, no hover-only behaviour, sticky bars (§9, §10). | None. |
| `emil-design-eng` | Yes | Motion decisions: animate only when it gives feedback, short ease-out transitions, no animation on frequent actions, reduced-motion handling (§11). | None. |
| `apple-design` | Yes (optional) | Read for interruptibility, response latency and reduced-motion principles; restrained use (sheets and dialogs respond immediately and can be dismissed at any time). | No gestures or spring physics were specified; the PRD does not call for them. |

### 1.6 Method and verification limits
- Wireframes were generated from structured definitions so every box aligns; they are text, not images.
- The prototype was checked in a DOM simulator (no script errors, picker, filter, wishlist and menu behaviour work, no network references) and by computing contrast ratios. **It was not rendered in a real browser** (none is available here), so layout polish, spacing and responsive appearance of the prototype have not been visually inspected. Treat it as a direction sample, not a verified design.
- Palette contrast ratios in §3 and §10 were computed, not estimated.
- A manual design critique against the principles in §2 is recorded in §14.6.

## 2. Design principles and visual positioning

### 2.1 Positioning
NexaCart is a **credible, premium-feeling consumer retailer for technology and sport**. It should look like a store people would trust with a real purchase: quiet confidence, strong product photography, prices that are easy to read and honest about what will be charged. It is also a demonstration product: the interface must make fictional listings and simulated payment unmistakable without feeling apologetic.

### 2.2 Principles

| ID | Principle | What it means in practice |
|---|---|---|
| DP-01 | The product is the hero | Photography carries colour and personality; the interface stays neutral so five very different categories feel cohesive. |
| DP-02 | Price and availability are never ambiguous | Price, delivery cost, discount and total are always visible where a decision is made; availability is a text label, never colour alone; the server's numbers are the only numbers shown. |
| DP-03 | Say what will happen before it happens | Rules are stated up front (password rules, minimum order, simulated payment, what cancelling does), not discovered through errors. |
| DP-04 | Every state is designed | Loading, empty, error, unavailable, locked and pending states have the same care as the happy path (§8). |
| DP-05 | Calm, honest checkout | The checkout removes distractions, keeps the total in view, makes the simulation explicit and never implies a failed payment lost the reservation. |
| DP-06 | Restraint over decoration | One accent colour, flat surfaces, hairline borders, almost no shadows, no decorative animation (§11). |
| DP-07 | Accessible by construction | WCAG 2.2 AA is a design constraint, not a late audit: contrast, focus, targets, labels and reduced motion are specified here (§10). |
| DP-08 | Deterministic and testable | Fixed layouts, local assets, stable test identifiers and no runtime third-party dependencies, so UI automation is reliable (TR-001, TR-013). |

### 2.3 Direction exploration

Three directions were prototyped on the same home page and product card, using the same content and the same real interactions (category filter, wishlist toggle, mobile menu). Open `docs/planning/design/prototypes/home-direction-picker.html` in a browser; press 1, 2 or 3 to switch. Each direction varies a named axis.

| | **A: Gallery** | **B: Catalogue** | **C: Court** |
|---|---|---|---|
| Axis | Whitespace and typography lead; editorial rhythm | Information density and comparison; utility lead | Colour energy and contrast; sport-culture personality |
| Canvas and palette | White, cool greys, near-black ink, one cobalt accent | Pale grey-green canvas, white cards, deep green accent | Near-black canvas, white text, lime accent |
| Layout | Asymmetric hero, bento category tiles, four-column product row, generous spacing | Offer cards, persistent category rail, four-to-five-column bordered cards | Full-bleed colour hero, horizontal category rail, large cards with price pills |
| Product card | Borderless, 4:5 image, quiet text, price in semibold | Bordered, 1:1 image, large bold price, availability dot | Dark panel, 1:1 image, price as a lime pill |
| Density and motion | Low density, minimal motion | High density, minimal motion | Medium density, bolder type, minimal motion |
| Strength | Lets very different products look cohesive; most credible and premium; easiest to keep accessible | Fastest scanning of many similar items; strong promotions | Distinct, energetic; suits football and sneakers |
| Risk | Depends on strong photography; fewer products per screen | Can feel like a generic marketplace; cluttered with sparse data | Alienates the technology and audio categories; contrast and fatigue risks; heavy colour blocks are costly to keep deterministic |

**Approved visual direction: Gallery (A), confirmed by the owner on 2026-10-20.** Reasons: (1) NexaCart sells computers, phones, audio, football shirts and sneakers; the only thing they share is that they are well photographed, so a neutral canvas is the one treatment that suits all five. (2) It reads as a credible consumer retail product and keeps price and availability readable, which is the quality the PRD's risk areas depend on. (3) A neutral palette with one accent makes AA contrast simple and keeps the number of assets and design variants small. (4) It matches the requested leading candidate (premium, editorial, minimalist). (5) Static, restrained layouts are the easiest to test deterministically.

**Trade-offs accepted:** whitespace shows fewer products per screen than the Catalogue direction; photography quality matters more (see §12); the look is quieter, so promotion must be handled with clear copy and one accent, not colour blocks. **What is deliberately not borrowed:** no hybrid of the three. The Catalogue's density and the Court's colour blocks are rejected, not blended in. A modest idea from Catalogue, an availability marker with a text label, is already required by FR-024 and is used in Gallery's own style.

## 3. Brand identity

### 3.1 Brand strategy
- **Essence:** one clear route from discovery to doorstep.
- **Personality:** precise, calm, confident, friendly without chatter.
- **Voice:** plain English, sentence case, short sentences, concrete numbers. No exclamation marks, no hype, no jargon. Errors say what happened and what to do next.
- **What the brand is not:** loud, discount-driven, gamer-neon, or imitation of any real retailer. Brand and club names in listings are used only as product references (BR-017).

### 3.2 Logo direction
The mark is a single continuous **N-shaped path ending in a dot**: the shopper's route from start to arrival. It uses simple geometry that survives at 16 px (tab icon and favicon). The wordmark "NexaCart" is set in the brand typeface with tight tracking, weight 700.
- Concept sheet: `docs/planning/design/brand/nexacart-logo-concepts.svg` (primary lockup, reversed lockup, small sizes). The owner approved the N-and-dot concept on 2026-10-20. This remains concept artwork, not a production-ready logo asset; prepare final artwork and convert the wordmark to outlines as a separate brand-production task. Geist is already approved under DQ-17.
- **Clear space:** equal to the dot diameter on all sides. **Minimum size:** 16 px for the mark alone, 96 px wide for the lockup.
- **Colour use:** ink on light backgrounds, white on ink, dot in accent cobalt (lightened to `#8FA6FF` on ink). Never place the logo on photography without a solid or scrimmed area behind it.
- **Misuse:** no outlines or shadows, no stretching, no recolouring outside the palette, no use of the mark as an icon for "cart" (the cart has its own icon).

### 3.3 Colour palette
One accent, cool neutrals, restrained semantic colours. All values are HEX; every text pairing in §3.3 and §10 meets WCAG 2.2 AA.

| Token | HEX | Role |
|---|---|---|
| `--color-canvas` | `#FFFFFF` | Page background, cards |
| `--color-surface-1` | `#F6F7F8` | Image slots, panels, subtle sections |
| `--color-surface-2` | `#ECEEF0` | Neutral pills, selected rows, disabled backgrounds |
| `--color-border-subtle` | `#DDE0E4` | Dividers and card edges (decorative) |
| `--color-border-control` | `#8B919B` | Input, select, checkbox and radio borders |
| `--color-text-muted` | `#5B616B` | Secondary text, captions |
| `--color-text-body` | `#2A2E35` | Body text |
| `--color-ink` | `#14161A` | Headings, primary button background, strong text |
| `--color-accent` | `#2447D6` | Links, focus ring, selected states, the logo dot |
| `--color-accent-tint` | `#E6EEFB` | Info background, selected tint |
| `--color-accent-on-ink` | `#8FA6FF` | Accent on dark surfaces (logo dot on ink) |
| `--color-success-bg` | `#EAF4EC` | Success background |
| `--color-success-text` | `#1F5A2B` | Success text |
| `--color-warning-bg` | `#FBF1D8` | Warning background |
| `--color-warning-text` | `#7A5200` | Warning text |
| `--color-error-bg` | `#FCE9EA` | Error background |
| `--color-error-text` | `#8F1F26` | Error text on error background |
| `--color-error-on-white` | `#9B1C23` | Error text on white |
| `--color-info-text` | `#1B3F9A` | Info text on info background |

**Semantic use (status pills and messages)**

| Meaning | Background | Text | Used for |
|---|---|---|---|
| Neutral | `#ECEEF0` | `#14161A` | Cancelled, Unpaid, Not applicable, Inactive |
| Info | `#E6EEFB` | `#1B3F9A` | Confirmed, Processing, Shipped |
| Success | `#EAF4EC` | `#1F5A2B` | Delivered, Paid, Refunded, In stock confirmations |
| Warning | `#FBF1D8` | `#7A5200` | Pending, Low stock, Refund pending, Price changed |
| Error | `#FCE9EA` | `#8F1F26` | Failed, Out of stock, validation and blocking messages |

Status wording and the mapping above were proposals and are approved (DQ-25). Meaning is always carried by **text and an icon**, never by colour alone.

**Contrast of key pairings (computed)**

| Foreground | Background | Use | Ratio | Requirement | Result |
|---|---|---|---|---|---|
| `#14161A` | `#FFFFFF` | Headings and strong text on canvas | 18.11:1 | 4.5:1 | Pass |
| `#2A2E35` | `#FFFFFF` | Body text on canvas | 13.63:1 | 4.5:1 | Pass |
| `#5B616B` | `#FFFFFF` | Muted text on canvas | 6.24:1 | 4.5:1 | Pass |
| `#5B616B` | `#F6F7F8` | Muted text on surface-1 | 5.81:1 | 4.5:1 | Pass |
| `#2447D6` | `#FFFFFF` | Links on canvas | 7.13:1 | 4.5:1 | Pass |
| `#2447D6` | `#F6F7F8` | Links on surface-1 | 6.64:1 | 4.5:1 | Pass |
| `#FFFFFF` | `#14161A` | Primary button label | 18.11:1 | 4.5:1 | Pass |
| `#9B1C23` | `#FFFFFF` | Error text on canvas | 8.13:1 | 4.5:1 | Pass |
| `#1F5A2B` | `#EAF4EC` | Success pill | 7.30:1 | 4.5:1 | Pass |
| `#7A5200` | `#FBF1D8` | Warning pill | 6.15:1 | 4.5:1 | Pass |
| `#8F1F26` | `#FCE9EA` | Error pill | 7.52:1 | 4.5:1 | Pass |
| `#1B3F9A` | `#E6EEFB` | Info pill | 8.09:1 | 4.5:1 | Pass |
| `#14161A` | `#ECEEF0` | Neutral pill | 15.57:1 | 4.5:1 | Pass |
| `#8B919B` | `#FFFFFF` | Control borders | 3.17:1 | 3:1 | Pass |
| `#2447D6` | `#FFFFFF` | Focus ring on canvas | 7.13:1 | 3:1 | Pass |
| `#8FA6FF` | `#14161A` | Logo dot on ink | 7.82:1 | 3:1 | Pass |

### 3.4 Typography
- **Typeface:** Geist Sans for interface and display, Geist Mono for SKUs, order numbers and idempotency keys. Both are published under the SIL Open Font License 1.1 (checked against the upstream `LICENSE.txt` of the Geist font repository). They are **self-hosted** from the application's own static files. Fallback stack: `"Geist", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`. Geist was approved on 2026-10-17 (DQ-17); the fallback stack stays as the safe default until the font files are in place.
- **Weights:** 400 body, 500 labels, 600 headings and prices, 700 wordmark only.
- **Numerals:** tabular figures for prices, quantities, totals and tables so columns align.
- **Never below 16 px** for form inputs (prevents mobile zoom on focus) or body text.

| Style | Mobile (size/line) | Desktop (size/line) | Weight and tracking | Use |
|---|---|---|---|---|
| Display | 36/40 | 56/58 | 600, -0.03em | Home hero only |
| Heading 1 | 28/32 | 40/44 | 600, -0.02em | Page titles |
| Heading 2 | 22/28 | 28/34 | 600, -0.02em | Section titles |
| Heading 3 | 18/24 | 20/26 | 600 | Card titles, panel titles |
| Body | 16/24 | 16/24 | 400 | Default text, maximum 65 characters per line |
| Body small | 14/20 | 14/20 | 400 | Secondary text, table cells |
| Caption | 13/18 | 13/18 | 500 | Labels, helper text, badges |
| Price | 18/24 | 20/24 | 600, tabular | Product and summary prices |
| Mono | 14/20 | 14/20 | 400 | SKU, order number, keys |
| Button | 16/24 | 16/24 | 600 | All buttons |

### 3.5 Iconography
- **Set:** Phosphor Icons (MIT licence, checked against the upstream `LICENSE`), regular weight for interface icons and fill weight for active states (for example a saved wishlist heart), on a 24 px grid, used as inline SVG from a self-hosted sprite (AS-03). No emoji anywhere. This set was approved on 2026-10-17 (DQ-18).
- **Roles:** an icon supports a label; it does not replace one. Icon-only buttons (menu, close, remove, wishlist) always have an accessible name.
- **Icons needed:** magnifying glass, heart, user, shopping bag (cart), list (menu), x (close), caret down, caret right, sliders (filters), check, warning, info, lock, package, truck, receipt, seal-check, plus, minus, trash, pencil. **No credit-card icon is used anywhere**, to avoid implying card entry (FR-066).

### 3.6 Usage rules

| Do | Do not |
|---|---|
| Use ink for the primary button and the accent for links, focus rings and selected states | Use the accent as a large background, or add a second accent colour |
| Use whitespace and hairline borders to separate content | Add shadows to cards, nest cards inside cards or use gradients |
| Keep image slots at a fixed ratio (4:5 product, 16:10 editorial) | Crop or stretch product photography inconsistently |
| Show a text label with every colour or icon that carries meaning | Convey status by colour alone |
| Write sentence case and plain numbers | Use all capitals, exclamation marks or promotional shouting |
| Use one primary button per view | Place two equally weighted primary actions side by side |

### 3.7 Imagery direction
Product images: even, soft lighting on a neutral surface, product centred with consistent padding, 4:5 ratio, a primary image plus up to seven more. Editorial and hero images: one product or one clear scene, no text baked into the image, no brand logos or crests visible, no recognisable real people. Football shirts are generic designs without club crests or sponsor marks. Sourcing, licensing and alt-text rules are in §12.

## 4. Design tokens

Tokens are named so they can become CSS custom properties without translation. Colour tokens are in §3.3; the rest follow.

### 4.1 Spacing, containers and grid

| Token | Value | Notes |
|---|---|---|
| `--space-0` … `--space-9` | 0, 4, 8, 12, 16, 24, 32, 48, 64, 96 px | 4 px base unit; only these values are used |
| Section rhythm | 48 px mobile, 64 px desktop | Vertical gap between page sections |
| `--container-content` | 1200 px (1320 px from 1440 px up) | Storefront content width, centred |
| `--container-narrow` | 640 px | Login, registration, account forms |
| `--container-prose` | 720 px | Long text |
| Page margin | 16 px (xs), 24 px (sm), 32 px (md), 40 px (lg) | Horizontal padding |
| Grid | xs 4 columns / 16 px gutter; sm 8 / 24; md and lg 12 / 24 | Listing columns: 2 (xs), 3 (sm), 4 (md and lg), so 12 items fill whole rows |

### 4.2 Borders, radii, shadows, layering

| Token | Value | Use |
|---|---|---|
| `--border-subtle` | 1 px `#DDE0E4` | Dividers and card edges (decorative) |
| `--border-control` | 1 px `#8B919B` | Input, select, checkbox and radio borders (3.17:1 against white, meeting the 3:1 non-text rule) |
| `--focus-ring` | 2 px `#2447D6` with a 2 px white offset | Every focusable element |
| `--radius-sm` / `--radius-md` / `--radius-pill` | 4 px / 8 px / 999 px | Inputs and buttons / cards, images, dialogs / status pills and filter chips |
| `--shadow-none` | none | Default for everything |
| `--shadow-overlay` | `0 8px 32px rgba(20,22,26,0.06)` | Dialogs, sheets and the category flyout only |
| `--z-sticky` / `--z-flyout` / `--z-dialog` / `--z-toast` | 20 / 30 / 40 / 50 | Layering scale |

### 4.3 Breakpoints and reference viewports

| Name | Range | Reference viewport | Behaviour |
|---|---|---|---|
| xs | 360 to 599 px | 375 × 812 | One-column flows, sheets, sticky bars, drawer navigation |
| sm | 600 to 1023 px | 768 × 1024 | Two-column forms, three-column grids, drawer navigation |
| md | 1024 to 1439 px | 1280 × 800 | Full header with flyout navigation, side rails, four-column grids |
| lg | 1440 to 1920 px | n/a | Same as md with the wider container; content never stretches past it |

Layouts are fluid between breakpoints; breakpoints change structure, not just size. The page must never scroll horizontally at any width from 360 to 1920 px (NFR-013).

### 4.4 CSS custom properties
See Appendix B for the complete token sheet as CSS.

## 5. Information architecture

### 5.1 Site map and routes
Route paths are illustrative. Final paths belong to the technical architecture, except the customer routes that the acceptance criteria already name (`/cart`, `/wishlist`, `/checkout`, `/account`, `/orders`; AC-089).

| Route (illustrative) | Screen | Access | Release | Source |
|---|---|---|---|---|
| `/` | SCR-01 Home | Everyone | R1 | FR-030 |
| `/c/:category` and `/c/:category/:subcategory` | SCR-02 Category listing | Everyone | R1 | FR-016 |
| `/search?q=` | SCR-03 Search results | Everyone | R1 | FR-018 |
| `/p/:slug` | SCR-04 Product detail (SCR-16 reviews on it in R2) | Everyone; inactive product shows not found | R1 | FR-022, FR-025 |
| `/cart` | SCR-05 Cart | Customer (guest redirected to login) | R1 | FR-006 |
| `/checkout` | SCR-07 Checkout | Customer | R1 | FR-052 |
| `/orders/:id/payment` | SCR-08B and SCR-08C | Owner of the order | R1 | FR-059 |
| `/orders/:id/confirmation` | SCR-08A | Owner of the order | R1 | FR-065 |
| `/orders` and `/orders/:id` | SCR-09, SCR-10 | Customer | R1 | FR-068, FR-069 |
| `/wishlist` | SCR-15 | Customer | R1 | FR-043 |
| `/account`, `/account/addresses`, `/account/password` | SCR-13, SCR-06, SCR-14 | Customer | R1 | FR-007, FR-011, FR-008 |
| `/login`, `/register` | SCR-11, SCR-12 | Guest | R1 | FR-003, FR-001 |
| `/admin/products`, `/admin/products/:id` | SCR-17, SCR-18 (SCR-19 is a dialog) | Administrator | R2 | FR-083 |
| `/admin/categories` | SCR-20 | Administrator | R2 | FR-089 |
| `/admin/orders`, `/admin/orders/:id` | SCR-21, SCR-22 | Administrator | R2 | FR-091, FR-092 |
| `/admin/audit` | SCR-23 | Administrator | R2 | FR-099 |
| error pages | 403 forbidden, 404 not found (ST-12) | Everyone | R1 | CL-08, FR-025 |

### 5.2 Global header
The header has one job: get the shopper to a product or to their cart in one action.

| Element | Desktop (md and up) | Mobile and tablet (below 1024 px) | Behaviour |
|---|---|---|---|
| Skip link | First focusable element | Same | "Skip to main content"; visible on focus |
| Demo-store notice (CMP-03) | Thin bar above the header | Same, single line | Always visible, not dismissible (FR-028) |
| Logo (CMP-01) | Left | Centre | Links to home |
| Category navigation (CMP-05) | Row under the logo bar, five items | Menu button opens a left drawer | See §5.3 |
| Search (CMP-04) | Wide field in the logo bar | Full-width field under the logo bar | See §5.4 |
| Wishlist, Account, Cart (CMP-02) | Right, icon with label | Wishlist and Cart icons right; Account inside the drawer | Cart shows an item count for customers (FR-040); counts are text, not colour dots |
| Stickiness | Sticky on scroll; collapses to the logo bar only | Sticky | Checkout uses a reduced, non-sticky header (logo and "Back to cart") |

Header variants by role:

| Role | Shows | Notes |
|---|---|---|
| Guest | Logo, search, categories, Wishlist and Cart (both lead to login), "Log in" and "Register" | No counts [P, DQ-03] |
| Customer | Logo, search, categories, Wishlist, Cart with count, Account menu (Profile, Addresses, Orders, Wishlist, Password, Log out) | FR-040 is Should |
| Administrator on the storefront | Logo, search, categories, an "Admin" link and Log out; no Wishlist, Cart or checkout controls | Admin accounts cannot use shopping operations (BR-065); approved (DQ-23) |
| Admin area | Own shell: side navigation (Products, Categories, Orders, Audit log), user name and Log out | R2 |

### 5.3 Category navigation
Five top-level categories, each with its subcategories (PRD §5.1). Desktop: hovering or focusing a category opens a flyout panel listing its subcategories and an "All" link; the panel is reachable and closable by keyboard (Esc). Mobile: a drawer with an accordion per category.

| Category | Subcategories |
|---|---|
| Computers & Tech | Desktop PCs, Gaming PCs, Custom-built PCs, Laptops, Monitors, Keyboards & Mice, Gaming Accessories, PC Components |
| Smartphones | iPhone-style, Samsung Galaxy-style, Xiaomi, Google Pixel-style, Entry-level |
| Wearables & Audio | Earbuds, Headphones & Gaming Headsets, Bluetooth Speakers, Smartwatches, Fitness Bands |
| Football & Apparel | Club Shirts, National Team Shirts, Training Tops & Sportswear |
| Shoes & Sneakers | Running, Casual Sneakers, Training, Sports Shoes |

A parent category lists the products of its subcategories (CL-07). The category tree allows two levels only (BR-061).

### 5.4 Search
A single text field in the header, 2 to 100 characters, submitted with Enter or the search button. It searches product name and brand case-insensitively (BR-014). The PRD defines no suggestions, history or typo tolerance, so none is designed (DEC-15). Results use SCR-03.

### 5.5 Account area
Customers reach Profile, Addresses, Orders, Wishlist and Password through the Account menu (header) and a section navigation inside the account area (CMP-28). Log out is in the Account menu only.

### 5.6 Footer
Category links, account links (Log in, Register, Orders, Wishlist), and the demo-store statement: "NexaCart is a demonstration store. All listings are fictional and carry no sponsorship or brand affiliation. Payments are simulated and no card details are collected." The PRD specifies no About, Contact, Returns or legal pages, so none is designed; adding them is a product decision (DQ-22).

### 5.7 Orientation aids
- **Breadcrumbs** on listings and product pages (CMP-07).
- **Page titles** follow "Page name | NexaCart"; exactly one `h1` per page.
- **Headings** are hierarchical; landmarks are `header`, `nav`, `main`, `footer`; the account and admin section navigations are labelled `nav` regions.

## 6. Screens and wireframes

Every screen below has a purpose, its release and requirement references, a desktop wireframe (about 1280 px) and a mobile wireframe (about 375 px), and a table that explains each numbered region. Wireframes show **hierarchy, layout, navigation and states**, not final styling. `{image}` marks a product or editorial image slot; `[P]` marks an element that began as a proposal and was approved as a design decision on 2026-10-17 (see §14). Release labels are on each screen; nothing marked R2 is available in R1.

### SCR-01 — Home
**Purpose:** Orient a first-time visitor in five seconds, offer category entry points and a short list of featured products, and state the demo and delivery context honestly.
**Release:** R1 · **Stories:** US-020, US-013, US-025 · **PRD:** FR-028, FR-030, FR-016, BR-017, BR-076 · **Mode:** persuade.
**Layout rules:** one hero, one asymmetric category block, one four-column featured row, then the footer. Each section has a different structure (hero, bento tiles, product row) so the page does not read as a stack of identical blocks. The hero image must be a generated or licensed product photograph (§12), never a placeholder in production.

**Desktop**
```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│      Demo store: listings are fictional; no sponsorship or brand affiliation is implied. (0)       │
├──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┤
│ NEXACART (1)     │ [ Search by product name or brand                   │ Wishlist (3)   Account    │
│                  │ ..................... ] (2)                         │ (4)   Cart 0 (5)          │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│ Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers (6) │
├───────────────────────────────────────────────────────────┬────────────────────────────────────────┤
│ (7) HERO                                                  │ {hero image slot, 4:5}                 │
│                                                           │ {generated or licensed                 │
│ Headline, two lines at most                               │ product photograph}                    │
│ One sentence of support, 20 words at most.                │                                        │
│                                                           │                                        │
│ [ Shop sneakers ]    Shop everything >                    │                                        │
│                                                           │                                        │
│                                                           │                                        │
├───────────────────────────────────────────────────────────┴────────────────────────────────────────┤
│ (8) Slim promo strip [P]: Free Standard delivery on a first order from R250.00 to under R1,000.00  │
├─────────────────────────────────────────────────┬────────────────────────┬─────────────────────────┤
│ (9) Shop by category                            │ {tile: Smartphones}    │ {tile: Wearables &      │
│ {tile: Computers & Tech}                        │                        │ Audio}                  │
│ large, image-led                                │ Smartphones >          │                         │
│                                                 │                        │ Wearables & Audio >     │
├─────────────────────────────────────────────────┴┬───────────────────────┴─────────────────────────┤
│ {tile: Football & Apparel}                       │ {tile: Shoes & Sneakers}                        │
│ Football shirts and training tops >              │ Running, casual, training >                     │
├──────────────────────────────────────────────────┴─────────────────────────────────────────────────┤
│ (10) Featured products                                                          View all products  │
│ >                                                                                                  │
├────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┤
│ {image 4:5}            │ {image 4:5}            │ {image 4:5}            │ {image 4:5}             │
│ Brand                  │ Brand                  │ Brand                  │ Brand                   │
│ Product name           │ Product name           │ Product name           │ Product name            │
│ 4.6 (23)               │ No reviews yet         │ 4.2 (8)                │ 4.8 (41)                │
│ From R6,999.00         │ From R1,299.00         │ From R899.00           │ From R1,799.00          │
│ In stock               │ Low stock              │ Fictional listing      │ Out of stock            │
├────────────────────────┴────────┬───────────────┴─────────────────┬──────┴─────────────────────────┤
│ (11) Footer                     │ Account                         │ Demo-store notice              │
│ Categories (5 links)            │ Login / Register                │ Fictional listings             │
│                                 │ Orders  Wishlist                │                                │
└─────────────────────────────────┴─────────────────────────────────┴────────────────────────────────┘
```

**Mobile**
```text
┌──────────────────────────────────┐
│  Demo store: fictional listings  │
│               (0)                │
├──────┬───────────┬──────┬────────┤
│ Menu │  NEXACART │ Wish │ Cart 0 │
│ (6)  │    (1)    │ (3)  │ (5)    │
├──────┴───────────┴──────┴────────┤
│ [ Search products or brands (2)  │
│ ]                                │
├──────────────────────────────────┤
│ {hero image slot 4:5}            │
│ Headline, 2 lines                │
│ One sentence of support.         │
│ [ Shop sneakers ]  (7)           │
├──────────────────────────────────┤
│ (8) Promo strip [P]: first-order │
│             delivery             │
├──────────────────────────────────┤
│ (9) Shop by category             │
├────────────────┬─────────────────┤
│ {tile}         │ {tile}          │
│ Computers &    │ Smartphones     │
│ Tech           │                 │
├────────────────┼─────────────────┤
│ {tile}         │ {tile}          │
│ Wearables &    │ Football &      │
│ Audio          │ Apparel         │
├────────────────┴─────────────────┤
│ {tile, full width}               │
│ Shoes & Sneakers                 │
├──────────────────────────────────┤
│ (10) Featured products   View    │
│ all >                            │
├────────────────┬─────────────────┤
│ {image}        │ {image}         │
│ Brand          │ Brand           │
│ Name           │ Name            │
│ 4.6 (23)       │ No reviews yet  │
│ From R6,999.00 │ From R1,299.00  │
├────────────────┴─────────────────┤
│ (11) Footer: links, demo notice  │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 0 | Demo-store notice | CMP-03 | Always visible, one line, not dismissible; states that listings are fictional and no affiliation is implied | FR-028, BR-017 |
| 1 | Logo | CMP-01 | Links to home | PRD §1 |
| 2 | Search | CMP-04 | Submits to search results; 2 to 100 characters | FR-018, BR-014 |
| 3-5 | Wishlist, Account, Cart | CMP-02 | Guests are sent to login from Wishlist and Cart; cart shows an item count for customers | FR-006, FR-038, FR-040 |
| 6 | Category navigation | CMP-05 | Five top-level categories; subcategories in a panel on desktop, accordion in the mobile drawer | FR-016 |
| 7 | Hero | CMP-30 | One headline (two lines at most), one sentence, one primary action and one text link | FR-030 |
| 8 | Promo strip [P] | CMP-31 | Static line limited to approved rules, filled from configuration values, not hard-coded (DQ-14) | BR-076, DEC-29 |
| 9 | Category tiles | CMP-32 | Image-led links to each category; two rows, asymmetric | FR-016, FR-030 |
| 10 | Featured products | CMP-10 | Four product cards; "View all products" link | FR-030 |
| 11 | Footer | CMP-06 | Category links, account links, demo-store notice; no legal or help pages are specified in the PRD (DQ-22) | FR-028 |

### SCR-02 — Category listing
**Purpose:** Let a shopper scan a category quickly, compare price and rating at a glance and move to a product.
**Release:** R1 · **Stories:** US-013, US-014, US-017, US-018, US-019, US-023, US-056 · **PRD:** FR-016, FR-017, FR-020, FR-021, FR-024, FR-026, FR-027, BR-010, BR-012, BR-015, BR-016, CL-01, CL-07, CL-13 · **Mode:** persuade (browse).
**Layout rules:** 12 items per page by default (4 columns desktop, 3 tablet, 2 mobile, so every page is full rows); the filter panel is a left rail on desktop and a bottom sheet on mobile; sorting is a single select; the view state is mirrored in the URL (FR-027).

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Home > Smartphones                                                       (1) Breadcrumb            │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (2) Smartphones                          48 products                            Sort: [ Newest v ] │
│ (3)                                                                                                │
├────────────────────┬───────────────────────────────────────────────────────────────────────────────┤
│ (4) FILTERS        │ (5) Product grid, 12 per page, 4 columns                                      │
│ Category           │ {img}  {img}  {img}  {img}                                                    │
│ ( ) All            │ Brand  Brand  Brand  Brand                                                    │
│ smartphones        │ Name   Name   Name   Name                                                     │
│ (o) Entry-level    │ 4.6 (23)  No reviews  4.1 (9)  4.8 (41)                                       │
│ ( ) Samsung-style  │ From R6,999.00  From R2,499.00  From R4,199.00  From R15,999.00               │
│ Brand              │ In stock  Low stock  In stock  Out of stock                                   │
│ [x] Kestrel  [ ]   │ ... (rows 2 and 3 repeat the same card)                                       │
│ Orbit              │                                                                               │
│ Price (R)          │                                                                               │
│ [ min ] to [ max ] │                                                                               │
│ [ ] In stock only  │                                                                               │
│ [ Reset filters ]  │                                                                               │
├────────────────────┴───────────────────────────────────────────────────────────────────────────────┤
│                    (6) < Previous    1   2   3   4    Next >      (page 1 of 4)                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ [ Search products or brands ]    │
├──────────────────────────────────┤
│ Home > Smartphones (1)           │
├──────────────────────────────────┤
│ (2) Smartphones   48 products    │
├────────────────┬─────────────────┤
│ [ Filters (4)  │ [ Sort: Newest  │
│ ]              │ v (3) ]         │
├────────────────┼─────────────────┤
│ {img}          │ {img}           │
│ Brand          │ Brand           │
│ Name           │ Name            │
│ 4.6 (23)       │ No reviews      │
│ From R6,999.00 │ From R2,499.00  │
│ In stock       │ Low stock       │
├────────────────┼─────────────────┤
│ {img}          │ {img}           │
│ Brand          │ Brand           │
│ Name           │ Name            │
│ 4.1 (9)        │ 4.8 (41)        │
│ From R4,199.00 │ From R15,999.00 │
│                │ Out of stock    │
├────────────────┴─────────────────┤
│  ... 12 per page, 2 columns (5)  │
├──────────────────────────────────┤
│   (6) < Prev   1 of 4   Next >   │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Breadcrumb | CMP-07 | Home, category, subcategory; current page is not a link | FR-016 |
| 2 | Title and count | Heading | Category name and number of visible products | FR-017 |
| 3 | Sort | CMP-08 | Newest (default), price low to high, price high to low, rating | FR-020, BR-015 |
| 4 | Filters | CMP-09 | Category tree, brands (several), price min and max, in-stock only, reset | FR-019 |
| 5 | Product grid | CMP-10 | Cards show brand, name, rating and count or "No reviews yet", "From" price, availability; football shirts show "Fictional listing" | FR-017, FR-024, FR-028 |
| 6 | Pagination | CMP-11 | Previous, numbered pages, next; a page beyond the last shows the empty state | FR-021, BR-016 |

### SCR-03 — Search results, filtering and sorting
**Purpose:** Show that the shopper's search and filters are understood, make every active condition visible and removable, and recover cleanly from no results.
**Release:** R1 · **Stories:** US-015, US-016, US-017, US-018, US-019 · **PRD:** FR-018, FR-019, FR-020, FR-026, FR-027, BR-014, BR-015, DEC-15 · **Mode:** persuade (browse).
**Layout rules:** same grid and card as SCR-02. Active filters appear as removable chips above the grid. There is no search suggestion list, typo correction or relevance ranking because the PRD does not provide them (DEC-15).

**Desktop (results, active filters and the empty state)**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ adidas-style ........................ ] x         │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (1) Results for "runner"   17 products                              Sort: [ Price: low to high v ] │
│ (2)                                                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (3) Active filters:  [ Brand: Stride x ]  [ R500 - R2,000 x ]  [ In stock only x ]   Clear all     │
├────────────────────┬───────────────────────────────────────────────────────────────────────────────┤
│ (4) FILTERS        │ (5) Result grid (same product card)                                           │
│ Category (tree)    │                                                                               │
│ Brand              │ Empty result state (6): "No products match these filters."                    │
│ (multi-select)     │ [ Reset filters ]   [ Change search ]                                         │
│ Price min / max    │                                                                               │
│ In stock only      │                                                                               │
└────────────────────┴───────────────────────────────────────────────────────────────────────────────┘
```

**Mobile (filter sheet)**
```text
┌──────────────────────────────────┐
│  FILTER SHEET (4)   [ Close x ]  │
├──────────────────────────────────┤
│ Category (tree)                  │
│ ( ) All  (o) Running  ( ) Casual │
├──────────────────────────────────┤
│ Brand                            │
│ [x] Stride   [ ] Court Line      │
├──────────────────────────────────┤
│ Price (R)                        │
│ [ min ] to [ max ]               │
├──────────────────────────────────┤
│ [ ] In stock only                │
├────────────────┬─────────────────┤
│ [ Reset ]      │ [ Show 17       │
│                │ results ]       │
├────────────────┴─────────────────┤
│ Sheet slides up; focus moves to  │
│  it; Esc or Close returns focus  │
│      to the Filters button       │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Results heading | Heading | Search term and result count | FR-018 |
| 2 | Sort | CMP-08 | As SCR-02 | FR-020 |
| 3 | Active filter chips | CMP-12 | One chip per active filter; removing a chip updates the URL and results; "Clear all" | FR-019, FR-027 |
| 4 | Filters or filter sheet | CMP-09 | Bottom sheet on mobile with a result count on the apply button; focus is trapped while open | FR-019, UI-24 |
| 5 | Result grid | CMP-10 | Same cards as SCR-02 | FR-017 |
| 6 | Empty state | CMP-26 | Says nothing matches; offers "Reset filters" and "Change search" | FR-026 |

### SCR-04 — Product detail and variant selection
**Purpose:** Give enough evidence to decide (images, price, specifications, rating) and make the variant, availability and quantity unmistakable so "Add to cart" never surprises the buyer.
**Release:** R1 (reviews section R2) · **Stories:** US-021, US-022, US-023, US-024, US-025, US-026, US-030, US-032, US-056 · **PRD:** FR-022, FR-023, FR-024, FR-025, FR-028, FR-029, FR-032, FR-035, BR-010, BR-012, BR-017, BR-018, CL-13 · **Mode:** persuade.
**Layout rules:** two columns on desktop (gallery, then buy box); on mobile the gallery comes first, the buy box follows, and a sticky "Add to cart" bar appears when the main button scrolls out of view. Price and availability always describe the **selected variant**. Unavailable option values stay visible but disabled, with the reason as text.

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Home > Shoes & Sneakers > Running > Stride Run 2                          (1) Breadcrumb           │
├──────────────────────────────────────────────────┬─────────────────────────────────────────────────┤
│ (2) Gallery                                      │ (3) Brand                                       │
│ {primary image, 4:5}                             │ (4) Stride Run 2 running shoe                   │
│ {thumb} {thumb} {thumb} {thumb}  (1 to 8 images, │ 4.5 (12 reviews)                                │
│ alt text on each)                                │ (5) R1,799.00   (price of the selected variant) │
│                                                  │ SKU  STR-RUN2-BLK-9                             │
│                                                  │ (6) Availability: In stock | Low stock | Out of │
│                                                  │ stock                                           │
│                                                  │ (7) Colour:  (o) Black  ( ) Grey  ( ) Red       │
│                                                  │ (disabled: out of stock)                        │
│                                                  │ (7) Size (UK):  [3] [4] [5] [6] [7] [8] [9]     │
│                                                  │ [10]  (unavailable sizes disabled)              │
│                                                  │ (8) Quantity  [ - ] 1 [ + ]    max 10 or stock  │
│                                                  │ [ Add to cart ] (9)        [ Add to wishlist ]  │
│                                                  │ (10)                                            │
│                                                  │ Fictional listing: unofficial, no brand         │
│                                                  │ affiliation (11)                                │
├──────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ (12) Description                                 │ (13) Specifications                             │
│ Short paragraph of product copy.                 │ Upper material  Mesh                            │
│                                                  │ Sole  Foam                                      │
│                                                  │ Fit  Regular                                    │
├──────────────────────────────────────────────────┴─────────────────────────────────────────────────┤
│ (14) Reviews (R2): summary and list, see SCR-16                                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ Home > ... > Stride Run 2 (1)    │
├──────────────────────────────────┤
│ {primary image 4:5, swipe}       │
│ (2) o o o o  (1 to 8 images)     │
├──────────────────────────────────┤
│ (3) Stride                       │
│ (4) Stride Run 2                 │
│ 4.5 (12 reviews)                 │
│ (5) R1,799.00                    │
│ (6) In stock                     │
├──────────────────────────────────┤
│ (7) Colour                       │
│ (o) Black ( ) Grey ( ) Red -     │
│ Size (UK)                        │
│ [3][4][5][6][7][8][9][10]        │
├──────────────────────────────────┤
│ (8) Quantity [ - ] 1 [ + ]       │
├──────────────────────────────────┤
│ [ Add to cart ] (9)              │
│ [ Add to wishlist ] (10)         │
├──────────────────────────────────┤
│ (11) Fictional listing:          │
│ unofficial                       │
├──────────────────────────────────┤
│ (12) Description v   (13)        │
│ Specifications v                 │
│ (14) Reviews v (R2)              │
├──────────────────────────────────┤
│   Add to cart stays reachable:   │
│    sticky bar when the button    │
│       scrolls out of view        │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Breadcrumb | CMP-07 | Category path to the product | FR-016 |
| 2 | Gallery | CMP-13 | One to eight images, one primary; thumbnails; every image has alt text; a placeholder image appears if an image is missing | FR-029 |
| 3-4 | Brand, name, rating | Heading, CMP-14 | Rating average and review count, or "No reviews yet" | FR-022, BR-060 |
| 5 | Price | CMP-15 | Price of the selected variant; tabular figures | BR-010 |
| 6 | Availability | CMP-16 | In stock, Low stock (1 to 5 units), Out of stock; text label plus icon, never colour alone | FR-024, BR-012 |
| 7 | Variant selectors | CMP-17 | Option groups (colour, size, storage); selecting updates price, SKU and availability; combinations with no active variant or no stock are disabled | FR-023 |
| 8 | Quantity | CMP-18 | Whole numbers 1 to 10, never above available stock | BR-018 |
| 9 | Add to cart | CMP-19 | Primary action; disabled with a reason when out of stock; guests are sent to login and the item is added afterwards | FR-032, FR-038, FR-024 |
| 10 | Wishlist | CMP-20 | Toggle with a pressed state; guests are sent to login | FR-041, FR-038 |
| 11 | Fictional notice | CMP-03 | Shown on every product, prominently on football shirts | FR-028, BR-017 |
| 12-13 | Description, specifications | CMP-21 | Disclosure sections; specifications as label and value pairs | FR-022 |
| 14 | Reviews | SCR-16 | R2 | FR-081 |

### SCR-05 — Cart, coupon and shipping summary
**Purpose:** Show exactly what will be charged, why, and what must be fixed before checkout; keep the shopper in control of coupon and delivery choices.
**Release:** R1 · **Stories:** US-027, US-028, US-029, US-030, US-031, US-035, US-036, US-037, US-038, US-039, US-043 · **PRD:** FR-031 to FR-040, FR-046, FR-047, FR-049, FR-050, FR-111 to FR-113, FR-116, BR-018, BR-020, BR-022, BR-025 to BR-029, BR-071, BR-076, BR-077 · **Mode:** operate.
**Layout rules:** lines on the left, a summary panel on the right (sticky on desktop, placed below the lines on mobile with a sticky Checkout bar). Every amount is a server value; the interface never computes a total itself. The wireframe shows a **first-time buyer** whose pre-coupon subtotal (R1,147.00) is above the free-Standard-delivery band; Standard delivery is R60.00 because first-order free delivery applies only below R1,000.00 (BR-076), with one informational flag (price changed) and one blocking flag (not enough stock), so Checkout is disabled.

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (1) Shopping cart (2 items)                                                                        │
├───────────────────────────────────────────────────────────┬────────────────────────────────────────┤
│ (2) LINES                                                 │ (4) SUMMARY                            │
│ {img}  Orbit Buds - Graphite     [ - ] 1 [ + ]   R649.00  │ Subtotal   R1,147.00                 │
│ Remove                                                    │ (5) Coupon  [ code ] [ Apply ]         │
│       Price changed: was R599.00, now R649.00 (3)         │ Applied: SAVE100  -R100.00  [ Remove ] │
│ ----------------------------------------------------      │ (6) Delivery                           │
│ {img}  Pulse Mouse - Black  [ - ] 2 [ + ]               │ (o) Standard R60.00; 3-5 business days │
│       Unit R249.00 each; line total R498.00             │ ( ) Express R120.00; 1-2 business days │
│ Remove                                                  │ First-order offer not applied (subtotal ≥ R1,000.00) (7)          │
│       Only 1 left: reduce the quantity (3)              │                                        │
│ Clear cart (secondary link)                               │ (8) Total  R1,107.00                 │
│                                                           │ [ Checkout ] (9) disabled: fix the     │
│                                                           │ flagged line (10)                      │
└───────────────────────────────────────────────────────────┴────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) Shopping cart (2 items)      │
├──────────────────────────────────┤
│ {img} Orbit Buds                 │
│ Graphite                         │
│ [ - ] 1 [ + ]  R649.00           │
│ Remove                           │
│ Price changed: was R599.00 (3)   │
│ (2)                              │
├──────────────────────────────────┤
│ {img} Pulse Mouse                │
│ Black                            │
│ [ - ] 2 [ + ] Unit R249.00       │
│ Line total R498.00                │
│ Only 1 left (3)                  │
├──────────────────────────────────┤
│ (4) Summary                      │
│ Subtotal R1,147.00               │
│ (5) Coupon [ code ] [Apply]      │
│ SAVE100 -R100.00 [Remove]        │
├──────────────────────────────────┤
│ (6) Delivery                     │
│ (o) Standard R60.00              │
│ ( ) Express R120.00              │
│ (7) First-order offer not        │
│     applicable (subtotal ≥        │
│     R1,000.00)                    │
├──────────────────────────────────┤
│ (8) Total R1,107.00              │
├──────────────────────────────────┤
│     (9) [ Checkout ] sticky,     │
│    disabled with reason (10)     │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Heading | Heading | Item count; empty cart uses CMP-26 with a way back to shopping | FR-036 |
| 2 | Cart lines | CMP-22 | Image, name, variant, quantity stepper, unit and line price, Remove; "Clear cart" asks for confirmation | FR-033, FR-034, DQ-08 |
| 3 | Line flags | CMP-23 | `price_changed` is informational (old and new price shown); `unavailable`, `out_of_stock`, `insufficient_stock` block checkout and say how to fix | FR-037, BR-022 |
| 4 | Summary | CMP-24 | Subtotal, discount, delivery, total; all from the server | FR-036, FR-039, BR-025 |
| 5 | Coupon | CMP-25 | Code field and Apply; applied coupon with Remove; rejection shows the specific reason | FR-046, FR-047 |
| 6 | Delivery option | CMP-27 | Standard and Express with fee and static estimate; fee shown is the one that applies to this cart | FR-049, FR-050, BR-028 |
| 7 | First-order offer | CMP-23 | Shown only when BR-076 applies; the line reads "Free Standard delivery on your first order" | BR-076 |
| 8 | Total | CMP-24 | Largest figure in the summary | FR-036 |
| 9-10 | Checkout | CMP-19 | Disabled with a visible reason (blocking line, below minimum, locked cart); the reason is linked with `aria-describedby` | FR-037, FR-116 |

### SCR-06 — Address management
**Purpose:** Let customers keep up to ten delivery addresses, choose a default, and understand every validation rule without a trial-and-error loop.
**Release:** R1 · **Stories:** US-010, US-011, US-012 · **PRD:** FR-011 to FR-015, BR-008, BR-009, DEC-17 · **Mode:** operate.
**Layout rules:** an account area with a section navigation (Profile, Addresses, Orders, Wishlist, Password); address cards in a grid; the form opens in a side panel on desktop and a full-screen sheet on mobile. The country is fixed to the configured delivery country and shown read-only. Deleting an address asks for confirmation [P, DQ-08]; deleting never changes past orders (US-012).

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (1) Account: Profile | Addresses | Orders | Wishlist | Password                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (2) Delivery addresses (3 of 10 saved)                                       [ Add address ] (3)   │
├─────────────────────────────────┬─────────────────────────────────┬────────────────────────────────┤
│ (4) Recipient name  [Default]   │ (4) Recipient name              │ (4) Recipient name             │
│ 12 Example Street               │ 4 Sample Road, Unit 2           │ 9 Test Avenue                  │
│ Pretoria, Gauteng, 0001         │ Cape Town, Western Cape, 8001   │ Durban, KwaZulu-Natal, 4001    │
│ 082 000 0000                    │ 083 000 0000                    │ 084 000 0000                   │
│ [ Edit ] [ Delete ]             │ [ Edit ] [ Delete ] [ Make      │ [ Edit ] [ Delete ] [ Make     │
│                                 │ default ]                       │ default ]                      │
├─────────────────────────────────┴─────────────────────────────────┴────────────────────────────────┤
│ (5) Address form (opens in a side panel; same fields for add and edit)                             │
├──────────────────────────────────────────────────┬─────────────────────────────────────────────────┤
│ Recipient name *   [..............]              │ City *   [..............]                       │
│ Phone *   [..............]                       │ Province *   [..............]                   │
│ Address line 1 *   [..............]              │ Postal code * (4 digits)   [....]               │
│ Address line 2   [..............]                │ Country   South Africa (fixed)                  │
├──────────────────────────────────────────────────┴─────────────────────────────────────────────────┤
│           [ Save address ]   [ Cancel ]        Field errors appear under each field (6)            │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (7) At 10 addresses: "Maximum of 10 addresses saved. Delete one to add another." Add button        │
│ disabled.                                                                                          │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) Account: Addresses v         │
├──────────────────────────────────┤
│ (2) Delivery addresses 3 of 10   │
├──────────────────────────────────┤
│ [ Add address ] (3)              │
├──────────────────────────────────┤
│ (4) Recipient name [Default]     │
│ 12 Example Street                │
│ Pretoria, Gauteng, 0001          │
│ 082 000 0000                     │
│ [ Edit ] [ Delete ]              │
├──────────────────────────────────┤
│ (4) Recipient name               │
│ 4 Sample Road, Unit 2            │
│ Cape Town, 8001                  │
│ [ Edit ] [ Delete ] [ Default ]  │
├──────────────────────────────────┤
│ (5) FORM (full-screen sheet)     │
│ Recipient name *                 │
│ Phone *                          │
│ Address line 1 *                 │
│ Address line 2                   │
│ City *  Province *               │
│ Postal code * (4 digits)         │
│ (6) errors under fields          │
│ [ Save address ] [ Cancel ]      │
├──────────────────────────────────┤
│ (7) Limit reached: Add disabled  │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Account navigation | CMP-28 | Current section marked with `aria-current="page"` | FR-006 |
| 2 | Heading | Heading | "3 of 10 saved" so the limit is visible | BR-008 |
| 3 | Add address | CMP-19 | Disabled at ten with an explanation | BR-008 |
| 4 | Address cards | CMP-29 | Recipient, lines, city, province, postal code, phone; "Default" badge; Edit, Delete, Make default | FR-011, FR-012 |
| 5 | Address form | CMP-33 | Recipient name, phone, line 1, line 2 (optional), city, province, postal code (4 digits); country read-only | BR-008, FR-013 |
| 6 | Field errors | CMP-34 | Under each field and summarised at the top; focus moves to the first error | FR-013, FR-108 |
| 7 | Limit state | CMP-23 | "Maximum of 10 addresses saved. Delete one to add another." | BR-008 |

### SCR-07 — Checkout review and simulated payment
**Purpose:** Let the customer confirm address, delivery option, coupon and items, choose a simulated payment outcome and place the order, with the total visible throughout.
**Release:** R1 · **Stories:** US-040, US-041, US-042, US-044, US-043, US-037, US-038, US-039, US-035 · **PRD:** FR-052 to FR-057, FR-066, FR-110, FR-115, BR-074, BR-068, BR-070, BR-071 · **Mode:** operate (trust and clarity over expression).
**Layout rules:** a **single page** with five labelled sections on the left and a sticky order summary on the right (DQ-13). The header is reduced to the logo and "Back to cart" to keep attention on the task. There are no card fields; the simulated payment control is explicit that nothing is charged. "Place order" is disabled until an address and a payment outcome are chosen and no blocking condition exists; the reason is shown next to the button. At checkout entry, if a pending order already exists, show the pending-order banner with **Pay now** and **Cancel order** and route the customer to that existing order; do not expose a second order-placement flow (FR-111, FR-112, CL-18).

**Desktop**
```text
┌────────────────────┬─────────────────────────────────────────────────┬─────────────────────────────┐
│ NEXACART           │           Checkout (simulated payment)          │              < Back to cart │
├────────────────────┴─────────────────────────────────────────────────┴─────────────────────────────┤
│ (1) Review and pay                                                                                 │
├───────────────────────────────────────────────────────────┬────────────────────────────────────────┤
│ (2) 1. Delivery address                                   │ (7) ORDER SUMMARY (sticky)             │
│ (o) Recipient name, 12 Example Street, Pretoria 0001      │ Subtotal   R1,799.00                   │
│ [Default]                                                 │ Discount   -R0.00                      │
│ ( ) 4 Sample Road, Cape Town 8001                         │ Delivery   R60.00                      │
│ [ + Add a new address ] (inline form, saved to your       │ Total   R1,859.00                      │
│ address book)                                             │                                        │
│                                                           │ (8) [ Place order ]                    │
│ (3) 2. Delivery option                                    │ Disabled until an address and a        │
│ (o) Standard   R60.00   3-5 business days                 │ payment outcome are chosen             │
│ ( ) Express   R120.00   1-2 business days                 │                                        │
│                                                           │ (9) Blocking messages appear here:     │
│ (4) 3. Coupon                                             │ price changed, below minimum order,    │
│ [ code ........ ] [ Apply ]     none applied              │ item unavailable, pending order exists │
│                                                           │                                        │
│ (5) 4. Items                                              │                                        │
│ Stride Run 2 - Black, UK 9   x1   R1,799.00               │                                        │
│                                                           │                                        │
│ (6) 5. Simulated payment                                  │                                        │
│ Simulation only. No card details are collected.           │                                        │
│ ( ) Approved   ( ) Declined   ( ) Timeout   ( )           │                                        │
│ Processing error                                          │                                        │
└───────────────────────────────────────────────────────────┴────────────────────────────────────────┘
```

**Mobile**
```text
┌────────┬────────────────┬────────┐
│ NEXACA │    Checkout    │ < Cart │
│ RT     │                │        │
├────────┴────────────────┴────────┤
│ (1) Review and pay               │
├──────────────────────────────────┤
│ (2) 1. Delivery address  v       │
│ (o) Recipient, 12 Example St     │
│ ( ) 4 Sample Road, Cape Town     │
│ [ + Add a new address ]          │
├──────────────────────────────────┤
│ (3) 2. Delivery option  v        │
│ (o) Standard R60.00 3-5 days     │
│ ( ) Express R120.00 1-2 days     │
├──────────────────────────────────┤
│ (4) 3. Coupon  v                 │
│ [ code ] [ Apply ]               │
├──────────────────────────────────┤
│ (5) 4. Items  v (1 item)         │
├──────────────────────────────────┤
│ (6) 5. Simulated payment         │
│ No card details collected.       │
│ ( ) Approved                     │
│ ( ) Declined                     │
│ ( ) Timeout                      │
│ ( ) Processing error             │
├──────────────────────────────────┤
│ (7) Total R1,859.00  details v   │
├──────────────────────────────────┤
│ (8) [ Place order ] sticky       │
│ (9) blocking message above it    │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Heading | Heading | "Review and pay" | FR-053 |
| 2 | Delivery address | CMP-35 | Saved addresses as radios, default preselected; inline "Add a new address" saves to the address book | FR-052, BR-009 |
| 3 | Delivery option | CMP-27 | Same options and fees as the cart | FR-049, FR-050 |
| 4 | Coupon | CMP-25 | Same behaviour as the cart | FR-046 |
| 5 | Items | CMP-22 (read-only) | Items and quantities; link back to the cart | FR-053 |
| 6 | Simulated payment | CMP-36 | Radio group: Approved, Declined, Timeout, Processing error; no card, CVV or expiry fields; nothing preselected [P, DQ-12] | FR-057, FR-066 |
| 7 | Order summary | CMP-24 | Subtotal, discount, delivery, total | FR-053 |
| 8 | Place order | CMP-19 | Starts placement, then payment; shows the waiting state (SCR-08C) | FR-110 |
| 9 | Blocking messages | CMP-23 | Price changed (with fresh totals), below minimum order, unavailable item, no address; each says how to fix it | FR-054, FR-116, BR-074 |

### SCR-08 — Payment results
**Purpose:** Tell the customer clearly what happened to their payment and what they can do next, without ever implying a failed payment lost their reservation.
**Release:** R1 · **Stories:** US-044, US-045, US-046, US-047, US-048, US-049, US-053 · **PRD:** FR-058 to FR-065, FR-114, BR-044, BR-047, BR-049, BR-069, BR-073 · **Mode:** operate.

#### SCR-08A — Payment approved (order confirmation)
**Layout rules:** the confirmation states the order number first; items, address and totals are the **snapshot taken at placement**; the three statuses are shown together; the cart is empty and unlocked.

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├─────────────────────────────────┬──────────────────────────────────────────────────────────────────┤
│ (1) Order confirmed             │ (3) Items                                                        │
│ Thank you. Your simulated       │ Stride Run 2 - Black, UK 9   x1   R1,799.00                      │
│ payment was approved.           │                                                                  │
│                                 │ (4) Delivery address (as placed)                                 │
│ (2) Order number                │ Recipient name, 12 Example Street, Pretoria, Gauteng, 0001       │
│ NC-20261014-482913              │                                                                  │
│ Placed 14 Oct 2026, 10:42       │ (5) Totals                                                       │
│                                 │ Subtotal R1,799.00   Discount R0.00   Delivery R60.00   Total    │
│                                 │ R1,859.00                                                        │
├─────────────────────────────────┴──────────────────────────────────────────────────────────────────┤
│ (6) Order: Confirmed      Payment: Paid      Refund: Not applicable                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                            (7) [ View order ]     [ Continue shopping ]                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) Order confirmed              │
│ Your simulated payment was       │
│ approved.                        │
├──────────────────────────────────┤
│ (2) NC-20261014-482913           │
│ Placed 14 Oct 2026, 10:42        │
├──────────────────────────────────┤
│ (3) Stride Run 2 - Black, UK 9   │
│ x1  R1,799.00                    │
├──────────────────────────────────┤
│ (4) Delivered to                 │
│ Recipient name, 12 Example       │
│ Street, Pretoria 0001            │
├──────────────────────────────────┤
│ (5) Subtotal R1,799.00           │
│ Delivery R60.00                  │
│ Total R1,859.00                  │
├──────────────────────────────────┤
│ (6) Order Confirmed | Payment    │
│ Paid                             │
│ Refund Not applicable            │
├──────────────────────────────────┤
│ (7) [ View order ]               │
│ [ Continue shopping ]            │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Heading | Heading | "Order confirmed"; announced to assistive technology | FR-065 |
| 2 | Order number | CMP-37 | `NC-YYYYMMDD-NNNNNN`, selectable text; placement time | FR-070, BR-051 |
| 3-5 | Items, address, totals | CMP-38 | Snapshot values; subtotal, discount, delivery, total | FR-065, BR-050 |
| 6 | Statuses | CMP-39 | Order Confirmed, Payment Paid, Refund Not applicable | FR-069 |
| 7 | Actions | CMP-19 | View order; Continue shopping | FR-065 |

#### SCR-08B — Payment declined, timed out or failed (and attempts exhausted)
**Layout rules:** the heading and message change with the outcome (approved copy in §14.4). While the reservation is active, show **“Reserved until [time]”** on the payment page. The reservation deadline remains placement time plus 30 minutes; retries never extend it. The cart remains locked while the order is pending. After the third attempt only **Cancel order** remains. If the order has been cancelled or the reservation has expired, show that it is no longer payable and do not offer a retry (FR-114, CL-18).

**Desktop**
```text
┌────────────────────┬─────────────────────────────────────────────────┬─────────────────────────────┐
│ NEXACART           │           Checkout (simulated payment)          │              < Back to cart │
├────────────────────┴─────────────────────────────────────────────────┴─────────────────────────────┤
│ (1) Reserved until 14 Oct 2026, 11:12. Retry never extends deadline; cart remains locked.          │
├──────────────────────────────────────────────────┬─────────────────────────────────────────────────┤
│ (2) Payment declined | Payment timed out |       │ (4) Try again                                   │
│ Payment error                                    │ Simulated payment                               │
│ (heading and message depend on the outcome, see  │ ( ) Approved   ( ) Declined                     │
│ the copy table)                                  │ ( ) Timeout    ( ) Processing error             │
│                                                  │                                                 │
│ (3) Order NC-20261014-482913   Total R1,859.00   │ (5) [ Retry payment ]    [ Cancel order ]       │
│ Status: Pending      Payment: Failed             │                                                 │
│ Attempt 1 of 3 [P]                               │                                                 │
├──────────────────────────────────────────────────┴─────────────────────────────────────────────────┤
│   (6) After the third attempt: Retry and the outcome choices are removed; only [ Cancel order ]    │
│                                              remains                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌────────┬────────────────┬────────┐
│ NEXACA │    Checkout    │ < Cart │
│ RT     │                │        │
├────────┴────────────────┴────────┤
│ (1) Reserved until 14 Oct 2026,  │
│ 11:12; retries do not extend it  │
├──────────────────────────────────┤
│ (2) Payment declined             │
│ (or timed out, or error)         │
├──────────────────────────────────┤
│ (3) NC-20261014-482913           │
│ Total R1,859.00                  │
│ Pending | Payment Failed         │
│ Attempt 1 of 3 [P]               │
├──────────────────────────────────┤
│ (4) Simulated payment            │
│ ( ) Approved                     │
│ ( ) Declined                     │
│ ( ) Timeout                      │
│ ( ) Processing error             │
├──────────────────────────────────┤
│ (5) [ Retry payment ]            │
│ [ Cancel order ]                 │
├──────────────────────────────────┤
│   (6) Attempts exhausted: only   │
│              Cancel              │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Pending-order banner | CMP-40 | Shows “Reserved until [time]” while active; items are reserved and cart is locked; retries never extend deadline | FR-112, FR-059, CL-18 |
| 2 | Outcome heading | Heading | Declined, timed out or processing error | FR-059 to FR-061 |
| 3 | Order summary | CMP-38 | Order number, total, statuses; "Attempt 1 of 3" [P] | FR-062, BR-049 |
| 4 | Retry controls | CMP-36 | Same four outcomes; a new attempt on submit | FR-062 |
| 5 | Actions | CMP-19 | Retry payment; Cancel order (confirmation dialog, ST-13) | FR-072 |
| 6 | Exhausted note | CMP-23 | Retry and outcome choices are removed after attempt three | BR-049 |

#### SCR-08C — Payment in progress
**Layout rules:** shown for the simulated delay (the timeout outcome waits several seconds). While the reservation is active, keep “Reserved until [time]” visible; retries never extend the original 30-minute deadline. Use an indeterminate progress indicator, a sentence of explanation, all controls disabled, and announce the result automatically. If the order is cancelled or expires during the wait, show the “no longer payable” state, not an error screen (BR-073, CL-18).

```text
┌────────────────────┬─────────────────────────────────────────────────┬─────────────────────────────┐
│ NEXACART           │           Checkout (simulated payment)          │              < Back to cart │
├────────────────────┴─────────────────────────────────────────────────┴─────────────────────────────┤
│ Reserved until 14 Oct 2026, 11:12 — retry does not extend this deadline                            │
│                               (1) Processing your simulated payment                                │
│                                                                                                    │
│ [ ======>            ]  indeterminate progress                                                     │
│                                                                                                    │
│ This can take a few seconds. Please do not close this page.                                        │
│                                                                                                    │
│ (2) Controls are disabled. Result appears here automatically (announced to screen readers).        │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

On mobile the same content stacks in one column with the same behaviour.

### SCR-09 — Order history
**Purpose:** Let customers find any of their orders and see its state at a glance.
**Release:** R1 · **Stories:** US-050 · **PRD:** FR-068, BR-016, BR-064 · **Mode:** operate.
**Layout rules:** newest first, paginated like listings. The approved columns are order number, placement date, status, total and View (DQ-04). A pending order is visibly distinguished; View opens order detail with **Pay now**, while an eligible pending order can be cancelled (CL-18).

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (1) Account: Profile | Addresses | Orders | Wishlist | Password                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (2) Your orders                                                          12 orders, newest first   │
├─────────────────────────────┬───────────────────┬───────────────────┬───────────────────┬──────────┤
│ Order number                │ Placed            │ Status (pill)     │ Total             │ (3)      │
│ NC-20261014-482913          │ 14 Oct 2026       │ Pending           │ R1,859.00         │ View     │
│ NC-20261003-110224          │ 3 Oct 2026        │ Delivered         │ R799.00           │ View     │
│ NC-20260921-663901          │ 21 Sep 2026       │ Cancelled         │ R1,299.00         │ View     │
├─────────────────────────────┴───────────────────┴───────────────────┴───────────────────┴──────────┤
│ (4) Pending rows are distinguished; View opens the detail; eligible orders offer Cancel order     │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                  (5) < Previous   1   2   Next >                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) Account: Orders v            │
├──────────────────────────────────┤
│ (2) Your orders (12)             │
├──────────────────────────────────┤
│ (3) NC-20261014-482913   Pending │
│ 14 Oct 2026   R1,859.00   [ View │
│ ]                                │
├──────────────────────────────────┤
│ NC-20261003-110224   Delivered   │
│ 3 Oct 2026   R799.00   [ View ]  │
├──────────────────────────────────┤
│ NC-20260921-663901   Cancelled   │
│ 21 Sep 2026   R1,299.00   [ View │
│ ]                                │
├──────────────────────────────────┤
│   (5) < Prev   1 of 2   Next >   │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Account navigation | CMP-28 | Orders marked current | FR-006 |
| 2 | Heading | Heading | Number of orders | FR-068 |
| 3 | Order rows | CMP-41 | Order number (links to detail), date, status pill (text plus colour), total | FR-068 |
| 4 | Pending note | CMP-23 | Distinguish pending orders; eligible pending orders offer Cancel order; View opens detail with Pay now | FR-072, CL-18 |
| 5 | Pagination | CMP-11 | As listings | BR-016 |
| - | Empty state | CMP-26 | "You have no orders yet" with a link to shop | FR-068 |

### SCR-10 — Order detail
**Purpose:** Show exactly what was bought, where it goes and what has happened to the order and its money.
**Release:** R1 (refund and paid-cancellation parts R2) · **Stories:** US-051, US-052, US-053, US-054, US-055, US-012, US-043, US-044 · **PRD:** FR-069, FR-070, FR-072, FR-073, FR-074, FR-076, FR-112, CL-18, BR-029, BR-043, BR-050, BR-052, BR-053, BR-056, DEC-26 · **Mode:** operate.
**Layout rules:** all figures are the snapshot taken at placement and never change. Status, payment status and refund status are always shown together. For an active `pending` order, show **“Reserved until [time]”** using the original reservation deadline and provide **Pay now**; payment retries never extend the 30-minute deadline. An expired pending order is shown as cancelled and non-payable. In R1 refund status is “Not applicable” on every order, and **Cancel order** appears only on a `pending` order (DEC-26); from R2 it also appears on a `confirmed` order, with wording that explains the full refund. The status history is oldest first (CL-18).

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (1) < Orders    Order NC-20261014-482913   Placed 14 Oct 2026, 10:42                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (2) Order: Confirmed      Payment: Paid      Refund: Not applicable                                │
├───────────────────────────────────────────────────────────┬────────────────────────────────────────┤
│ (3) Items (snapshot at purchase)                          │ (5) Totals                             │
│ Stride Run 2 - Black, UK 9   SKU STR-RUN2-BLK-9           │ Subtotal   R1,799.00                   │
│ Unit R1,799.00   Qty 1   Line R1,799.00                   │ Discount   -R0.00                      │
│                                                           │ Delivery   R60.00                      │
│ (4) Delivery address (as placed)                          │ Total   R1,859.00                      │
│ Recipient name, 12 Example Street, Pretoria, Gauteng,     │                                        │
│ 0001                                                      │ (6) Actions                            │
│                                                           │ [ Cancel order ] pending in R1,        │
│                                                           │ confirmed from R2                      │
├───────────────────────────────────────────────────────────┴────────────────────────────────────────┤
│ (7) Status history (oldest first)                                                                  │
│ 14 Oct 2026 10:42   Pending -> Confirmed   system (approved payment)                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) < Orders                     │
│ Order NC-20261014-482913         │
│ Placed 14 Oct 2026, 10:42        │
├──────────────────────────────────┤
│ (2) Confirmed | Paid | Refund    │
│ n/a                              │
├──────────────────────────────────┤
│ (3) Stride Run 2 - Black, UK 9   │
│ SKU STR-RUN2-BLK-9               │
│ 1 x R1,799.00                    │
├──────────────────────────────────┤
│ (4) Delivered to                 │
│ Recipient name, 12 Example St    │
├──────────────────────────────────┤
│ (5) Subtotal R1,799.00           │
│ Delivery R60.00                  │
│ Total R1,859.00                  │
├──────────────────────────────────┤
│ (7) History                      │
│ 14 Oct 10:42 Pending > Confirmed │
├──────────────────────────────────┤
│ (6) [ Cancel order ] when        │
│ allowed                          │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Header | Heading | Order number and placement time; back to orders | FR-070 |
| 2 | Statuses | CMP-39 | Order, payment (`unpaid`, `failed`, `paid`), refund (`not_applicable`, `refund_pending`, `refunded`) | BR-043, BR-044, BR-056 |
| 3 | Items | CMP-38 | Name, variant, SKU, unit price, quantity, line total | BR-050 |
| 4 | Delivery address | CMP-38 | Snapshot | BR-050 |
| 5 | Totals | CMP-24 | Subtotal, discount, delivery, total (total = subtotal minus discount plus delivery) | BR-029 |
| 6 | Actions | CMP-19 | Cancel order (R1 pending; R2 also confirmed) with confirmation | FR-072, FR-073 |
| 7 | Status history | CMP-42 | Chronological list: from, to, who, when (UTC shown in local time with the timezone named) | FR-076, BR-052 |

### SCR-11 — Login
**Purpose:** Get a returning user into their account with one clear form and one clear failure message.
**Release:** R1 · **Stories:** US-002, US-003, US-005, US-006 · **PRD:** FR-003, FR-005, FR-009, BR-004, BR-007 · **Mode:** operate.
**Layout rules:** a single narrow column with a reduced header. One generic error for every credential failure. There is **no forgot-password link**, because password reset by email is a non-goal (NG-02). After login the user returns to the page they came from (FR-005).

**Desktop**
```text
┌────────────────────┬─────────────────────────────────────────────────┬─────────────────────────────┐
│ NEXACART           │           Checkout (simulated payment)          │              < Back to cart │
├────────────────────┴─────────────────────────────────────────────────┴─────────────────────────────┤
│                                             (1) Log in                                             │
│                                                                                                    │
│ Email *  [......................................]                                                  │
│ Password *  [......................................]                                               │
│                                                                                                    │
│ [ Log in ]                                                                                         │
│                                                                                                    │
│ New here?  Create an account (2)                                                                   │
│                                                                                                    │
│ (3) Errors: "Email or password is incorrect." (same text for any failure) | "Too many attempts.    │
│ Try again later."                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌────────┬────────────────┬────────┐
│ NEXACA │    Checkout    │ < Cart │
│ RT     │                │        │
├────────┴────────────────┴────────┤
│ (1) Log in                       │
├──────────────────────────────────┤
│ Email *                          │
│ [ ............................ ] │
│ Password *                       │
│ [ ............................ ] │
├──────────────────────────────────┤
│ [ Log in ]                       │
├──────────────────────────────────┤
│ New here? Create an account (2)  │
├──────────────────────────────────┤
│ (3) Error banner above the form  │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Form | CMP-33 | Email and password, labelled; browser autofill allowed (`autocomplete="username"` and `"current-password"`) | FR-003 |
| 2 | Register link | Link | "Create an account" | FR-001 |
| 3 | Errors | CMP-34 | One generic message for wrong email or password; a "try again later" message when locked | BR-004, BR-007 |

### SCR-12 — Registration
**Purpose:** Create an account with the fewest possible fields and no verification step.
**Release:** R1 · **Stories:** US-001 · **PRD:** FR-001, FR-002, BR-001 to BR-003, NG-02, DEC-27 · **Mode:** operate.
**Layout rules:** name, email, password. The password rule is shown **before** the user types, not only after an error. On success the app signs the user in and returns them to where they were; there is no email or code step.

**Desktop**
```text
┌────────────────────┬─────────────────────────────────────────────────┬─────────────────────────────┐
│ NEXACART           │           Checkout (simulated payment)          │              < Back to cart │
├────────────────────┴─────────────────────────────────────────────────┴─────────────────────────────┤
│                                      (1) Create your account                                       │
│                                                                                                    │
│ Name *  [......................................]                                                   │
│ Email *  [......................................]                                                  │
│ Password *  [......................................]                                               │
│ 8 to 128 characters, at least one letter and one digit (2)                                         │
│                                                                                                    │
│ [ Create account ]                                                                                 │
│                                                                                                    │
│ Already registered?  Log in                                                                        │
│                                                                                                    │
│ (3) After success the app signs you in and returns you to where you were. No email step.           │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌────────┬────────────────┬────────┐
│ NEXACA │    Checkout    │ < Cart │
│ RT     │                │        │
├────────┴────────────────┴────────┤
│ (1) Create your account          │
├──────────────────────────────────┤
│ Name *                           │
│ [ ......................... ]    │
│ Email *                          │
│ [ ......................... ]    │
│ Password *                       │
│ [ ......................... ]    │
│ (2) 8-128 characters, a letter   │
│ and a digit                      │
├──────────────────────────────────┤
│ [ Create account ]               │
├──────────────────────────────────┤
│ Already registered? Log in       │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Form | CMP-33 | Name, email, password (`autocomplete="name"`, `"email"`, `"new-password"`) | BR-001 to BR-003 |
| 2 | Password rule | CMP-34 | "8 to 128 characters, at least one letter and one digit"; linked to the field with `aria-describedby` | BR-001 |
| 3 | Success path | n/a | Automatic sign-in; failure falls back to login with a notice | DEC-27, US-001 |

### SCR-13 — Profile
**Purpose:** Let customers correct their name and phone number.
**Release:** R1 · **Stories:** US-007, US-004 · **PRD:** FR-007, BR-003, DEC-04 · **Mode:** operate.
**Layout rules:** the email address is shown as read-only text with a short explanation; it cannot be changed in the MVP. "Log out" lives in the account menu in the header (CMP-02), not on this page.

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├─────────────────────────┬──────────────────────────────────────────────────────────────────────────┤
│ (1) Account             │ (2) Profile                                                              │
│                 Profile │ Name *   [......................................]                        │
│ Addresses               │ Email   name@example.test  (read-only) (3)                               │
│ Orders                  │ Phone   [......................................]  optional, 7-15 digits  │
│ Wishlist                │                                                                          │
│ Password                │ [ Save changes ]      (4) Saved. confirmation, or field errors           │
└─────────────────────────┴──────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) Account: Profile v           │
├──────────────────────────────────┤
│ (2) Name *                       │
│ [ ......................... ]    │
│ Email (read-only) (3)            │
│ name@example.test                │
│ Phone                            │
│ [ ......................... ]    │
├──────────────────────────────────┤
│ [ Save changes ] (4)             │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Account navigation | CMP-28 | Profile marked current | FR-006 |
| 2 | Form | CMP-33 | Name (required), phone (optional, 7 to 15 digits) | BR-003 |
| 3 | Email | Text | Read-only, with "Email cannot be changed" | FR-007 |
| 4 | Feedback | CMP-43 | Saved confirmation or field errors | FR-013 |

### SCR-14 — Change password
**Purpose:** Let customers change their password safely.
**Release:** R1 · **Stories:** US-008 · **PRD:** FR-008, BR-001, BR-005 · **Mode:** operate.
**Layout rules:** collect the current password and the compliant new password, with the rule shown up front. On success, invalidate all previously issued tokens, redirect the customer to login and show the confirmation there: “Password changed. Log in with your new password.” The customer must authenticate again using the new password (FR-008, CL-17).

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├─────────────────────────┬──────────────────────────────────────────────────────────────────────────┤
│ (1) Account             │ (2) Change password                                                      │
│ Profile                 │ Current password *   [......................................]            │
│ Addresses               │ New password *   [......................................]                │
│ Orders                  │ 8 to 128 characters, a letter and a digit; not your email; not the same  │
│ Wishlist                │ as the current one (3)                                                   │
│                Password │                                                                          │
│                         │ [ Update password ]                                                      │
│                         │                                                                          │
│                         │ (4) On success, redirect to login; confirmation appears on login page                 │
└─────────────────────────┴──────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) Account: Password v          │
├──────────────────────────────────┤
│ (2) Current password *           │
│ [ ......................... ]    │
│ New password *                   │
│ [ ......................... ]    │
│ (3) rules hint                   │
├──────────────────────────────────┤
│ [ Update password ]              │
├──────────────────────────────────┤
│ (4) Redirect to login             │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Account navigation | CMP-28 | Password marked current | FR-006 |
| 2 | Form | CMP-33 | Current and new password (`autocomplete="current-password"` and `"new-password"`) | FR-008 |
| 3 | Password rule | CMP-34 | Length, letter and digit, not your email, not the current password | BR-001 |
| 4 | Success transition | CMP-43 | Redirect to login; show confirmation there and require the new password | FR-008, CL-17, DQ-01 |

### SCR-15 — Wishlist
**Purpose:** Hold products for later and make moving them to the cart quick and honest about availability.
**Release:** R1 · **Stories:** US-032, US-033, US-034 · **PRD:** FR-041 to FR-045, BR-023 · **Mode:** operate (task) with product-card styling.
**Layout rules:** the same card as listings with a different action row. Unavailable items stay in the list with a clear label. A product with several variants shows "Choose variant", which opens a small dialog; a single-variant product moves straight to the cart. Moving is all-or-nothing.

**Desktop**
```text
┌──────────────────┬─────────────────────────────────────────────────────┬───────────────────────────┐
│ NEXACART         │ [ Search by product name or brand .......... ]      │ Wishlist  Account  Cart 2 │
├──────────────────┴─────────────────────────────────────────────────────┴───────────────────────────┤
│   Computers & Tech    Smartphones    Wearables & Audio    Football & Apparel    Shoes & Sneakers   │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (1) Account: Profile | Addresses | Orders | Wishlist | Password                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (2) Wishlist (4 items)                                                                             │
├────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┤
│ {image}                │ {image}                │ {image}                │ {image}                 │
│ Brand                  │ Brand                  │ Brand                  │ Brand                   │
│ Name                   │ Name                   │ Name                   │ Name                    │
│ From R649.00           │ From R1,299.00         │ No longer available    │ 3 variants              │
│ In stock               │ Out of stock (5)       │ (5)                    │ [ Choose variant ] (6)  │
│ [ Move to cart ] (3)   │ [ Move to cart ]       │ (product inactive)     │ Remove                  │
│ Remove (4)             │ disabled               │ Remove                 │                         │
│                        │ Remove                 │                        │                         │
└────────────────────────┴────────────────────────┴────────────────────────┴─────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────┬──────┬────────┐
│ Menu │  NEXACART │ Wish │ Cart 2 │
├──────┴───────────┴──────┴────────┤
│ (1) Account: Wishlist v          │
├──────────────────────────────────┤
│ (2) Wishlist (4 items)           │
├────────────────┬─────────────────┤
│ {image}        │ {image}         │
│ Brand          │ Brand           │
│ Name           │ Name            │
│ From R649.00   │ From R1,299.00  │
│ In stock       │ Out of stock    │
│ [ Move to cart │ (5)             │
│ ]              │ Remove          │
│ Remove         │                 │
├────────────────┼─────────────────┤
│ {image}        │ {image}         │
│ Brand          │ Brand           │
│ Name           │ Name            │
│ No longer      │ 3 variants      │
│ available      │ [ Choose        │
│ Remove         │ variant ] (6)   │
└────────────────┴─────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Account navigation | CMP-28 | Wishlist marked current | FR-006 |
| 2 | Heading | Heading | Item count | FR-043 |
| 3 | Move to cart | CMP-19 | Disabled when out of stock; the entry stays on any failure; locked cart shows the locked message | FR-044 |
| 4 | Remove | Link | Removes the entry (no confirmation, DQ-08) | FR-042 |
| 5 | Availability flags | CMP-16 | Out of stock, or "No longer available" for inactive products | FR-043 |
| 6 | Choose variant | CMP-44 | Dialog with the option selectors, then adds to the cart | FR-044 |

### SCR-16 — Product reviews (R2)
**Purpose:** Let shoppers read reviews and let customers who received a product rate it.
**Release:** R2 (read-only seeded ratings appear in R1 on listings and the product header) · **Stories:** US-057, US-058, US-059 · **PRD:** FR-077 to FR-082, BR-058 to BR-060, DEC-14 · **Mode:** persuade (reading) and operate (writing).
**Layout rules:** a summary (average and count) then the list, then the form. The form appears only for customers with a delivered order for the product; for everyone else it is absent. Comments are always shown as plain text. Show the reviewer's first name only, sort newest first, and paginate 10 reviews per page; customers cannot edit reviews after submission (DQ-05). An administrator hides a review using the Hide control on that review in the admin product editor; there is no Hide control on the public page (DQ-21).

**Desktop**
```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ (R2) Reviews section on the product page (SCR-04, item 14)                                         │
├─────────────────────────────────┬──────────────────────────────────────────────────────────────────┤
│ (1) Summary                     │ (2) Review list                                                  │
│ 4.5 out of 5                    │ 5 / 5   Comment text, shown as plain text.                       │
│ 12 reviews                      │ 4 / 5   Another comment.                                         │
│                                 │ First name only; newest first; 10 per page [DQ-05]                │
├─────────────────────────────────┴──────────────────────────────────────────────────────────────────┤
│ (3) Write a review (only after a delivered order)                                                  │
│ Rating *  ( ) 1  ( ) 2  ( ) 3  ( ) 4  ( ) 5                                                        │
│ Comment (optional)  [ ........................................ ]  0 / 1000                         │
│ [ Submit review ]      Messages: not eligible | already reviewed | invalid rating (4)              │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────────────────────────────────┐
│ (R2) Reviews (SCR-04 item 14)    │
├──────────────────────────────────┤
│ (1) 4.5 out of 5 - 12 reviews    │
├──────────────────────────────────┤
│ (2) 5 / 5  Comment text          │
│ 4 / 5  Another comment           │
├──────────────────────────────────┤
│ (3) Write a review               │
│ Rating *                         │
│ (1)(2)(3)(4)(5)                  │
│ Comment 0 / 1000                 │
│ [ ........................ ]     │
│ [ Submit review ]                │
├──────────────────────────────────┤
│ (4) Messages: not eligible |     │
│ duplicate | invalid              │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Summary | CMP-14 | Average (one decimal) and count | BR-060 |
| 2 | Review list | CMP-45 | Rating and comment per review; plain text | FR-081, BR-059 |
| 3 | Review form | CMP-46 | Rating 1 to 5 (required), comment up to 1,000 characters with a live counter | FR-077, FR-079 |
| 4 | Messages | CMP-34 | Not eligible, already reviewed, invalid rating | FR-078, FR-080 |

### SCR-17 — Admin: product list (R2)
**Purpose:** Give administrators a quick way to find a product and see its status and stock.
**Release:** R2 · **Stories:** US-060, US-063, US-064 · **PRD:** FR-083, FR-086, FR-087, BR-065 · **Mode:** operate.
**Layout rules:** the admin shell has a fixed side navigation on desktop and a menu drawer on mobile. The list search, filters and paging were proposed and are approved [P, DQ-07] because the PRD specifies only that administrators can inspect products. Inactive products are shown, with a status label.

**Desktop**
```text
┌────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ NEXACART Admin │ (1) Products (R2)                                         [ + New product ] (2)   │
│                │ [ Search name or SKU ... ] (3)  Status: [ All v ]   Category: [ All v ]   [P]     │
│ Products       │                                                                                   │
│ Categories     │ Name            Category        Variants   Stock   Status     Actions             │
│ Orders         │ Stride Run 2    Running         8          126     Active     Edit                │
│ Audit log      │ Orbit Buds      Earbuds         3          0       Inactive   Edit                │
│                │ Pulse Mouse     Keyboards/Mice  2          41      Active     Edit                │
│ Signed in as   │                                                                                   │
│ admin          │ (4) < Prev   1   2   3   Next >      (list search and filters: GAP-07) [P]        │
│ [ Log out ]    │                                                                                   │
└────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────────────┬───────┐
│ Menu │   NEXACART Admin  │ Out   │
├──────┴───────────────────┴───────┤
│ (1) Products (R2)  [ + New ] (2) │
├──────────────────────────────────┤
│ [ Search name or SKU ] (3)       │
├──────────────────────────────────┤
│ Stride Run 2   Active            │
│ Running - 8 variants - 126 in    │
│ stock   [ Edit ]                 │
├──────────────────────────────────┤
│ Orbit Buds   Inactive            │
│ Earbuds - 3 variants - 0 in      │
│ stock   [ Edit ]                 │
├──────────────────────────────────┤
│ (4) < Prev  1 of 3  Next >       │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Heading | Heading | Products | FR-087 |
| 2 | New product | CMP-19 | Opens the editor (SCR-18) | FR-084 |
| 3 | Search and filters [P] | CMP-47 | Name or SKU; status; category | DQ-07 |
| 4 | Pagination | CMP-11 | As listings | BR-016 |

### SCR-18 — Admin: product editor with variants (R2)
**Purpose:** Create and maintain products, variants and images without being able to break identifiers or stock history.
**Release:** R2 · **Stories:** US-061, US-062, US-063, US-064, US-065, US-068, US-069, US-070 · **PRD:** FR-084, FR-085, FR-086, FR-088, FR-095, FR-097, BR-010, BR-013, BR-061, CL-02, CL-03 · **Mode:** operate.
**Layout rules:** sections for Details, Images and Variants. Identifier fields (id, slug, SKUs) are read-only after creation. Images are chosen from the managed asset set; there is no upload and no external link (NG-10). **Stock is not editable in the variants table**; it changes only through "Adjust stock" (CL-03). Deactivate replaces delete.

**Desktop**
```text
┌────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ NEXACART Admin │ (1) < Products / Stride Run 2   [Active]            [ Deactivate ] (2)            │
│                │                                                                                   │
│ Products       │ (3) Details                                                                       │
│ Categories     │ Name *  [......................]   Brand *  [..........]                          │
│ Orders         │ Category *  [ Running v ]   Slug / base SKU (read-only after creation)            │
│ Audit log      │ Description  [.........................................]                          │
│                │ Specifications  key [......] value [......]  [ + row ]                            │
│                │                                                                                   │
│                │ (4) Images (choose from the managed asset set; no uploads)                        │
│                │ {img} {img} {img}   [ Choose images ]  alt text required                          │
│                │                                                                                   │
│                │ (5) Variants                                                                      │
│                │ SKU            Options           Price      Stock   Active                        │
│                │ STR-RUN2-BLK-9 Black / UK 9      R1,799.00  12      on    [ Adjust stock ] (6)    │
│                │ STR-RUN2-GRY-9 Grey / UK 9       R1,799.00  0       on    [ Adjust stock ]        │
│                │ [ + Add variant ]  Stock changes only through Adjust stock                        │
│                │                                                                                   │
│                │ [ Save product ]     Errors: duplicate SKU or slug, price must be a positive      │
│                │ integer (7)                                                                       │
└────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────────────┬───────┐
│ Menu │   NEXACART Admin  │ Out   │
├──────┴───────────────────┴───────┤
│ (1) < Products / Stride Run 2    │
│ [Active]  [ Deactivate ] (2)     │
├──────────────────────────────────┤
│ (3) Details                      │
│ Name *                           │
│ Brand *                          │
│ Category *                       │
│ Description                      │
│ Specifications (rows)            │
├──────────────────────────────────┤
│ (4) Images from the asset set    │
│ {img}{img}{img} [ Choose ]       │
├──────────────────────────────────┤
│ (5) Variants                     │
│ STR-RUN2-BLK-9                   │
│ Black / UK 9  R1,799.00          │
│ Stock 12  [ Adjust stock ] (6)   │
│ [ + Add variant ]                │
├──────────────────────────────────┤
│ [ Save product ]  (7) errors     │
│ inline                           │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Header | Heading | Product name and status | FR-087 |
| 2 | Deactivate | CMP-19 | Confirmation; reactivation uses the same control | FR-086 |
| 3 | Details | CMP-33 | Name, brand, category, description, specification rows | FR-085 |
| 4 | Images | CMP-48 | Choose from the asset set; alt text required | FR-097, FR-029 |
| 5 | Variants | CMP-49 | SKU, options, price, stock (read-only), active toggle | FR-088, BR-010 |
| 6 | Adjust stock | CMP-19 | Opens SCR-19 | FR-090 |
| 7 | Errors | CMP-34 | Duplicate SKU or slug, invalid price | CL-02, FR-095 |

### SCR-19 — Admin: inventory adjustment (R2)
**Purpose:** Change a variant's stock in one explained, reversible-by-record step.
**Release:** R2 · **Stories:** US-067 · **PRD:** FR-090, BR-042, BR-062, CL-11 · **Mode:** operate.
**Layout rules:** a modal dialog. The administrator chooses **Change by** (a positive or negative whole number) or **Set to** (zero or more), sees the resulting stock before applying, and must give a reason of 1 to 200 characters. Any error leaves stock unchanged and says why.

**Desktop**
```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│            (1) Adjust stock - STR-RUN2-BLK-9 (modal dialog; focus moves in, Esc closes)            │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Current stock: 12                                                                                  │
│ (2) Mode  (o) Change by   ( ) Set to                                                               │
│ Change by  [ +5 ]  (a positive or negative whole number, not zero)                                 │
│ Resulting stock: 17 (preview, must not be below zero) (3)                                          │
│ (4) Reason *  [ Stock received ................ ]  1 to 200 characters                             │
│ (5) [ Apply adjustment ]   [ Cancel ]      Errors under the field; stock is unchanged on any error │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────────────────────────────────┐
│ (1) Adjust stock                 │
│ STR-RUN2-BLK-9  current 12       │
├──────────────────────────────────┤
│ (2) (o) Change by  ( ) Set to    │
│ [ +5 ]                           │
│ (3) Resulting stock: 17          │
├──────────────────────────────────┤
│ (4) Reason *                     │
│ [ ........................ ]     │
│ 1-200 characters                 │
├──────────────────────────────────┤
│ (5) [ Apply ]  [ Cancel ]        │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Dialog title | CMP-44 | Variant SKU and current stock; focus moves in, Esc closes, focus returns to the opener | FR-090 |
| 2 | Mode | CMP-36 | Change by, or Set to | CL-11 |
| 3 | Preview | CMP-23 | Resulting stock; an error if it would be below zero | BR-062 |
| 4 | Reason | CMP-33 | Required, counter, 1 to 200 characters | BR-062 |
| 5 | Actions | CMP-19 | Apply adjustment, Cancel | FR-090 |

### SCR-20 — Admin: categories and small-goods designation (R2)
**Purpose:** Maintain the two-level category tree and say which categories count as small goods.
**Release:** R2 · **Stories:** US-066 · **PRD:** FR-089, BR-061, BR-077, CL-02, DEC-29 · **Mode:** operate.
**Layout rules:** an indented tree with Active and Small goods columns. Subcategories show "inherited" when the parent is small goods. A category with active products or subcategories cannot be deactivated and the screen says why.

**Desktop**
```text
┌────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ NEXACART Admin │ (1) Categories (R2)                       [ + New category ] (2)                  │
│                │                                                                                   │
│ Products       │ Name                       Active   Small goods   Actions                         │
│ Categories     │ Computers & Tech           on       off           Edit                            │
│ Orders         │   Laptops                  on       off           Edit                            │
│ Audit log      │ Wearables & Audio          on       on            Edit   (3)                      │
│                │   Earbuds                  on       inherited     Edit                            │
│                │                                                                                   │
│                │ (4) Maximum two levels. A category with active products or subcategories cannot   │
│                │ be deactivated: "Category still has active products." (5)                         │
└────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────────────┬───────┐
│ Menu │   NEXACART Admin  │ Out   │
├──────┴───────────────────┴───────┤
│ (1) Categories (R2)  [ + New ]   │
│ (2)                              │
├──────────────────────────────────┤
│ Computers & Tech                 │
│ Active | Small goods: off  [     │
│ Edit ]                           │
├──────────────────────────────────┤
│ Wearables & Audio (3)            │
│ Active | Small goods: on  [ Edit │
│ ]                                │
├──────────────────────────────────┤
│ Earbuds                          │
│ Active | Small goods: inherited  │
├──────────────────────────────────┤
│ (5) Cannot deactivate while it   │
│ has active products              │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Heading | Heading | Categories | FR-089 |
| 2 | New category | CMP-19 | Maximum two levels | FR-089 |
| 3 | Small-goods toggle | CMP-50 | Affects the minimum-order check for new placements | BR-077 |
| 4 | Rule note | CMP-23 | Explains the two-level limit | BR-061 |
| 5 | Error | CMP-34 | "Category still has active products" | BR-061 |

### SCR-21 — Admin: order list (R2)
**Purpose:** Let administrators find the orders they need to act on.
**Release:** R2 · **Stories:** US-071 · **PRD:** FR-091, BR-016, CL-04 · **Mode:** operate.
**Layout rules:** a filter bar (status, date range, order number, customer email), a table, paging. Newest first. On mobile each row becomes a card.

**Desktop**
```text
┌────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ NEXACART Admin │ (1) Orders (R2)                                                                   │
│                │ (2) Status [ All v ]  From [ date ]  To [ date ]  Order number [ ... ]  Customer  │
│ Products       │ email [ ... ]  [ Apply ]                                                          │
│ Categories     │                                                                                   │
│ Orders         │ Order number        Placed       Customer             Status      Payment   Total │
│ Audit log      │ NC-20261014-482913  14 Oct 2026  a@example.test       Confirmed   Paid            │
│                │ R1,859.00                                                                         │
│                │ NC-20261003-110224  3 Oct 2026   b@example.test       Shipped     Paid            │
│                │ R799.00                                                                           │
│                │ NC-20260921-663901  21 Sep 2026  c@example.test       Cancelled   Failed          │
│                │ R1,299.00                                                                         │
│                │                                                                                   │
│                │ (3) Newest first, paginated    < Prev  1  2  Next >      (filter semantics:       │
│                │ CL-04)                                                                            │
└────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────────────┬───────┐
│ Menu │   NEXACART Admin  │ Out   │
├──────┴───────────────────┴───────┤
│ (1) Orders (R2)                  │
│ [ Filters (2) ]                  │
├──────────────────────────────────┤
│ NC-20261014-482913  Confirmed    │
│ 14 Oct 2026  Paid  R1,859.00     │
│ a@example.test                   │
├──────────────────────────────────┤
│ NC-20261003-110224  Shipped      │
│ 3 Oct 2026  Paid  R799.00        │
│ b@example.test                   │
├──────────────────────────────────┤
│ (3) < Prev  1 of 2  Next >       │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Heading | Heading | Orders | FR-091 |
| 2 | Filters | CMP-47 | Status, dates, order number, customer email | FR-091, CL-04 |
| 3 | Paging | CMP-11 | As listings | BR-016 |

### SCR-22 — Admin: order detail (R2)
**Purpose:** Let administrators investigate a payment or inventory question and move or cancel an order.
**Release:** R2 · **Stories:** US-072, US-073, US-074 · **PRD:** FR-092, FR-093, FR-094, BR-043, BR-053 to BR-057, CL-09, CL-12 · **Mode:** operate.
**Layout rules:** summary at the top, then items and address, totals, every payment attempt (all fields including the idempotency key), refund, stock movements and status history. The primary action is the single permitted next status; **Cancel order** asks for a reason of 1 to 200 characters. Only allowed transitions are offered.

**Desktop**
```text
┌────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ NEXACART Admin │ (1) < Orders / NC-20261014-482913        Status: Confirmed   Payment: Paid        │
│                │ Refund: Not applicable                                                            │
│ Products       │                                                                                   │
│ Categories     │ (2) Items and address (snapshots)   Stride Run 2 - Black, UK 9  x1  R1,799.00     │
│ Orders         │ Recipient name, Pretoria                                                          │
│ Audit log      │ (3) Totals   Subtotal R1,799.00  Discount R0.00  Delivery R60.00  Total R1,859.00 │
│                │                                                                                   │
│                │ (4) Payment attempts                                                              │
│                │ #  Status    Amount      Time (UTC)        Idempotency key                        │
│                │ 1  approved  R1,859.00   2026-10-14 08:42  k3f9...                                │
│                │ (5) Refund: none      (6) Stock movements: order_placed  Stride Run 2  -1         │
│                │ (7) Status history: 14 Oct 10:42 Pending -> Confirmed (system)                    │
│                │                                                                                   │
│                │ (8) [ Advance to Processing ]     [ Cancel order ]  asks for a reason (1-200      │
│                │ characters)                                                                       │
└────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────────────┬───────┐
│ Menu │   NEXACART Admin  │ Out   │
├──────┴───────────────────┴───────┤
│ (1) < Orders                     │
│ NC-20261014-482913               │
│ Confirmed | Paid | Refund n/a    │
├──────────────────────────────────┤
│ (2) Items and address            │
│ Stride Run 2 x1  R1,799.00       │
├──────────────────────────────────┤
│ (3) Total R1,859.00              │
├──────────────────────────────────┤
│ (4) Payment attempts             │
│ #1 approved R1,859.00            │
│ 08:42 UTC  key k3f9...           │
├──────────────────────────────────┤
│ (5) Refund none  (6) Stock       │
│ movements v                      │
│ (7) History v                    │
├──────────────────────────────────┤
│ (8) [ Advance to Processing ]    │
│ [ Cancel order ]                 │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Header | Heading | Order number and the three statuses | FR-092 |
| 2-3 | Items, address, totals | CMP-38 | Snapshots | BR-050 |
| 4 | Payment attempts | CMP-51 | Attempt number, status, amount, UTC time, idempotency key | FR-067, CL-12 |
| 5 | Refund | CMP-39 | Status and amount | BR-056 |
| 6 | Stock movements | CMP-51 | Ledger lines linked to the order | BR-042 |
| 7 | Status history | CMP-42 | Chronological | FR-076 |
| 8 | Actions | CMP-19 | Advance to the next status; Cancel order with a reason | FR-093, FR-094 |

### SCR-23 — Admin: audit log (R2, Should)
**Purpose:** Show who did what, read-only.
**Release:** R2 · **Stories:** US-076 (events are written by US-075) · **PRD:** FR-098 to FR-100, BR-066, DEC-20 · **Mode:** operate.
**Layout rules:** filter bar (actor, action, entity, date range), a table, paging. There are no edit or delete controls anywhere on this screen.

**Desktop**
```text
┌────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ NEXACART Admin │ (1) Audit log (R2, Should)                                                        │
│                │ (2) Actor [ ... ]  Action [ All v ]  Entity [ All v ]  From [ date ]  To [ date ] │
│ Products       │ [ Apply ]                                                                         │
│ Categories     │                                                                                   │
│ Orders         │ Time (UTC)        Actor    Action                Entity               Summary     │
│ Audit log      │ 2026-10-14 09:10  admin    inventory_adjusted    variant STR-RUN2     12 -> 17    │
│                │ 2026-10-14 09:02  admin    order_status_changed  order NC-2026...     Confirmed   │
│                │ -> Processing                                                                     │
│                │ 2026-10-14 08:55  admin    admin_login           user admin           -           │
│                │                                                                                   │
│                │ (3) Read-only: events cannot be edited or deleted. < Prev  1  2  Next >           │
└────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```

**Mobile**
```text
┌──────┬───────────────────┬───────┐
│ Menu │   NEXACART Admin  │ Out   │
├──────┴───────────────────┴───────┤
│ (1) Audit log (R2)  [ Filters ]  │
│ (2)                              │
├──────────────────────────────────┤
│ 2026-10-14 09:10 UTC             │
│ admin - inventory adjusted       │
│ variant STR-RUN2: 12 -> 17       │
├──────────────────────────────────┤
│ 2026-10-14 09:02 UTC             │
│ admin - order status changed     │
│ Confirmed -> Processing          │
├──────────────────────────────────┤
│ (3) Read-only  < Prev 1 of 2     │
│ Next >                           │
└──────────────────────────────────┘
```

| # | Element | Component | Behaviour and content | Source |
|---|---|---|---|---|
| 1 | Heading | Heading | Audit log | FR-099 |
| 2 | Filters | CMP-47 | Actor, action, entity, dates | FR-099 |
| 3 | Read-only note | CMP-23 | Events cannot be edited or deleted | FR-100 |

## 7. Component inventory

Components are named once here and reused. "Test id" is the proposed `data-testid` stem for UI automation following the `area-element` convention of TR-001; list items and variants get a suffix (for example `cart-line-qty`). Accessible roles and names are mandatory in addition (TR-002).

| ID | Component | Role | Key states and variants | Used on | Test id stem |
|---|---|---|---|---|---|
| CMP-01 | Logo | Brand mark, home link | Default, reversed | All | `header-logo` |
| CMP-02 | Header actions | Wishlist, account menu, cart indicator | Guest, customer, admin; cart count | All storefront | `header-cart`, `header-wishlist`, `header-account` |
| CMP-03 | Demo notice | States fictional listings and no affiliation | Site-wide bar; per-product line | All; product | `demo-notice`, `fictional-notice` |
| CMP-04 | Search field | Find products by name or brand | Empty, focused, error (under 2 characters) | Header | `header-search` |
| CMP-05 | Category navigation | Browse the category tree | Flyout (desktop), drawer (mobile); open, closed | Header | `nav-category` |
| CMP-06 | Footer | Links and notices | Default | All | `footer` |
| CMP-07 | Breadcrumb | Orientation | Default | Listings, product | `breadcrumb` |
| CMP-08 | Sort select | Order results | Closed, open; four options | Listings | `listing-sort` |
| CMP-09 | Filter panel and sheet | Narrow results | Rail (desktop), sheet (mobile); applied count | Listings, search | `filter-panel` |
| CMP-10 | Product card and grid | Scan and choose products | Default, low stock, out of stock, fictional, no reviews | Home, listings, wishlist | `product-card` |
| CMP-11 | Pagination | Move between pages | First, middle, last; disabled previous or next | Listings, orders, admin | `pagination` |
| CMP-12 | Filter chip | Show and remove an active filter | Default, focused | Search | `filter-chip` |
| CMP-13 | Image gallery | Product images | Primary plus thumbnails; one image; missing image | Product | `gallery` |
| CMP-14 | Rating summary | Average and count | Rated, no reviews | Cards, product, reviews | `rating` |
| CMP-15 | Price block | Price of the selected variant | Default, "From" price | Cards, product | `price` |
| CMP-16 | Availability badge | In stock, Low stock, Out of stock | Three states; text plus icon | Cards, product, cart, wishlist | `availability` |
| CMP-17 | Variant selector | Choose option values | Selected, available, disabled (with reason) | Product, wishlist dialog | `variant-option` |
| CMP-18 | Quantity stepper | Choose quantity 1 to 10 | Default, minimum, maximum or stock limit, error | Product, cart | `qty` |
| CMP-19 | Button | Actions | Primary (ink), secondary (outline), text; default, hover, focus, pressed, disabled with reason, loading | All | per action, for example `checkout-place-order` |
| CMP-20 | Wishlist toggle | Save or unsave | Unsaved, saved (`aria-pressed`) | Product, cards [P] | `wishlist-toggle` |
| CMP-21 | Disclosure | Description, specifications | Collapsed, expanded | Product | `disclosure` |
| CMP-22 | Cart line | One variant in the cart | Normal, price changed, unavailable, out of stock, insufficient stock, read-only (locked) | Cart, checkout | `cart-line` |
| CMP-23 | Inline message | Banners, notes, flags | Info, success, warning, error; with icon and text | Many | `message` |
| CMP-24 | Order summary | Subtotal, discount, delivery, total | Default, with coupon, with free delivery, loading | Cart, checkout, order | `summary` |
| CMP-25 | Coupon input | Apply or remove a code | Empty, applied, rejected (reason) | Cart, checkout | `coupon` |
| CMP-26 | Empty state | Nothing to show | Search, cart, orders, wishlist | Many | `empty-state` |
| CMP-27 | Delivery option | Choose Standard or Express | Selected; fee and estimate; free first-order fee | Cart, checkout | `delivery-option` |
| CMP-28 | Account navigation | Move between account sections | Current marked with `aria-current` | Account | `account-nav` |
| CMP-29 | Address card | One saved address | Default, other | Addresses | `address-card` |
| CMP-30 | Hero | Home introduction | Default | Home | `home-hero` |
| CMP-31 | Promo strip [P] | One rule-accurate promotion line | Default | Home | `promo-strip` |
| CMP-32 | Category tile | Image-led category link | Default | Home | `category-tile` |
| CMP-33 | Form field group | Label, input, hint, error | Default, focused, filled, error, disabled, read-only | Forms | `field-<name>` |
| CMP-34 | Field error and summary | Explain what to fix | Inline; summary with links to fields | Forms | `field-error`, `error-summary` |
| CMP-35 | Address selector | Choose a delivery address | Selected, other, add new | Checkout | `address-select` |
| CMP-36 | Radio group | Payment outcome, modes | Selected, unselected, disabled | Checkout, payment, admin | `outcome`, `mode` |
| CMP-37 | Order number | Selectable identifier | Default | Orders | `order-number` |
| CMP-38 | Snapshot block | Items, address, totals as placed | Read-only | Confirmation, order, admin | `snapshot` |
| CMP-39 | Status pills | Order, payment, refund status | Neutral, info, success, warning, error | Orders, admin | `status-order`, `status-payment`, `status-refund` |
| CMP-40 | Pending-order banner | Explain a reserved order and offer Pay now and Cancel | Default; attempts exhausted | Cart, payment | `pending-banner` |
| CMP-41 | Order row | One order in a list | Pending, confirmed, delivered, cancelled | Order history | `order-row` |
| CMP-42 | Status history | Chronological transitions | Default | Order detail | `status-history` |
| CMP-43 | Toast and inline success | Confirm an action | Auto-dismiss (4 seconds) or persistent for errors | Many | `toast` |
| CMP-44 | Dialog and sheet | Confirm or collect input | Open, closed; focus trapped | Cancel, delete, adjust stock, variant choice, filters | `dialog` |
| CMP-45 | Review list | Reviews as plain text | Empty, populated | Reviews (R2) | `review-list` |
| CMP-46 | Review form | Rating and comment | Default, error, success | Reviews (R2) | `review-form` |
| CMP-47 | Admin filter bar | Filter admin lists | Default, applied | Admin (R2) | `admin-filters` |
| CMP-48 | Image picker | Choose from the asset set | Selected, none | Admin (R2) | `image-picker` |
| CMP-49 | Variants table | Edit variants | Row states; stock read-only | Admin (R2) | `variants-table` |
| CMP-50 | Toggle switch | Boolean setting | On, off, disabled, inherited | Admin (R2) | `toggle` |
| CMP-51 | Data table | Admin lists, attempts, movements | Sortable only where specified; empty; loading | Admin (R2) | `data-table` |
| CMP-52 | Skeleton loader | Loading placeholder | Static under reduced motion | Listings, detail, cart | `skeleton` |
| CMP-53 | Progress indicator | Indeterminate waiting | Active | Payment in progress | `progress` |
| CMP-54 | Skip link | Jump to main content | Hidden until focused | All | `skip-link` |
| CMP-55 | Admin shell | Side navigation and header | Desktop rail, mobile drawer | Admin (R2) | `admin-nav` |

## 8. Interaction states

### 8.1 State treatments
Each state in `USER_STORIES_AND_FLOWS.md` §7 (UI-01 to UI-27) has one design treatment. The wireframe fragments ST-01 to ST-13 follow.

| UI | State | Treatment | Components | Fragment or screen |
|---|---|---|---|---|
| UI-01 | Loading | Skeleton shapes in the final layout, a visible "Loading" label, `aria-busy`; actions that would repeat an in-flight request are disabled | CMP-52 | ST-01 |
| UI-02 | Success feedback | Toast with `role="status"` for 4 seconds, plus the changed value on screen (cart count, saved heart) | CMP-43 | ST-09 |
| UI-03 | Field validation error | Message under the field in error colour with an icon, error summary for several errors, focus to the first error, input kept | CMP-33, CMP-34 | ST-03 |
| UI-04 | Request failed | Plain message and a retry control; the request id in small text | CMP-23 | ST-10 |
| UI-05 | Empty result | Short explanation plus recovery controls | CMP-26 | ST-02 |
| UI-06 | Unavailable product | Text label "Out of stock" or "No longer available", reduced image emphasis, disabled primary action with the reason | CMP-16, CMP-22 | ST-04 |
| UI-07 | Low stock | "Low stock" label next to the price block when 1 to 5 units remain | CMP-16 | SCR-04 |
| UI-08 | Price changed | Old and new price on the line, informational message, checkout still possible | CMP-22, CMP-23 | ST-05 |
| UI-09 | Empty cart | Empty state with a path to shopping | CMP-26 | SCR-05 |
| UI-10 | Locked cart | Banner, read-only lines, disabled controls with the reason "Locked by your pending order" | CMP-40, CMP-22 | ST-07 |
| UI-11 | Below minimum order | Rule stated beside the summary, Checkout disabled with the reason linked | CMP-23, CMP-19 | ST-06 |
| UI-12 | Coupon result | Applied: discount line and Remove. Rejected: the specific reason; totals unchanged | CMP-25 | SCR-05 |
| UI-13 | Shipping fee | Each option shows the fee for this cart; free first-order fee shown as R0.00 with the offer line | CMP-27 | SCR-05 |
| UI-14 | Checkout blocked | "Place order" disabled with an explanation; inline add address | CMP-19, CMP-35 | SCR-07 |
| UI-15 | Simulated payment control | Labelled radio group, "no card details are collected" | CMP-36 | SCR-07 |
| UI-16 | Payment in progress | Indeterminate progress, controls disabled, result announced | CMP-53 | SCR-08C |
| UI-17 | Payment approved | Confirmation page | CMP-38, CMP-39 | SCR-08A |
| UI-18 | Payment not approved | Outcome heading and message, “Reserved until [time]” while active; retry/cancel state; retries do not extend deadline; expired orders are non-payable | CMP-40, CMP-36 | SCR-08B, SCR-10 |
| UI-19 | Attempts exhausted | Retry and outcome choices removed, only Cancel | CMP-40 | SCR-08B |
| UI-20 | Order cancelled or expired | Status `cancelled`, "no longer payable" message, cart shown unlocked | CMP-23 | SCR-10, SCR-08B |
| UI-21 | Cancel confirmation | Dialog with the safe action focused | CMP-44 | ST-13 |
| UI-22 | Session ended | Login with a notice; returns to the previous page | CMP-23 | ST-11 |
| UI-23 | Forbidden and not found | Dedicated pages with a way out | CMP-23 | ST-12 |
| UI-24 | Responsive navigation | Drawer and sheets below 1024 px | CMP-05, CMP-44 | SCR-01, SCR-03 |
| UI-25 | Keyboard and assistive technology | See §10 | all | §10 |
| UI-26 | Demo-store notice | Site-wide bar and per-product line | CMP-03 | SCR-01, SCR-04 |
| UI-27 | Administrator results | Result or specific error after each admin action | CMP-23, CMP-34 | SCR-17 to SCR-23 |
| UI-28 | Session-expiry warning | Five minutes before access token expiry, display and announce “Your session is about to expire”; no token refresh, renewal or extension. On expiry follow UI-22 | CMP-23 | Shared authenticated shell, ST-11; FR-005, CL-20 |

### 8.2 State fragments

**ST-01 Loading**
```text
┌────────────────────────────────────────────────────────────────┐
│ (1) LOADING: listing skeleton (shapes only, no spinner-only    │
│ state)                                                         │
├─────────────────────┬─────────────────────┬────────────────────┤
│ [ grey block ]      │ [ grey block ]      │ [ grey block ]     │
│ [ ---- ]            │ [ ---- ]            │ [ ---- ]           │
│ [ -- ]              │ [ -- ]              │ [ -- ]             │
├─────────────────────┴─────────────────────┴────────────────────┤
│   Region has aria-busy="true"; a visible "Loading products"    │
│         label; shimmer is static under reduced motion          │
└────────────────────────────────────────────────────────────────┘
```

**ST-02 Empty result**
```text
┌────────────────────────────────────────────────────────────────┐
│ (2) EMPTY: no products match                                   │
├────────────────────────────────────────────────────────────────┤
│         No products match "runner" with these filters.         │
│ [ Reset filters ]    [ Change search ]                         │
└────────────────────────────────────────────────────────────────┘
```

**ST-03 Validation error**
```text
┌────────────────────────────────────────────────────────────────┐
│ (3) VALIDATION ERROR: field and summary                        │
├────────────────────────────────────────────────────────────────┤
│ Email *                                                        │
│ [ not-an-email ............ ]                                  │
│ Enter a valid email address.  (text under the field, error     │
│ colour plus icon)                                              │
├────────────────────────────────────────────────────────────────┤
│ Summary at the top for forms with several errors; focus moves  │
│                   to the first invalid field                   │
└────────────────────────────────────────────────────────────────┘
```

**ST-04 Unavailable item**
```text
┌────────────────────────────────────────────────────────────────┐
│ (4) UNAVAILABLE: out of stock card, and unavailable cart or    │
│ wishlist line                                                  │
├────────────────────────────────┬───────────────────────────────┤
│ {img, 70% opacity}             │ Pulse Mouse  x2               │
│ Stride Run 2                   │ No longer available           │
│ From R1,799.00                 │ Remove this line to continue  │
│ Out of stock (text label, not  │ (cart) [ Remove ]             │
│ colour alone)                  │                               │
└────────────────────────────────┴───────────────────────────────┘
```

**ST-05 Price changed**
```text
┌────────────────────────────────────────────────────────────────┐
│ (5) PRICE CHANGED (informational, does not block checkout)     │
├────────────────────────────────────────────────────────────────┤
│ Orbit Buds - Graphite   x1   R649.00                           │
│ Price changed: was R599.00, now R649.00                        │
│ If you place the order, the new total is used. (a stale total  │
│ is refused with fresh totals)                                  │
└────────────────────────────────────────────────────────────────┘
```

**ST-06 Below minimum order**
```text
┌────────────────────────────────────────────────────────────────┐
│ (6) BELOW MINIMUM ORDER (blocks checkout)                      │
├────────────────────────────────────────────────────────────────┤
│ Subtotal R198.00                                               │
│ Minimum order is R250.00, or add 4 or more Wearables and Audio │
│ items.                                                         │
│ [ Checkout ] disabled (reason linked by aria-describedby)      │
└────────────────────────────────────────────────────────────────┘
```

**ST-07 Cart locked and pending order**
```text
┌────────────────────────────────────────────────────────────────┐
│ (7) CART LOCKED + PENDING ORDER                                │
├────────────────────────────────────────────────────────────────┤
│ Banner: You have an order waiting for payment                  │
│ (NC-20261014-482913).                                          │
│ [ Pay now ]   [ Cancel order ]                                 │
├────────────────────────────────────────────────────────────────┤
│ Cart lines read-only. Quantity, Remove, Coupon, Delivery       │
│ controls disabled with the reason "Locked by your pending      │
│ order".                                                        │
└────────────────────────────────────────────────────────────────┘
```

**ST-08 Pending order**
```text
┌────────────────────────────────────────────────────────────────┐
│ (8) PENDING ORDER (order detail)                               │
├────────────────────────────────────────────────────────────────┤
│ Status: Pending   Payment: Failed                             │
│ Reserved until [time] — original deadline, not extended by retry│
├────────────────────────────────────────────────────────────────┤
│ [ Pay now ]   [ Cancel order ]                                 │
└────────────────────────────────────────────────────────────────┘
```

**ST-09 Success**
```text
┌────────────────────────────────────────────────────────────────┐
│ (9) SUCCESS: confirmation toast (role="status", about 4        │
│ seconds, dismissible)                                          │
├────────────────────────────────────────────────────────────────┤
│ Added to cart.   [ View cart ]      cart count increments      │
└────────────────────────────────────────────────────────────────┘
```

**ST-10 Request failed**
```text
┌────────────────────────────────────────────────────────────────┐
│ (10) REQUEST FAILED (not a field error)                        │
├────────────────────────────────────────────────────────────────┤
│ Something went wrong. Please try again.   [ Try again ]        │
│ Reference: 7f3c... (request id, GAP-09)                        │
└────────────────────────────────────────────────────────────────┘
```

**ST-11 Session ended**
```text
┌────────────────────────────────────────────────────────────────┐
│ (11) SESSION ENDED                                             │
├────────────────────────────────────────────────────────────────┤
│ Log in page with notice: "Your session ended. Log in to        │
│ continue." Returns you to the page you were on.                │
└────────────────────────────────────────────────────────────────┘
```

**ST-12 Forbidden and not found**
```text
┌────────────────────────────────────────────────────────────────┐
│ (12) FORBIDDEN and NOT FOUND pages                             │
├────────────────────────────────┬───────────────────────────────┤
│ 403                            │ 404                           │
│ You do not have access to this │ We could not find that page   │
│ page.                          │ or product.                   │
│ [ Go to home ]                 │ [ Browse categories ]         │
└────────────────────────────────┴───────────────────────────────┘
```

**ST-13 Cancel confirmation**
```text
┌────────────────────────────────────────────────────────────────┐
│ (13) CANCEL CONFIRMATION (dialog; focus on the safe action)    │
├────────────────────────────────────────────────────────────────┤
│ Cancel order NC-20261014-482913?                               │
│ Stock is released. Paid orders are refunded in full (R2).      │
│ [ Keep order ]    [ Yes, cancel order ]                        │
└────────────────────────────────────────────────────────────────┘
```

## 9. Responsive behaviour

### 9.1 Reference layouts
The three reference viewports (375×812, 768×1024, 1280×800) are the design targets; the layout must also work at every width from 360 to 1920 px without horizontal scrolling (NFR-013). Structure changes at the breakpoints in §4.3.

| Area | 375 × 812 (xs) | 768 × 1024 (sm) | 1280 × 800 (md) |
|---|---|---|---|
| Header | Menu button, centred logo, wishlist and cart icons; search under the bar; drawer navigation | Same as xs with a wider search field | Logo bar plus category row with flyouts |
| Listing grid | 2 columns, 12 items | 3 columns, 12 items | 4 columns, 12 items; filter rail on the left |
| Filters | Bottom sheet from the Filters button | Left drawer from the Filters button | Left rail |
| Product page | Gallery on top, buy box below, sticky "Add to cart" bar | Gallery and buy box side by side (7:5) | Gallery and buy box side by side (7:5) |
| Cart | Lines, then summary, sticky Checkout bar | Lines and summary side by side | Lines (3 parts) and sticky summary (2 parts) |
| Checkout | Accordion sections, sticky total and "Place order" bar | Single column with the summary below | Sections left, sticky summary right |
| Forms | One column, labels above fields | One column, narrow container (640 px) | One column, narrow container |
| Order and admin tables | Rows become cards | Compact tables | Full tables |
| Dialogs | Full-screen or bottom sheet | Centred dialog | Centred dialog |

### 9.2 Rules for the full width range
- **360 px (narrowest):** content reflows to a single column; no truncation of prices, totals or order numbers; long text wraps; images scale with their ratio. The interface should also reflow at 320 CSS px for zoom (WCAG 1.4.10) even though the PRD minimum is 360 px.
- **1920 px (widest):** the content container stops growing at 1320 px and is centred; images and type do not scale beyond their maximum sizes.
- **Between breakpoints:** fluid widths and `clamp()` type; images keep their aspect ratio; grids use `minmax(0, 1fr)` so long names cannot force overflow.
- **Wide content** (tables, code-like keys) scrolls inside its own container, never the page.
- **Touch:** interactive targets are at least 44 × 44 px with at least 8 px between neighbours; inputs are at least 16 px so mobile browsers do not zoom; hover is never the only way to reveal anything.
- **Mobile browser chrome:** full-height layouts use `100dvh`, not `100vh`; sticky bars add `env(safe-area-inset-bottom)`; the viewport allows content under notches (`viewport-fit=cover`) with safe-area padding; no overscroll hijacking and no pull-to-refresh conflicts in the checkout.
- **Orientation:** layouts work in portrait and landscape; no orientation is required.

## 10. Accessibility requirements

The target is WCAG 2.2 AA for every customer flow and admin screen (NFR-011, NFR-012), with no critical or serious automated violation on the six core pages (home, listing, product, cart, checkout, login; AC-072).

| ID | Requirement | Detail |
|---|---|---|
| AX-01 | Contrast | Text at least 4.5:1 (3:1 for 24 px regular or 19 px bold and above); UI boundaries and focus indicators at least 3:1. The palette in §3.3 meets this; the table above lists the computed ratios. |
| AX-02 | Colour is never the only signal | Status, stock, errors, selected states and links combine colour with text, an icon or a shape. |
| AX-03 | Focus | Every interactive element has a visible 2 px focus ring with a 2 px offset (`:focus-visible`); the ring is never removed; focus order follows reading order; focus is moved into dialogs and sheets and returned to the opener on close. |
| AX-04 | Keyboard | Everything is operable by keyboard alone; see the interaction table below. No keyboard traps; Esc closes any overlay. |
| AX-05 | Names and labels | Every control has an accessible name; every input has a visible `label` (placeholders are never labels); icon-only controls have `aria-label`; groups use `fieldset` and `legend` or `role="group"` with a name. |
| AX-06 | Forms | Errors are linked to fields with `aria-describedby` and `aria-invalid`; an error summary links to fields; required fields are marked in text; helper text (such as the password rule) is shown before input. Use the correct `autocomplete` tokens: `name`, `email`, `username`, `current-password`, `new-password`, `tel`, `address-line1`, `address-line2`, `address-level2`, `address-level1`, `postal-code`. |
| AX-07 | Status messages | Cart updates, payment results, coupon results and errors are announced with `role="status"` (polite) or `role="alert"` (blocking errors) without moving focus. |
| AX-08 | Structure | One `h1` per page, ordered headings, landmarks (`header`, `nav`, `main`, `footer`), a skip link, descriptive page titles, `lang="en"`. |
| AX-09 | Images | Every product image has meaningful alt text describing the product and view (for example "Stride Run 2 running shoe in black, side view"); decorative images use empty alt; a missing image shows a placeholder with alt text (FR-029). |
| AX-10 | Target size | At least 44 × 44 px for touch targets (above the WCAG 2.2 minimum of 24 px). |
| AX-11 | Motion | `prefers-reduced-motion` removes all non-essential motion, including skeleton shimmer and transitions; no information is conveyed by motion alone (§11). |
| AX-12 | Zoom and reflow | Layouts remain usable at 200% zoom and reflow without horizontal scrolling at 320 CSS px. |
| AX-13 | Time and sessions | Five minutes before the 30-minute access token expires, display and announce “Your session is about to expire.” This informational warning does not refresh, renew or extend the token. On expiry, redirect to login and restore the intended destination after successful login (FR-005, CL-20). The 30-minute order reservation deadline is shown as “Reserved until [time]” on the payment page and order detail (CL-18). |
| AX-14 | Tables | Data tables use real `table` markup with header cells and scope; on mobile the card layout keeps the same reading order. |
| AX-15 | Dialogs | `role="dialog"` with `aria-modal`, a labelled title, focus trapped inside, background inert, Esc to close, the safe action focused first on destructive dialogs. |

**Keyboard interactions**

| Component | Keys |
|---|---|
| Category flyout (CMP-05) | Enter or Space opens, arrow keys move between items, Esc closes and returns focus to the trigger |
| Mobile drawer | Menu button has `aria-expanded`; focus is trapped while open; Esc closes |
| Filter sheet (CMP-09) | Opens from the Filters button; focus trapped; Esc closes; apply and reset are buttons |
| Variant selector (CMP-17) | Radio-group semantics: arrow keys change the selection, Tab leaves the group; disabled options are skipped but their reason is readable |
| Quantity stepper (CMP-18) | Plus and minus buttons plus a numeric field; Up and Down arrows change the value |
| Payment outcome (CMP-36) | Radio group; arrow keys select; the chosen value is announced |
| Dialog (CMP-44) | Tab cycles inside; Esc closes |
| Pagination (CMP-11) | Links with `aria-label` (for example "Page 2") and `aria-current="page"` |

## 11. Animation guidance

The product is a transactional retail site. Motion is used only to confirm that an action registered or to explain where something went, and it is kept out of every high-frequency path (Emil-style rule: if a user does something many times a day, do not animate it).

### 11.1 Motion that earns its place

| ID | Element and trigger | Property | Duration and easing | Purpose |
|---|---|---|---|---|
| MO-01 | Buttons, chips and cards on press | `transform: scale(.97)` | 100 ms, ease-out | Confirms the press registered; no delay |
| MO-02 | Hover on links, cards and buttons (pointer devices only, gated by `@media (hover: hover)`) | `opacity` or `background-color` | 150 ms, ease-out | Shows what is interactive; never the only cue |
| MO-03 | Drawer, filter sheet and dialog open and close | `transform` and `opacity` | 200 ms open, 150 ms close, `cubic-bezier(.2,.7,.2,1)` | Explains where the panel came from; immediate response; can be dismissed at any moment |
| MO-04 | Category flyout | `opacity` | 120 ms, ease-out | Prevents a hard flash; opens instantly for keyboard users |
| MO-05 | Toast | `opacity` and small `translateY` | 150 ms in, 120 ms out | Confirms an action without moving the layout |
| MO-06 | Wishlist toggle | Icon swap (outline to fill) | 120 ms | Confirms the saved state |
| MO-07 | Cart count change | Number swap with a short `opacity` change | 150 ms | Draws attention to the changed count |
| MO-08 | Payment in progress | Indeterminate progress bar | continuous, linear | States that work is happening during the simulated delay |
| MO-09 | Skeleton loader | Shimmer | 1.2 s loop; static fill under reduced motion | Shows layout while data loads |
| MO-10 | Disclosure open and close | `height` replaced by a quick fade of content | 150 ms | Avoids layout jumps |

Only `transform` and `opacity` (and colour for hover) are animated, to stay off the layout path. Easing is ease-out for entering and responding; there is no bounce or spring.

### 11.2 Elements that stay static
Page navigation and route changes; the header and its category links; product cards when they enter the viewport (no scroll-triggered reveals); prices, totals and status pills (they change instantly); the quantity stepper value; table rows; form fields and error messages (they appear immediately); the hero (no parallax, no carousel, no auto-advancing slides); anything on the checkout other than the waiting state.

### 11.3 Reduced motion and performance
- With `prefers-reduced-motion: reduce`, all transitions and the skeleton shimmer are removed; panels appear and disappear instantly; the waiting indicator becomes static text plus a non-animated bar.
- A test flag disables animation so UI automation is deterministic (TR-012).
- No animation may block interaction or delay a response beyond 200 ms.

## 12. Asset and licensing rules

| ID | Rule |
|---|---|
| AS-01 | **No third-party runtime dependencies.** The storefront loads no remote image, font, icon, script, stylesheet or analytics at runtime (TR-013). Everything is served by the application. |
| AS-02 | **Images** are original, generated by a tool whose terms permit this use, or properly licensed with the licence kept on record. No scraping or copying of retail websites (PRD §5.3, NG-15). Each asset has a provenance record (source, author or tool, licence or terms, date, file name) kept with the asset set. |
| AS-03 | **Fonts and icons** are self-hosted files under open licences that permit redistribution: Geist (SIL OFL 1.1) and Phosphor Icons (MIT), both verified against their upstream licence files. The licence texts ship with the files. Final approval of both is DQ-17 and DQ-18. |
| AS-04 | **Determinism.** Images are stored locally with stable file names and fixed aspect ratios (4:5 product, 16:10 editorial); the baseline seed references them by name. No random or date-based image selection. |
| AS-05 | **Brand and club references.** Names are used only as product references. No logos, crests, sponsor marks, kit trademarks or imitation of a real retailer's identity appear in images or interface. Football shirts are generic designs. Every product shows the fictional-listing notice, prominently on football shirts (FR-028, BR-017). |
| AS-06 | **No implied affiliation.** No statement, badge or layout suggests endorsement or sponsorship by any brand. |
| AS-07 | **Alt text** is required for every product image at upload or seed time and describes the product and view (AX-09). |
| AS-08 | **Format and weight.** Images are served in an efficient format at two or three widths; as a guideline [P], the primary image on a listing card is about 80 KB or less and no image is larger than the viewport needs. Exact formats and pipeline belong to the architecture. |
| AS-09 | **Placeholders.** Until real images exist, development uses clearly labelled neutral placeholders at the right ratio. Placeholders must never reach a release (AC-072 and MET-07 depend on stable images). |
| AS-10 | **Test fixtures.** The fixture products of PRD §5.4 each have a deterministic image so UI tests can rely on them. |

## 13. Requirements traceability

Generated from the screens in §6 and from the story, requirement and acceptance-criterion identifiers in `USER_STORIES_AND_FLOWS.md`. Acceptance criteria are the PRD's; this brief adds none.

### 13.1 Screens to stories, requirements and acceptance criteria

| Screen | Release | Stories | Functional requirements and rules | Acceptance criteria (from the stories) |
|---|---|---|---|---|
| SCR-01 Home | R1 | US-013, US-020, US-025 | FR-016, FR-028, FR-030; BR-017, BR-076 | AC-022, AC-092 |
| SCR-02 Category listing | R1 | US-013, US-014, US-017, US-018, US-019, US-023, US-056 | FR-016, FR-017, FR-020, FR-021, FR-024, FR-026, FR-027; BR-010, BR-012, BR-015, BR-016 | AC-015, AC-016, AC-018, AC-019, AC-022, AC-092, AC-109 |
| SCR-03 Search results, filtering and sorting | R1 | US-015, US-016, US-017, US-018, US-019 | FR-018, FR-019, FR-020, FR-026, FR-027; BR-014, BR-015 | AC-016, AC-017, AC-018, AC-022 |
| SCR-04 Product detail and variant selection | R1 (reviews section R2) | US-021, US-022, US-023, US-024, US-025, US-026, US-030, US-032, US-056 | FR-022, FR-023, FR-024, FR-025, FR-028, FR-029, FR-032, FR-035; BR-010, BR-012, BR-017, BR-018 | AC-018, AC-019, AC-020, AC-021, AC-022, AC-023, AC-024, AC-028, AC-030, AC-079, AC-092, AC-094, AC-109 |
| SCR-05 Cart, coupon and shipping summary | R1 | US-027, US-028, US-029, US-030, US-031, US-035, US-036, US-037, US-038, US-039, US-043 | FR-031, FR-032, FR-033, FR-034, FR-035, FR-036, FR-037, FR-038, FR-039, FR-040, FR-046, FR-047, FR-049, FR-050 (+4 more); BR-018, BR-020, BR-022, BR-025, BR-026, BR-027, BR-028, BR-029, BR-071, BR-076, BR-077 | AC-025, AC-026, AC-027, AC-028, AC-029, AC-032, AC-033, AC-036, AC-076, AC-078, AC-079, AC-080, AC-081, AC-090 (+7 more) |
| SCR-06 Address management | R1 | US-010, US-011, US-012 | FR-011, FR-012, FR-013, FR-014, FR-015; BR-008, BR-009 | AC-012, AC-013, AC-014, AC-062, AC-091 |
| SCR-07 Checkout review and simulated payment | R1 | US-035, US-037, US-038, US-039, US-040, US-041, US-042, US-043, US-044 | FR-052, FR-053, FR-054, FR-055, FR-056, FR-057, FR-066, FR-110, FR-115; BR-068, BR-070, BR-071, BR-074 | AC-027, AC-032, AC-033, AC-034, AC-036, AC-037, AC-042, AC-045, AC-047, AC-048, AC-076, AC-077, AC-078, AC-079 (+10 more) |
| SCR-08 Payment results | R1 | US-044, US-045, US-046, US-047, US-048, US-049, US-053 | FR-058, FR-059, FR-060, FR-061, FR-062, FR-063, FR-064, FR-065, FR-114; BR-044, BR-047, BR-049, BR-069, BR-073 | AC-038, AC-039, AC-040, AC-041, AC-043, AC-044, AC-046, AC-048, AC-053, AC-054, AC-055, AC-075, AC-081, AC-082 (+8 more) |
| SCR-09 Order history | R1 | US-050 | FR-068; BR-016, BR-064 | AC-050, AC-110 |
| SCR-10 Order detail | R1 (refund and paid-cancellation parts R2) | US-012, US-051, US-052, US-053, US-054, US-055 | FR-069, FR-070, FR-072, FR-073, FR-074, FR-076; BR-029, BR-043, BR-050, BR-052, BR-053, BR-056 | AC-014, AC-051, AC-052, AC-053, AC-054, AC-055, AC-056, AC-057, AC-074, AC-075, AC-085, AC-096, AC-097, AC-108 (+2 more) |
| SCR-11 Login | R1 | US-002, US-003, US-005, US-006 | FR-003, FR-005, FR-009; BR-004, BR-007 | AC-004, AC-005, AC-007, AC-008, AC-011, AC-061, AC-089 |
| SCR-12 Registration | R1 | US-001 | FR-001, FR-002; BR-001, BR-002, BR-003 | AC-001, AC-002, AC-003, AC-010, AC-088 |
| SCR-13 Profile | R1 | US-004, US-007 | FR-007; BR-003 | AC-006, AC-089 |
| SCR-14 Change password | R1 | US-008 | FR-008; BR-001, BR-005 | AC-009 |
| SCR-15 Wishlist | R1 | US-032, US-033, US-034 | FR-041, FR-042, FR-043, FR-044, FR-045; BR-023 | AC-029, AC-030, AC-031, AC-079, AC-094 |
| SCR-16 Product reviews (R2) | R2 (read-only seeded ratings appear in R1 on listings and the product header) | US-057, US-058, US-059 | FR-077, FR-078, FR-079, FR-080, FR-081, FR-082; BR-058, BR-059, BR-060 | AC-058, AC-059, AC-060 |
| SCR-17 Admin: product list (R2) | R2 | US-060, US-063, US-064 | FR-083, FR-086, FR-087; BR-065 | AC-061, AC-063, AC-090, AC-099, AC-112 |
| SCR-18 Admin: product editor with variants (R2) | R2 | US-061, US-062, US-063, US-064, US-065, US-068, US-069, US-070 | FR-084, FR-085, FR-086, FR-088, FR-095, FR-097; BR-010, BR-013, BR-061 | AC-027, AC-063, AC-099, AC-100, AC-103, AC-112 |
| SCR-19 Admin: inventory adjustment (R2) | R2 | US-067 | FR-090; BR-042, BR-062 | AC-049, AC-064 |
| SCR-20 Admin: categories and small-goods designation (R2) | R2 | US-066 | FR-089; BR-061, BR-077 | AC-065, AC-100, AC-118 |
| SCR-21 Admin: order list (R2) | R2 | US-071 | FR-091; BR-016 | AC-101 |
| SCR-22 Admin: order detail (R2) | R2 | US-072, US-073, US-074 | FR-092, FR-093, FR-094; BR-043, BR-053, BR-054, BR-055, BR-056, BR-057 | AC-056, AC-101, AC-102 |
| SCR-23 Admin: audit log (R2, Should) | R2 | US-075, US-076 | FR-098, FR-099, FR-100; BR-066 | AC-066 |

### 13.2 State coverage
All 28 UI states of the approved user stories (UI-01 to UI-28) have a design treatment in §8.1: **28 of 28 covered**. Thirteen are also drawn as fragments (ST-01 to ST-13); the rest are shown inside the screen or shared authenticated shell that owns them.

### 13.3 Story coverage

| Story | Title | Pri | Release | Screens or reason |
|---|---|---|---|---|
| US-001 | Register a customer account | M | R1 | SCR-12 |
| US-002 | Log in | M | R1 | SCR-11 |
| US-003 | Throttle repeated failed logins | S | R1 | SCR-11 |
| US-004 | Log out | M | R1 | SCR-13 |
| US-005 | Resume after session expiry | M | R1 | SCR-11 |
| US-006 | Protected pages require login | M | R1 (admin routes R2) | SCR-11 |
| US-007 | View and update my profile | M | R1 | SCR-13 |
| US-008 | Change my password | M | R1 | SCR-14 |
| US-009 | Provision administrator accounts safely | M | R1 | Operator provisions administrator accounts by seed or CLI; no screen |
| US-010 | Manage saved delivery addresses | M | R1 | SCR-06 |
| US-011 | Default delivery address | M | R1 | SCR-06 |
| US-012 | Past orders keep their delivery address | M | R1 | SCR-06, SCR-10 |
| US-013 | Browse categories | M | R1 | SCR-01, SCR-02 |
| US-014 | Product listing and pagination | M | R1 | SCR-02 |
| US-015 | Search by product name or brand | M | R1 | SCR-03 |
| US-016 | Filter products | M | R1 | SCR-03 |
| US-017 | Sort products | M | R1 | SCR-02, SCR-03 |
| US-018 | Empty results | M | R1 | SCR-02, SCR-03 |
| US-019 | Shareable listing URLs | S | R1 | SCR-02, SCR-03 |
| US-020 | Home page entry points | S | R1 | SCR-01 |
| US-021 | View product details | M | R1 | SCR-04 |
| US-022 | Choose product variants | M | R1 | SCR-04 |
| US-023 | Availability and out-of-stock handling | M | R1 | SCR-02, SCR-04 |
| US-024 | Inactive products are not found | M | R1 | SCR-04 |
| US-025 | Demo-store and fictional-listing notices | M | R1 | SCR-01, SCR-04 |
| US-026 | Add a product variant to my cart | M | R1 | SCR-04 |
| US-027 | Change quantities, remove lines or clear the cart | M | R1 | SCR-05 |
| US-028 | See my cart summary with server-calculated totals | M | R1 | SCR-05 |
| US-029 | See what has changed or cannot be bought | M | R1 | SCR-05 |
| US-030 | Guests are sent to login and their action completes | M | R1 | SCR-04, SCR-05 |
| US-031 | My cart persists and is mine alone | M | R1 | SCR-05 |
| US-032 | Add and remove wishlist items | M | R1 | SCR-04, SCR-15 |
| US-033 | View my wishlist | M | R1 | SCR-15 |
| US-034 | Move a wishlist item to my cart | M | R1 | SCR-15 |
| US-035 | Apply a coupon code | M | R1 | SCR-05, SCR-07 |
| US-036 | Remove an applied coupon | M | R1 | SCR-05 |
| US-037 | Choose a shipping option and see its fee | M | R1 | SCR-05, SCR-07 |
| US-038 | Free Standard shipping on a qualifying first order | M | R1 | SCR-05, SCR-07 |
| US-039 | Minimum order and the small-goods exception | M | R1 | SCR-05, SCR-07 |
| US-040 | Review my order before paying | M | R1 | SCR-07 |
| US-041 | Place the order and reserve stock | M | R1 | SCR-07 |
| US-042 | Retries never create a second order | M | R1 | SCR-07 |
| US-043 | One pending order and a locked cart | M | R1 | SCR-05, SCR-07 |
| US-044 | Choose a simulated payment outcome | M | R1 | SCR-07, SCR-08 |
| US-045 | Approved payment confirms my order | M | R1 | SCR-08 |
| US-046 | Failed payments and retries | M | R1 | SCR-08 |
| US-047 | Duplicate payment requests are safe | M | R1 | SCR-08 |
| US-048 | Unpaid orders expire and release their stock | M | R1 | SCR-08 |
| US-049 | Payment, cancellation and expiry never conflict | M | R1 | SCR-08 |
| US-050 | See my order history | M | R1 | SCR-09 |
| US-051 | See the full detail of an order | M | R1 (refund fields populated from R2) | SCR-10 |
| US-052 | Order status always follows the allowed transitions | M | R1 (administrator transitions R2) | SCR-10 |
| US-053 | Cancel an unpaid pending order | M | R1 | SCR-08, SCR-10 |
| US-054 | Cancel a paid order (R2) | M | R2 | SCR-10 |
| US-055 | Simulated refund completes (R2) | M | R2 | SCR-10 |
| US-056 | See ratings in listings and on product pages | M | R1 (read-only seeded data) | SCR-02, SCR-04 |
| US-057 | Read reviews on a product (R2) | M | R2 | SCR-16 |
| US-058 | Rate and review a product I received (R2) | M | R2 | SCR-16 |
| US-059 | Hide a review (R2, optional) | C | R2 | SCR-16 |
| US-060 | Administrators only | M | R2 | SCR-17 |
| US-061 | Create a product | M | R2 | SCR-18 |
| US-062 | Update a product | M | R2 | SCR-18 |
| US-063 | Deactivate and reactivate a product | M | R2 | SCR-17, SCR-18 |
| US-064 | Inspect any product | M | R2 | SCR-17, SCR-18 |
| US-065 | Manage variants | M | R2 | SCR-18 |
| US-066 | Manage categories and the small-goods designation | M | R2 | SCR-20 |
| US-067 | Adjust inventory with a reason | M | R2 | SCR-19 |
| US-068 | Choose product images from the managed set | S | R2 | SCR-18 |
| US-069 | Catalog changes affect carts but never orders | M | R2 | SCR-18 |
| US-070 | Administrator input follows the same rules | M | R2 | SCR-18 |
| US-071 | List and filter orders | M | R2 | SCR-21 |
| US-072 | Inspect an order, its payments and its stock movements | M | R2 | SCR-22 |
| US-073 | Move an order forward | M | R2 | SCR-22 |
| US-074 | Cancel an order on a customer's behalf | M | R2 | SCR-22 |
| US-075 | Sensitive administrator actions are recorded | S | R2 | SCR-23 |
| US-076 | Review the audit log | S | R2 | SCR-23 |
| US-077 | Customers receive in-app notifications (R3, optional) | C | R3 | R3 optional notifications, not designed (DQ-24) |
| US-078 | Read and clear my notifications (R3, optional) | C | R3 | R3 optional notifications, not designed (DQ-24) |
| US-079 | Know when the system is alive and ready | M | R1 | Platform health endpoints; no screen |
| US-080 | Reset to a known baseline | M | R1 | Seed and reset tooling; no screen |
| US-081 | Guarded test-support tools | M | R1 | Test-support tooling; no screen |
| US-082 | A trustworthy API description | M | R1 | API description; no screen |
| US-083 | Business parameters are configuration | M | R1 | Configuration; no screen |
| US-084 | One consistent error format | M | R1 | Error envelope; shown through UI-03, UI-04 and the field-error component, no dedicated screen |
| US-085 | Core flows work on any screen and with a keyboard | M | R1 (admin screens R2) | Cross-cutting: §9 responsive and §10 accessibility apply to every screen |
| US-086 | Testable and diagnosable screens | M | R1 | Cross-cutting: §7 test-id stems and §11 reduced-motion flag apply to every screen |

### 13.4 Release boundaries
Every screen carries a release label. 23 screens: 15 are R1 (some with a named R2 part, such as the refund fields on SCR-10 and the reviews section of SCR-04) and 8 are R2 (SCR-16, SCR-17, SCR-18, SCR-19, SCR-20, SCR-21, SCR-22, SCR-23). Check result: no screen mixes a later-release story with an unlabelled R1 screen. R3 notifications (US-077, US-078) are not designed. Customer wireframes never show an R2 control without an R2 label (for example, Cancel order on a confirmed order, and Reviews).

## 14. Design questions and approved defaults

**Status: all 26 questions (DQ-01 to DQ-26) were approved by the owner on 2026-10-17, as recommended.** They are design decisions and are kept separate from PRD business rules: nothing here changes an approved PRD rule. Wireframe elements marked `[P]` use these approved defaults. Four of the decisions describe behaviour the PRD does not specify (DQ-01, DQ-06, DQ-10, DQ-20) and are listed in §14.7 for recording in the PRD.

### 14.1 Design questions and approved defaults

| ID | Question | Approved default | Related | Status |
|---|---|---|---|---|
| DQ-01 | After a password change, does the app sign the customer in again, or require login? | Show a confirmation and require login (the PRD ends all earlier sessions) | GAP-01, FR-008, SCR-14 | Approved 2026-10-17; aligned with CL-17 on 2026-10-20 |
| DQ-02 | What does the interface do for a product that becomes unavailable between viewing and adding? | The product page already shows not found or out of stock; any failed add shows the API's message inline. The API response itself is an architecture matter | GAP-02, SCR-04 | Approved 2026-10-17 |
| DQ-03 | What do guests see in the header for wishlist and cart? | Both links are shown and lead to login; no counts for guests; no wishlist count for anyone | GAP-03, FR-040 | Approved 2026-10-17 |
| DQ-04 | Which columns does the order history show? | Order number, placement date, status, total, a View link | GAP-04, SCR-09 | Approved 2026-10-17 |
| DQ-05 | How are reviews presented? | First name only, newest first, 10 per page; no review editing | GAP-05, SCR-16 | Approved 2026-10-17 |
| DQ-06 | Is the payment deadline shown, and how does a customer return to a pending order? | Show "Reserved until [time]" on the payment page and order detail; the pending-order banner on the cart and checkout entry; a Pay now link on the pending order's detail; retries never extend the deadline | GAP-06, FR-112 | Approved 2026-10-17; aligned with CL-18 on 2026-10-20 |
| DQ-07 | How are admin product lists searched and paged? | Search by name or SKU, filter by status and category, 12 per page as in BR-016 | GAP-07, SCR-17 | Approved 2026-10-17 |
| DQ-08 | Which actions need a confirmation step? | Cancel order (already in WF-08), delete address, clear cart. Not remove line or remove from wishlist | GAP-08 | Approved 2026-10-17 |
| DQ-09 | What is the microcopy tone, and is the request id shown? | Plain English, sentence case; request id shown in small text only on unexpected failures | GAP-09, §14.4 | Approved 2026-10-17 |
| DQ-10 | Do customers give a reason when cancelling? | No; none is specified for customers (administrators give one) | GAP-10, FR-094 | Approved 2026-10-17; aligned with CL-19 on 2026-10-20 |
| DQ-11 | Which coupon error is shown when several apply? | Show the single code the API returns; the interface does not choose | GAP-11 | Approved 2026-10-17 |
| DQ-12 | Is a payment outcome preselected in checkout? | None selected; "Place order" is disabled until one is chosen, so tests and users choose explicitly | FR-057, SCR-07 | Approved 2026-10-17 |
| DQ-13 | Is checkout one page or several steps? | One page with five sections and a sticky summary | SCR-07 | Approved 2026-10-17 |
| DQ-14 | Does the home page carry a promo strip? | Yes, one static line limited to approved rules and filled from configuration values (never hard-coded figures) | FR-030, BR-076, DEC-29 | Approved 2026-10-17 |
| DQ-15 | Is the wishlist heart on product cards, or only on the product page? | Both, with guests sent to login | FR-041, FR-038 | Approved 2026-10-17 |
| DQ-16 | Can shoppers change the page size? | No; fixed at 12 (maximum 48 is an API limit) | BR-016 | Approved 2026-10-17 |
| DQ-17 | May the brand typeface be Geist, self-hosted? | Yes (OFL 1.1, verified); otherwise the system stack | §3.4, AS-03 | Approved 2026-10-17 |
| DQ-18 | May icons be Phosphor, self-hosted as an inline sprite? | Yes (MIT, verified) | §3.5, AS-03 | Approved 2026-10-17 |
| DQ-19 | Is a dark theme required? | No; the PRD does not ask for one. Tokens are semantic so one could be added later | NFR-011 | Approved 2026-10-17 |
| DQ-20 | Should the interface warn before the 30-minute session ends? | Yes. Five minutes before access-token expiry, display and announce “Your session is about to expire.” Do not refresh, renew or extend the token; expiry follows FR-005. | FR-005, AX-13, CL-20 | Revised and aligned with CL-20 on 2026-10-20 |
| DQ-21 | Where does an administrator hide a review? | A "Hide" control on each review in the admin product editor, not on the public page | US-059, FR-082 | Approved 2026-10-17 |
| DQ-22 | Which footer or help pages exist? | None beyond the demo statement; the PRD defines no About, Contact, Returns or legal pages | FR-028 | Approved 2026-10-17 |
| DQ-23 | What does an administrator see on the storefront? | An "Admin" link and Log out; no cart, wishlist or checkout controls | BR-065 | Approved 2026-10-17 |
| DQ-24 | Are R3 notifications designed now? | No; R3 is optional and needs separate approval. The header reserves no space for it | FR-101, FR-102 | Approved 2026-10-17 |
| DQ-25 | Status wording and colours | As in §3.3 (Pending, Confirmed, Processing, Shipped, Delivered, Cancelled; Unpaid, Paid, Failed; Not applicable, Refund pending, Refunded) | BR-043, BR-044, BR-056 | Approved 2026-10-17 |
| DQ-26 | Is there image zoom or a lightbox on the product page? | No; the PRD asks for a gallery only | FR-022 | Approved 2026-10-17 |

### 14.2 Observation disposition and architecture follow-ups

The observations in User Stories v0.3 have been reconciled as follows. GAP-01, GAP-06 and GAP-10 are resolved in PRD v0.7 by CL-17, CL-18 and CL-19 respectively. DQ-03–DQ-09 supply approved design defaults for the remaining visual questions. GAP-02 and GAP-11 remain architecture follow-ups because the interface decision does not define backend validation/error semantics.

| GAP | Disposition | Design decision or remaining follow-up | Reference |
|---|---|---|---|
| GAP-01 | Resolved | Successful password change invalidates previous tokens, redirects to login and shows confirmation there; customer logs in using new password | CL-17, FR-008, US-008 |
| GAP-02 | Architecture follow-up | UI displays the API's message inline if adding an unavailable item fails. Define the API response for inactive, removed or unknown products/variants in architecture; the UI does not invent the response contract | DQ-02, US-026, US-033 |
| GAP-03 | Design disposition approved | Guests see Wishlist and Cart links leading to login, without counts; no wishlist count for any user | DQ-03 |
| GAP-04 | Design disposition approved | Order-history columns: order number, placement date, status, total and View | DQ-04 |
| GAP-05 | Design disposition approved | Reviewer first name only; newest first; 10 reviews per page; no review editing | DQ-05 |
| GAP-06 | Resolved | Show reservation deadline and Pay now route as specified; retries never extend the 30-minute deadline | CL-18, FR-112, US-043, US-044, US-051 |
| GAP-07 | Design disposition approved | Admin product search by name/SKU, filter by status/category, 12 rows per page | DQ-07 |
| GAP-08 | Design disposition approved | Confirmation for order cancellation, address deletion and cart clearing; no confirmation for cart-line or wishlist-item removal | DQ-08 |
| GAP-09 | Design disposition approved | Plain English and sentence case; request ID shown only for unexpected failures | DQ-09 |
| GAP-10 | Resolved | Customer cancellation requires no reason for eligible orders; administrator cancellation still requires a 1–200 character reason | CL-19, FR-072, FR-073, FR-094, US-053, US-054, US-074 |
| GAP-11 | Architecture follow-up | UI displays the coupon error code/message returned by the API. Architecture must define deterministic validation precedence when multiple coupon errors apply | DQ-11, US-036, US-037 |

### 14.3 Owner decisions
All 26 design questions have approved dispositions. The owner approved Gallery (A), the N-and-dot logo concept and the corrected full design baseline on 2026-10-20. DQ-01, DQ-06, DQ-10 and DQ-20 are reconciled with PRD v0.7 clarifications CL-17 to CL-20. GAP-02 and GAP-11 remain architecture follow-ups, not open visual-design approvals.

### 14.4 Approved payment outcome copy
Microcopy was proposed and is approved [P, DQ-09]. Every outcome message says what happened, that nothing was charged (it is a simulation) and what the customer can do.

| Situation | Heading | Message | Primary action |
|---|---|---|---|
| Approved | Order confirmed | Thank you. Your simulated payment was approved. | View order |
| Declined | Payment declined | This simulated payment was declined. Nothing was charged. Your items are still reserved. | Retry payment |
| Timed out | Payment timed out | The simulated payment did not complete in time. Nothing was charged. Your items are still reserved. | Retry payment |
| Processing error | Payment could not be processed | Something went wrong while processing the simulated payment. Nothing was charged. Your items are still reserved. | Retry payment |
| Attempts exhausted | No attempts left | You have used all 3 payment attempts for this order. You can cancel it and start again. | Cancel order |
| Order expired | Order expired | This order was cancelled because payment was not completed in time. Your cart has been restored. | Back to cart |
| Order cancelled | Order cancelled | This order was cancelled. | Back to cart |
| In progress | Processing your payment | This can take a few seconds. Please do not close this page. | none |

### 14.5 Discrepancies between the PRD and the user stories
The brief was reconciled against PRD v0.7 and User Stories & Flows v0.3 for the four updated behaviours (CL-17 to CL-20), screen references, resolved observations and state coverage. GAP-01, GAP-06 and GAP-10 are closed in the PRD and stories; GAP-02 and GAP-11 are explicitly retained as architecture follow-ups. No additional business-rule discrepancy was identified in this review. The PRD remains authoritative if a discrepancy appears later. The prototype has not been visually inspected in a real browser, and runtime accessibility testing remains a future verification task.

### 14.6 Design critique (manual)
`impeccable`'s critique references were not available, so this is a manual review against §2 and the generic-template tells listed by `design-taste-frontend`.

| Check | Finding | Action |
|---|---|---|
| Repetitive "three identical cards" layout | Home uses three different structures (hero, asymmetric tiles, product row, editorial band) | None |
| Hierarchy on the cart and checkout | The total is the strongest figure in the summary; blocking reasons sit next to the disabled button | Verify with the design review |
| Sticky bars on mobile can cover content | Sticky "Add to cart", Checkout and Place order bars | Reserve bottom padding equal to the bar height plus the safe area |
| Informational price-changed flag can be missed | Shown on the line and again as a message near the summary | Keep icon and text; do not rely on colour |
| Simulated payment could look like a real card form | Radio group, no card icon, "No card details are collected" in text | Keep the explanatory line visible without a tooltip |
| Filter chips and long product names at 360 px | Chips wrap; names wrap to two lines | Wrap, never truncate prices or availability |
| Photography dependence | The chosen direction relies on good images | Make the image pipeline (§12) a prerequisite for visual review |
| No dark theme | Not required | DQ-19 |

### 14.7 PRD clarifications already incorporated

The four decisions previously listed as defaults to record in the PRD were incorporated into PRD v0.7 and User Stories v0.3. They are not outstanding documentation tasks. The PRD clarifications are authoritative for architecture and test design.

| Design question | Approved behaviour | PRD clarification | Story alignment |
|---|---|---|---|
| DQ-01 | Password change invalidates previous tokens, confirms success, redirects to login and requires the new password | CL-17, FR-008, AC-009 | US-008 |
| DQ-06 | Active reservation deadline is shown on payment and order detail; pending-order banner offers Pay now and Cancel order; detail offers Pay now; retry does not extend the deadline | CL-18, FR-112, AC-120 | US-043, US-044, US-051 |
| DQ-10 | Customer cancellation does not require a reason; admin cancellation still requires one | CL-19, FR-072, FR-073, FR-094, AC-121 | US-053, US-054, US-074 |
| DQ-20 | Show and announce the session-expiry warning five minutes before access-token expiry; no token refresh or extension | CL-20, FR-005, AC-119 | US-005, UI-28 |

## Appendix A — Visual exploration assets

| File | What it is | How to use it | Verification |
|---|---|---|---|
| `docs/planning/design/prototypes/home-direction-picker.html` | One self-contained page with three home-page directions (Gallery, Catalogue, Court), identical content and real interactions (category filter, wishlist toggle, mobile menu) | Open in a browser; press 1, 2 or 3, or use the toolbar; resize to see responsive behaviour. Gallery (A) is the approved direction. The prototype is isolated from production code and is not the storefront | Script behaviour checked in a DOM simulator; zero external network references; contrast of the three palettes computed. **Not rendered in a real browser.** Product images are labelled placeholders; products and brands are fictional |
| `docs/planning/design/brand/nexacart-logo-concepts.svg` | Approved logo concept sheet: N-and-dot mark, wordmark, reversed lockup, small sizes | Open in a browser or vector editor | SVG concept sheet; contrast of mark colours computed. Geist is approved; final artwork preparation and wordmark outline conversion remain production-artwork tasks |

## Appendix B — Design tokens as CSS custom properties

```css
:root {
  --color-canvas: #FFFFFF;
  --color-surface-1: #F6F7F8;
  --color-surface-2: #ECEEF0;
  --color-border-subtle: #DDE0E4;
  --color-border-control: #8B919B;
  --color-text-muted: #5B616B;
  --color-text-body: #2A2E35;
  --color-ink: #14161A;
  --color-accent: #2447D6;
  --color-accent-tint: #E6EEFB;
  --color-accent-on-ink: #8FA6FF;
  --color-success-bg: #EAF4EC;
  --color-success-text: #1F5A2B;
  --color-warning-bg: #FBF1D8;
  --color-warning-text: #7A5200;
  --color-error-bg: #FCE9EA;
  --color-error-text: #8F1F26;
  --color-error-on-white: #9B1C23;
  --color-info-text: #1B3F9A;
  --font-sans: "Geist", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 96px;
  --container-content: 1200px;  /* 1320px from 1440px up */
  --container-narrow: 640px;
  --container-prose: 720px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-pill: 999px;
  --border-subtle: 1px solid var(--color-border-subtle);
  --border-control: 1px solid var(--color-border-control);
  --focus-ring: 0 0 0 2px var(--color-canvas), 0 0 0 4px var(--color-accent);
  --shadow-overlay: 0 8px 32px rgba(20, 22, 26, 0.06);
  --z-sticky: 20;
  --z-flyout: 30;
  --z-dialog: 40;
  --z-toast: 50;
  --ease-out: cubic-bezier(0.2, 0.7, 0.2, 1);
  --duration-press: 100ms;
  --duration-fast: 150ms;
  --duration-panel: 200ms;
}
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; } }
```

## Appendix C — Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-17 | First draft for owner review, based on PRD v0.6 and the user stories draft. No application code and no other planning document was created |
| 0.2 | 2026-10-17 | Owner approved all design questions DQ-01 – DQ-26 ("approve all"). Status changed to approved baseline; wording describing proposals as pending was updated; §14.3 and a new §14.7 added. No wireframe, token, component or requirement reference changed; the document version is 0.2 |
| 0.3 | 2026-10-20 | Owner approved Gallery (A), the N-and-dot logo concept and the full design baseline. Reconciled the brief with PRD v0.7 and approved User Stories v0.3; updated CL-17–CL-20 behaviour, closed GAP-01/06/10, retained GAP-02/11 as architecture follow-ups, corrected cart arithmetic and UI-state coverage, and updated traceability/metadata. Real-browser and runtime accessibility verification remain outstanding |
