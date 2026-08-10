# Loop Labs — Technical Specification & Implementation Plan

*The engineering companion to the Consolidated Specification. That document says what the system does; this one says how it is built and in what order.*

*The stages here are ordered by **technical dependency** — what must exist before what. What ships when, and what is in scope for each release, remains the CEO's proposal for founder approval.*

* * *

# Part One — Technical Specification

## 1\. Architecture Overview

Four deployable components:

| Component | Technology | Responsibility |
| --- | --- | --- |
| API | Python 3.11\+ / FastAPI | All business logic, the system of record |
| Client | Flutter | Customer, business, and employee apps — mobile and web |
| Realtime | Firebase Realtime Database | Live location only |
| Cockpit | Python / FastAPI | Agent orchestration, founder interface — separate repository |

**Data stores:** PostgreSQL (system of record), Redis (cache, sessions, matching hot path), Firebase (auth, push, file storage, live location).

**The load\-bearing decision:** live GPS never touches PostgreSQL. Location updates are high\-frequency and ephemeral; routing them into the relational store would put the heaviest write load in the system directly on top of the data that matters most. Only meaningful location events — arrived, started, completed — are persisted relationally.

## 2\. Data Model

### 2\.1 The critical distinction — Job versus Booking

**A booking is a customer's request. A job is work performed.**

Most jobs have a booking behind them. **Walk\-ins and competitor\-platform work do not.** This is not an edge case — it is central to the SaaS\-first strategy, because a business's operational data is only complete if externally\-sourced work is captured too.

Modelling these as one entity would be a painful migration to undo later. `Job.booking_id` is nullable, and that nullable column carries real weight:

- A job **without** a booking counts in the business's own insights, and **never** feeds the platform duration model, the benchmark pool, or pricing.
- A job **with** a booking feeds everything.

### 2\.2 Core entities

**Market** — `code` (BH, AE), `currency`, `timezone`. Every business, booking, price, and employee carries a market. Adding Saudi or Kuwait later must be configuration, not migration.

**Business** — account\-level. Legal name, licence, market, subscription state, deposit, marketplace\-visible flag (false is valid and supported), benchmark\-pool opt\-in flag.

**Branch** — belongs to a business. Location, address, service radius for mobile. Staff belong to branches; ratings aggregate to the business.

**Employee** — belongs to a branch, reassignable. Name, photo, phone, language preference. Consent record with timestamp.

**Shift** — employee, branch, start, end. **Availability is derived from shifts, not from published business hours.** Only slots with a scheduled employee are bookable.

**ServiceCategory** — platform\-defined standard types (exterior wash, interior clean, full detail). Fixed list.

**BusinessService** — a business's offering of a category: price, declared duration, fixed or mobile, included\-in\-membership flags, opt\-in for Loop Labs Custom.

**Customer** — phone (identity), name, market. Guest browsing requires no record.

**Vehicle** — customer, make, model, colour, plate. All required. Multiple per customer.

**Address** — customer, label, coordinates. Multiple per customer.

**Booking** — customer, branch, type (scheduled or immediate), state, market, requested time, **price snapshot taken at confirmation**, notes, linked\-visit reference for additions.

**BookingItem** — booking, business\_service, vehicle, price at time of booking. A booking has many items; this is what makes multi\-service and multi\-vehicle work.

**Job** — nullable booking, branch, employee(s), vehicle, service, state, actual start and end, source (platform / walk\-in / external). Per\-vehicle, not per\-booking.

**JobPhoto** — job, type (before/after), URL, capture coordinates, timestamp. Photos are the status trigger, the dispute evidence, and the chargeback evidence.

**Payment** — booking or membership, amount, currency, gateway reference, state, idempotency key.

**WalletTransaction** — owner (business or customer), amount signed, type (earning, withdrawal, commission, tax, chargeback, refund, deposit), reference, running balance. **Append\-only.** Balance is derived, never stored as a mutable field.

**Membership** — type (business tier or Loop Labs Custom), business (null for Custom), tier, customer, purchased date, period end, price paid, discount applied.

**MembershipEntitlement** — membership, service, quantity total, quantity redeemed, expiry. **A membership is a purchased entitlement independent of any booking** — a customer can buy without booking anything.

**Review** — booking, customer, stars, optional text, edit window expiry, moderation state. Attributed internally to the job's employee; shown publicly only at business level.

