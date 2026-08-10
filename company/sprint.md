# Sprint State and Approved Milestone Breakdown

**Status: APPROVED by Hasan, on behalf of both founders, 2026-08-10.** The shape and ordering are approved; the *contents* of M6 onward are explicitly not, and will change as the pilot teaches us things. M4 (payroll and commission) approved including its self-imposed limit. Security pulled forward into M3 approved.

No sprint is running yet. The weekly founder review is Saturdays at 10:00 Bahrain time; **M1 goes there as the first sprint plan.**

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

### Positioning at onboarding — founding member, not free (founder directive, 2026-08-10)

**These businesses run without charge because billing does not exist yet, not because we are giving anything away.** Hasan's instruction: set that expectation explicitly at onboarding — a founding-member arrangement, price coming, terms agreed later. Businesses that receive something free for months resist paying for it afterwards, and that would be a self-inflicted problem at exactly the moment we need conversion evidence.

Practical consequence: the provisional price should be stated to pilot businesses *during* onboarding, not after the pilot. They should agree in principle to a number before they have months of free use behind them. This also makes M5 a real willingness-to-pay test rather than a usage test with a pricing conversation bolted on later.

### What failure looks like — written before the pilot, not after

**Founder directive, 2026-08-10 (Hasan):** a decision point whose criteria are set afterwards gets rationalised into a pass. So these are fixed now. **Thresholds marked provisional are to be confirmed with Hasan before the pilot starts** — he is the domain authority on what normal job volume and staffing look like, and I should not invent numbers he can supply.

**The primary metric is logging completeness, not logins.** Jobs logged in Loop Labs as a fraction of jobs the business actually performed in the same period. Incomplete logging is the failure that matters, because the insights they pay for are worthless on partial data — and this is the number that tells us whether the employee app works in the hands of the actual workforce. Provisional bar: sustained above 80% by week three, measured against the owner's own count.

**Failure mode one — they use it for two weeks and then stop.** Meaning: the tooling is not load-bearing in their day, and they reverted to manual because the app costs more effort than it saves. This is the most serious of the three because it invalidates the SaaS-first premise itself, not the pricing. Response: **do not build the marketplace on top of it.** Diagnose which side broke — the employee app (logging burden falling on staff who cannot or will not do it) or the owner side (dashboard showing nothing they did not already know). Fix or narrow before proceeding to M6.

**Failure mode two — they use it daily but say they would not pay.** Meaning: real utility, wrong price or wrong package. Materially less serious than mode one, because the product works and the commercial construction does not. Response: establish the number they *would* pay. If that number cannot support the business, the fault is in the packaging — likely that value needs concentrating into commission calculation and insights rather than spread thinly across a base fee.

**Failure mode three — they ask for something we have not built.** Meaning depends entirely on what. If it is already later in the plan, that is confirmation of the sequence and costs nothing. If it is not in the plan at all and is blocking their adoption, that is a specification gap and **the most valuable finding of the three** — it is cheaper to learn now than after the marketplace is built on the wrong base.

**A fourth mode I am adding, because it is the one that hides.** The owner back-filling job records themselves at the end of the day, while employees do not use the app. That reads as healthy usage in every metric and is actually a failure: it means the employee app did not work, the data is retrospective and unverified rather than GPS-and-photo verified, and the payroll case collapses because there is nothing for staff to trust. **Detection: check whether job records are created near the job's actual time and from the employee's device, not merely that they exist.**

**What a pass looks like.** Logging completeness sustained past week four without founder prompting; employees logging their own jobs rather than the owner back-filling; the owner referring to the revenue or staff view unprompted; and agreement in principle to the provisional price. All four, not three of four.

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

The charter puts Security in the third wave. **Pulled forward to M3 — approved 2026-08-10.** M3 is where employee personal data, photographs, GPS-verified job status and consent records first appear, and PDPL applies from the first record rather than from launch. Security is a blocking gate on exactly that surface, and retrofitting it after the data model is settled is the expensive order.

## Tensions I am not resolving quietly

The formal trial cannot begin before M6. The specification requires the trial to include the paid add-ons and to last long enough that insights have appeared. Until insights exist, a trial would demonstrate the free tier only. That is why M5 is a free founder-led pilot rather than the commercial trial.

Deposit sizing stays blocked. It depends on the gateway's real chargeback dispute windows, which depends on gateway selection, which depends on registration. The founders cut the pricing circularity at the price link instead; this one waits and must not hold up anything else.

Wallet licensing remains the highest-consequence open item. Building it is a founder decision already taken. The mitigation is that all wallet logic sits behind a clear internal boundary so a forced change is contained rather than a rebuild.

The marketing add-on is genuinely undefined. Nothing here depends on it.

## What was approved, and what was not

**Approved 2026-08-10:** the shape and the ordering. M4 including its constraint. Security into M3.

**Deliberately not approved:** the contents of M6 onward. Those will change as we learn from the pilot, and treating them as settled would be false precision. Re-propose them after M5, not before.

**Next:** M1 as the first sprint plan, at the Saturday review.
