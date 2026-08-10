# Sprint State and Proposed Milestone Breakdown

**Status: the milestone breakdown below is PROPOSED, not approved.** Presented to the founders 2026-08-10. No sprint is running. The weekly founder review is Saturdays at 10:00 Bahrain time; the first sprint plan goes there.

**In flight right now:** Architect run 16, the ownership map, delivered to `company/reports/2026-08-10-architect-run16.md`. Awaiting CEO review then founder approval. Nothing else is running.

---

## The shape, and why this shape

Two things drive it. The founders have decided to lead with the business tooling and let the marketplace follow. And everything downstream of payments is blocked on company registration, which has not started.

Those combine well rather than badly. The tooling needs no payment gateway, so the blocked path and the chosen path are not the same path. But it has a consequence worth stating plainly: **we can build the product before we can charge for it.** Loop Labs' primary revenue line — subscription billing — is behind registration, so the first businesses run on the product without being billed by it.

I have deliberately not put dates on any of this. The founders have set no deadline and I have no basis for estimating durations with one agent's output observed so far. Sequence and gates are real; dates would be invented.

## Founder track — runs in parallel, starting now, not a milestone

Not CEO work and not shortened by any number of agents. It is the critical path for everything after M6.

Company registration, and the jurisdiction choice between Bahrain and the UAE.

Four advisor conversations: wallet licensing, VAT treatment, data residency, payroll exposure. Licensing is the expensive one and the CEO keeps flagging it.

The three-business validation, with a provisional price the CEO proposes, marked provisional.

## M1 — Foundations

The Architect's six deliverables: ownership map, geospatial decision framework, scheduling model, Flutter state management, performance targets, API contract v1. Repositories, branch protection, CI skeleton.

Organisation added: Product Manager, DevOps.

Exit: an agent can be given a task and knows what it owns, what the contract is, and what target it is building against.

## M2 — Skeleton

Database schema for the tooling entities with migration tooling, Backend as sole author. FastAPI skeleton with path versioning, error handling and idempotency middleware. Three Flutter app shells on the agreed state management. Firebase project, phone and OTP authentication with SMS fallback. Dev and staging environments with a synthetic data generator. CI running with contract tests. Feature flags from this point on.

Organisation added: Backend, QA, then Frontend, UX/UI, then Integrations.

Exit: a user can sign in on all three apps. Nothing else works, and that is correct.

## M3 — The sellable product

This is the one that matters. Business registration with licence and bank details and founder approval. Branch management. Services from pre-filled templates with prices and declared durations. Staff, shifts, branch reassignment. Employee app: schedule, job list, availability, and real internationalisation rather than a language field. Job logging with guided photo capture, including walk-ins with no booking. Basic revenue view for today, this week, this month. Business dashboard on web and mobile.

Dashboard leads with money and staff, per Hasan, and nothing else competes for the top of the screen.

Organisation added: Security, before any personal-data work merges.

Exit: a real carwash business can run its daily operations on Loop Labs without any customer ever using the platform.

## M4 — Payroll and commission

**This is the CEO's addition and is not a stage in the technical plan.** Commission calculation from job records, per-employee earnings, anomalous-logging patterns surfaced to the owner, export.

Reasoning: staff are paid salary plus a per-job or commission element, so job records are already payroll input. This turns the tooling from useful into operationally necessary, gives employees a real reason to log correctly, and is probably a better first version of the accounting add-on than full bookkeeping. It needs no payment gateway, because it calculates and reports rather than moving money.

Constraint: **calculate and display, never file or pay**, until the payroll advisor has been consulted. The specification flags employment-law exposure if the platform calculates pay.

Exit: an owner can pay staff from Loop Labs' numbers instead of working it out by hand.

## M5 — Pilot

Founder-led, not a build. The businesses ready to start are onboarded personally by the founders and run on M3 plus M4, free, since billing does not exist yet.

This is the real validation and the genuine decision point. If businesses do not use it daily, building the marketplace on top would be building on an unproven base.

Exit: we know whether they use it daily, and whether they would pay.

## M6 — Insights v1

Cannot precede the pilot, because it needs weeks of real data. Private insights on the business's own data: staff performance, demand, revenue, retention. Money and staff first. Speed metrics withheld until quality signals exist. Export as PDF and spreadsheet. Insights link to the action that fixes them.

Organisation added: Data/ML.

Exit: an owner opens the dashboard and learns something they did not know, from their own data.

## M7 — Money

**Gated on company registration and a gateway account.** Gateway integration for both markets and currencies. Payment intents, idempotency, webhooks. Wallet ledger, append-only with derived balances, commission and commission tax as separate lines. Deposits. Withdrawals. Subscription billing: plans, deposit before trial, trial with all add-ons enabled, recurring billing, seven-day grace period, add-on entitlement, clean departure with final settlement.

Exit: a business signs up, places a deposit, trials the full product, converts, is billed monthly, and can leave cleanly without manual intervention.

## M8 onward — the marketplace arc

Sequence, held deliberately loose because decisions this far out are low-value now.

Discovery and booking, which can be built before M7 but cannot launch before it, since booking requires prepayment. Then live tracking. Then memberships. Then support, trust and reviews. Then launch readiness: load testing, external penetration test, failure injection, backup restore verification, minimum supported version enforcement, legal documents.

Organisation added across these: CTO when four or more technical agents run in parallel, Performance when there is something real to measure, SRE before production, HR when agent count justifies monitoring the agents rather than the work.

## Deliberate deviation from the charter's waves

The charter puts Security in the third wave. **I propose pulling it forward to M3.** M3 is where employee personal data, photographs, GPS-verified job status and consent records first appear, and PDPL applies from the first record rather than from launch. Security is a blocking gate on exactly that surface, and retrofitting it after the data model is settled is the expensive order.

## Tensions I am not resolving quietly

The formal trial cannot begin before M6. The specification requires the trial to include the paid add-ons and to last long enough that insights have appeared. Until insights exist, a trial would demonstrate the free tier only. That is why M5 is a free founder-led pilot rather than the commercial trial.

Deposit sizing stays blocked. It depends on the gateway's real chargeback dispute windows, which depends on gateway selection, which depends on registration. The founders cut the pricing circularity at the price link instead; this one waits and must not hold up anything else.

Wallet licensing remains the highest-consequence open item. Building it is a founder decision already taken. The mitigation is that all wallet logic sits behind a clear internal boundary so a forced change is contained rather than a rebuild.

The marketing add-on is genuinely undefined. Nothing here depends on it.

## What I recommend approving

Approve the shape and the ordering, not the contents of M6 onward — those will change as we learn from the pilot, and pretending otherwise would be false precision.

Then M1 as the first sprint at the Saturday review.