**Deposit** — business, amount, held\-since, state.

**Chargeback** — payment, amount, reason, state, evidence references.

### 2\.3 Invariants to enforce in the schema

- A booking may only reference services from **one branch**
- A booking's market must match the customer's market
- Wallet balance is the sum of transactions — never a stored mutable number
- Prices on `BookingItem` are **snapshots**, never foreign keys to current price
- Location data outside a shift window is **not stored at all**, rather than stored and hidden
- Every job has at least one before photo and one after photo before it can be marked complete, unless the business has disabled photos for externally\-logged jobs

## 2\.4 Corrections to the data model

**`Job.employee` is singular, not plural.** Multiple employees may work a multi\-vehicle *booking*, but a job is per\-vehicle and has exactly one responsible employee. Plural employees on a job would reintroduce precisely the attribution ambiguity that per\-vehicle jobs exist to remove, and would corrupt per\-employee metrics.

**`Review` attaches to the booking**, and its rating is attributed to **each job's employee** for internal metrics. A booking spanning three vehicles worked by two employees produces one public business rating and internal attribution to both. Define this mapping explicitly rather than leaving it implied.

**`Booking` needs:** `preferred_employee_id` (nullable), `recurring_series_id` (nullable), `linked_visit_id` (nullable, for additions), and `payer_id` distinct from `customer_id`.

**`BusinessService` needs:** `price_floor` (nullable) — unused until occupancy pricing, but the field belongs in the original schema.

**`Employee`** has `language`, and the employee app requires real internationalisation from Stage 3 — not a field alone. The workforce is predominantly South Asian, and a worker who cannot read the job screen produces bad data.

**Fleet accounts are not built, but do not preclude them.** Avoid hard\-coding one\-vehicle\-per\-customer or one\-payer\-per\-booking assumptions; the `payer_id` split costs nothing now and saves a migration later.

## 3\. API Design

**REST, versioned in the path** — `/v1/...`. Mobile clients cannot be force\-updated, so old versions must keep working. A minimum supported version below which clients are forced to upgrade exists from the start.

**Contract tests fail CI on any mismatch** between client expectations and server responses. This is the mechanical guard on the seam between Backend and Frontend ownership.

**Authentication:** Firebase phone auth issues the token; the API verifies it and maps to an internal identity. Role — customer, business owner, employee, founder — determines scope.

**Idempotency is mandatory** on booking creation, payment, and additions. A retried request with the same key returns the original result rather than creating a second booking or a second charge. This is a hard requirement, not a nicety: without it, a customer on a poor connection gets double\-charged, and that is the failure that damages trust fastest.

**Endpoint groups:**

- `/v1/discovery` — search, ranked providers, service details (public, guest\-accessible)
- `/v1/bookings` — create, modify, cancel, additions
- `/v1/jobs` — status transitions, photo upload, cannot\-complete, external job logging
- `/v1/business` — services, staff, shifts, availability, dashboard, wallet
- `/v1/employees` — schedule, current job, availability, earnings
- `/v1/memberships` — purchase, entitlements, redemption
- `/v1/payments` — intents, confirmations, webhooks
- `/v1/insights` — private, public comparison, pool
- `/v1/admin` — founder\-only

## 4\. Real\-Time Architecture

**Live location: Firebase Realtime Database.**

Path structure: `/live/{branch_id}/{employee_id}` holding coordinates, heading, timestamp, and current job reference.

- Employee app writes at a throttled interval while on shift **and** on an active job
- Customer app subscribes to the single employee assigned to their booking
- Business dashboard subscribes to its own branch
- Security rules restrict reads to the assigned customer and the owning business
- Data is **ephemeral** — cleared on job completion and on shift end

**Nothing else uses Firebase Realtime.** Booking status, job progress, and notifications flow through the API and push. Keeping one narrow use prevents it becoming a shadow database.

**Persisted location events** — arrived, started, completed — are written to PostgreSQL as discrete records with coordinates, because they are evidence and audit, not tracking.

## 5\. The Matching and ETA Engine

The core query, and the hardest performance surface.

**Inputs:** customer location, service basket, requested time (now or scheduled), market.

**Steps:**

1. **Candidate set** — branches within service radius, in the customer's market, offering all requested services, with an employee on shift. Geospatial query.
2. **Availability** — capacity not exceeded, no conflicting bookings, schedule\-compatible with the basket duration.
3. **ETA per candidate** — predicted remaining time on current job, plus travel time to the customer.
4. **Rank by ETA**, return list. The customer chooses.

**Duration prediction:** the business's declared duration is the starting estimate. The model refines it per employee and per business from real completion times — **platform bookings only**. Externally\-logged jobs never train it.

**Travel time:** Google Maps, cached aggressively. Distance Matrix calls are a per\-request cost.

**Performance:** this query runs on every discovery request and is the first thing to degrade under load. It is the primary target for the load testing in Section 37 of the specification, and the geospatial approach — PostGIS versus a Redis geo index versus hybrid — is benchmarked before commitment.

## 6\. Payments and Wallet

**Flow for a standard booking:**

1. Client requests a payment intent, with an idempotency key
2. API creates a pending payment and calls the gateway
3. Client completes payment through the gateway SDK
4. Gateway webhook confirms; API marks the booking confirmed and notifies the business
5. On job completion, a wallet transaction credits the business, with separate lines for commission and commission tax

**Wallet is append\-only.** Balance is always derived by summation. This makes every figure auditable and makes a negative balance a natural state rather than an error condition.

**Withdrawals** are requested or scheduled, subject to a minimum threshold, and produce a debit transaction plus a gateway payout.

**Chargebacks:** webhook creates a chargeback record, debits the business wallet — going negative if needed — and attaches the job photos as evidence. If the negative balance reaches the deposit, the business is suspended from taking new work.

**Memberships:** payment on purchase creates entitlements and records the money as a **liability, not revenue**. Redemption creates a job, decrements the entitlement, and credits the business its share. Only commission is recognised as revenue.

**Regulatory note:** the wallet holds funds on behalf of businesses and customers. The founders have chosen to build it and resolve licensing later. Isolating all wallet logic behind a clear internal boundary is worth doing anyway, so that if the model must change, the change is contained.

## 7\. Security Architecture

**Secrets** in a dedicated manager, injected at runtime. Never in a repository, never in agent context. Automatic detection and redaction on everything an agent reads and writes.

**Edge:** rate limiting, WAF, DDoS protection. OTP endpoints are rate\-limited per phone number and per IP — SMS\-pumping fraud costs real money. Discovery endpoints are rate\-limited against competitor scraping.

**Data:** location retained only within shift windows. Deletion anonymises rather than erases, preserving financial records. Photos survive while a dispute window remains open. Synthetic data only in non\-production environments.

**Access:** no agent touches production data. Model training runs inside production; agents see code, synthetic data, and aggregated metrics.

**Audit:** append\-only, including founder override actions.

## 8\. Infrastructure

**Region:** single GCC region. Backups replicated to a second region — recovery, not redundancy.

**Compute:** containers on managed orchestration. Auto\-scaling with a floor that protects response times and a ceiling that protects the bill.

**Environments:** dev, staging, production. Staging mirrors production shape; synthetic data only.

**CI:** relevant tests during work, full suite before merge. Linting, dependency scanning, secret scanning, contract tests. Blocking.

**Deploy:** automated smoke tests immediately after — authentication, search, booking, payment — with automatic rollback on failure.

**Observability:** logs, metrics, distributed traces, error tracking. Tracing especially: a slow booking could be the matching query, Maps, the gateway, or the client.

**Feature flags** from the first deployable increment.

* * *

# Part Two — Implementation Plan

**These stages are ordered by technical dependency.** Each requires the previous to exist. What is included in each, how far each goes, and what constitutes a releasable milestone remain the CEO's proposal for founder approval.

## Stage 0 — Cockpit and CEO

**Built by:** Faisal, in Claude Code.

FastAPI cockpit, Agent SDK integration, streaming chat, memory read and write, run log, `assign_task` tool. The CEO's brief and the company memory folder.

**Exit condition:** a founder can hold a conversation with the CEO, it has read the specification, and a decision made in one session is present in the next. **Verify persistence deliberately** — this failing silently is the worst outcome available.

## Stage 1 — Foundations

**Requires:** Stage 0.

The Architect activates. Deliverables, all before any application code:

- **The ownership map** — directory\-level, every directory assigned
- **Geospatial approach** — benchmarked, not assumed
- **Scheduling model** — fixed slots versus variable duration, resolved against the ETA engine's needs
- **Flutter state management** — structural, expensive to retrofit
- **Performance targets** — concrete numbers
- **API contract v1** — the seam between Backend and Frontend

Repository setup: GitHub, both repositories, branch protection, CI skeleton.

**Exit condition:** an agent can be given a task and knows what it owns, what the contract is, and what target it is building against.

## Stage 2 — Platform Skeleton

**Requires:** Stage 1.

- PostgreSQL schema — markets, businesses, branches, employees, customers, services. Migration tooling, Backend as sole author
- Firebase project — auth, storage buckets, security rules
- Phone plus OTP authentication end to end, with SMS fallback
- FastAPI skeleton with versioning, error handling, idempotency middleware
- Flutter skeleton with the agreed state management, three app shells
- CI running, contract tests in place
- Dev and staging environments, synthetic data generator

**Exit condition:** a user can sign in on all three apps. Nothing else works, and that is correct.

## Stage 3 — Business Tooling

**Requires:** Stage 2. **This is the product businesses actually pay for.**

- Business registration, licence and bank details, founder approval flow
- Branch management
- Service setup from templates — categories, prices, declared durations
- Staff management, shifts, branch reassignment
- Employee app: schedule, job list, availability
- **Job logging with guided photo capture** — including walk\-ins, with no booking
- Basic revenue view — today, week, month
- Business dashboard, web and mobile

**Exit condition:** a real carwash business can run its daily operations on Loop Labs without any customer ever using the platform. This is the SaaS\-first proposition, standing alone.

## Stage 4 — Discovery and Booking

**Requires:** Stage 3.

- Geospatial candidate query
- Availability computation from shifts, capacity, and radius
- Duration estimation from declared durations
- Travel time integration, cached
- Ranked provider list with filters
- Guest browsing
- Booking creation — scheduled and immediate, multi\-service, multi\-vehicle
- Vehicles, addresses, notes
- Automatic employee assignment, reassignment on unavailability
- Job status transitions driven by photos with GPS verification
- Cannot\-complete flow
- Notifications — push with SMS for critical

**Exit condition:** a customer can find a provider, book, and have the job performed and documented. No money has moved yet.

## Stage 4b — Booking Completeness

**Requires:** Stage 4. Items the specification requires that the core booking flow does not cover:

- **Recurring bookings** — series entity, per\-occurrence price locking, pause and re\-confirm when a business changes prices or drops a service
- **In\-progress additions** — bidirectional proposal, mutual confirmation, schedule\-compatibility check against the assigned employee's next commitment, slot locking from the moment of request
- **The escalation chain** — three notifications, then an automated voice call, then three minutes for the business to confirm. **This requires a voice provider, which is not in the stack.** Integrations must select one.
- **Preferred employee requests** — a field on the booking, with fallback to normal assignment when unavailable
- **Booking modification** — time, service, or vehicle, recalculated against originally agreed prices. This re\-runs the booking logic against an existing record; it is not a field edit.
- **Business\-configurable price floors** per service — the field that later enables occupancy\-based pricing. Cheap now, awkward to add once pricing logic is settled.

**Exit condition:** the booking lifecycle matches the specification in full, not just the happy path.

## Stage 5 — Payments

**Requires:** Stage 4, a registered company, and a gateway account.

- Gateway integration, both markets, both currencies
- Payment intents, idempotency, webhooks
- Prepayment at booking; saved cards held by the gateway
- Wallet ledger — append\-only, derived balances
- Commission and commission tax as separate lines
- Withdrawals, on demand and scheduled
- Deposits
- Cancellation credit, refunds, no\-show and dispatch fees
- Chargeback handling with photo evidence, negative balances, suspension at deposit limit
- Receipts

**Exit condition:** money moves correctly end to end, and every figure reconciles from the ledger.

*This stage is gated on company registration. Everything before it can proceed in parallel with that being arranged.*

## Stage 5b — Business Subscription Billing

**Requires:** Stage 3 and a gateway account. **This is Loop Labs' primary revenue line and it was missing from earlier drafts of this plan.**

- Subscription plans — base fee per market, add\-on catalogue and pricing
- Refundable deposit collection at signup, before the trial
- Trial state and expiry, with **all paid add\-ons enabled during the trial**
- Recurring billing, retries on failure
- **Seven\-day grace period** on a failed payment, then suspension
- Add\-on entitlement — which insights, accounting, and marketing features a business has access to
- Deposit refund on cancellation during trial; deposit held past the dispute window on later departure
- Thirty days notice handling, final settlement, wallet payout on departure

**Exit condition:** a business can sign up, place a deposit, trial the full product, convert to paid, be billed monthly, and leave cleanly — without manual intervention.

*This can run in parallel with Stage 4. It depends on the business tooling existing, not on the marketplace.*

## Stage 6 — Real\-Time

**Requires:** Stage 4.

- Firebase Realtime location writing from the employee app, shift\-bounded
- Security rules
- Customer live map
- Business branch view
- ETA refinement from live position
- Persisted location events for arrival, start, completion
- Automatic cleanup on completion and shift end

**Exit condition:** a customer watches their provider approach, and no location data exists outside shift windows.

## Stage 7 — Learning and Insights

**Requires:** Stages 3 and 4, plus accumulated data.

- Event schema, instrumentation across client and server
- Duration prediction model — platform bookings only, per employee and per business
- Business\-internal duration estimates — all jobs including walk\-ins
- Private insights: staff performance, demand, revenue, retention
- **Speed metrics withheld until quality signals exist**
- Public comparison — prices, service types, ratings
- Opt\-in benchmark pool with minimum sample enforcement
- Recommendations layer
- Export

**Exit condition:** a business owner opens the dashboard and learns something they did not know, from their own data.

*The model cannot be built before there is data. Declared durations carry the product until then, which is by design.*

## Stage 8 — Memberships

**Requires:** Stage 5.

- Business tiers — definition, service inclusion, discount, commission
- Loop Labs Custom — opt\-in per service, 5% plus commission
- Entitlements independent of bookings
- Redemption, no stacking
- Liability accounting, revenue recognition on redemption
- Refunds on business departure — wallet or original method
- Expiry

**Exit condition:** memberships sell, redeem, and reconcile without manual intervention.

## Stage 9 — Support and Trust

**Requires:** Stages 4 and 5.

- Support bot: entitlement execution, escalation, single\-source rules
- Founder admin dashboard: approvals, disputes, complaints, platform\-wide view
- Reviews: verified\-only, edit window, moderation filter, business dispute
- In\-app messaging, booking\-window scoped
- Blocking and platform bans
- Emergency button

## Stage 10 — Launch Readiness

**Requires:** everything above.

- Load testing against agreed targets, focused on the matching query and location fan\-out
- **External penetration test**
- Failure injection: gateway, Maps, SMS outages against defined fallbacks
- Backup restore verification
- Production environment, monitoring, alerting, on\-call paths
- Minimum supported version enforcement
- Legal: terms, privacy policy, PDPL evidence generation
- TestFlight and APK distribution

## Cross\-Cutting — Continuous Throughout

These are not stages; they run from Stage 2 onward:

- **Feature flags** on every increment
- **Contract tests** maintained as the API evolves
- **Documentation** as part of done
- **Security review** on anything touching auth, payments, personal data, or location
- **Agent additions** — one at a time, each with a shadow period, when the work demands it
- **Cockpit improvements** — built by agents, prioritised by what founders find painful

## Dependency Summary

```
Stage 0  Cockpit + CEO
   ↓
Stage 1  Foundations (Architect)
   ↓
Stage 2  Platform Skeleton
   ↓
Stage 3  Business Tooling  ─────────────┐  (standalone SaaS product)
   ↓                                     │
Stage 4  Discovery + Booking             │
   ↓         ↓                           ↓
Stage 5  Payments    Stage 6 Real-Time   Stage 7 Insights
   ↓                                     
Stage 8  Memberships
   ↓
Stage 9  Support + Trust
   ↓
Stage 10 Launch Readiness
```

**Note the branch at Stage 3.** Business tooling is a complete, sellable product on its own. Stages 4 onward add the marketplace. Whether to put Stage 3 in front of real businesses before building Stage 4 is a commercial decision for the founders and the CEO — but it is technically possible, and that optionality is worth knowing you have.

## What Is Deliberately Not Here

**No dates, no durations, no milestone boundaries.** These are technical dependencies, not a schedule. The CEO proposes what constitutes a milestone, what is in scope for each, and in what order the optional paths are taken — for founder approval, after it has read everything and confirmed its understanding.
