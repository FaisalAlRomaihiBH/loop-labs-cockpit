# AI Company Architecture — Carwash App Venture

## 1\. Vision

Instead of building the carwash app through one continuous, linear conversation with Claude Code, this design turns the effort into a small organization of specialized AI agents, each with a defined role, a defined cadence, and a memory of its own decisions. A **CEO agent** holds the vision, the budget, and the plan, and delegates execution to **employee agents** — a Backend Developer, a Frontend Developer, a Marketing Strategist, and others added as the venture grows. The goal is not just faster output, but a system that behaves like a real organization: decisions get made at the right level, work gets recorded, and each function improves over time based on what actually happened rather than repeating the same instructions from scratch every session.

This document lays out the org structure, how the agents coordinate, how "learning" concretely works for agents that cannot retrain themselves, and how to build this in Claude Code specifically — since that's where the underlying carwash app is already being built.

## 2\. Org Chart

| Role | Reports to | Core responsibility |
| --- | --- | --- |
| CEO Agent | You (founder) | Holds the vision, budget, and roadmap. Assigns work to employee agents, reviews their output, resolves conflicts between departments, decides what ships. |
| Backend Developer Agent | CEO | Owns the server, database, and API layer of the carwash app. Implements features assigned by the CEO, reports blockers and technical risk. |
| Frontend Developer Agent | CEO | Owns the UI/UX and client\-side app. Implements features assigned by the CEO, flags design or usability issues. |
| Marketing Strategist Agent | CEO | Owns growth: budget allocation, campaign planning, positioning. Reports performance against spend. |
| *(future)* QA / Test Agent | CEO | Verifies what Backend/Frontend ship actually works before it's considered done. |
| *(future)* Data Analyst Agent | CEO | Turns raw metrics (usage, revenue, campaign data) into a weekly digest the CEO and other agents consume. |
| *(future)* HR / Recruiter Agent | CEO | Drafts the brief and memory scaffold for any *new* role the CEO decides the company needs. |

Every agent below the CEO only talks to the CEO — not directly to each other. That's a deliberate constraint, not a limitation: it keeps one place (the CEO) where priorities get set and conflicts get resolved, and it keeps the system easy to reason about as it grows. If the CEO decides Backend and Frontend need to coordinate directly on an interface contract, it can hand both agents the same spec rather than being a bottleneck for routine detail — but decisions about *priority, scope, and budget* stay with the CEO.

## 3\. The CEO Agent

**Mandate.** The CEO agent holds the company's charter: the product idea (the carwash app), the current budget, the current strategic priorities, and the standing rule that no employee agent commits real money or ships a customer\-facing change without the CEO's sign\-off recorded in the log.

**Inputs each run:**

- The charter (vision, budget, current priorities) — stable, rarely changes
- The latest report from each employee agent since its last check\-in
- Key metrics (app usage, revenue, campaign spend/ROI) once those exist
- Any direction you've given it directly since the last run

**Outputs each run:**

- Updated task assignments for each employee agent (what to build/plan next, and why)
- A short founder\-facing summary: what shipped, what's blocked, what decisions were made, what needs your input
- An updated roadmap/priority list
- A log entry recording the reasoning behind any nontrivial decision (budget shifts, scope cuts, hiring a new role)

**Decision authority.** The CEO can reprioritize work between existing agents and adjust plans within the budget you've set. It should **not** be authorized to change the budget itself, hire a new role, or make an irreversible/external\-facing move (real ad spend, a public release, a legal or financial commitment) without flagging it to you first. Treat those as hard stops, not soft suggestions — this is the main safety valve on the whole system.

## 4\. Employee Agents

### Backend Developer Agent

- **Mandate:** implement and maintain the server, database, and API surface of the carwash app, per tasks assigned by the CEO.
- **Inputs:** current codebase, the specific task from the CEO, any bug reports or QA findings.
- **Outputs:** shipped code (committed to the repo), a short changelog entry, a list of blockers or technical debt worth the CEO's attention.
- **Constraints:** no schema or infrastructure change that affects cost or data safety without flagging it in the report for CEO sign\-off.
- **Cadence:** daily, or triggered directly when the CEO assigns a task.

### Frontend Developer Agent

- **Mandate:** implement and maintain the UI/UX of the carwash app, per tasks assigned by the CEO.
- **Inputs:** current codebase, design/product direction from the CEO, usability feedback.
- **Outputs:** shipped UI code, screenshots or a short demo note of what changed, flags on any backend dependency it's waiting on.
- **Cadence:** daily, or triggered when assigned a task.

### Marketing Strategist Agent

- **Mandate:** plan and report on growth activity within the budget the CEO has approved.
- **Inputs:** monthly/weekly budget figure, current campaign performance data (once there's live data — before that, market research and positioning work), the product's current feature set from the CEO (no promising features that don't exist yet).
- **Outputs:** a weekly roadmap ("this week: X, Y, Z, and why"), a running record of what's been tried and its result, budget\-remaining tracking.
- **Constraints:** proposes spend, doesn't execute real spend — the CEO approves before anything real\-money happens, at least until you're comfortable raising that ceiling.
- **Cadence:** weekly planning, with a lightweight daily check\-in once campaigns are actually live.

Each of these briefs is deliberately short. The detail lives in the memory file (below), not in an ever\-growing prompt.

## 4a. Adding roles later

QA, Data Analyst, and HR follow the same template once they're needed — QA sits between "Dev agents say it's done" and "CEO says it ships," Data Analyst turns raw numbers into the weekly digest the CEO and Marketing both read, and HR drafts the brief/memory scaffold for whatever role the CEO decides to add next. Don't build these until the first three agents are actually producing useful output — see the rollout plan in Section 9.

## 5\. Shared Company Workspace

All agents need a shared place to read from and write to — this is what makes the system stateful instead of starting from zero every run. Since the carwash app already lives in a Claude Code repo, the natural home is a `/company` folder inside that same repo, version\-controlled alongside the code:

```
/company
  charter.md              — vision, budget, current priorities (CEO maintains this)
  /ceo
    memory.md              — decision log: what was decided, when, and why
    roadmap.md              — current live priority list
  /backend
    brief.md                 — role definition (rarely changes)
    memory.md                — running log: what shipped, what was learned, open issues
  /frontend
    brief.md
    memory.md
  /marketing
    brief.md
    memory.md
    playbook.md              — accumulated rules ("channel X underperforms below $Y CPC")
  /reports
    2026-08-09-ceo-summary.md   — dated founder-facing summaries
  /metrics
    latest.json               — snapshot of usage/revenue/campaign data, refreshed periodically
```

Every agent's run follows the same shape: read its `brief.md` (who am I, what do I own), read its `memory.md` (what happened last time, what did I learn), read whatever the CEO assigned it this cycle, do the work, then **append** to its `memory.md` and write its report. Because it's a git repo, every change is versioned and diffable — you can literally watch the company's institutional memory evolve commit by commit, and roll anything back if an agent goes off the rails.

## 6\. Coordination Protocol

1. CEO agent runs first in each cycle: reads the charter, reads each employee's latest report, decides priorities, writes updated task assignments into each employee's inbox (a simple `next-task.md` per agent is enough).
2. Each employee agent runs, does its assigned work, writes its report and updates its own memory.
3. CEO agent's next run reads those reports before assigning the next round of work — this is the loop that makes the system iterative rather than static.
4. **Conflicts** (e.g., Marketing wants a feature Backend says isn't ready) get resolved by the CEO, not negotiated between the two employee agents directly.
5. **Escalation to you** happens whenever an agent's proposed action crosses one of the hard\-stop lines in Section 3, or when the CEO explicitly flags something as needing founder input in its summary. Early on, plan to actually read every CEO summary — this is your board meeting.

## 7\. Technical Implementation in Claude Code

This maps onto Claude Code's actual features without needing anything exotic:

- **Agents as subagents.** Define each role as a custom subagent in `.claude/agents/` (e.g. `ceo.md`, `backend-developer.md`, `frontend-developer.md`, `marketing-strategist.md`). Each subagent file's system prompt *is* the role brief from Section 4, plus an instruction to read and update its `/company/<role>/memory.md` file at the start and end of every run. Restrict each subagent's tool access to what its role actually needs (e.g. Marketing doesn't need write access to the codebase).
- **The CEO as orchestrator.** The CEO subagent uses Claude Code's Task tool to invoke the employee subagents, or you invoke each one directly and have the CEO's turn be a review\-and\-reassign step. Either works; starting with you manually kicking off each agent's turn is the simplest way to build confidence in the loop before automating it.
- **Cadence without a built\-in scheduler.** Claude Code doesn't have native cron. For daily/weekly automated runs, use your OS's cron (or a scheduled GitHub Action if the repo lives on GitHub) to invoke Claude Code headlessly, e.g. `claude -p "Run today's CEO review" --agent ceo`. Until that's set up, running each agent's turn manually once a day is a perfectly good starting point — automate the schedule once you trust the output.
- **Audit trail.** Because `/company` lives in the same git repo as the app, every agent action is a commit. This gives you a free audit log and an easy way to review what an agent actually did before it compounds into the next cycle.
- **Access boundaries.** Give each subagent only the tool permissions its role needs — Backend/Frontend get repo write access, Marketing and the CEO generally shouldn't need to touch code directly. This limits the blast radius of any one agent's mistake.

## 8\. The Learning Loop — What "Improvement" Actually Means

Worth being precise about this, since it's the part most likely to be oversold: none of these agents retrain or adjust weights. "Learning" here means something narrower and more mechanical, but it's real and it compounds:

1. An agent acts (ships a feature, runs a campaign plan, makes a call).
2. The outcome gets recorded as data — a metric, a bug report, a campaign result.
3. On its next run, the agent reads that outcome alongside its own memory file and **writes an explicit rule or note** based on it (e.g. Marketing's `playbook.md` gains a line: "Channel X underperforms below $30 CPC — deprioritize unless CPC improves").
4. That rule is now part of what the agent reads on every future run, so the behavior actually changes.

This only works if the memory files stay concise and rule\-like rather than turning into an ever\-growing diary — a `playbook.md` of twenty sharp rules is far more useful than five hundred lines of narrative log. Periodically (say, monthly), have the CEO agent's job include *pruning and consolidating* each department's playbook, not just appending to it.

## 9\. Rollout Plan

Building the full org chart on day one is the biggest risk to this actually working — it's much easier to debug one agent than five agents whose miscommunications compound. Phase it:

**Phase 1 — One agent, proven end to end.** Stand up the CEO agent and *one* employee (Backend or Frontend — whichever the app needs most right now). Run it manually for a few cycles. Confirm the memory\-file loop actually produces better output over time, not just more output.

**Phase 2 — Both dev agents.** Add the second developer agent once Phase 1's loop is trustworthy. This is also when the "employees report to CEO, not to each other" discipline gets its first real test.

**Phase 3 — Marketing.** Add the Marketing Strategist once there's an actual product to market and, ideally, some real usage data — a marketing agent working from zero data is just generating generic advice.

**Phase 4 — Automate cadence.** Move from manually kicking off each agent to a real schedule (cron / GitHub Action), once you trust the outputs enough not to want to review every single run.

**Phase 5 — Expand the org.** Add QA, Data Analyst, HR, or others, only as a specific gap becomes obvious (e.g. you keep finding bugs Backend/Frontend missed → add QA).

## 10\. Risks & Guardrails

- **Cost.** Every agent run is real API usage. Daily runs across five\-plus agents adds up — start with weekly cadence for anything that isn't urgent, and watch actual spend before automating daily runs across the whole org.
- **Runaway autonomy.** The hard stops in Section 3 (no real spend, no irreversible action, no new hires without founder sign\-off) exist specifically so a bad CEO\-agent decision can't cascade through the whole company unattended. Keep them non\-negotiable, especially early on.
- **Memory bloat / drift.** Left unpruned, memory files degrade into noise the agent stops effectively using. Build in the periodic consolidation step from Section 8.
- **False sense of "data\-driven."** An agent's output is only as good as the data it's actually given. Marketing "analyzing performance" before there's real campaign data is just an LLM generating plausible\-sounding strategy — useful for planning, but don't mistake it for the real analysis loop you're aiming for until real metrics are flowing in.
- **You are still the board.** This system is designed to reduce how much you have to hold in your head, not to remove you from decisions that matter. Read the CEO's summaries, especially in the first few weeks.

## 11\. Milestone 1 Charter — Loop Labs

Everything below is locked in from our planning conversation. This is the operating charter for Milestone 1 — treat it as the source of truth `charter.md` gets built from.

**Name.** The venture/operating entity is called **Loop Labs** — designed to extend beyond the carwash app to future ventures later, even though the carwash app itself doesn't have a name yet.

**Org for Milestone 1.** CEO Agent \+ Backend Developer \+ Frontend Developer \+ QA Agent, built and launched together. Backend and Frontend work in parallel on separate tasks. QA is the quality gate on every dev task — no separate automated\-test requirement beyond what QA needs to do its job. Beyond these four, no future role (Marketing, Data Analyst, Product, Design, DevOps, etc.) gets scaffolded until a real gap makes it obviously necessary — the long\-term aim is a full startup\-style org, phased in as needed, not built in advance.

**Autonomy.** Low. The CEO proposes every task; nothing gets assigned to Backend or Frontend until you approve it. Approval happens through live chat with the CEO agent, expected roughly daily. You also get a push notification whenever something needs your approval.

**Work rhythm.** Organized into weekly sprints with a stated goal, with individual tasks inside each sprint kept small and bite\-sized (hours to a day), so approvals stay frequent and reviewable rather than batched into large opaque chunks.

**Quality bar.** When QA rejects a dev agent's work, it goes straight back to the originating agent with QA's notes — no extra escalation needed for a routine fix. The CEO actively drives revision cycles using the full team's input (dev self\-reports \+ QA sign\-off) rather than passively trusting one signal or re\-reviewing raw code diffs itself — its job is to keep sending work back until it's actually good, not just to rubber\-stamp what QA passes. A task counts as fully **done** only once: code is merged, QA has passed it, and you've given final approval.

**Coordination & storage.** Plain git\-tracked markdown files in the real project repo — role briefs, per\-agent memory/playbook logs, dated reports — no ticketing system. Git workflow defaults to direct commits to main, since tasks are already approved before an agent starts (a second commit\-time gate would be redundant for a pilot this size); revisit if the pilot shows it's needed.

**Models & identity.** Every agent runs on the same Claude model — no per\-role tiering. Each agent gets a light identity (a name and a one\-line decision style) to keep reports and chat readable, without adding real operational overhead.

**Handling uncertainty.** When an agent hits something it can't resolve — missing info, conflicting instructions, a bug it can't fix — it stops and flags it rather than guessing or silently retrying. When you override or change a CEO recommendation, that override gets logged as an explicit lesson in the CEO's own playbook, not just recorded as an outcome — the point is that your judgment becomes part of what the system learns from, too.

**Data & metrics.** No live usage data exists yet — the app is pre\-launch. Rather than wait for Marketing to eventually need it, the CEO proactively flags what usage/analytics events are worth starting to track now, so real data exists by the time it matters.

**Safety boundaries.** Agents never handle real credentials or secrets directly — they reference configuration by name, and you manage actual secret values outside the agent system entirely. Deployment (staging or production) is always a manual action you take yourself; agents prepare and hand off, they don't push anything live. Cost is not a constraint for this pilot.

**Dashboard.** A local HTML status page, regenerated by the CEO agent at the end of each cycle, that you open in your browser — no extra service to run, always reflects current state, sits alongside the chat and written reports as a third way to check in.

## 12\. Additional Operating Details

**Direct access.** Everything routes through the CEO by default — it has the fullest context and experience across the company — but you can talk directly to Backend, Frontend, or QA any time you want a technical deep\-dive without going through the CEO first.

**Documentation.** Backend and Frontend keep a real technical README/architecture doc for the app current, separate from their internal memory logs — documentation is part of what "done" means, not an afterthought.

**Sprint carryover.** If a weekly sprint goal isn't fully met, the CEO automatically rolls the unfinished work into the next sprint rather than bringing it back to you as a decision each time.

**Kill switch.** A single, explicit pause mechanism every agent checks before doing anything — if it's set, nothing proceeds, regardless of what's mid\-flight. This is separate from (and faster than) simply not approving new tasks.

**New roles.** When it's time to add a role beyond the Milestone 1 four, the CEO drafts the proposed brief and you approve it before that agent goes live — same pattern as task approval.

**Technical authority.** The CEO stays out of day\-to\-day implementation, but weighs in on major architecture calls — choosing a database, a significant refactor, a new core dependency — even though it isn't writing code itself.

**Payments & customer data.** Beyond the general rule that agents never touch real secrets, any work that touches payments or personal customer data gets explicitly flagged in reports for your attention — it doesn't just flow through as a routine task.

**Report tone.** Plain\-English by default; full technical detail (code specifics, stack traces, reasoning) is included whenever it's actually relevant or you ask for it — not gatekept behind a separate request.

**Kickoff.** How the CEO's very first task gets framed is left to be decided when we actually start building — whichever gets Milestone 1 moving fastest at that point.

**Backlog.** Ideas or opportunities an agent notices outside the current sprint's scope get logged to a running backlog rather than acted on or discarded — the CEO can propose pulling one into a future sprint.

**Language.** English, for all reports, chat, and documentation.

**Urgent bugs.** A critical bug gets fixed immediately, jumping the sprint queue at the CEO's judgment of severity; anything less than critical waits for normal sprint planning.

**QA disputes.** If QA and a dev agent disagree about whether something actually passes, the CEO makes the final call using both sides' reasoning — it only comes to you if it reflects a recurring pattern worth knowing about.

**QA scope.** QA owns functional correctness, code quality, security, and performance review — not just "does it work."

**Approval reminders.** If a task sits waiting on your approval for 24 hours, the CEO sends a reminder on top of the initial push notification.

**Cost visibility.** Even though cost isn't a constraint for this pilot, overall API/cost spend is tracked and shown in reports and the dashboard, so there are no surprises later.

**Changing role briefs.** A role's brief isn't frozen — the CEO can propose sharpening or expanding it later, subject to your approval, same as everything else.

**Dependency licensing.** Before adding a new third\-party library or package, Backend/Frontend flag its license type so a restrictive or commercial license doesn't slip in unnoticed.

## 13\. Growth, Trust & Continuity

**Graduating Milestone 1.** Left open deliberately — we'll define what "working" looks like once we see how the first real sprint actually goes, rather than locking in a metric now that might not fit what we learn.

**Shared learning.** Agents keep a company\-wide "lessons learned" file alongside their own individual playbooks — a lesson Backend learns that's relevant to Frontend or QA gets captured once, centrally, instead of staying siloed in one department's memory.

**Autonomy growth.** Stays Low by default, but the CEO can make the case to you for more independence after building a track record of good calls — you still approve any actual change in autonomy level; it's a proposal right, not a self\-granted one.

**Extended absence.** If you go 3 days with no response to a pending approval (even after the 24\-hour nudge), the CEO auto\-pauses everything rather than letting things pile up or drift.

**Approval queue.** Pending tasks are sent to you one at a time as they come up, not batched into a digest.

**Research.** Agents — CEO included — can use web research (competitor info, technical best practices) whenever it's useful, without waiting for a dedicated Marketing/Research role to exist.

**Role retirement.** If a role is consistently not working out, the CEO can propose retiring or rebuilding it, same as it proposes new roles — subject to your approval, never automatic.

## 14\. Oversight & Roles Detail

**Codebase access.** The CEO has full read access to the actual codebase, not just summaries — supports its architecture\-level judgment. It stays out of code style and conventions, though, which remain owned by Backend/Frontend/QA — architecture calls, not line\-level style.

**Scope drift.** If an agent realizes mid\-task that the work needs to differ from what was approved, it stops and re\-requests approval for anything beyond a trivial adjustment, rather than proceeding on its own judgment and explaining afterward.

**Notification timing.** Sent whenever ready, with no awareness of time of day — no special handling for Bahrain daytime hours.

**Monthly retrospective.** Beyond weekly sprint reviews, the CEO produces a monthly step\-back comparing Loop Labs' actual trajectory against the original charter/vision — catching drift that week\-to\-week sprint reports alone would miss.

**CEO self\-assessment.** Weekly sprint reports include a genuine "here's what I'd do differently next time" self\-critique from the CEO, not just a factual account of what happened — this feeds directly back into its own playbook.

**Multi\-venture structure.** If a new venture beyond the carwash app is ever added, one CEO agent oversees all of Loop Labs' ventures rather than each venture getting its own CEO — keeps prioritization and budget tradeoffs unified at a single point.

## 15\. Governance & Founder Relationship

**Charter mutability.** The charter itself isn't locked to you alone — the CEO can propose changes to it too, same as it can propose changes to briefs, subject to your approval. Nothing in the system is completely off\-limits to CEO proposal; your approval gate is what keeps it safe, not document\-level locks.

**CEO asking questions.** When something is genuinely ambiguous, the CEO checks with you rather than guessing — mirroring how this planning conversation has worked. It shouldn't manufacture questions when the answer is actually clear from the charter, but it also shouldn't silently assume on real ambiguity.

**Returning from a pause.** When you come back after an auto\-pause from extended absence, the CEO gives you one full catch\-up summary — everything that happened or queued up while you were gone — before anything resumes.

**Data vs. your preference.** If your stated preference conflicts with what the data suggests, the CEO can make its case with the data once, but your call is final — it doesn't keep pushing after you've decided, and it doesn't silently comply without surfacing the conflict either.

## 16\. The Product Itself — Loop Labs' Carwash App

This is what the CEO and dev agents are actually building, and it's a materially bigger idea than "a carwash booking app":

**Structure.** A three\-sided marketplace — customers, carwash businesses, and each business's own employees/staff — starting in the GCC region.

**Service model.** Both fixed\-location and on\-demand mobile carwashes are supported — a business chooses whether customers travel to it, or its staff travel to the customer. This is why employee GPS tracking matters: for mobile service, it's real dispatch tracking, not just attendance.

**Customer side.** Find the closest available carwash (fixed or mobile), book an appointment. Free to use — no platform fee on top of the wash price.

**Business side.** Businesses register and get an operations toolkit: AI\-driven insights on their employees (location, timetable, attendance), plus marketing and accounting tooling. Monetized via monthly fees — a base app fee plus paid add\-ons for the extra tooling a business opts into. New businesses go through manual approval before going live on the platform (not self\-serve/instant).

**Employee side.** Staff are tracked in real time (GPS) as part of the business's operations tooling.

**Platform & tech.** Flutter for a shared mobile \+ web client, Python/FastAPI backend, Redis, Firebase.

**Milestone 1 scope.** Deliberately narrow: the core booking loop only — a customer finding and booking a nearby carwash (fixed or mobile), and the business receiving that booking. Employee management, AI insights, marketing tooling, and accounting come later, once the core loop actually works end to end.

## 16a. Product Details, Continued

**Business approval.** You personally review and approve new business applications for now — there's no dedicated ops role in Milestone 1 to delegate this to. Verification uses one simplified step regardless of country for Milestone 1 — full per\-country legal/regulatory verification (Bahrain vs. UAE each have their own systems) comes later, once there's real business volume to justify the depth.

**Language.** The app itself launches English\-only; Arabic support is a later milestone, not part of the initial build.

**Currency.** ~~Single currency at launch~~ — corrected in Section 16m: Milestone 1 launches in both Bahrain and UAE simultaneously, so both BHD and AED are supported at launch, each market showing its own local currency with no cross\-market conversion.

**Ratings.** Customers can rate/review a carwash after a booking — included in Milestone 1 despite its otherwise narrow scope, since it's core to marketplace trust.

## 16b. Booking, Pricing & Access

**Scheduling.** Two booking modes: scheduled bookings in 30\-minute slots, and immediate/on\-demand bookings matched by the customer's current location.

**Pricing.** Each business sets its own services and prices — not standardized platform\-wide.

**Employee access.** Staff get their own login/portal, separate from the business owner's — necessary for real\-time GPS tracking and attendance to actually work.

**Authentication.** Phone number \+ OTP as the primary login method, fitting GCC user expectations.

## 16c. Matching & Booking Rules

**Matching.** For immediate bookings, the customer sees a list of nearest available providers and picks one — not auto\-assigned.

**Cancellation.** Free cancellation up until 1 hour before the booked time.

**Notifications.** Booking confirmation plus status updates (en route/started/completed).

**No availability.** If nothing is available nearby for an immediate booking, the customer sees "none available" and is offered a scheduled booking instead.

## 16d. Payment & Business Operations

**Payment timing.** Customers prepay at booking time — reduces no\-shows and settles payment before the appointment happens.

**Completion.** The employee/business marks a booking complete; no separate customer confirmation step required.

**Business dashboard (Milestone 1).** Businesses can view and accept/reject bookings, define their own services and prices, and set their availability.

**Disputes.** Not decided yet — revisit once real bookings are actually happening and the shape of real disputes is clearer.

## 16e. Payments Infrastructure

**Gateway.** A GCC\-focused payment gateway (e.g. Tap Payments, PayTabs) rather than a global\-only processor — better native support for local payment methods.

**Cancellation outcome.** No refunds — a cancelled booking (before the 1\-hour cutoff) can only be rescheduled, not refunded.

**Payouts.** Businesses are paid out daily.

**Maps.** Google Maps powers nearest\-carwash search and GPS tracking, for reliability and coverage across the GCC.

## 16f. Discovery & Business Structure

**Services.** Standardized service categories (exterior wash, interior cleaning, full detail, etc.) that every business prices individually — keeps comparison consistent across the marketplace.

**Ranking.** Not purely distance\-based — providers are ranked by estimated time\-to\-arrival, combining an approximate job\-duration estimate with travel time to the customer. Rather than requiring employees to post live status updates, that duration estimate is a model that improves over time as it studies historical job data — a busier\-but\-faster\-finishing provider can still rank above an idle\-but\-farther one.

**Vehicles.** Customers can save multiple vehicles to their profile (useful since price/service often depends on vehicle size).

**Business structure.** A single business account can register and manage multiple branches/locations, each with its own separate staff — not a shared pool across branches.

**Guest access.** Customers can browse nearby carwashes without an account; authentication (phone \+ OTP) is only required at the point of booking.

**Job assignment.** The system auto\-assigns the specific employee for a job within a business, using the same availability/timing logic that powers customer\-facing ranking.

## 16g. Learning Model & Assignment Rules

**Timing model.** The job\-duration prediction learns both per employee and per business — capturing that individual staff differ in speed while also reflecting business\-level patterns (equipment, process, location).

**Job acceptance.** Auto\-assignment is final — no employee accept/reject step.

**Guest visibility.** Full details (prices, ratings, availability) are visible to guests before signup; only booking itself requires authentication.

**Future AI insights.** Once employee/business features move beyond Milestone 1, insights should cover per\-employee efficiency/speed and demand patterns (busiest hours, trends) — directly actionable for a business owner, not just raw logs.

## 16h. Failure Handling & Staffing

**Customer no\-show.** If a customer isn't present for an on\-demand mobile wash, they're charged a no\-show fee and can rebook — unless they cancelled before the 1\-hour cutoff, in which case normal cancellation rules apply.

**Shifts.** Employees work fixed shifts set by the business, not flexible sign\-in/sign\-out.

**Promo codes.** Out of scope for Milestone 1 — revisit once the core booking loop is proven.

**Fee failure.** A business with a failed monthly platform fee payment gets a grace period before suspension, rather than being hidden immediately.

## 16i. Compliance & Business Verification

**Grace period.** 7 days after a failed monthly fee payment before a business is suspended.

**Data compliance.** Agents build with Bahrain's Personal Data Protection Law (PDPL) in mind from Milestone 1 — consent, retention limits, and careful handling apply especially to the real\-time employee GPS data at the core of this product, not bolted on after the fact.

**Business onboarding.** Requires business license verification and bank account details (for payouts), on top of the manual approval step already defined.

**Rating threshold.** Not decided yet — revisit once there's real rating data to make the call meaningfully.

## 16j. Liability, Trust & Founder Visibility

**Damage liability.** Not decided yet — revisit once there's real service activity to make the call meaningfully.

**Staff vetting.** Businesses vet their own staff; the platform doesn't run background checks itself — responsibility for hiring stays with each business.

**Founder admin view.** A separate admin dashboard, distinct from the CEO's company\-operating dashboard — raw platform\-wide visibility into all bookings, businesses, and revenue, as the actual business owner.

**App distribution.** Milestone 1 targets internal/test distribution only (not a public App Store/Play Store release) — faster iteration while the core loop is still being proven.

## 16k. Admin Tooling & Abuse Prevention

**Admin format.** The founder admin dashboard is a standalone web dashboard, separate from the Flutter app's release cycle.

**Test builds.** Delivered as real installable builds — TestFlight for iOS, a direct APK/link for Android — not just web access.

**Admin capability.** The founder dashboard supports both visibility and direct action (approve/suspend a business, resolve a dispute), not read\-only — matches you being the de facto ops team during Milestone 1.

**Abuse prevention.** Basic fraud/abuse protections (rate\-limiting fake bookings, spam account detection) are built in from Milestone 1, not retrofitted later.

## 16l. Infrastructure & Legal Groundwork

**Environments.** Dev and production only for Milestone 1 — a staging environment gets added once there's real traffic worth protecting production from.

**Support routing.** Customer complaints/support requests come in through an in\-app contact form, landing in the same system the agents already read and report through — no separate inbox to check.

**Legal documents.** The CEO drafts placeholder Terms of Service and Privacy Policy for an actual lawyer to review — a starting point, not a substitute for real legal sign\-off before anything is binding.

**Backups.** Automated daily backups of platform data (bookings, business/customer records).

## 16m. Launch Market & Multi\-Country Currency

**Markets.** Milestone 1 launches in Bahrain and the UAE simultaneously — not Bahrain alone, and not the full GCC yet.

**Currency.** Because both markets launch together, both BHD and AED are supported from day one — this supersedes the earlier single\-currency assumption made before UAE was in scope. Each market shows its own local currency; there's no cross\-market price conversion since businesses and customers operate within one country at a time.

**Payments infrastructure.** The payment gateway (Section 16e) needs to support both markets from the start — Backend confirms a GCC\-focused provider (e.g. Tap Payments, PayTabs) that actually covers both Bahrain and UAE before committing to it, rather than assuming.

**Staff payout.** The platform pays the business only, in full — it doesn't pay individual employees directly. How a business compensates its own staff is that business's internal matter.

**Staff management.** Business owners add and remove their own employees freely via the dashboard — no platform approval required per employee, only at the business level.

**Solo operators.** A business with no separate employees is allowed — the owner can register and act as their own staff. This matters for early supply in a brand\-new marketplace.

## 16n. Employee Portal, Search & Reliability

**Earnings visibility.** The employee portal shows jobs completed and hours worked, even though the platform doesn't pay employees directly — useful to the employee, and it's data a business's own payroll process would want anyway.

**Search filters.** Customers can filter by service type and price range on top of the ETA\-based ranking, not just see one ranked list.

**SMS fallback.** Critical messages — OTP and booking confirmations — also go out via SMS, not push notifications alone, since push can fail silently.

## 16o. Memberships — Superseded

The original description here (a single platform\-wide subscription of fixed washes, redeemable at any business) is **superseded by Section 40**, which defines two distinct membership products with different owners, economics, and rules. Read Section 40 instead.

The one element that carries forward unchanged: memberships remain out of the first build, coming after the core product works.

## 16p. Membership Economics & Live Tracking

**Membership payout.** When a member redeems a wash, the platform pays the business the standard price for that service — same incentive as a regular paying customer.

**Wash expiry.** Unused membership washes expire at the end of each period rather than rolling over.

**Live tracking.** For on\-demand mobile bookings, customers see a live map tracking the employee traveling to them — a natural extension of the GPS data already being collected, and a real trust/UX win.

**Business revenue visibility.** The free business dashboard includes basic revenue numbers — the paid accounting add\-on goes deeper (detailed reports, categorization, exports), it doesn't gate the basic total.

## 16q. Milestones Are Not Decided

**This is important enough to state plainly: no milestones have been decided.** The phrase "Milestone 1" appears throughout this document as shorthand for "the first thing we build," and every scope statement attached to it — core booking loop first, defer memberships, defer AI insights, and so on — is a **working assumption captured during planning, not an agreed plan**.

The actual milestone breakdown will be decided in conversation with the CEO agent, based on its recommendation after it has read this entire charter. That is one of its first real jobs. Until that conversation happens and you approve a breakdown, nothing in this document should be treated as a committed sequence, a fixed cut line, or a promise about what ships when.

Read every "Milestone 1 scope" reference in this document as *context for the CEO's planning*, not as instructions constraining it.

**Remaining product details locked in this round:**

- Memberships will offer multiple tiers from the start (not just one fixed plan), once memberships are built.
- The business revenue view defaults to rolling totals — today, this week, this month.
- Displayed prices are tax\-inclusive (VAT included in what the customer sees, no surprise at checkout).

## 16r. Kickoff Details

**Milestone planning.** The CEO proposes the actual milestone breakdown once it has reviewed this full charter, rather than us defining it further in advance — it'll have the complete picture (product, constraints, priorities) to work from.

**Timeline.** No hard deadline — quality over speed for Milestone 1. Revisit pacing once real progress is visible.

**App branding.** No name/logo/visual identity for the app itself yet (distinct from the "Loop Labs" company name) — the CEO/agents can propose this as part of early work.

**Competitive awareness.** The CEO keeps light, ongoing awareness of comparable GCC carwash/on\-demand marketplace apps to inform positioning — not a dedicated research project, just standing context.

## 16s. Time, Discovery & Market Boundaries

**Time zones.** Bahrain (UTC\+3) and UAE (UTC\+4) are different time zones — the backend stores all times in UTC and displays local time per market. Called out explicitly since it's an easy bug to introduce silently across two markets.

**Scheduled search.** Uses the same ranked list as immediate bookings, filtered to whoever has an opening at the customer's chosen date/time — not a separate calendar\-style interface.

**Business availability.** Set via a recurring weekly schedule (e.g. "open Sun–Thu 9am–9pm") with manual overrides for exceptions, rather than fully manual day\-by\-day entry.

**Market boundaries.** Booking is restricted to businesses within the customer's own market — a Bahrain customer can't book a UAE business and vice versa, matching physical service reality.

## 16t. Trust Signals & Booking Details

**Ratings.** Star rating plus an optional written review — a stronger trust signal than a number alone for a brand\-new marketplace.

**Waitlist.** None — if a business is fully booked for a scheduled slot, the customer picks a different business or time from the ranked list rather than queuing.

**Business profile.** Businesses get real profiles — photos and a description, not just name and location — as part of registration. (Per the note in Section 16q: exactly which build phase this lands in isn't fixed yet, but the feature itself is confirmed.)

**Booking notes.** Customers can add an optional notes field to a booking (e.g. parking/access details) — particularly useful for mobile on\-demand service where staff need to actually locate the customer.

## 16u. Trust, Notifications & Recovery

**Review replies.** One\-directional — customers review, businesses can't publicly respond.

**Employee visibility — corrected.** For mobile on\-demand bookings, the customer sees the assigned employee's name and photo before arrival, but the **rating shown is the business's rating, not an individual employee rating** — ratings are attached to the business, not to each employee. This is also why new employees need no special "unrated" handling (Section 16bb): there's no per\-employee rating to be missing in the first place.

**Business notifications.** Businesses get the same immediate push\+SMS urgency for new bookings that customers get for status updates — a missed booking directly costs them money, so it gets the same reliability bar.

**Account recovery.** Handled manually, routed to you for now — consistent with how disputes are handled during Milestone 1, since there's no dedicated support role yet.

## 16v. Documentation, Data Retention & Pricing Dynamics

**Photo documentation.** Before/after photos are required, uploaded by the employee — they double as both damage\-dispute evidence and the actual signal that marks a job as started and completed (the photo upload *is* the status trigger, not a separate step).

**Business offboarding.** A departed business's historical data is retained under a PDPL\-compliant retention policy (for financial/legal purposes) — it simply stops appearing in customer search, data isn't deleted outright.

**Weather disruptions.** Handled manually between business and customer, outside the app, for Milestone 1 — no weather\-integration logic built in yet.

**Pricing dynamics — corrected.** No surge/dynamic pricing on regular bookings — businesses set flat prices for their own services, full stop. Dynamic pricing instead applies to **memberships**, which Loop Labs itself prices and controls (since memberships are the platform's own product, not a per\-business one) — the mechanics of how membership pricing flexes are still open, to be defined when memberships are actually built (Section 16o/16p).

## 16w. Membership Pricing Basis & Job\-Status Verification

**Membership pricing basis.** Loop Labs prices memberships based on the average car wash prices across all businesses on the platform — the membership's value is calibrated against real marketplace pricing, adjusting over time as those averages shift, rather than being set arbitrarily or per\-market.

**Status verification.** A GPS location match is required before an employee can upload a "started" or "completed" photo — ties the photo\-based status system to the GPS tracking already in place, preventing a status update from somewhere the employee isn't actually at.

**Photo notifications.** Customers are notified with the actual before\-photo itself when a job starts, not just a status word — more tangible and trust\-building.

**Photo retention.** Before/after photos remain permanently visible in the customer's booking history, not just immediately after completion — supports disputes raised later, not only in the moment.

## 16x. Cancellations, Coordination & Capacity

**Business\-side cancellation.** If a business cancels a confirmed booking, the customer gets a full refund with no penalty — different treatment than the customer's own no\-refund cancellation policy, since it's the business's fault, not the customer's.

**In\-app messaging.** Basic chat between the customer and the assigned employee/business exists for real\-time coordination (e.g. "running 5 min late," access details) — beyond just the booking notes field and status updates.

**Capacity limits.** The system automatically prevents a business from being booked beyond its actual employee capacity — no accepting more simultaneous jobs than it has staff to deliver.

**Employee enforcement.** The platform stays out of the employer\-employee relationship — even if GPS/photo data reveals a pattern of an employee not following process, managing that employee is the business's responsibility, not the platform's.

## 16y. Chat, Dispatch Cancellation & Vehicle Data

**Chat lifecycle.** In\-app chat is only open during the active booking window — it closes once the job is marked complete.

**Cancellation after dispatch.** Once an employee is dispatched/traveling for an on\-demand job, cancelling triggers a fee regardless of the standard 1\-hour\-free rule — the employee has already committed travel time.

**Employee\-visible info.** Full customer contact info, including the actual phone number, is shared with the assigned employee — not masked.

**License plate.** Required at booking — practical for mobile staff identifying the right vehicle, and feeds the saved vehicle profiles.

## 16z. Contact Symmetry & Vehicle Identification

**Contact visibility.** Symmetric — the customer also sees the employee's real phone number, same as the employee sees the customer's.

**Vehicle details.** Make, model, and color are required alongside the license plate — plates are hard to spot at a distance, visual details make identification practical.

**Wrong\-vehicle handling.** No rigid system rule — an employee flags a mismatch via chat/photos, and the business (or CEO, if escalated) resolves it case by case using that evidence.

**Scheduled booking lead time.** No minimum notice — a customer can schedule for any future time, even just minutes out, rather than being forced into the immediate/on\-demand flow.

## 16aa. Tax, Reliability & Receipts

**VAT handling.** Not decided yet — this genuinely needs real accountant/legal input rather than a planning\-conversation guess. Flagged as a follow\-up to resolve with an actual advisor before real transactions go live in either market.

**Offline handling.** The employee app queues status/photo updates locally and syncs automatically once connectivity returns — a job doesn't get stuck just because of a dead zone.

**Ranking.** Purely current ETA\-based for Milestone 1 — no reliability\-history scoring (past cancellations, lateness) yet. Worth revisiting once there's enough real usage data for that signal to be meaningful.

**Receipts.** Customers can view and download a receipt for every booking.

## 16bb. Onboarding, Payout Verification & Founder Access

**Employee onboarding.** Minimal — just a phone number to create the account. No ID/photo verification requirement at signup (revisit if trust/safety issues surface).

**Bank verification.** Micro\-deposit verification before a business's daily payouts begin — a small test deposit confirms account ownership.

**Provider ranking display.** No special tie\-break logic needed — customers already see a ranked list of options with the fastest ETA shown first, and they choose from it themselves (per Section 16f). A "tie" just means two options appear adjacently in that same list.

**Founder override.** A founder\-level override role exists beyond the admin dashboard's normal approve/suspend/dispute actions — true root\-level access for genuine emergencies.

## 16cc. Trust Model Clarified & Override Security

**Employee trust signal.** No upfront ID verification for employees — trust comes from the business's own vetting plus the platform's business\-level rating history (see correction in 16u: ratings live at the business level, not per employee).

**Founder override security.** Requires extra authentication beyond normal admin login — a separate confirmation step, matching the seriousness of true root\-level access.

**Override logging.** Every founder\-override action is automatically logged and visible later — bypassing the normal approval flow doesn't mean bypassing the audit trail.

## 16dd. Ratings Scope & Review Integrity

**Multi\-branch ratings.** One combined rating across all of a business's branches, not per\-branch — reinforces that the customer\-facing rating lives at the business\-account level. Branches still operate independently for staffing, scheduling, and capacity (Sections 16f/16x) — only the reputation score is combined, not day\-to\-day operations.

**Employee\-level rating — internal only.** Employees do have their own rating/performance data, but it's for the business's internal use only (feeding the per\-employee AI insights in Section 16g) — never shown to customers, who only ever see the business\-level rating.

**Review editing.** Customers can edit or delete a review within a time window after posting; the business is notified when a review they've seen changes.

**Review verification.** Only customers with a verified, completed booking at that business can leave a review — prevents fake or competitor reviews.

**Review disputes.** A business can dispute a review it believes is unfair or false — routed to you for manual review, consistent with how other disputes are handled during Milestone 1.

**Founder override account.** Elevated permissions layered onto your existing admin login, not a structurally separate super\-admin account — but the extra authentication step (Section 16cc) is re\-confirmed on every override action, not just once per session.

## 16ee. Booking Composition & Scheduling Flexibility

**Multi\-service, multi\-vehicle bookings.** A single booking can include multiple services and multiple vehicles — duration, price, and capacity are calculated across the whole basket rather than assuming one service on one car.

**Baseline service duration.** Each business declares how long each of its services takes when it sets prices. That declared duration is the ETA model's starting estimate (Section 16f/16g); the model then refines it per employee and per business from real job data over time.

**Recurring bookings.** Customers can set up repeating scheduled bookings (e.g. every Friday at 9am) with the same business — a separate mechanic from memberships, which handle bundled recurring *value* rather than a repeating time slot.

**Saved addresses.** Customers can save multiple service addresses (home, office) the same way they save multiple vehicles, and pick one at booking time or use their live GPS position instead.

## 17\. Agent Infrastructure & Communication

This section supersedes the lighter "local HTML file" dashboard description in Section 11 — the cockpit is now a real application, not a generated status page.

**The Loop Labs cockpit.** The dashboard is a full interactive web app, not a regenerated HTML file. It is where you actually run the company: live status across all agents, pending approvals with approve/reject actions, sprint and report views, cost visibility, and — critically — a chat panel wired directly to the CEO agent. This is the primary surface for founder↔CEO communication, replacing the terminal as the default.

**Founder ↔ CEO session model.** Each conversation with the CEO is a **fresh session** that rebuilds its context by reading the charter, its own memory and decision log, the current sprint state, and recent agent reports. Nothing depends on a long\-lived conversation staying alive. This scales indefinitely, survives restarts, and — importantly — forces the memory files to stay genuinely useful, because they are the *only* continuity the CEO has. If the memory files degrade, the CEO visibly degrades, which is a healthy feedback signal rather than a hidden failure.

**CEO ↔ employee delegation.** When the CEO assigns work, the employee agent receives a **scoped task brief plus a short "why this matters"** — its own role brief, its own memory/playbook, the specific task, and one or two sentences of strategic context. It does not receive the CEO's full reasoning or the entire charter. This keeps each agent focused and each run cheap, without leaving agents guessing at intent.

**CEO oversight of employees.** The CEO reads employee **reports by default**, and pulls the full raw working output only when something looks wrong or a report doesn't add up. QA remains the real quality gate; the CEO's job is direction and judgment, not re\-reviewing every transcript.

**Implication to plan for.** Because the cockpit is a real web app that invokes agents, it needs a backend of its own — a service that can trigger agent runs, stream their output back to the browser, and record approvals. This is genuinely part of the build, not a side artifact, and should appear explicitly in whatever milestone breakdown the CEO proposes.

## 17a. Execution Model & Isolation

**Hosting.** The cockpit is hosted and reachable from anywhere, not localhost\-only — this is what makes the push\-notification and daily\-check\-in rhythm actually work, since you can approve a pending task from your phone without being at your desk. It needs real authentication, and it should be treated as a production surface with access to your repo and agent runs, not a toy internal tool.

**Execution.** Approving a task queues it; agents run in the background and the cockpit updates as results land. You approve and walk away. This is what makes Backend and Frontend genuinely parallel rather than serialized behind your attention.

**Interruption.** You can stop *and* redirect an agent mid\-run from the cockpit. If an agent is heading the wrong direction, you halt it and give corrective direction rather than waiting for it to finish badly and burning the cycle. This is distinct from the kill switch (Section 12), which stops everything company\-wide.

**Parallel isolation.** Each agent works in its own isolated git worktree, so simultaneous Backend and Frontend runs can never clobber each other's files. Work merges back only after QA passes. This removes an entire category of failure structurally, rather than depending on the CEO scoping tasks perfectly enough to avoid overlap.

**Note on the git workflow.** This supersedes the earlier "direct commits to main" default from Section 11: agents commit within their own worktree, and merging to main happens after QA sign\-off and your final approval, consistent with the definition of done.

## 17b. Cadence, Failure Handling & Transparency

**CEO scheduling.** The CEO runs on a scheduled daily cycle *and* on demand. Each morning it wakes, reviews the current state (sprint progress, agent reports, metrics, backlog), and prepares its proposals — so when you open the cockpit, work is already queued and waiting for your approval rather than starting cold. You can also engage it any time outside that cycle.

**Agent failure.** A failed or stuck agent run retries **once**, then escalates to the CEO as a real blocker. Transient failures self\-heal; persistent ones surface rather than silently burning cycles. This is the one deliberate exception to the general stop\-and\-flag\-immediately rule (Section 11), because a single retry costs little and catches most flakiness.

**Report visibility.** You read the CEO's synthesis by default, with **drill\-down** into any individual agent's full report when you want the underlying detail. This matters for a low\-autonomy setup: you can always check the CEO's summary against its source rather than taking synthesis on faith.

**Live output.** The cockpit streams agent output live, collapsed by default. You can expand any running agent and watch it work — which is what makes mid\-run redirection (Section 17a) actually usable, since catching a wrong direction requires seeing it happen.

## 17c. Memory, Escalation & Proposal Style

**Chat persistence.** The CEO writes decisions to its memory/decision log **as they happen** during conversation. This is load\-bearing: because every CEO session is fresh (Section 17), anything decided in chat that isn't written down is genuinely lost. Recording in the moment — not at end of session, which may never come — is what makes the fresh\-session model safe.

**Needs\-your\-input queue.** Questions and pending approvals appear as distinct actionable items in the cockpit, separate from the chat stream. Nothing important gets buried in conversation, and you can see everything waiting on you at a glance.

**Proposal style.** The CEO presents **two or three options with a clear recommendation** — you see the alternatives it considered and which it favours, rather than either a bare directive or an unfiltered menu.

**Escalation path.** Backend, Frontend, and QA always escalate through the CEO; they never reach you directly. One filter, one queue — four agents pinging you independently would defeat the structure. (You can still initiate a direct conversation with any agent yourself, per Section 12.)

## 18\. Revised Org — Full Team From Day One

This section revises the phased four\-agent rollout in Sections 9 and 11. The priorities are now explicit: **speed, security, and performance**, with conflict\-avoidance treated as a structural requirement rather than a planning discipline.

**The day\-one team is eight agents:**

| Role | Owns | Why it exists from day one |
| --- | --- | --- |
| CEO | Direction, priorities, your approval queue | Single point of coordination and the only agent you routinely talk to |
| Architect / Tech Lead | System design, API contracts, file\-ownership map | The primary anti\-conflict role — defines the seams so other agents never collide |
| Backend Developer | Server, database, API implementation | Core build |
| Frontend Developer | Flutter client (mobile \+ web) | Core build |
| QA | Functional correctness, code quality, regressions | Quality gate before merge |
| Security Engineer | Auth, payments, PDPL/personal data, secrets, location surface | Security is a stated top priority — too important to be a QA side\-duty |
| DevOps / Infrastructure | Environments, CI, deploys, monitoring, cockpit backend | Owns release speed and operational reliability |
| Performance Engineer | Latency, load, query and app performance | The real\-time GPS/ETA matching engine is the hardest performance surface in this product |

**Conflict prevention — strict domain ownership.** Every file and module has exactly one owning agent. No agent edits outside its domain; it proposes the change to the owner instead. Combined with per\-agent worktree isolation (Section 17a), collisions become structurally impossible rather than merely unlikely. The Architect owns and maintains the ownership map itself, and resolves any boundary dispute.

**Security as a hard gate.** The Security Engineer reviews every change touching authentication, payments, personal data, or location before it can merge. This is a blocking gate, not advisory — a change can pass QA and still be held by Security.

**Concurrency.** Unlimited. Because ownership and worktrees remove the collision risk, agents run fully in parallel for maximum speed, and cost is not a constraint for this build.

**Honest trade\-off worth naming.** Eight agents on day one is materially harder to debug than four — when the loop misbehaves, there are more places for it to go wrong, and your approval queue fills faster. The mitigation is that the extra roles are precisely the ones that *reduce* chaos (Architect defines boundaries, Security and Performance are gates rather than free\-running builders), and that the CEO still filters everything before it reaches you. Worth watching in the first sprint: if the approval queue becomes overwhelming, throttling concurrency is the first lever to pull, not removing roles.

## 18a. The Delivery Pipeline

Every change moves through the same pipeline, designed so that speed comes from parallelism and automation rather than from skipping checks.

**Stage 1 — Automated CI (blocking).** DevOps sets up CI that runs first on every change: tests, linting, dependency scanning, and secret scanning. It blocks on failure. Machine checks catch cheap failures in seconds so the agent gates spend their time on real judgment — this is the single biggest speed win in the pipeline.

**Stage 2 — Three gates in parallel.** Once CI passes, QA, Security, and Performance review the change **simultaneously**, not in sequence. Sequential gates would triple the wait on every task. A change merges only when all three pass; any one of them can hold it.

**Automatic triggering.** Gates fire automatically on every completed change — the CEO does not assign them. This keeps the pipeline moving without waiting on a planning cycle and means nothing slips through unreviewed. The CEO's role is direction and priorities, not merge traffic control.

**Performance targets.** The Architect proposes concrete, measurable targets in the first sprint — search/matching response time, app cold start, booking confirmation latency, and similar — for your approval. Without real numbers, "performance" is unenforceable; with them, the Performance Engineer has something objective to hold the build to.

**Full path of a change:** dev agent builds in an isolated worktree → CI runs → QA \+ Security \+ Performance review in parallel → CEO reviews outcome → your final approval → merge to main. The definition of done from Section 11 still holds: merged, passed, and approved by you.

## 18b. Architect Authority & Operational Separation

**Design review before building.** The Architect signs off on the approach before a dev agent starts implementing. This adds a step, but catching a wrong design upfront is far cheaper than having three gate agents reject finished work — a net speed gain, not a tax. It also means the full path of a change is: Architect design sign\-off → build in isolated worktree → CI → three parallel gates → CEO → you.

**Technical arbitration.** When QA, Security, and Performance make conflicting demands on the same change, the **Architect** arbitrates. This is a design question, not a priority question — the Architect owns the system's shape and is best placed to resolve trade\-offs between them. It escalates to the CEO only when the conflict becomes a scope or timeline matter rather than a technical one. (This is a deliberate carve\-out from the CEO\-arbitrates\-everything rule in Section 12: the CEO resolves *disputes about work*; the Architect resolves *disputes about design*.)

**Repository separation.** The Loop Labs cockpit lives in its own repository, separate from the carwash app. The cockpit is the control plane for running the company, not part of the product — keeping them apart means agents cannot break the very system you'd need working in order to fix a broken build. DevOps owns the cockpit repo.

**Agent observability.** Monitoring and alerting on the agents themselves, distinct from application monitoring: run duration, failure and retry rates, gate rejection rates, and cost per agent. With eight agents running in parallel, a silently degrading agent is easy to miss — this surfaces it before it wastes a sprint rather than after.

## 18c. Cockpit Security, Secrets & Recovery

The cockpit is hosted, holds repository access, and can trigger agent runs — it is the highest\-value target in the entire system. It gets treated accordingly.

**Cockpit authentication.** Single\-user auth with MFA and IP restrictions. Only you can ever log in. There is no multi\-user permission system to misconfigure, which keeps the attack surface as small as it can be while still being reachable from your phone.

**Secrets.** A dedicated secrets manager with runtime injection — nothing in any repository, nothing in any agent's context, credentials delivered only to the running process that needs them. This preserves the standing rule that agents never handle real secrets (Section 12) while still letting the cockpit invoke agents and DevOps deploy.

**Rollback.** One\-click rollback to the last known\-good deploy, triggered by you directly from the cockpit — no waiting for an agent to diagnose first. The CEO runs its root\-cause review (Section 12) afterward, once service is restored. Recovery speed matters most exactly when things are worst, so this path stays manual and immediate.

**Model tiers — revised.** This supersedes the single\-model decision in Section 11, which was made when the team was four agents. The CEO, Architect, and Security Engineer run on the strongest available model, since they make the judgment calls with the widest blast radius: direction, system design, and what is safe to ship. Backend, Frontend, QA, DevOps, and Performance run on a faster model, keeping the build\-and\-review loop quick. Cost remains a non\-constraint; this split is about matching capability to consequence, not saving money.

## 18d. Memory Location & Access Model

This revises the `/company` folder layout in Section 5, which assumed a single repository.

**Company memory lives in the cockpit repo.** Role briefs, per\-agent playbooks and memory, the CEO decision log, the shared lessons\-learned file, the ownership map, sprint state, and reports all live with the control plane — not in the app repo. Company memory is control\-plane data, not product code, and separating it means agents building the app cannot accidentally corrupt the institutional knowledge that makes the company work. The app repo stays purely the product.

**Access model — read broad, write narrow.** Agents can read anything, across both repos. They can write only within the domain they own. This is the heart of how conflict prevention actually functions: ownership restricts *modification*, never *understanding*. An agent that can't read the API it's calling makes worse decisions, not safer ones.

**Cross\-domain change requests.** When an agent needs a change in a file it doesn't own, it files a specific change request queued to the owning agent, which implements it in its own worktree. Single\-writer ownership stays intact and the CEO doesn't become a bottleneck on routine cross\-domain work. The Architect gets involved only when the request suggests the *boundary itself* is drawn wrong.

**Memory protection.** Git history plus automated off\-site backup. Version control gives every past state and the ability to roll back a bad memory edit; off\-site backup covers loss of the repo itself. This data is the only continuity the agents have — unlike code, it cannot be regenerated from anything if lost.

## 18e. Testing, Learning & Run Limits

**Test ownership.** Dev agents write tests alongside the code that needs them; QA verifies those tests and adds the edge cases the developer didn't think of. This is faster than QA writing everything from scratch, and it keeps QA's judgment focused where it adds most value. It also revises the earlier assumption (Section 12) that QA's existence removed the need for devs to write tests — devs write them, QA is not a substitute for that.

**Cross\-agent learning.** Every agent reads the company\-wide shared lessons file (Section 13) in addition to its own playbook. A lesson learned once benefits the whole team, without loading every agent with every other agent's full report history. Individual reports remain available on demand rather than read by default.

**Run limits.** Agent runs get a generous timeout with an alert at the halfway mark — long enough that legitimate deep work is never cut off, early enough that you can look in and redirect (Section 17a) before anything is killed. Combined with agent observability (Section 18b), a stuck agent surfaces as a signal rather than a silent stall.

**The ownership map comes first.** Defining the file and domain ownership map is the **Architect's first task, before any building begins**. This is non\-negotiable sequencing: the map is what makes parallel agents safe, and the first parallel sprint is precisely where undefined boundaries would cause conflicts. Build nothing until the seams exist.

## 19\. Final Org — Thirteen Agents

This supersedes the eight\-agent team in Section 18. The organisation now has a management layer, and the roles that were previously implicit (product definition, design, the prediction model, production reliability) have explicit owners.

**Leadership**

| Role | Owns |
| --- | --- |
| CEO | Direction, priorities, budget, your approval queue, the founder relationship |
| CTO | All technical coordination: gate outcomes, cross\-team sequencing, technical escalation |
| Product Manager | Specs and acceptance criteria — turning your vision into buildable, testable definitions |
| Architect / Tech Lead | System design, API contracts, the ownership map, technical arbitration |

**Build**

| Role | Owns |
| --- | --- |
| UX / UI Designer | Design system and user flows across all three user types, before implementation |
| Backend Developer | Server, database, API implementation |
| Frontend Developer | Flutter client (mobile \+ web) |
| Data / ML Engineer | Job\-duration prediction model, ETA engine, analytics pipeline behind AI insights |

**Gates & Operations**

| Role | Owns |
| --- | --- |
| QA | Functional correctness, code quality, regression coverage |
| Security Engineer | Auth, payments, PDPL/personal data, secrets, location surface — blocking gate |
| Performance Engineer | Latency, load, query and client performance against agreed targets |
| DevOps / Infrastructure | Environments, CI, deploys, cockpit backend |
| SRE / Reliability | Uptime, incident response, alerting, error budgets in production |

**Why a CTO exists.** With this many agents, one role cannot hold both strategic judgment and the technical detail of eleven engineers without one of them degrading. The CEO now handles direction, product, and you; the CTO handles technical coordination, gate outcomes, and escalation. The Architect still arbitrates *design* disputes (Section 18b); the CTO sequences and coordinates *work*.

**Structure by technical layer.** Agents are organised by layer (Backend, Frontend, Data) rather than by feature squad. This matches the single\-writer ownership map directly and keeps file boundaries clean. Revisit only if the team ever grows past the point where layer ownership becomes a bottleneck.

**Approval queue — revised.** The one\-at\-a\-time approval model from Section 13 does not survive a team this size. The CEO now batches pending approvals into **one prioritised daily review session**, so you make decisions in a single focused sitting rather than absorbing a constant stream. Genuinely urgent items can still interrupt.

**The honest trade\-off.** Thirteen agents is a real organisation, and the failure mode is no longer "not enough coverage" — it is coordination overhead, and you becoming the bottleneck. The mitigations are already in place: the CTO layer absorbs technical coordination, batched approvals protect your attention, ownership plus worktrees prevent collisions, and gates run in parallel. If the first sprint feels heavy, the levers to pull in order are: throttle concurrency, widen what the CEO can approve without you, and only then reduce roles.

## 19a. HR — Agent Lifecycle Owner

**The fourteenth role.** HR here manages the *agents*, not people. It is the only role whose subject is the company itself rather than the product, and it owns work that would otherwise pile onto an already\-loaded CEO.

**HR owns:**

- Drafting role briefs and memory scaffolding when a new agent is added
- Monitoring agent performance using the observability data from Section 18b — failure rates, retry counts, gate rejection rates, run durations
- Pruning and consolidating playbooks and memory files, so institutional knowledge stays sharp rather than bloating into unusable narrative (the consolidation duty from Section 8, moved here from the CEO)
- Proposing changes to an underperforming agent's brief, for your approval
- Proposing retirement or rebuild of a role that consistently isn't working (Section 13)

**Authority.** HR can propose brief changes directly rather than routing everything through the CEO. This matters: an agent that keeps failing should have its instructions sharpened, and a role that notices problems but cannot act on them is a wasted role. Your approval is still required for any actual change — HR proposes, you decide.

**Why this is the org's own learning loop.** Section 8 describes how each agent learns from outcomes. HR is the layer above that: it watches whether the *agents themselves* are working, and improves the roles rather than the work. Without it, a quietly degrading agent stays degraded indefinitely, because every other role is looking at the product rather than at the team.

## 19b. Rollout — Full Architecture, Activated in Waves

**Business\-side roles stay out for now.** Marketing, Finance, and Customer Support are deliberately not part of the initial organisation. Pre\-launch, they would be generating plausible\-sounding output with no real data behind it — the exact failure mode warned about in Section 10. Disputes, complaints, and account recovery continue routing to you personally (Sections 16d, 16u); the open VAT question (Section 16aa) still needs a real advisor, not a Finance agent. These roles get added when there is a real product and real data for them to work from.

**Every brief gets written now.** All fourteen role briefs, the ownership map, and the memory scaffolding are defined upfront, so the architecture is correct and coherent from the start rather than accreting.

**Activation happens in waves,** so the first sprint doesn't bet everything on all fourteen agents behaving:

1. **Wave 1 — Foundation.** CEO, CTO, Architect, Product Manager. Nothing is built yet: this wave produces the ownership map (Section 18e), the performance targets, the specs, and the proposed milestone breakdown for your approval.
2. **Wave 2 — Core build.** UX/UI Designer, Backend, Frontend, plus QA and the CI pipeline from DevOps. The first real code, with a real quality gate.
3. **Wave 3 — Full gates and operations.** Security, Performance, SRE, Data/ML Engineer, HR. The complete organisation running.

Wave boundaries are advisory, not rigid — the CEO can propose pulling a role forward if a real need appears earlier, subject to your approval like anything else.

**What this buys you.** The full architecture exists on paper from day one, so nothing has to be restructured later, but the blast radius during the riskiest period stays small. If the loop misbehaves in Wave 1, four agents are far easier to debug than fourteen.

## 19c. Working Style & Cold\-Start Realities

**Work intake — lightweight.** The CEO assigns outcomes, and the agents sequence the work among themselves rather than passing it down a fixed PM → UX → Architect → build chain. This keeps process light and lets specialists coordinate directly.

*Reconciling this with the Architect gate:* the Architect's design sign\-off (Section 18b) remains a **gate, not a stage** — agents self\-organise how they get to a design, but nothing gets built until the Architect approves the approach. Self\-sequencing governs *how work flows between agents*; it does not remove the checkpoint. If this proves too loose in the first sprint — agents duplicating effort or building against mismatched assumptions — tightening intake into an explicit chain is the first correction to make.

**UX/UI output.** The Designer produces a design system and component specs **as code**\: tokens, spacing, typography, and component behaviour expressed as Flutter theme and widget specifications. Frontend consumes these literally rather than interpreting a description. This sidesteps the fact that an agent cannot draw, and it produces something more directly useful than wireframe prose would be.

**Daily cycle ownership.** The CTO runs the daily engineering cycle across the technical team and reports upward; the CEO synthesises that into your single daily approval session (Section 19). Technical detail stays inside the engineering org rather than reaching your queue — you see decisions and blockers, not stand\-up notes.

**ML cold start.** The prediction model has no data to learn from pre\-launch, and that's fine. Data/ML builds the pipeline and the platform ships using the durations businesses declare for their own services (Section 16ee). Real completion data is collected from the very first booking, and the learned model takes over once there's enough volume to be trustworthy. No synthetic training data — a model that learned invented patterns would be worse than the honest declared estimate it replaced.

## 20\. Technical Architecture Decisions

**Data layer — Postgres primary, Firebase scoped.** The relational database is the system of record: bookings, businesses, employees, vehicles, payments, payouts, memberships, reviews. These are deeply relational and have money attached, which is exactly where a document store becomes painful and reconciliation gets dangerous. Firebase is deliberately scoped to what it is genuinely best at: **authentication, push notifications, and file storage** (job photos). Redis handles caching, session state, and the availability/matching hot path.

**Real\-time location — isolated by design.** Live GPS tracking flows through **Firebase Realtime Database**, kept entirely out of the primary database. Location updates are high\-frequency and ephemeral; writing them into Postgres would put the heaviest write load in the system directly on top of the data that matters most. Only meaningful location events (job started at location, completed at location) are persisted relationally. This is the single most important performance decision in the product.

**API — REST, versioned.** FastAPI generates schema and documentation automatically, and versioning is non\-negotiable because mobile clients cannot be force\-updated: an old app version must keep working against a newer server. The Architect owns the contract, and it becomes a hard boundary between Backend and Frontend ownership.

**Stack summary:** Flutter (mobile \+ web) · Python/FastAPI · PostgreSQL · Redis · Firebase (auth, push, storage, live location) · Google Maps · GCC payment gateway covering Bahrain and UAE.

## 20a. Fifteenth Role — Integrations Engineer

**Added.** Owns every third\-party surface: the payment gateway, Google Maps, SMS/OTP delivery, and Firebase. Four external dependencies, each an independent failure point, each requiring sandbox credentials, retry and backoff logic, webhook handling, and graceful degradation when a provider is down. Unowned, these land on Backend by default and become the quiet source of most production incidents.

**Deliberately not added, with reasons:**

- **Compliance / Legal.** The regulatory surface is real — PDPL across two countries, the open VAT question (Section 16aa), ToS and Privacy Policy, payment regulation. But an agent cannot give legal advice, and this needs an actual lawyer and accountant. It stays a CEO responsibility executed with human advisors, per Section 16l. Revisit only if the volume of compliance work genuinely justifies coordination.
- **Data Analyst.** No data exists pre\-launch. Same reasoning that defers Marketing and Finance (Section 19b) — an analyst with nothing to analyse produces plausible\-sounding output with nothing behind it. Data/ML owns the pipeline until there's volume worth analysing.
- **Technical Writer.** Documentation is already part of the definition of done (Section 12) and is best written by whoever wrote the code. A separate role adds a handoff without improving the result.

**Final team: fifteen agents.** CEO, CTO, Product Manager, Architect, HR · UX/UI, Backend, Frontend, Data/ML, Integrations · QA, Security, Performance, DevOps, SRE.

## 20b. Infrastructure Decisions

**Hosting region — GCC, single region.** Infrastructure runs in a GCC region (UAE or Bahrain — both AWS and Azure have UAE regions). Two reasons, and both matter: personal and location data stays in\-region for PDPL and UAE data\-protection purposes, and servers sit physically close to users, which is a direct latency win for live tracking and the matching query. Single region for now; multi\-region is a scale problem, not a launch problem. **Confirm the specific residency requirements with your legal advisor before committing** — this decision is expensive to reverse once real customer data exists.

**Deployment — containers on managed orchestration.** Predictable performance, no cold starts, and full control over the real\-time and matching workloads. Serverless was rejected deliberately: cold starts would land directly on the on\-demand booking path, which is the experience most sensitive to delay, and long\-lived connection limits fight against live tracking.

**Repository structure — monorepo for the product.** The FastAPI backend and Flutter client live in one repository, so an API contract change and its client update land as a single atomic change. Separation between agents comes from the ownership map and worktree isolation (Sections 18d, 17a), not from repository walls. The cockpit remains a separate repository (Section 18b) — that separation is about blast radius, not organisation.

**Geospatial search — deferred to Wave 1 benchmarking.** "Find nearest available provider, ranked by ETA" is the core query of the entire product, so it gets decided on evidence rather than preference. The Architect and Performance Engineer benchmark the candidates (PostGIS geospatial indexing versus a Redis in\-memory geo index, or a hybrid) against the agreed performance targets and propose a recommendation for your approval. This is explicitly a Wave 1 deliverable, alongside the ownership map and performance targets.

## 20c. Operational Safeguards

**Schema migrations — the one gap worktrees can't close.** Two agents working in isolated worktrees can each create a migration that looks fine alone and conflicts on merge; isolation prevents file collisions but not logical ones. So: the **Backend agent is the sole writer of migrations** — no other agent may create one — **and the Architect approves every migration before it merges**. Single\-writer ownership applied to the schema, plus a design checkpoint on anything touching the data model. This is the highest\-risk conflict surface in the whole system and gets both controls, not one.

**Photo pipeline.** Images are compressed on the employee's device before upload, stored in Firebase Storage, and served to customers through a CDN. Compression before upload matters because employees are on mobile data in the field; CDN delivery matters because photos are viewed repeatedly and retained permanently (Section 16w). Cheapest and fastest at every stage of the path.

**Feature flags — from day one.** Work can merge before it is finished or before it is approved to be visible, and a broken feature can be killed instantly without a rollback. With many agents merging in parallel, decoupling *merging* from *releasing* is what keeps a shared main branch safe. This also gives you a softer control than the kill switch: turn off one feature rather than halting the company.

**Observability — full stack from the start.** Logs, metrics, distributed traces, and error tracking. Tracing is the one people skip and regret: a slow booking could be the matching query, the Maps API, the payment gateway, or the client — without traces you are guessing, and guessing is expensive when performance is a stated priority. This serves both SRE's uptime ownership and the Performance Engineer's targets, and it is distinct from the agent\-health monitoring in Section 18b.

## 20d. Environments, Edge Protection & Load

**Environments — revised to dev, staging, production.** This supersedes the dev\-and\-production\-only decision in Section 16l, which was made when the team was four agents and there were no specialist gates. QA, Security, Performance, and SRE all need an environment that mirrors production to verify against — without staging they would be testing against dev (which proves little) or against production (which is dangerous once real payments and real customer data exist). The gates are only as trustworthy as what they test against.

**Edge protection — rate limiting, WAF, and DDoS protection.** Two specific threats justify this beyond general good practice. OTP endpoints attract **SMS\-pumping fraud**, where an attacker triggers mass OTP sends and you pay for every message — real money leaving your account, and a common early attack on new phone\-auth apps. Location endpoints attract **scraping** for competitor supply intelligence. Both are cheap to prevent upfront and expensive to discover after the fact. Security owns this surface.

**Load testing before launch.** Run against the performance targets the Architect proposes in Wave 1. The two things that break under load are the matching/ETA query and the live\-tracking fan\-out — precisely the two hardest surfaces in the product. Discovering their limits during your first busy weekend, in a market where a failed on\-demand booking means someone standing next to an unwashed car, is the worst available time to learn.

**Client architecture decided upfront.** The Architect chooses the Flutter state\-management approach in Wave 1, before any UI is built. It is structural: retrofitting state management means rewriting most of the client, making it one of the most expensive late corrections available. It belongs with the ownership map, performance targets, and API contract as a foundation decision.

## 20e. Incidents, Versions & Instrumentation

**Emergency autonomy — the one deliberate exception.** Low autonomy is right for building; it is wrong for outages. SRE holds a **pre\-authorised list of emergency actions** it may take during a live production incident without waiting for you: roll back to last known\-good, disable a feature flag, restart a service, scale up capacity. Every action is logged and reviewed with you afterward, and the CEO's root\-cause review (Section 12) still follows. Anything outside that list still waits for approval. This is the only place in the system where an agent acts on production without you, and it is bounded deliberately: reversible actions only, no schema changes, no data operations, no deploys of new code.

**Minimum supported version.** The client enforces a minimum app version, below which users get a blocking upgrade screen. Mobile clients cannot be force\-updated, so without this mechanism a version with a security flaw or a broken payment path stays live in users' hands indefinitely. Build it early even though it should rarely be used — retrofitting a kill mechanism into already\-released clients is impossible by definition.

**Offline support — employee app only.** Staff queue photos and status updates in dead zones and sync when connectivity returns (Section 16aa). Customer browsing and booking require connectivity anyway, and full offline support across all three apps would add substantial sync and conflict\-resolution complexity for little real benefit.

**Analytics instrumentation.** Data/ML owns the event schema — what events exist, their names, and their shape. Backend and Frontend instrument their own code against that schema, which respects single\-writer ownership while keeping the data consistent. Inconsistent event naming is one of the hardest problems to fix retroactively, because the bad data is already collected; central schema ownership prevents it from starting.

## 21\. Agent Implementation

**Runtime — Claude Agent SDK (Python).** The cockpit backend imports the SDK directly rather than shelling out to the CLI. This matters for three reasons that map onto decisions already made: it returns **structured messages** rather than text to parse, it supports **partial\-message streaming** (which is what makes the live output panel in Section 17b actually work), and it enforces **per\-agent tool permissions** at the runtime layer. Sessions persist to disk, giving the fresh\-session model (Section 17) real mechanics. Since the cockpit backend is FastAPI, the Python SDK sits natively inside it and streams to the browser over SSE or WebSocket.

Docs: `https://code.claude.com/docs/en/agent-sdk/overview.md`

**Tool permissions — least privilege, enforced not requested.** Each agent's `allowed_tools` list is scoped to its role. QA, Security, and Performance get read and test\-execution tools but no write access. The Product Manager gets no code write access at all. Backend gets write access only within its domain. This is the critical point: **an instruction can be misread, a permission cannot be exceeded.** The ownership map (Section 18d) is enforced at the tool layer rather than depending on every agent correctly interpreting its boundaries — which is what makes fifteen parallel agents genuinely safe rather than merely well\-intentioned.

**Role brief template — six fixed sections.** Every agent's brief follows the same structure:

1. **Mandate** — what this role exists to do, in one or two sentences
2. **Ownership** — exactly which files, modules, and decisions belong to it
3. **Inputs** — what it reads at the start of every run
4. **Outputs** — what it must produce, and in what form
5. **Constraints** — hard limits, including what it may never do without approval
6. **Escalation** — what it does when blocked, and to whom

Consistent structure means HR (Section 19a) can compare briefs across roles, spot gaps, and improve them systematically. It also means an agent always knows where to look for its own boundaries.

**Run protocol — fixed open and close.** Every agent, every run:

- **Open:** read the charter, its own brief, its own memory/playbook, the shared lessons file, the ownership map, and its assigned task.
- **Close:** write its report, update its own playbook with anything learned, and log any open questions or blockers.

The close step is what makes the learning loop real rather than aspirational. Without an enforced ritual, memory updates are the first thing skipped when a run gets long — and skipped memory means the fresh\-session model quietly degrades into agents that never learn anything.

## 21a. Orchestration & Agent Interface

**Orchestration — cockpit executes, CEO decides.** The CEO does not spawn other agents inside its own session. It outputs *decisions* ("assign this task to Backend"), and the **cockpit backend** spawns the agents. This separation of judgment from execution is what makes everything else in Section 17 implementable: a real job queue, per\-run retries, individual monitoring, and the ability to stop or redirect one agent without killing the CEO's session. Nested subagent runs would collapse all of that into one opaque process.

**Action interface — custom MCP tools.** Agents take structured actions through purpose\-built tools rather than by writing files freely: `submit_report`, `request_change_from_owner`, `flag_blocker`, `update_playbook`, and similar. Output is validated and machine\-readable, so the cockpit renders it directly instead of parsing whatever markdown an agent happened to produce. This also makes the cross\-domain request flow (Section 18d) a real queued action rather than a note someone hopes gets read.

**Brief versioning.** Every brief change is a git commit with a maintained changelog recording *what changed and why*. This is what gives HR's role teeth (Section 19a): you can correlate a shift in an agent's performance with the exact brief change that preceded it, and revert a change that made things worse. Raw git history alone would show the diff but not the reasoning.

**Dry\-runs before live work.** Each of the fifteen agents is tested on a throwaway task before it touches anything real — verifying it respects its ownership boundaries, writes its memory correctly, reports in the expected shape, and escalates properly. Fifteen agents is a large amount of untested machinery to switch on at once, and a boundary violation discovered on a real repo is far more expensive than one found in a sandbox.

## 21b. Where This Gets Built — An Honest Scoping Note

**The three layers, distinguished.** *Cowork* (where this charter was written) and *Claude Code* (where the carwash app is being built) are products. The *Claude Agent SDK* is the library both are built on. Loop Labs is built on the SDK — not inside either product — because spawning fifteen agents with per\-role permissions, a job queue, and browser streaming requires code you own and run, not a product you converse with.

**What that actually means for effort.** The cockpit is a genuine software project: a FastAPI service with single\-user MFA auth, a job queue, SSE or WebSocket streaming, a database for runs and approvals, agent orchestration via the SDK, and a frontend. DevOps owns it, and it lives in its own repository (Section 18b).

**The risk worth naming.** This is real work that happens *before* the carwash app gains a single new feature. There is a genuine sequencing question — build the full cockpit first, or start with a thinner version and grow it — and it should be answered deliberately rather than by accident. It belongs in the CEO's Wave 1 milestone proposal alongside everything else, scoped honestly rather than assumed to be small.

## 21c. Bootstrap, Memory Limits & Resilience

**Bootstrap decision — the cockpit is built first.** Founders' decision, after considering the alternative of starting agents from the terminal.

The cockpit comes before product work, and **its core is the chat with the CEO.** The reasoning is that the entire operating model runs through a conversation with the CEO (Section 22) — so that conversation is the foundation, not a convenience added later. Building it first means **both founders can participate from day one**, rather than one working through a terminal and relaying to the other.

*The trade\-off, recorded honestly:* this is founder time spent on infrastructure before any product exists. The alternative considered — running Wave 1 from the terminal immediately and having agents build the cockpit — would start product thinking sooner but exclude the non\-technical founder until the interface existed. The founders chose participation over speed, which is defensible for a two\-person company where both are full\-time and either can approve anything.

*The risk to watch:* scope. The cockpit is a real application (Section 21b), and the failure mode is it quietly growing into months of solo work. Keep the first version to what is genuinely needed to hold a conversation with the CEO and act on it; everything else is work the agents themselves can do once they exist.

**Memory limits — hard cap, enforced.** Every memory and playbook file has a maximum size. Exceeding it triggers HR to consolidate rules rather than letting the file silently bloat past what fits in context. This turns the pruning discipline from Section 8 into a mechanism rather than an intention — the failure mode it prevents is subtle and severe: an oversized memory file gets truncated, the agent loses its earliest and often most important rules, and nothing visibly breaks while its judgment quietly degrades.

**Validation hooks.** The SDK's hook system validates every agent run before it is accepted: did the agent stay within its ownership boundary, did it write its memory, did it produce a valid report in the expected shape. Protocol violations — especially skipped memory writes — are silent and compound over time, and no gate agent is looking for them. QA reviews the *work*; hooks verify the *process*.

**Cockpit failure — pause with a CLI escape hatch.** If the cockpit is down, agent work stops cleanly rather than continuing unmonitored. But any agent can still be run directly from the terminal for emergencies, so the cockpit is not a single point of total failure. This matters most in the worst case: the cockpit going down *during* a production incident, when SRE's emergency actions (Section 20e) are exactly what you need and the normal path to them is unavailable.

## 22\. One Point of Control — The CEO Interface

The goal is that you operate the entire company from a single place: a conversation with the CEO. This section revises the approval model to make that actually true rather than nominally true.

**Approval level — revised to the sprint plan.** This supersedes the per\-task approval decision in Sections 11 and 19. You approve **what a sprint contains and why**; the CEO then assigns tasks within that approved plan without returning to you for each one. One meaningful decision replaces forty small ones.

What still requires your explicit approval, regardless of sprint scope:

- Anything touching payments, personal data, or security
- Anything irreversible or externally visible (deploys, public releases, real spend)
- Anything outside the approved sprint plan
- Adding, retiring, or rewriting an agent role
- Charter changes

This keeps the original safety intent — the hard stops in Section 3 are unchanged — while removing the routine friction that would otherwise make you the throughput ceiling for fifteen agents.

**The CEO answers, it doesn't route.** When you ask something it doesn't already know, the CEO **consults the relevant agent live and comes back with a real answer**. Ask "why is booking slow?" and it queries the Performance Engineer in the moment. This is what makes it genuinely one interface rather than a receptionist reading yesterday's reports back to you. You should never need to know which agent owns what in order to get an answer.

**Your direction takes effect immediately.** When you give an instruction mid\-cycle, the CEO applies it now — stopping in\-flight runs where necessary using the interruption mechanism in Section 17a. "Stop the payment work, do X first" happens when you say it, not at the next planning boundary.

**The CTO prevents idle waiting.** Dependency management is the CTO's job: sequencing work so Frontend isn't blocked on Backend's API, unblocking stalled agents, and resolving contention without involving you. Deadlock is a coordination failure, and coordination is precisely what the management layer exists to handle. It reaches you only if a block becomes a scope or priority decision.

**What this looks like day to day.** You open the cockpit. The CEO tells you what happened, what's blocked, and what it recommends next. You approve a sprint, ask questions and get real answers, redirect when you want to. Everything else — assignment, sequencing, gates, escalation, merges — happens beneath that conversation without needing you in it.

## 22a. Making It Smooth

**Founder\-preferences profile.** The CEO maintains a profile of how *you* decide, built from what you approve, reject, redirect, and consistently ask about. Over weeks it needs to ask less because it has genuinely learned your judgment — which work you always want flagged, which you never care about, how much detail you want, where you're risk\-tolerant and where you aren't. This is the single biggest lever on the loop feeling smooth rather than repetitive, and it extends the override\-logging decision from Section 12: your corrections don't just get recorded, they change future behaviour.

**Vague direction gets decomposed, then confirmed.** When you say "make the app faster" or "improve onboarding," the CEO turns it into concrete work and **shows you its interpretation before starting**. You correct the interpretation rather than having to specify everything upfront. This is deliberately the opposite of asking clarifying questions first — the CEO does the specification work and you validate it, which is the right division of labour when you are the constraint on the system.

**Interruptions are bounded.** Only four things reach you outside your session: production incidents, security findings, items needing explicit approval under Section 22, and the sprint being genuinely blocked. Everything else waits. Without this bound, sprint\-level approval would simply be replaced by a constant stream of pings, and the single\-point model would be lost by a different route.

**Session format — four things.** Each session opens with a short plain\-English brief: **what shipped, what's blocked, what needs you, what's next.** Everything else is available by asking. Short enough that you actually read it rather than skim, and the drill\-down (Section 17b) is always there when you want the detail behind any line of it.

## 22b. Sprint Mechanics & Company Health

**Absence resolved.** This corrects a contradiction between the 3\-day auto\-pause (Section 13) and week\-long approved sprints. **Approved sprint work continues** through your absence — agents keep executing what you already authorised. What pauses after 3 days of silence is anything requiring a *fresh* decision: new sprints, hard\-stop items, off\-plan work, and anything in the explicit\-approval list (Section 22). Your absence no longer wastes a sprint you already signed off, and nothing new starts without you. The catch\-up summary on return (Section 15) still applies.

**Sprint length — one week.** Frequent enough that a wrong direction surfaces within days, long enough that approval isn't constant.

**Sprint reversal.** If a sprint proves misdirected: merged work that passed all gates **stays**, in\-flight work **stops immediately**, and the CEO proposes a corrected plan. Feature flags (Section 20c) are what make this safe — merged\-but\-unwanted work can simply stay switched off rather than needing to be torn out. Reverting everything would discard genuinely good work for the sin of being aimed at the wrong goal.

**Company health metrics.** The CEO tracks whether the *organisation* is working, not just the product: throughput per sprint, rework rate, and gate rejection rates by type. These are diagnostic. Rising rework points at spec or design quality upstream. Rising gate rejections point at a degrading agent — which is HR's cue to investigate (Section 19a). Without hard numbers, "is this actually working?" is answered by feel, and by the time it feels wrong you've lost weeks. This complements the monthly retrospective (Section 14) rather than replacing it: metrics say *what* is happening, the retrospective asks *whether it still makes sense*.

## 23\. Contradiction Resolutions

A review of this document found thirty\-two internal contradictions, accumulated because early sections were written for a four\-agent phased plan and later ones for a fifteen\-agent SDK\-based organisation. The mechanical ones (stale references, superseded implementation details, retired roles) are corrected in place. The ones that required a real decision are resolved here, and **these rulings win over anything earlier in the document that conflicts with them.**

### 23\.1 You are the final merge gate

Sections 17a, 18a, 18b and 22 disagreed on whether you approve individual merges. **Resolution: yes, you do.**

The two approval levels are distinct and both apply:

- **Sprint approval** governs *what gets worked on*. The CEO assigns tasks freely within an approved sprint without returning to you.
- **Merge approval** governs *what enters the codebase*. No code lands in main without your explicit approval, regardless of how many gates it passed.

Full path of a change: Architect design sign\-off → build in isolated worktree → CI → QA \+ Security \+ Performance in parallel → CEO review → **your approval** → merge.

*Trade\-off, named honestly:* this means several merge approvals per day once all fifteen agents are running, and merge throughput is capped by your availability. This is a deliberate choice for control over speed. If it becomes the binding constraint, the first lever is delegating routine merges (tests, docs, refactors) while keeping the gate on anything user\-visible or sensitive — not removing the gate entirely.

### 23\.2 Agents may communicate laterally, within structure

Section 2's rule that "every agent below the CEO only talks to the CEO" is **retired**. It was written for a four\-agent team and does not survive fifteen.

Agents may interact directly for **defined, structured purposes only**, all through MCP tools (Section 21a): filing change requests to a file's owner, coordinating work sequencing, and taking design questions to the Architect. Everything else still routes through the CEO — priorities, scope, anything reaching you, and any dispute that isn't purely technical.

The single\-point principle is preserved where it matters: **you** talk to one agent. The agents do not need to route every technical exchange through the CEO to make that true.

### 23\.3 QA gets write access to test files only

Section 18e assigns QA the duty of adding edge\-case tests; Section 21's read\-only permissions made that impossible. **Resolution: QA's `allowed_tools` include write access scoped to test files exclusively.** It can add the cases it finds; it still cannot touch production code. Both the duty and the boundary survive.

### 23\.4 SRE restores production during incidents

Section 18c ("rollback stays manual, triggered by you") and Section 20e ("SRE holds pre\-authorised rollback") conflicted. **Resolution: SRE acts immediately.**

During a live production incident, SRE rolls back to the last known\-good deploy on its own authority and reports afterward — downtime measured in minutes rather than in however long you take to see an alert. You retain the ability to trigger rollback yourself at any time. SRE's pre\-authorised list remains bounded to reversible actions only (rollback, feature\-flag disable, restart, scale up): no schema changes, no data operations, no deploying new code.

This is the second deliberate exception to low autonomy, alongside the first in Section 20e, and both exist for the same reason: outages are the one situation where waiting for approval costs more than acting without it.

### 23\.5 Agents read a constitution, not the full charter

Section 17 said employee agents should not receive the full charter; Section 21's run protocol said every agent reads it every run. **Resolution: a short constitution.**

A one\-to\-two page document that every agent reads on every run, containing only: the hard stops (Section 3), the ownership model, the definition of done, escalation paths, and the three stated priorities (speed, security, performance). This full charter remains in the repository and any agent reads the sections relevant to its current task — the Architect and Product Manager will read most of it; DevOps rarely needs the cancellation policy.

*Rationale:* sixteen thousand words × fifteen agents × every run is context spent mostly on detail the reading role doesn't need, and it makes the rules that matter compete for attention with product minutiae. A short document agents genuinely absorb beats a long one they skim. The CEO owns keeping the constitution in sync when the charter changes.

### 23\.6 Employee name and photo are collected at signup

Customers were meant to see the assigned employee's name and photo, but signup collected only a phone number. **Resolution: the business provides the employee's name and photo when creating their account.** No ID verification — consistent with businesses vetting their own staff (Section 16cc) — but enough for the customer\-facing screen to work. This matters specifically because mobile service means someone arriving at a customer's home.

### 23\.7 Cancellation gives credit, not cash

"Free cancellation up to 1 hour before" (Section 16c) and "no refunds, reschedule only" (Section 16e) were incompatible under prepayment. **Resolution: cancelling before the 1\-hour cutoff converts the payment into platform credit toward a future booking.** "Free" means no penalty, not money returned. Cash refunds remain reserved for **business\-side** cancellations (Section 16x), where the customer did nothing wrong.

### 23\.8 Scheduling model deferred to the Architect

Three incompatible descriptions existed: fixed 30\-minute slots (Section 16b), any future start time with no minimum notice (Section 16z), and variable durations calculated from multi\-service baskets (Section 16ee). **Resolution: this is a Wave 1 design decision for the Architect**, who proposes a single coherent model for your approval.

The tension to resolve: a fixed slot grid is simpler for availability and capacity logic, but cannot express arbitrary start times or a basket whose duration is the sum of several services on several vehicles. Variable\-duration booking is more flexible and matches the product as specified elsewhere, at the cost of harder availability computation. The Architect should also confirm the choice works with ETA\-based ranking (Section 16f), which depends on knowing when a provider's current job actually ends.

### 23\.9 Businesses cannot reject bookings

Section 16d let businesses accept or reject bookings, but the system auto\-assigns employees, auto\-enforces capacity (Section 16x), and takes prepayment with no cash refunds. A rejection would leave a paying customer with a broken booking and no clean resolution. **Resolution: rejection is removed.**

Businesses control their supply through availability settings, declared service durations, and staff capacity — all of which the system already enforces. A booking that gets through those controls is one the business has effectively already agreed to. The business dashboard shows incoming bookings; it does not gate them.

### 23\.10 Membership pricing — one platform price, converted per market

Membership pricing was defined as the average carwash price "across all businesses on the platform" while markets are isolated and there is no cross\-market conversion. **Resolution: a single platform\-wide membership value, converted into each market's local currency.**

*Note the implication:* this is a deliberate exception to the no\-conversion rule in Section 16m, which governs *booking* prices — those remain purely local, set by businesses in their own currency. Membership is Loop Labs' own product, priced once and expressed in BHD and AED. The Finance work this implies (choosing and maintaining a conversion basis) is another item for a real advisor rather than an agent, alongside the open VAT question.

### 23\.11 Wave assignments corrected

- **Performance Engineer moves to Wave 1.** The geospatial search benchmark (Section 20b) is a Wave 1 deliverable and explicitly requires the Performance Engineer; it cannot be assigned to an agent that isn't active yet.
- **Integrations Engineer joins Wave 2.** It was added after the waves were defined and belonged to none of them. Wave 2 is when payment gateway, Maps, and SMS work actually begins.

Revised waves: **Wave 1** — CEO, CTO, Architect, Product Manager, Performance Engineer. **Wave 2** — UX/UI, Backend, Frontend, Integrations, QA, DevOps. **Wave 3** — Security, SRE, Data/ML, HR. Total: fifteen agents (Sections 19b's "fourteen" counts predate the Integrations Engineer).

### 23\.12 Technical authority belongs to the technical roles

Section 12 gave the CEO authority over major architecture calls — written before the CTO and Architect existed. **Resolution: that authority is retired.**

- **Architect** decides system design, contracts, and arbitrates design disputes.
- **CTO** coordinates technical work, sequencing, dependencies, and gate outcomes; technical escalation terminates here rather than at the CEO.
- **CEO** handles direction, product, priorities, and you. It retains codebase read access (Section 14) for context, not for authority.

Genuinely major architectural decisions still reach you through the CEO as part of sprint planning — the CEO carries them, it does not make them.

### 23\.13 Ratings — one input, two audiences

Sections 16u and 16dd disagreed on whether employee ratings exist. **Resolution: they do, and they are derived rather than separately collected.**

A customer rates the **order**. That single rating serves two purposes with two different audiences:

- **The business rating** — aggregated across all of a business's orders (and all its branches, per Section 16dd), shown publicly to other customers on the platform.
- **The employee rating** — the same order ratings attributed to whichever employee performed each job, aggregated per employee and **visible only to that employee's business owner**. Never shown to customers.

This resolves the earlier confusion cleanly: there is one rating mechanism, not two. Customers never rate an individual person, and never see one. Business owners see how their own staff are performing, which is exactly the input the per\-employee AI insights (Section 16g) and the duration\-prediction model (Section 16w) need.

### 23\.14 Solo operators are not supported — reversal

Section 16m allowed a business with no separate employees, where the owner acts as their own staff. **This is reversed.** The business model is built on employees performing washes under a registered business; an owner\-only account is not a supported configuration. Every business has staff, and the business\-owner and employee roles remain distinct accounts as described in Section 16b.

*Consequence:* the account\-separation question this raised disappears entirely, and business onboarding should require at least one employee before the business can go live.

### 23\.15 Penalty fees go to the business

No\-show fees (Section 16h) and cancel\-after\-dispatch fees (Section 16y) sat awkwardly beside the "free for customers, no platform fee" promise. **Resolution: these fees go to the business**, compensating it for wasted staff time and travel — which is who actually bore the loss. The platform takes no share, so the no\-platform\-fee claim remains literally true: Loop Labs' only customer\-side revenue is memberships, and its only business\-side revenue is monthly subscription fees.

### 23\.16 Complaints surface in the founder admin dashboard

The in\-app complaint form was described as landing "in the system agents already read," but Customer Support was cut and complaints route to you personally. **Resolution: complaints appear in the founder admin dashboard** (Section 16k), alongside business approvals and disputes — one place for everything needing your attention, with no agent in the loop. This is the product admin dashboard, distinct from the Loop Labs cockpit.

### 23\.17 Mechanically corrected without needing a decision

The following were stale rather than contested, and are corrected in place: Section 7's entire `.claude/agents` and cron approach (superseded by the SDK and cockpit orchestration); Section 6's file\-inbox coordination protocol (superseded by MCP tools and the job queue); Section 4/4a/5/8's Marketing Strategist role, brief, folder and worked example (the role was cut); Section 10's cost\-caution guidance (superseded by cost being a non\-constraint); Section 16's stack line (missing PostgreSQL); Section 11's app\-repo memory location (moved to the cockpit repo); Section 14's always\-fire notification rule and Section 12's per\-task reminders (superseded by bounded interruptions); Section 4a's instruction not to build QA or HR yet; Section 17c's stale three\-agent escalation list; Section 21's "sessions persist to disk" wording (the SDK persists sessions; Loop Labs deliberately starts fresh ones); and three miscited cross\-references pointing at Section 12 where the content actually lives in Section 11.

## 24\. Concurrency & Operational Safety

Fifteen agents running in parallel create failure modes that don't exist with one. These are the mechanisms that keep concurrent operation correct rather than merely fast.

**Stale worktrees — auto\-rebase before gates.** Main moves as work merges, so an agent can finish against a codebase that no longer exists. Every worktree **rebases onto current main before entering review, and CI re\-runs**. Gates therefore always test against what will actually be merged rather than a stale snapshot. This closes the gap that worktree isolation alone leaves open: isolation prevents agents from colliding *while working*, rebasing prevents them from colliding *on arrival*.

**Merge queue — ordered by the CTO, presented in batch.** When several agents finish simultaneously, the CTO orders the queue by dependency and risk: work that unblocks other work first, risky changes flagged. You see a prioritised batch rather than six unordered requests. Merges then execute **one at a time with CI re\-run between each**, so two independently\-approved changes cannot conflict on the way in. This directly reduces the thinking each approval costs you, which matters because you are the merge gate (Section 23.1).

**Partial failure — discard and retry clean.** A run that fails partway (files half\-written, memory not updated) has its **worktree discarded entirely** and retries from scratch. No half\-finished state can reach main or confuse the next run. This is precisely why worktree isolation is worth its cost: a failed run leaves nothing behind to clean up. The single\-retry rule (Section 17b) still applies — a second failure escalates.

**Prompt injection — external content is data, never instruction.** Agents research the web and read third\-party code, issues, and dependency files, any of which can contain text crafted to look like instructions. Every agent is explicitly instructed that **fetched or third\-party content is information to evaluate, never a directive to obey.** This pairs with least\-privilege tooling (Section 21) to give defence in depth: even if an agent were persuaded by injected text, it lacks the permissions to act outside its domain. Security owns this threat model and should treat any agent behaviour traceable to external content as an incident worth reviewing.

## 24a. Capacity, State & Recovery

**Rate limits — priority queue.** Fifteen concurrent agents will hit API rate limits; this is a certainty, not a risk. When capacity is constrained, runs are ordered by priority: **SRE incident work first, then blocking gates, then routine build work.** "Unlimited concurrency" (Section 18) therefore means *as fast as capacity allows, in the right order* — not everything degrading equally. Without this, a production incident could sit behind a batch of routine refactors, which is exactly backwards.

**Source of truth — git.** The cockpit database tracks runs, approvals, and sprint state; git holds the actual code and company memory. When they disagree — a cockpit crash mid\-merge, a partial write — **git is authoritative and the cockpit rebuilds its index by reading the repositories.** This makes cockpit database loss recoverable rather than catastrophic, and it means the off\-site git backup (Section 18d) genuinely protects everything that matters. The cockpit is a control plane and a queryable view, never the system of record.

**Secret leakage — scan and redact in both directions.** Agents never handle secrets directly, but they read config files, error messages, and logs, where credentials routinely leak by accident. Automatic secret\-pattern detection runs on **anything entering an agent's context** (redacting before it reaches the model) and on **anything an agent writes or displays** (catching accidental leaks outward). This is distinct from the pre\-merge CI secret scan (Section 20c), which only catches secrets being committed — this catches them being *read*, which is where a leak into a model context or a streamed log would otherwise go unnoticed.

**Undoing an approved merge — two levers.** When a merge you approved turns out to be wrong: **flip the feature flag** to disable it instantly (mitigation in seconds), then have Backend **revert the commit** properly (clean permanent fix). The CEO logs why it was wrong, which feeds both its own playbook and the company health metrics (Section 22b) — a merge you approved and then reverted is a signal about the review process, not just about that one change. This is distinct from production rollback (Section 23.4), which undoes a whole deploy rather than one change.

## 24b. Removing Bottlenecks, Preventing Drift

**Architect review — scoped to what matters.** This revises Section 18b, which required Architect design sign\-off before *any* build. With fifteen agents that made the Architect the pacing constraint for the entire organisation, on top of owning contracts, the ownership map, migration approval, and arbitration.

**Design review is now required only for:** work crossing a domain boundary, changes to the API contract, schema migrations, and anything the CTO flags as risky. Work entirely inside a single agent's own domain proceeds without sign\-off. This keeps every check that actually prevents conflict while removing the review that mostly just added latency — an agent working alone inside its own files is precisely the case where the ownership map already guarantees safety.

**Contract drift — machine\-checked.** The API contract is the seam between Backend and Frontend, and a change on one side without the other breaks the app. **Contract tests fail CI on any mismatch**, so a breaking change is caught before it reaches any gate. This is deliberately automated rather than reviewed: it is exactly the kind of check that machines do reliably and reviewers miss when tired. API versioning (Section 20) still protects already\-released clients; contract tests protect the ones being built.

**Decision history — searchable, queryable through the CEO.** Every decision is recorded with its reasoning and date, and you retrieve it by asking the CEO in plain language rather than searching files yourself. This serves two purposes: you can ask "why did we build it this way?" months later and get a real answer, and the CEO can check whether a question has already been settled instead of re\-litigating it. It extends the single\-point principle (Section 22) — institutional memory is something you access by asking, not by digging.

**Audit log — append\-only.** Audit entries can be written by agents but never edited or deleted by them. The log's entire value is being an independent record of what actually happened, including anything that went wrong or was later reverted — and a record that the actors can rewrite is not independent. This is cheap to enforce and it is what makes the override log (Section 11), the founder\-override log (Section 16cc), and the company health metrics (Section 22b) trustworthy rather than merely present.

## 24c. Self\-Repair, Gate Quality & Graceful Degradation

**The cockpit circularity.** The cockpit runs the agents, so a bad cockpit change can break the very thing needed to fix it. Two protections break the circle: changes to the cockpit get **stricter review than app changes** (the blast radius is the whole company, not one feature) and always deploy in a quickly revertible form; and the **terminal fallback** (Section 21c) lets you run any agent directly, bypassing the cockpit entirely. If the cockpit dies, you open a terminal, run DevOps, and have it repair the cockpit — a path that by definition doesn't depend on the cockpit working.

**Gate quality — measured, not assumed.** A gate that passes everything is worse than no gate, because it creates false confidence. Two signals are tracked: **rejection rate trending toward zero**, and **escaped\-defect attribution** — work that passed a gate and later broke gets traced back to the gate that should have caught it. Either signal flags the gate to HR for brief review (Section 19a). This turns "is this gate actually working?" from a matter of trust into a measurable question, and it is the specific mechanism by which a quietly degrading agent gets caught rather than silently reducing quality for weeks.

**Provider outages — degrade per provider, not uniformly.** Each third\-party dependency gets its own defined fallback, owned by the Integrations Engineer: SMS down falls back to push for OTP delivery; Maps down shows cached locations without live ETA rather than blocking discovery entirely; payments down blocks *new* bookings with a clear message rather than failing silently mid\-transaction. The principle is that a single provider failing should degrade one capability, not take down the platform — and that the customer should always be told plainly what isn't working.

**Duplicate work.** All in\-flight work is visible on a single active\-work board, and the **CTO verifies nothing overlaps before assigning a task.** Ownership boundaries prevent two agents editing the same *files*, but they do not prevent two agents independently attacking the same *problem* from different domains — that's a coordination failure, and coordination is the management layer's job.

## 24d. Incident Triggers, Model Policy & Deploy Verification

**Incidents are declared by monitoring, not by SRE.** Section 23.4 gave SRE authority to act without approval "during a live production incident" without defining one — meaning the agent effectively decided when it was allowed to bypass you. **Resolution: SRE's autonomy unlocks only on objective monitoring signals** — service down, error rate above threshold, payment failures spiking. The agent cannot declare an incident itself, and therefore cannot self\-authorise. This closes the most significant remaining hole in the safety model: every other autonomy boundary was bounded by scope, but this one was bounded only by the agent's own judgment.

**Model policy — always latest.** Agents run on the newest available model rather than pinned versions, taking improvements as they ship.

*Trade\-off worth naming, since reliability is a stated priority:* this means agent behaviour can shift without warning, potentially mid\-sprint, and a change in output quality may not be obviously attributable to a model update. The mitigations already in place partly cover this — agent health monitoring (Section 18b) and gate rejection rates (Section 24c) would surface a behavioural shift as a metrics change, and HR investigates degradation (Section 19a). If unexplained behaviour changes ever become a real problem, pinning versions is the correction; it does not need deciding now.

**Gate efficiency — shared analysis, specialist lenses.** One pass produces a structured summary of what changed; each of QA, Security, and Performance then reads that summary plus the specific files its own concern touches. Same coverage at roughly a third of the reading cost, and the gates still run in parallel (Section 18a). Since every change passes through all three, this is one of the largest available speed gains in the whole pipeline.

**Deploy verification — smoke tests with auto\-rollback.** Immediately after every deploy, critical paths are exercised automatically: authentication, search and matching, booking creation, and payment. Any failure triggers **immediate automatic rollback** without waiting for a human or an incident declaration. This closes the gap between "the deploy succeeded" and "the app actually works," which is where a large share of real outages live — the deploy reports success, monitoring looks normal because there's no traffic yet, and the first person to discover the breakage is a customer trying to book a car wash.

## 24e. Test Data, CI Speed, Backups & Patching

**Synthetic test data only.** Staging and dev never receive copies of production data — not even anonymised ones. Test data is generated to look realistic while representing nobody. This confines PDPL exposure entirely to production, and means a breach of a less\-hardened environment leaks nothing real. Anonymisation was rejected deliberately: it is easy to get subtly wrong, and location history in particular is notoriously hard to anonymise, since movement patterns can re\-identify a person even without a name attached.

**CI — incremental during work, full suite before merge.** While an agent is working, only the tests relevant to what it changed run, giving feedback in seconds rather than minutes. The **complete suite runs before anything merges**, so nothing enters the codebase unverified. Speed where iteration happens, thoroughness at the gate. With fifteen agents making changes continuously, the difference between seconds and minutes of feedback compounds into a substantial share of total throughput.

**Backups are verified by restoring them.** An automated restore test runs on a schedule: a backup is restored to a throwaway environment and verified to actually work. This applies to both the product database and the company memory (Section 18d). Untested backups are a well\-known false comfort — the failure is discovered at precisely the moment recovery is needed, and "we have daily backups" becomes worthless the first time one doesn't restore.

**Dependency patching — security fast\-tracked, features batched.** A known vulnerability is patched as priority work, jumping the normal queue. Routine version bumps batch into scheduled maintenance to avoid constant churn. Security owns the judgment of which is which, and CI's dependency scanning (Section 20a) is what surfaces them. This keeps the system current on the updates that matter without every minor release becoming a task.

## 24f. Disaster Recovery, Data Isolation & Operating Signal

**Region failure — recovery, not redundancy.** The single\-region choice (Section 20b) means a full region outage takes the platform down. This is accepted deliberately for now: multi\-region redundancy is expensive, complex, and complicates the data\-residency position, which is a poor trade for a pre\-launch product. The mitigation is **backups stored in a second region**, so the platform can be rebuilt elsewhere if the worst happens. This accepts hours of downtime in a rare event rather than paying continuously to prevent it — a reasonable position that should be revisited once real revenue makes downtime genuinely costly.

**No agent touches production data.** No agent — including SRE and Data/ML — queries the production database directly. Agents work with code, synthetic data, and **aggregated metrics** only. This removes an entire class of risk at once: no accidental PDPL violation, no customer records in a model context, and no data exfiltration path if an agent is ever compromised or manipulated by injected content (Section 24). Aggregated metrics cover essentially every legitimate need — SRE diagnoses from error rates and traces, Data/ML trains on aggregated job\-duration statistics rather than individual customer records.

**Cycle time — measured against a target.** Time from task assigned to change merged is tracked with a target. This makes speed measurable rather than aspirational, and — more usefully — when it slows, the stage\-by\-stage breakdown shows exactly where: gates, CI, rework, or waiting on your approval. Given that you are the merge gate (Section 23.1), this is also the metric that would tell you honestly whether your availability has become the constraint, rather than leaving it to impression.

**Operating signal — one indicator.** The cockpit's primary signal is a **single status indicator** covering production health, agent health, and whether anything is blocked or waiting on you, with drill\-down behind it. Green means genuinely nothing needs your attention. This is the practical expression of the single\-point principle (Section 22): the goal is not a dashboard you consult daily, but a signal that lets you *not* consult it — and tells you unambiguously when you must.

## 24g. Verified Resilience, External Audit & Day One

**Fallbacks are tested by breaking things.** Provider failures are simulated on a schedule in staging — payment gateway, Maps, and SMS each deliberately failed to verify the defined degradation (Section 24c) actually behaves as designed. This is the same reasoning as restore\-testing backups: **fallback code is the least\-exercised code in any system**, which means it is the most likely to have quietly rotted, and it is discovered at the worst possible moment.

**External penetration test before launch.** The Security Engineer reviews every change, but reviewing your own team's work is structurally different from an adversary actively trying to break in. Before real customers use the platform, a human specialist tests it. This is warranted specifically by the surface: payments, personal data, and continuous location tracking, across two regulated markets. An agent auditing code written by its own colleagues has a blind spot that no amount of diligence closes.

**Scaling — automatic, bounded.** Capacity follows demand automatically, with a **floor** that keeps response times good even at quiet hours and a **ceiling** that prevents a traffic spike or an attack producing a surprise bill. Carwash demand is genuinely spiky — weekends and evenings — so fixed capacity would mean paying for peak all week or degrading at peak. DevOps and Performance own the specific thresholds, set against the agreed performance targets.

**Day one — the CEO interviews you before it plans anything.** The first thing that happens when the cockpit works is not a plan. The CEO reads this entire charter, then tells you **what it understands, what it thinks the priorities are, and what remains genuinely ambiguous** — and asks its own questions. You correct its understanding before it proposes a single milestone.

This matters more than it might appear. Everything downstream — the milestone breakdown, sprint plans, what gets built first — flows from the CEO's reading of this document. A misunderstanding at that moment propagates into every decision after it. Spending the first session confirming comprehension rather than producing output is the cheapest correction available, and it sets the pattern for the relationship: the CEO checks its understanding with you rather than assuming it.

## 25\. Scalability

**Guarding the CEO.** Everything routes through the CEO, which makes it the one role nothing else oversees — a degraded CEO (corrupted memory, a bad brief change, drifting judgment) would misdirect every decision downstream with nothing to catch it. Two protections: **HR monitors the CEO exactly as it monitors any other agent** (Section 19a), tracking decision quality and flagging degradation; and **you see the CEO's reasoning in every proposal**, not just its conclusions, so poor judgment surfaces to you directly rather than propagating silently. This is also why proposals include two or three options with a recommendation (Section 17c) rather than a bare directive — visible reasoning is what makes the CEO auditable at all.

**Market as a first\-class concept.** Every business, booking, price, currency, and employee is tagged to a market from day one. Adding Saudi Arabia, Kuwait, or Qatar later becomes configuration rather than a rewrite. This is cheap to build now and genuinely expensive to retrofit — market assumptions leak into schema, pricing, availability, search, and payments, and unpicking them after real data exists is among the more painful migrations available. It also makes the existing market\-isolation rules (Section 16s) explicit in the data model rather than implicit in application logic.

**Data scaling — designed for, built when needed.** The Architect designs with scaling paths in mind (indexing strategy, read replicas, archival of completed bookings, partitioning by market and date) but does not implement them until monitoring shows the need. This avoids both failure modes: premature complexity that slows early development, and a painful retrofit under load. The trigger is metrics, not intuition — query performance against the agreed targets (Section 18a) is what signals it's time.

**Ownership at directory level, not file level.** Agents own directories and modules rather than individual files, so newly created files inherit ownership automatically. This keeps the ownership map small and accurate as the codebase grows tenfold, rather than turning it into a maintenance burden on the Architect. The reasoning is practical: a map that is expensive to maintain will drift out of date, and a stale ownership map protects nothing while appearing to — the worst possible state for the mechanism the entire conflict\-prevention model rests on.

## 25a. Organisational Scaling

**Multiple ventures — separate teams under one CEO.** When Loop Labs takes on a second venture, it gets its **own full engineering team** rather than sharing the carwash team's capacity. One CEO still oversees everything (Section 14), keeping prioritisation and budget trade\-offs unified at a single point, but the teams don't contend for each other's agents.

*Worth planning for:* this roughly doubles agent count and duplicates infrastructure ownership, so the CEO's span widens considerably at that moment. The natural structure is a CTO per venture reporting to the shared CEO — which is exactly the layering principle below, applied at the venture level rather than the team level. This is also the point at which the cockpit must handle multiple products cleanly, so it is worth the Architect keeping venture\-scoping in mind even while only one exists.

**New agents get a shadow period.** An agent added after launch has its **first few tasks reviewed by the CTO before anything merges**, confirming it respects its ownership boundaries and produces work of the expected standard. This is the dry\-run principle (Section 21a) extended to live work: the failure it prevents — a new agent misunderstanding its boundary and writing outside its domain — is precisely what the ownership map exists to stop, and precisely what a brand\-new agent is most likely to get wrong.

**Bad boundaries surface themselves.** If two agents constantly file cross\-domain change requests to each other, the boundary between them is drawn in the wrong place. **Cross\-domain request volume is tracked as a metric**, and a sustained spike between any two agents flags the Architect to redraw that boundary. The system reports its own structural mistakes rather than depending on someone noticing friction — which matters because the friction is distributed across agents that each only feel their own share of it.

**Growing past fifteen — add a layer, don't widen.** The CTO currently coordinates eleven technical agents, which is already substantial. Beyond roughly fifteen, the correction is **team leads beneath the CTO**, not more agents reporting directly to it. This is the same reasoning that introduced the CTO beneath the CEO (Section 19): a coordinating role holding too much detail degrades at exactly the job it exists to do. Depth scales; width does not.

## 26\. Two Founders

This revises the single\-user model in Section 18c. **Loop Labs has two co\-founders — Faisal and his brother — and both operate the company.** Throughout this document, "you" should be read as "either founder."

**Access.** Two accounts, each with MFA and the IP restrictions from Section 18c. The security posture is unchanged in kind — the cockpit remains the highest\-value target in the system and gets the same protection — but it is no longer a single\-user system, and it should not be built as one.

**Approval authority.** **Either founder can approve anything independently**, including merges, sprints, hard\-stop items, and overrides. Whoever is available keeps the company moving; neither becomes a bottleneck when the other is busy. This matters given you are the merge gate (Section 23.1) — two approvers roughly doubles merge throughput without weakening the gate itself.

**Preferences profile.** One shared profile capturing how *Loop Labs* decides, plus small individual notes for personal preferences like preferred detail level. The CEO should not develop meaningfully different judgment depending on which founder it is talking to — that would let the company's direction drift toward whoever engages more often.

**Conflicting direction.** If the two of you give the CEO conflicting instructions, it **stops and surfaces the conflict to you both**. It never picks a side, and it never simply follows whoever spoke most recently. This is deliberate: an agent that resolves founder disagreements by default becomes the accidental arbiter of your partnership, which is not a role it should ever hold. The disagreement is yours to settle; the CEO's job is to make sure it is visible rather than silently resolved.

**Attribution.** Every approval, direction, and override is recorded in the append\-only audit log (Section 24b) against the founder who made it. This serves coordination as much as accountability — each of you can see what the other decided and why, without having to ask.

**Continuity benefit.** Two operators also resolves the availability risk that a single\-founder system carries: the 3\-day auto\-pause (Section 22b) and the approval bottleneck both become far less likely to bind, since the company only stalls if *both* founders are unavailable.

## 26a. Compliance Evidence & Cockpit Engineering

**Compliance evidence generated automatically.** PDPL can require demonstrating correct data handling, not merely doing it. The system produces that evidence as a by\-product of normal operation: records of data access, consent given, retention applied, and deletion requests honoured. Reconstructing this under regulatory pressure months later is painful and often impossible; capturing it continuously costs almost nothing. This complements the append\-only audit log, which covers company operations rather than customer\-data handling.

**Cockpit engineered to product standard.** The cockpit is built with the same rigour as the customer\-facing app rather than treated as a lightweight internal tool. It carries genuine load — fifteen agents streaming concurrently, queued runs, sprint state, two operators — and more importantly it is the control plane for everything else: if it is unreliable, nothing else can be relied on either. Given the cockpit circularity (Section 24c), reliability here is worth more than it would be for an ordinary internal tool.

**One company\-wide sprint.** A single sprint across all agents, working toward one goal each week, with one plan for the founders to approve. Separate per\-discipline sprints would mean multiple plans to review and reconcile, which directly undermines operating from a single point (Section 22).

## 27\. The Add\-Ons — Loop Labs' Revenue Model

Businesses pay a base platform fee plus individually\-priced add\-ons, choosing the tooling they want rather than buying bundles (Section 16). This section defines what those add\-ons actually contain — previously the least\-specified part of the product despite being what generates revenue.

### 27\.1 AI Insights

All four capabilities, built from data the platform already captures:

- **Staff performance** — speed per employee, jobs completed, punctuality. Draws on the per\-employee ratings and duration data established in Sections 23.13 and 16w, visible to the business owner only.
- **Demand patterns** — busiest hours, days, and locations, so owners can staff appropriately.
- **Revenue analysis** — which services and price points actually earn, and how that shifts over time.
- **Recommendations** — concrete suggested actions rather than raw data: "add staff Thursday evenings," "your interior clean is priced below comparable businesses nearby."

The recommendations layer is what distinguishes this from a dashboard, and it is the hardest part to do honestly. It needs enough real data behind it to be genuinely useful rather than plausible\-sounding — the failure mode warned about in Section 10. Data/ML owns it, and it should be held back until the data supports it rather than shipped as confident\-sounding guesswork.

### 27\.2 Accounting

**Full bookkeeping** — expenses, payroll, and tax filing, beyond the free revenue view every business gets (Section 16p).

*This deserves an honest flag.* Full bookkeeping is a substantially larger build than reporting and exports, and it competes directly with established accounting software that businesses may already use. It also carries real regulatory weight: payroll and tax filing differ between Bahrain and the UAE, and getting either wrong creates liability for the businesses relying on it — which is a different class of risk from a booking bug. This intersects the open VAT question (Section 16aa) and needs the same real accountant input, not agent judgment.

Worth considering when it gets scoped: whether a first version covering reports, exports, and payout reconciliation would capture most of the value at a fraction of the cost and risk, with full bookkeeping following once there are paying businesses asking for it. That is a decision for the CEO's planning, not a change to the intent recorded here.

### 27\.3 Marketing

**Not decided yet.** The options considered were in\-platform promotion (featured placement, promoted listings, discounts to nearby customers — using assets Loop Labs already controls), external marketing tooling (social posts, ads, SMS campaigns — a much larger build competing with existing tools), or in\-platform first with external later. This remains genuinely open and should be revisited when there are real businesses to ask what they'd actually pay for.

## 28\. The Employee App

The third user type, and where GPS tracking, photo capture, and job execution all actually happen.

**Home view.** The employee sees their **current job prominently, with the full list of their assigned jobs also available** — enough to work the job in front of them without losing the ability to see the whole day.

**Navigation.** For mobile service, the app hands off to **Google Maps** for turn\-by\-turn directions rather than building navigation in\-app. Employees already know how to use it, and navigation is a hard thing to build well against a free tool everyone has.

**Cannot\-complete flow.** A structured report with a **reason and photo evidence** when a job genuinely can't be done — car inaccessible, wrong vehicle, customer absent. This is deliberately structured rather than freeform chat, because the reported reason drives what happens to the money: a customer\-absent report triggers the no\-show fee (Section 23.15), an access problem may warrant a reschedule, and a business\-side failure may warrant a refund. Without a structured flow, every one of these becomes a manual dispute landing in the founders' dashboard.

**Availability.** Employees can mark themselves unavailable during a shift (break, vehicle problem, illness), which **stops the system assigning them work and notifies the business owner**. This matters more than it looks: job assignment is automatic and final (Section 16g), so without a self\-service unavailable status the system would keep assigning jobs to someone who cannot take them, producing failed bookings that nothing in the flow would catch until a customer was left waiting.

**Note for the ETA model.** Unavailability, cannot\-complete reports, and their reasons are all signal for the duration\-prediction model and the per\-employee insights (Sections 16w, 27.1) — but they should be excluded from performance judgments where the cause was outside the employee's control. An employee whose jobs fail because customers keep being absent should not read as a slow or unreliable employee.

## 29\. Go\-to\-Market — SaaS First, Marketplace Second

This is the strategic core of the product and it reframes everything else, so it belongs stated plainly:

**Businesses do not join Loop Labs to get customers. They join to run their business better.** The all\-in\-one operational tooling — staff tracking, scheduling, AI insights, accounting — is valuable on day one even with zero platform customers. This dissolves the classic marketplace cold\-start problem rather than solving it: there is no chicken\-and\-egg, because the business side has standalone value independent of demand.

**Demand then follows from two directions.** Businesses that find the system useful promote it to their own existing customers, bringing their demand onto the platform. Loop Labs advertises the consumer app directly in parallel.

**Externally\-sourced jobs are recorded too.** Employees can log a wash that came from a walk\-in or another platform, not just a Loop Labs booking. This is strategically important and easy to underrate: it means a business's operational data is **complete** regardless of where its bookings originate, so the AI insights are genuinely accurate rather than reflecting only the slice that came through Loop Labs. A business seeing partial data would find the insights useless — which would undermine the entire reason it joined.

### 29\.1 Implication — Non\-Platform Job Recording

This requires a feature not previously specified: **recording a job that did not originate from a platform booking.** It needs care to avoid contaminating other systems:

- The employee logs the job, service type, and vehicle, with photo documentation as normal
- It **counts** toward staff performance, demand patterns, duration prediction, and the business's own revenue view
- It carries **no platform payment** — no prepayment, no payout, no platform fee
- It must be **clearly distinguishable** in the data, so revenue reporting and payout reconciliation never confuse a cash walk\-in with a platform\-paid booking
- It should not appear in customer\-facing ratings, since no platform customer exists to leave one

The Architect should treat "job" and "booking" as distinct concepts from the start rather than assuming every job has a booking behind it — retrofitting that distinction after the schema assumes one\-to\-one would be a painful migration.

### 29\.2 Business Dashboard — Web and Mobile

Full management, reports, and accounting on **web**; incoming bookings, staff status, and availability on **mobile**. This matches how owners actually work — on\-site and moving during the day, at a desk for the analytical work.

### 29\.3 Empty State — Show Nearest Regardless of Distance

When no carwash is available nearby, the customer sees the nearest options anyway rather than an empty screen.

*One boundary to respect:* this must stay within the customer's own market (Section 16s) — a Bahrain customer should never be shown a UAE business, however near the border. "Nearest regardless of distance" means within\-market only.

**Returning customer home screen:** deliberately left open, to be decided later.

## 29\.4 What This Means for the Product

Following the go\-to\-market logic through changes several assumptions carried earlier in this document. Recorded here so the CEO plans against the real shape of the business rather than the marketplace framing it started with.

**Business tooling is the actual product.** Staff management, scheduling, job logging, and insights are what businesses pay for and what closes a sale. The customer booking marketplace matters, but it is not the thing generating revenue.

*This has direct implications for sequencing.* Several sections of this document assume the core booking loop is the natural first thing to build — an assumption formed before the SaaS\-first strategy was articulated. The CEO should weigh this explicitly when proposing a breakdown: the tooling businesses pay for may reasonably come before the marketplace they don't. Nothing here decides that; it flags that the earlier assumption deserves re\-examination rather than inheritance.

**SaaS\-only businesses are supported and expected.** A business can pay for the tooling without ever accepting platform bookings or appearing to customers. This may be a large share of early revenue, and forcing marketplace participation would block sales to businesses that only want the operational software. Some will switch bookings on later once they trust the platform — but that is a bonus, not the plan.

*Design implication:* marketplace listing is a **setting, not a requirement.** Business accounts, staff management, job logging, and insights must all work fully for a business that is invisible to customers.

**Revenue model unchanged.** Monthly base fees plus add\-ons from businesses, memberships from customers, no commission on bookings, free customer access. Free access maximises the demand Loop Labs can bring businesses, which makes the tooling more valuable — the pieces reinforce each other.

**Job logging is free; insights are paid.** Recording jobs — including walk\-ins and externally\-booked work — is never charged for. The analysis built on that data is the paid add\-on. Charging for the input would produce incomplete data, and incomplete data would make the insights inaccurate, which would destroy the value of the thing businesses actually pay for. Never charge for the input that makes your own product work.

## 30\. Competitive Position & Business Adoption

**The gap Loop Labs fills.** Carwash businesses in Bahrain and the UAE already use software — but that software only connects them to customers. It offers no operational insight, so owners manage staff, scheduling, and analysis manually. **Loop Labs is not another booking app; it is the operational layer nobody is providing.**

This is a stronger position than competing on marketplace demand, and it explains why the SaaS\-first strategy works: businesses aren't being asked to abandon what they have, they're being offered something they currently don't have at all.

**The realistic adoption path.** A business keeps its existing booking platform and adds Loop Labs for operations. Over time, as it sees what platform bookings are worth, it may move bookings across. This means **coexistence with competitors is the normal early state, not an edge case** — and it reframes external job logging (Section 29.1): its primary purpose is capturing jobs booked through *competitor platforms*, with walk\-ins secondary. Without it, a business's data would cover only the fraction of work that came through Loop Labs, and the insights would be worthless.

**Competitor integration — manual first.** Employees log external jobs manually. Automatic import from competitor platforms is worth exploring later, but adoption must never depend on access competitors have no incentive to grant.

**Displacement — let the data make the case.** Loop Labs shows the business what platform bookings earn versus externally\-sourced ones and lets the owner decide. Insights are the product; using them to demonstrate value is both honest and difficult to argue with. No pushy prompts to switch.

### 30\.1 Minimum Business Tooling

The four capabilities a business needs before it can genuinely run on Loop Labs:

1. **Staff list and shift scheduling** — add employees, set who works when
2. **Job logging with photos** — every wash recorded, including walk\-ins and competitor\-sourced jobs
3. **Services and pricing setup** — what they offer and what they charge
4. **Basic revenue view** — earnings today, this week, this month (free per Section 16p)

Everything else in the product builds on these.

### 30\.2 Pricing & Trial

**Base fee: not decided.** Requires market research into what comparable tools charge in the GCC — a task for the CEO before pricing is proposed.

**Free trial covering everything, add\-ons included.** A trial limited to the free tier would demonstrate nothing about the product businesses actually pay for. They need to experience the insights.

**Progressive insight value.** Simple statistics appear immediately — job counts, revenue, staff activity — with patterns and recommendations emerging as weeks of data accumulate. This sets honest expectations: an empty dashboard in week one would undermine the pitch before the product had a chance to prove itself.

*Note the tension worth watching:* the trial period must be long enough that meaningful insights have appeared before it ends. A trial that expires while the dashboard is still thin converts poorly. The CEO should set trial length against how long the data actually takes to become interesting, not against a conventional default.

## 31\. Insights — Detailed Specification

Expanding Section 27.1, since this is the product businesses actually pay for.

### Three categories of insight

**1\. Private — a business's own data.** Staff performance and speed, job durations, demand patterns, revenue, customer retention. Always available to the business about itself, never exposed to anyone else by default.

**2\. Public comparison — available to everyone.** Benchmarks built only from information already visible on the platform: **prices, service types offered, and ratings.** Any customer browsing the app can see these, so comparing them exposes nothing new. Available to every business with no consent required.

**3\. Opt\-in comparison — the contributing pool.** A business may **choose to contribute its private operational data** (job durations, demand patterns) to anonymised cross\-business benchmarks. Contribution is entirely voluntary.

**Reciprocity governs the pool.** Only businesses that contribute receive the richer benchmarks built from it. This makes the exchange fair and explicit — you see what others' data reveals because your data helps reveal it — and it prevents free\-riding that would otherwise collapse the pool. A business that declines still gets everything in categories 1 and 2.

**Why this resolves the earlier tension.** Mandatory contribution meant a business's commercially sensitive operating data fed a product its competitors use, without being asked. Restricting benchmarks to public data alone solved that but gutted the insight and removed the competitive moat. Opt\-in with reciprocity keeps both: businesses that see the value join and get comparisons no competitor platform can offer, and businesses uncomfortable sharing simply don't, losing only the comparative layer.

*Design requirements:* contribution must be genuinely informed (the business understands what it shares and what it gets), reversible (it can withdraw, though data already aggregated into historical benchmarks cannot be retrospectively unpicked), and anonymised such that no individual business is identifiable in any output — which reintroduces the **minimum\-sample rule** for this category: pool comparisons appear only when enough contributors exist that no single one can be inferred.

### Pool mechanics

**Access is determined by contribution, not by subscription.**

- **Contributing businesses** receive benchmarks built from all contributors' data, in addition to their own insights and public comparisons.
- **Non\-contributing businesses** receive their own data plus public comparisons only — other businesses' prices, service types, and ratings.

**Withdrawal.** A business may stop contributing at any time. Forward data is no longer shared; aggregates already computed stand, since retroactively unpicking historical benchmarks would degrade them for every other contributor. This must be stated plainly at the point of opting in, not discovered later.

**Minimum sample.** Pool comparisons appear only when enough contributors exist in a comparison set that no individual business could be inferred from the aggregate.

**Wider use of pooled data.** Contributed data may also power aggregated market reports that Loop Labs publishes or sells.

*This must be disclosed explicitly at the point of opt\-in* — in the consent itself, not buried in general terms. Wording along the lines of "your contributed data may also be used in aggregated market reports Loop Labs publishes or sells" costs nothing in terms of the option it preserves, and it is the difference between a business having agreed and a business having technically agreed.

The reasoning is practical rather than legalistic: broad, vague consent is weaker under most data frameworks and easier to challenge, and a business discovering an unexpected use of its data will not be reassured that the terms permitted it. Businesses that would object to this will object whenever they discover it — better at opt\-in, when the relationship survives it.

## 31a. Insights — Scope & Interaction

**Customer insights — aggregated retention and repeat patterns.** Businesses see what proportion of customers return and within what period, which services drive repeat business, and how retention is trending. Retention is where carwash profitability actually lives, and no owner can calculate it manually across hundreds of jobs.

*Two constraints:* it must be **aggregated**, not a per\-customer profile handed to businesses — that would raise PDPL problems and expose Loop Labs' customer relationships. And walk\-in jobs have no customer identity attached, so retention figures should be clear about what portion of activity they cover rather than silently reporting on a subset.

**Branch comparison.** For multi\-branch businesses, insights compare locations directly: which is fastest, busiest, most profitable, best rated. This is precisely the question a multi\-branch owner cannot answer alone, and it is one of the clearest cases for the add\-on paying for itself. Note this sits deliberately alongside the decision that customer\-facing ratings are combined across branches (Section 16dd) — publicly one reputation, internally full per\-branch visibility.

**Insights link to action.** An insight that identifies a problem offers the fix in the same place: "you're short\-staffed Saturday" comes with a way to adjust the schedule directly. An insight requiring the owner to navigate elsewhere and remember what it said usually goes unacted on — and insights that never lead to action do not renew a subscription. This connects the analysis layer to the scheduling and pricing tools rather than leaving them as separate parts of the product.

**Export — PDF and spreadsheet.** Owners share numbers with partners, accountants, and banks, particularly when seeking financing. Cheap to build, and it makes the tooling useful beyond the app itself. Deliberately not reserved for the accounting add\-on: export is a small feature that makes insights more valuable, and gating it would be a poor trade against adoption.

## 32\. App Experience Details

**Booking modification.** Customers can change the time, service, or vehicle of an existing booking up until the **1\-hour cutoff**, with the price adjusted accordingly. This aligns with the cancellation window (Section 23.7) and avoids forcing a cancel\-and\-rebook cycle for what is usually a small change.

*Implementation note:* a modification touches price, duration, capacity, and potentially employee assignment simultaneously — it is meaningfully harder than it appears, and effectively a re\-run of the booking logic against an existing record. Worth the Architect treating it as such rather than as a simple field edit.

**Saved payment methods.** Cards are stored **with the payment gateway, never by Loop Labs.** The platform holds only a token, so customers get one\-tap repeat booking while Loop Labs never touches card data — which keeps it out of scope for the most sensitive class of payment compliance and means a breach of your systems exposes no card details. Standard practice, and the right default given prepayment on every booking.

**Business setup — pre\-filled templates.** New businesses start from standard carwash services with suggested prices already populated, adjusting rather than building from an empty screen.

*This matters more than it sounds.* Setup friction is where SaaS trials die, and your target businesses are described as currently managing everything manually (Section 30) — an empty configuration screen is exactly where a non\-technical owner abandons the trial. The suggested prices also quietly serve a second purpose: they anchor pricing sensibly and give Loop Labs better early data for the benchmarking product (Section 31) than a field of wildly inconsistent self\-entered values would.

**Fleet accounts — not now, but don't block them.** Taxi firms, delivery companies, and car rental operators are high\-value recurring customers, but they need multi\-vehicle management and consolidated billing — a genuinely different product. Not built now; the Architect should simply avoid assumptions (one vehicle per customer, one payer per booking) that would make it a rewrite later. The multi\-vehicle booking support already specified (Section 16ee) is a reasonable foundation.

## 32a. Customer Experience Details

**Notification control — granular.** Customers choose which notification types they receive. Booking\-critical messages (confirmation, OTP) always send; optional ones like photo notifications at each job stage can be switched off individually. The failure this prevents is real: a single unwanted notification type, with only an all\-or\-nothing toggle available, leads customers to disable notifications entirely — and then they miss the ones that matter.

**Favourites.** Customers can save businesses they liked. Carwash choice is habitual — people return to whoever did a good job — and this directly supports the repeat booking behaviour that the retention insights (Section 31a) are built to measure and sell.

**Booking detail before confirming.** Price, ETA, rating, and **what the service actually includes**. The last is easy to overlook and matters most: "full detail" means different things at different businesses, and a customer who expected interior cleaning and didn't get it becomes a dispute, a bad review, and a refund request. Since businesses set their own prices against standardised service categories (Section 16f), the description of what's covered is what makes those categories comparable in practice.

**Connectivity handling — unambiguous state, safe retry.** Booking is the moment connectivity failure hurts most, because it involves payment. Two requirements: the customer must **never be left uncertain whether they were charged**, and retrying must **never create a duplicate booking or a double charge**.

*Implementation note:* this means booking creation and payment need idempotency — a retried request with the same identifier must return the original result rather than creating a second booking. This is a genuine engineering requirement rather than a UI concern, and it's cheap to build correctly upfront and painful to retrofit after the first customer is double\-charged.

## 33\. Data Rights, Moderation & Feedback

**Account deletion — anonymise, don't erase.** PDPL grants customers a right to deletion, but booking and payment records must be retained for financial and tax purposes. These genuinely conflict, and the resolution is to **strip the person from the record rather than destroy the record**\: name, phone, addresses, saved vehicles, and job photos are removed; the booking and payment history survives with no identifiable person attached.

*Flag for your advisor:* this is the standard approach and it satisfies both requirements in most jurisdictions, but whether it satisfies PDPL and UAE law specifically is a legal question, not a product one. It belongs alongside the open VAT and data\-residency questions (Sections 16aa, 20b) on the list for a real lawyer. Note also that anonymisation must be genuine — a booking history tied to a specific address and vehicle can re\-identify someone even without a name.

**Business data export.** Businesses can export their staff records, job history, and revenue data on request, including after cancelling.

*Why this is a growth feature, not just a compliance one:* lock\-in fear is a real objection when selling software to businesses that have never used any. A business confident it can leave with its data is more willing to commit in the first place — and given your adoption path involves businesses running Loop Labs alongside a competitor (Section 30), portability makes trying it feel low\-risk.

**Review moderation — automated filter plus dispute route.** Obvious abuse is caught automatically before a review publishes; anything more subjective goes through the existing dispute process to the founders (Section 16dd). This builds on mechanisms already decided rather than adding a new one. The reason a filter is warranted despite the extra work: businesses **cannot publicly respond** to reviews (Section 16u), so abusive content stays visible with no right of reply — which is a strong reason for a business to leave the platform entirely.

**Rating prompt — immediately after completion, with the after\-photo.** The customer is asked to rate when the experience is fresh and they're already looking at the result of the wash. This is the moment with the highest response rate, and rating volume is what makes both the public business rating and the internal per\-employee insights (Section 23.13) statistically meaningful rather than noise from a handful of responses.

## 34\. Pricing Changes, Access Control & Safety

**Price changes don't affect existing bookings.** Businesses adjust their prices freely at any time, but a booking already made is honoured at the price the customer agreed to. Since customers prepay (Section 16d), this is largely automatic — the payment is already taken — but it must also hold for modifications (Section 32): changing a booking recalculates against the **originally agreed prices**, not current ones.

**Business\-level customer blocking.** A business can block a specific customer from booking with it — for abuse, repeat no\-shows, or any reason it judges sufficient. The customer remains free to book elsewhere on the platform. This matters most for mobile service, where a business is sending its staff to that person's home and should not be compelled to.

**Platform\-wide bans.** The founders can ban a customer from the platform entirely for genuinely dangerous behaviour — threats, assault, fraud. Business\-level blocking handles ordinary problems; some behaviour warrants removal altogether, and a platform that sends workers into private homes has a real obligation not to keep routing them to someone dangerous. Bans are founder\-only, logged with attribution (Section 26) like any other consequential action.

**Staff emergency button.** The employee app includes an emergency alert: one tap sends the employee's live location, current job details, and customer information to **their business owner as primary responder**, with Loop Labs notified in parallel.

*Reasoning, since this was a judgement call:* mobile service is the differentiating feature and also the riskiest — an employee alone at a stranger's address is the most exposed anyone gets in this product. The mechanism is cheap because every input already exists (identity, live GPS, job details, customer record). It is also a sales feature: a business owner deciding whether to put staff on the platform will ask how they're protected.

*The obligation it creates:* a button that summons help must actually summon help. Routing to the business owner first is deliberate — they are closest to the employee, it is their staff member, and Loop Labs has no support team (Section 19b). The founders are notified in parallel rather than as first responders. What Loop Labs does on receiving an alert should be defined before this ships, not improvised during the first real incident.

## 35\. Assignment, Coverage & Mobile Service Reality

**Preferred employee requests.** A customer can request an employee they've had before. This is a partial exception to fully automatic assignment (Section 16g) and needs care in the details: what happens when the requested person is unavailable (fall back to normal assignment, don't fail the booking), whether requesting narrows availability enough to worsen the customer's ETA, and how it interacts with the ranked provider list. Customers still cannot *avoid* a specific employee, and still never see per\-employee ratings (Section 23.13) — this is about continuity with someone who did good work, not about picking from a leaderboard.

**Mid\-shift reassignment.** If the assigned employee becomes unavailable (illness, breakdown, marking themselves unavailable per Section 28), the system **automatically reassigns to another available employee at that business and notifies the customer.** Only when nobody is available does it become a business\-side cancellation with a full refund (Section 16x). This keeps a routine staffing problem from becoming a lost booking.

**Business\-defined service radius.** Businesses set how far they will travel for mobile service. Without this, ETA\-based ranking could route staff on journeys that lose money once travel time is counted — and the rational business response would be to disable mobile service entirely, removing the supply that differentiates the product. A business\-controlled radius keeps mobile viable for them.

**Service requirements — declared and surfaced.** Mobile washing needs water and power, and setups differ: some units are fully self\-contained, others need the customer's tap or an outlet. Businesses **declare what they provide and what they require**, and customers see those requirements before booking.

*Why structurally rather than in booking notes:* an unmet requirement means the employee travels, cannot work, files a cannot\-complete report (Section 28), and the outcome becomes a dispute over who pays for a wasted trip. Capturing it as structured data lets the system prevent the mismatch instead of adjudicating it afterward — and disputes are the thing that currently lands on the founders personally.

## 36\. Workforce Reality & Recurring Bookings

**Employee app needs more languages than the rest.** This is a deliberate exception to the English\-only decision (Section 16a). Carwash staff across Bahrain and the UAE are predominantly South Asian workers who may not read English confidently, so the **employee app supports additional languages** (Hindi, Urdu, Bengali or similar, based on the actual workforce) even while the customer and business apps remain English\-only.

*Why this is not a nice\-to\-have:* the employee app is where GPS tracking, photo capture, job status, and the cannot\-complete flow all happen. A worker who cannot read their own job screen cannot follow the process — which means missing photos, wrong statuses, and corrupted data feeding the insights businesses are paying for. The business will notice this immediately and blame the platform. The whole SaaS proposition depends on staff actually being able to use it.

*Design note:* pairing translation with heavy use of icons, photos, and colour would make the app usable even for workers with limited literacy in any language. Worth the UX/UI agent treating low\-text design as a requirement rather than a preference.

**Tips go to the business to distribute.** Customers can tip, and the tip is paid to the business along with the booking amount, with the owner responsible for passing it to the employee.

*Trade\-off worth naming:* this keeps the payment model consistent — the platform pays businesses, never individuals (Section 16m) — and avoids building individual payouts. The cost is that the employee depends on the owner passing it on, which Loop Labs cannot enforce. Showing the tip amount clearly in the employee's own app (alongside their jobs and hours, Section 16n) at least makes it visible to them rather than invisible.

**Employee removal — history stays, person anonymised.** When a business removes an employee, the job history, durations, and ratings remain so the business's operational data and insights stay accurate, while the individual's personal details are removed. This mirrors the customer deletion approach (Section 33) and for the same reason: the business needs its historical record intact, and the individual should not have their personal data retained indefinitely after leaving.

**Recurring bookings pause on change.** If a business raises its price or stops offering a service that a customer has booked recurringly, the recurring booking **pauses and the customer is notified to re\-confirm** rather than silently continuing at a new price or quietly failing. Surprise charges are among the fastest ways to lose a customer's trust, and a recurring arrangement that breaks without explanation is nearly as bad.

## 36a. Price Locking — Clarified

The rule from Section 34 is absolute: **businesses cannot change the price of an appointment already booked.** This section resolves how that applies to recurring bookings, where "already booked" is ambiguous.

**Price locks per occurrence, at the point it is charged.** A recurring weekly booking is not one locked price forever — it is a series of individual appointments, each of which locks its price when it is confirmed and charged.

The practical consequence:

- The **next scheduled occurrence** is already booked and paid. Its price cannot change, regardless of what the business does to its pricing.
- **Later occurrences** are not yet booked. If the business changes its price before they are charged, that change would apply to them.
- When that happens, the recurring series **pauses and the customer is notified to re\-confirm** at the new price (Section 36). Nothing is charged at a price the customer has not agreed to, and nothing silently continues.

**Why per\-occurrence rather than locking the whole series:** locking a series indefinitely would leave a business honouring a price from a year ago with no way out, which would make businesses reluctant to offer recurring bookings at all. Per\-occurrence locking keeps the customer fully protected — no charge they didn't agree to, ever — while letting pricing stay current over time.

The same logic applies if a business **stops offering** a service entirely: the already\-booked occurrence stands, and the series pauses with the customer notified.

## 37\. Payment Risk, Seasonality & Storage

**Chargebacks — platform absorbs, recovers from the business.** When a customer disputes a charge with their bank, Loop Labs covers it immediately and recovers the amount from the business's next payout. The before/after photos (Section 16v) are the evidence used to contest the dispute — which is a second, unplanned benefit of requiring them.

*Why this arrangement:* daily payouts (Section 16e) mean the money has already left before any dispute arrives, so someone must hold that risk in the gap. The platform is better placed than a small business to absorb the timing, while the business remains ultimately responsible for its own transaction. Worth watching as a fraud vector — a pattern of chargebacks against one business, or from one customer, should surface rather than being quietly absorbed each time.

**Ramadan and seasonal patterns — manual for now.** Businesses adjust their normal availability schedule rather than switching to a stored seasonal profile.

*One thing to carry forward regardless:* the demand\-forecasting model (Section 31) must not treat Ramadan as an anomaly to smooth away. Operating hours and demand shift dramatically across both markets simultaneously and predictably every year — a model that flags it as noise will produce bad staffing recommendations at exactly the busiest evening periods. Data/ML should treat known seasonal shifts as signal.

**Temporary closure — explicit pause.** A business can pause its listing for a holiday, equipment failure, or staff shortage: it stops receiving new bookings while remaining subscribed, and must **explicitly resolve any bookings already made** rather than leaving customers stranded. Simply clearing availability would prevent new bookings but say nothing about existing ones — which is precisely the case that produces a customer waiting for someone who is never coming.

**Photo retention — full quality recent, compressed long\-term.** Photos stay at full quality while disputes are realistically possible, then compress to lower resolution for indefinite storage. This preserves the permanent customer\-facing history (Section 16w) and long\-term dispute evidence at a fraction of the cost. With two or more photos on every job across every business, this is one of the few storage costs in the system that grows without any natural ceiling.

## 38\. Job Execution & Documentation

**Guided photo capture with required angles.** The employee app prompts for specific shots — front, back, sides — and rejects obviously unusable images (too dark, too blurry, obscured). This is deliberate rigour rather than over\-engineering: photos carry three separate loads in this system. They trigger job status transitions (Section 16w), they are the evidence in damage disputes (Section 16v), and they are what contests a bank chargeback (Section 37). All three fail simultaneously if an employee submits one dark photo of a bumper. Guided capture removes that from individual judgement, and it also suits the low\-literacy workforce reality (Section 36) — a prompt showing which angle to shoot needs no reading.

**Multi\-vehicle jobs — multiple employees can share a booking.** A booking covering several vehicles can be worked by more than one employee in parallel, rather than assigned to a single person.

*Consequences the Architect needs to design for, since this is more complex than single assignment:*

- **Per\-vehicle documentation.** Before/after photos and status belong to each *vehicle*, not to the booking as a whole. A dispute about one car must be resolvable without ambiguity about which vehicle the photos show.
- **Attribution for insights.** Per\-employee performance data (Sections 23.13, 31) depends on knowing who did what. A shared booking must record which employee handled which vehicle, or shared jobs will quietly corrupt the per\-employee metrics businesses are paying to see.
- **Duration modelling.** The job\-duration prediction (Section 16w) must understand that three cars worked in parallel by three people is not the same as three cars worked sequentially by one — otherwise ETA estimates degrade whenever a shared job occurs.
- **Completion.** The booking completes only when every vehicle is done; partial completion needs a defined state.

**Customer first\-run experience.** Deliberately left open, to be decided later — alongside the returning\-customer home screen (Section 29.3).

**Accessibility — not a priority now.** No specific accessibility work beyond framework defaults at this stage.

*Worth revisiting at some point:* accessibility work is considerably cheaper built in than retrofitted, and several of its elements — scalable text, strong contrast, large tap targets — would also serve the low\-literacy employee workforce this product depends on. Not a change to the decision, just a note that the two needs overlap more than they might appear to.

## 39\. In\-Progress Additions

While a job is in progress, work can be added — and **either side can propose it, with the other side confirming.**

**Bidirectional proposal, mutual confirmation.**

- The **customer** proposes from their live "service in progress" status page; the **employee confirms** from their end.
- The **employee** proposes from the job screen; the **customer confirms** from theirs.

Nothing is added, performed, or charged without both parties agreeing. This is the safeguard that makes employee\-initiated proposals acceptable: the customer confirms deliberately in the app rather than being pressured face to face by someone already at their home. That confirmation should stay an explicit action — never a default\-yes, and never a verbal agreement recorded by the employee on the customer's behalf.

**Two kinds of addition.**

1. **Add\-ons to the current vehicle** — an interior clean added to a booked exterior wash.
2. **An entire additional vehicle** — a second car washed during the same visit, as a full service in its own right, provided the schedule allows.

The second is more than an upsell: it effectively appends a new job to an in\-progress visit, and needs treating as such in scheduling, documentation, and pricing rather than as a modifier on the original booking.

**Only schedule\-compatible additions are offered.** Whichever side proposes, the app offers only services the assigned employee genuinely has time to complete before their next commitment. A customer never sees an option that would make the following booking late, and an employee cannot propose one — so nobody has to refuse anyone, and the constraint is handled invisibly rather than becoming an awkward conversation.

*Implementation note:* this is a live scheduling check evaluating remaining time against the employee's next booking and each candidate service's declared duration (Section 16ee), recalculated as the job progresses. It is not a static service menu.

**Documentation.** Added work is documented like any other: before/after photos for an added service, and full per\-vehicle documentation (Section 38) for an added vehicle. Without this, work the customer paid extra for would have no evidence it was performed — a hole in the photo\-as\-evidence chain (Sections 16v, 37) exactly where money changed hands.

**Payment on confirmation.** The addition is charged to the customer's saved card (Section 32) once both sides have confirmed, consistent with prepayment everywhere else and capturing payment before the extra work begins.

## 39a. Availability & Staffing Reality

**Booking horizon — a few weeks ahead.** Long enough for normal planning, short enough that availability and pricing remain meaningful. Longer\-term repeat arrangements are served by recurring bookings (Section 16ee) rather than by distant one\-off bookings.

**Staff availability overrides business hours.** Only time slots with an employee actually scheduled are bookable. Published business hours become display information rather than booking capacity. A business open 9am–9pm with staff until 5pm shows bookable slots until 5pm — because a booking nobody can fulfil is considerably worse than a slot not being offered, and capacity is already enforced automatically (Section 16x).

**Staff transfer between branches.** The owner can reassign employees between branches, with their job history and performance record following them. Real businesses move people to cover shortages constantly; blocking it would push that coordination off\-platform and leave the system's view of who works where permanently inaccurate.

## 39b. Addition Pricing & Future Dynamic Pricing

**Additions use the current price.** An addition is charged at whatever the business has listed **at the moment it is proposed and confirmed** — not the price list from when the original booking was made. The customer sees a price and agrees to it in that moment, so nothing is hidden and no expectation is broken. Price\-locking (Section 36a) protects what was actually booked; an addition is newly agreed work.

### Future direction — occupancy\-based dynamic pricing

Planned for a later release, **not part of the first implementation.** This supersedes the note in Section 16v that dynamic pricing applies only to memberships — it will eventually apply to bookings too, but in a specific and deliberately customer\-friendly form.

**How it works:** when a business has low occupancy, its prices fall toward a floor **that the business itself sets**. A provider running at capacity charges its normal rate; a provider sitting idle becomes cheaper, and customers see the better price.

**Why this shape matters.** It flexes *downward* from a normal price rather than upward from a baseline. Surge pricing makes customers feel penalised for needing something at a busy moment; occupancy\-based discounting makes them feel rewarded for flexibility, while the business fills time that would otherwise earn nothing. The business controls its own floor, so it can never be pushed below what it considers viable — which also means Loop Labs is not setting anyone's prices, only providing the mechanism.

**What it needs, to be designed for now rather than retrofitted:**

- **Occupancy as a live signal.** The system already tracks capacity and staff availability (Sections 16x, 39a); dynamic pricing turns that into a pricing input.
- **A business\-configurable floor** per service, alongside the normal price.
- **Price transparency at booking.** The customer must see clearly what they are paying and, ideally, that they are getting a reduced rate — a discount only builds goodwill if the customer knows they received one.
- **Price locking still holds absolutely.** A booking confirmed at a discounted price stays at that price (Section 36a), regardless of occupancy changing afterward.

**Open question for when this is built:** provider ranking is currently pure ETA (Section 16f). Once prices vary by occupancy, a slightly slower but noticeably cheaper provider may be the better choice for many customers — so whether price enters the ranking, appears as a filter, or is simply displayed will need deciding then.

## 39c. Confirmation Mechanics

**Nothing added is ever performed or charged without confirmation.** There is no goodwill\-unpaid path and no proceed\-anyway option. An unconfirmed addition simply does not happen.

### The escalation chain

When a customer requests an addition from the in\-progress service page:

1. **The worker is prompted** — three notifications, followed by an automated call if still unanswered. The escalation reflects the context: an employee mid\-wash has wet hands and may not see a single silent notification.
2. **If the worker does not respond, it escalates to the business** — the provider receives a notification to confirm and accept on the worker's behalf, with a **3\-minute limit**.
3. **If the business does not respond either, the request is cancelled** and the customer is told plainly: no answer was received from the business, so the request has been cancelled — with a button to **re\-request the same service** in one tap.

The wording matters. The customer is told what actually happened rather than being left with a request that silently expired, and re\-requesting costs them one tap rather than navigating the flow again.

### On confirmation

- The customer **pays the extra amount**.
- The **booking information is extended** to include the added work.
- The worker **may only begin the additional service once payment has completed.** Payment is the gate on starting, not a step settled afterward.

This keeps the additions flow consistent with prepayment everywhere else, and it means no employee ever performs work that hasn't been paid for.

### Schedule locking

**The moment a customer requests an addition or a booking that fits the schedule, that schedule slot is blocked** — held until the request is either confirmed, refused, or cancelled.

*Why this matters:* without it, the same time could be offered to another customer while a request is pending, and a confirmation arriving seconds later would have nothing to confirm into. Holding the slot is what makes "only schedule\-compatible additions are offered" (Section 39) actually true rather than true\-at\-the\-moment\-of\-asking.

*Implementation notes:* the lock must release on every terminal outcome — confirmation, refusal, cancellation, and the escalation chain timing out — with no path that leaves a slot held indefinitely. Because the escalation has hard time limits (three prompts, a call, then 3 minutes at the business level), the maximum hold duration is bounded by design rather than open\-ended.

**Added vehicles are separate bookings, linked to the visit.** An entire extra car added during a visit creates its **own booking** — its own vehicle, photos, price, rating, and payout record — linked to the original so the employee sees a single trip.

*Reasoning:* a dispute about the second car should be resolvable without entangling the first, per\-vehicle documentation stays unambiguous (Section 38), and payout reconciliation remains clean. This was a judgement call rather than an explicit decision, and is straightforward to reverse if the founders prefer otherwise.

## 40\. Memberships — Two Products

This supersedes Section 16o entirely. There are **two distinct membership products** with different owners, economics, and rules.

### 40\.1 Business Memberships — Bronze, Silver, Gold

**Owned and defined by each business.** A business creates its own tiers, chooses which of its services are included in each, and funds the discount from its own margin in exchange for guaranteed recurring revenue and customer loyalty.

**Tiers and discounts:** Bronze 15%, Silver 20%, Gold 25% off the business's normal prices.

**Example (Silver):** four normal washes priced at 30 individually. Silver applies 20%, so the customer pays 24. The business receives 24 **minus Loop Labs' commission**. The business is funding the discount, which is coherent because the business chose to offer the tier and is buying committed repeat custom with it.

**How customers use them:**

- Book all wash dates and times upfront when purchasing, **or**
- Book some now and redeem the remaining washes later, **or**
- Buy the membership without booking anything at all, redeeming entirely at their own pace.

That last case matters technically: a membership is a **purchased entitlement that exists independently of any booking**, not a bundle of pre\-created bookings. The data model must treat it that way from the start.

### 40\.2 Loop Labs Custom Membership

**Owned and defined by Loop Labs.** The customer chooses any services they want from any provider, and books under the same rules as above.

**Economics:** providers grant Loop Labs a **5% discount** on the normal price of any service they permit into this membership. Loop Labs offers customers a **5% discount** on those services. Providers choose which of their services may be included.

**Availability:** only services a provider has explicitly opted into appear in this membership. It is opt\-in per service, not automatic.

### 40\.3 Commission

Commission applies to **memberships only**; standard bookings remain commission\-free. This is the first step rather than a permanent boundary — extending commission to bookings later stays open if the numbers call for it.

### 40\.4 Membership Refunds

If a business leaves the platform or is suspended, a customer holding unredeemed washes chooses whether the remaining value is refunded to their **in\-app wallet** or to their **original payment method**. Loop Labs sold the membership and therefore carries the obligation.

### 40\.5 Loop Labs Custom — Margin Resolved

The provider grants Loop Labs **5% plus commission**. The customer receives the 5% discount; Loop Labs retains the commission as margin. The customer\-facing offer is unchanged, and the arithmetic now closes.

### 40\.6 Stacking

A customer may hold a business membership and a Loop Labs Custom membership simultaneously, but **the two discounts never combine on a single wash.** Each wash draws from one entitlement or the other. Without this rule a provider would fund both discounts on the same job.

### 40\.7 Unredeemed Washes

Washes expire at the end of the period with no refund, consistent with Section 16p. The business held capacity for them, and an accumulating balance of owed washes would become a growing liability.

### 40\.8 Membership Liabilities

**Business departure or suspension.** If a business leaves or is suspended while customers hold unredeemed washes from its memberships, Loop Labs refunds those customers immediately (to wallet or original payment method, their choice — Section 40.4) and **recovers the amount from the business's wallet, going negative if required** (Sections 41.1, 41.2). The business took payment for those washes, so the business bears the cost; Loop Labs fronts the customer so they are never left waiting on a dispute they have no part in.

**Tier changes are not retroactive.** A business may change or discontinue a membership tier at any time, but **existing members keep the terms they purchased until their period ends.** Changes apply to new purchases only. This follows the same principle as price\-locking (Section 36a): what someone has already paid for cannot be altered underneath them.

**Open item — prepaid float.** Memberships are paid to Loop Labs upfront while businesses are credited only as washes are redeemed, so Loop Labs holds unredeemed membership money, potentially for months. This is **flagged as needing modelling** rather than decided.

Two things make it worth modelling properly. It is a genuine cash\-flow advantage — money held before work is performed, with unredeemed washes expiring in Loop Labs' favour (Section 40.7). It is also precisely the kind of held customer money that sharpens the licensing question in Section 41.1: prepaid balances owed to customers are closer to stored value than a payment passing straight through. The commercial upside and the regulatory exposure come from the same fact, and should be assessed together rather than separately.

## 41\. The Wallet Model — Replacing Daily Payouts

**This supersedes the daily payout model in Section 16e.** Businesses are not paid on a fixed daily cycle.

**How it works.** Loop Labs collects payment on the provider's behalf. Each business has a **wallet** showing its current balance, net of commission and the tax on that commission. The business either **requests a transfer on demand**, or **sets transfer dates in advance** for automatic withdrawal.

**Deductions.** The business receives its balance minus Loop Labs' commission and minus the revenue tax applying to that commission.

**Two wallets exist in the system.** The business wallet described here, and the customer wallet (Section 40.4) holding membership refunds and credits. They serve different purposes and should not be conflated in the data model, but both represent money Loop Labs holds on someone else's behalf.

**Knock\-on effects of this change:**

- **Chargebacks** (Section 37) are now recovered from the business's wallet balance rather than deducted from a next\-day payout. This is actually cleaner — the balance is already held, so recovery does not depend on future earnings.
- **Membership payouts** resolve naturally: a business is credited as each membership wash is redeemed and completed, not when the membership is sold. Loop Labs never pays for work that has not been performed.
- **Business offboarding** (Section 16i) needs a defined settlement: a departing business's remaining wallet balance must be paid out, and any open chargeback exposure resolved, before the account closes.

### 41\.1 Wallet Rules & Regulatory Position

**Decision: build the wallet; treat licensing as a later problem.** Recorded as an explicit founder decision rather than an oversight.

**The risk, stated once.** Holding balances on behalf of businesses and customers is legally distinct from processing a payment and passing it through. In Bahrain and the UAE this can require payment service provider licensing, segregated client accounts, and central bank authorisation. If that proves to be the case after the platform is built around held balances, the correction is a payment architecture rebuild rather than an adjustment. This remains the highest\-consequence open item alongside VAT (Section 16aa) and data residency (Section 20b).

**What reduces the exposure, and is already chosen:**

- **No customer top\-ups.** The customer wallet receives money only from refunds, cancellation credits, and membership settlements — never from a customer loading funds. Customer stored value attracts the most regulatory attention, and this avoids it entirely.
- The business wallet remains the larger and longer\-held balance. Encouraging businesses to set scheduled automatic transfers (Section 41) keeps balances short\-lived, which is worth doing for its own sake.

**Withdrawal rules.** A minimum balance threshold applies before withdrawal, to limit transfer fees. No holding period against chargebacks.

**Consequence requiring a decision:** with no chargeback hold, a business can withdraw its full balance before a chargeback arrives — and chargebacks can land weeks after a job. Section 37 assumes recovery from the wallet balance, which may then be empty. The system needs a defined answer: most likely a **negative wallet balance** carried against future earnings, recovered as the business earns again. Without that, an unrecoverable chargeback becomes a direct loss to Loop Labs every time it happens after a withdrawal — and a predictable one for anyone who notices.

**Commission tax.** The tax on Loop Labs' commission is borne by the business and deducted from its wallet balance alongside the commission itself. This must be **shown as a distinct line** in the wallet, not folded into the commission figure — an unexplained deduction reads as a hidden fee and is exactly the kind of thing that erodes trust in a platform holding your money. The correct treatment may be prescribed by law rather than chosen, so confirm it with an accountant alongside the VAT question.

## 41\.2 Security Deposit & Chargeback Protection

**A security deposit is taken at initial setup and held for the contract term.** Collected as part of the setup fee, it exists specifically as a buffer against chargebacks and other amounts a business ends up owing.

**How the protection works:**

1. A chargeback is recovered from the business's **wallet balance** first.
2. If the wallet is empty or insufficient, the balance goes **negative**, and future earnings pay it down before anything becomes withdrawable again.
3. The **deposit is the limit.** A business continues operating while negative, since earnings are how the debt clears — but once the negative balance reaches the deposit amount, the business **stops operating** until it is settled.

This is a genuinely good structure. It lets a business trade its way out of a small debt rather than being suspended the moment a chargeback lands, while capping Loop Labs' exposure at a known amount decided upfront rather than an open\-ended one.

**Why the buffer is needed at all — chargeback timing.** A chargeback can arrive **months after the job**. Card scheme dispute windows commonly extend to around 120 days from the transaction, with some categories longer. A wash completed today can be reversed in the autumn, long after the business withdrew the money and forgot the job existed. Exact windows and reason codes are defined by the chosen payment gateway and should be obtained **in writing during gateway selection**, since they determine precisely how long the platform carries exposure — and therefore how the deposit should be sized.

**Deposit sizing.** Should be informed by realistic chargeback exposure per business rather than picked arbitrarily: roughly, the value of jobs a business might complete and withdraw within the dispute window. Too small and it protects nothing; too large and it becomes a barrier to signing businesses up.

**Settlement at contract end.** The deposit is returned when the contract ends, less anything owed. Business offboarding (Section 41) must therefore hold the deposit until the full dispute window has passed on the business's final jobs — releasing it immediately would reopen exactly the exposure the deposit exists to close.

## 41\.3 Commercial Terms

**Contract shape.** Priced and presented as an **annual term**, with a business able to exit early on **30 days notice**. In practical terms this is a rolling contract at an annual price — low commitment risk for the business, and it should be described honestly as such rather than implying twelve\-month lock\-in.

**Deposit timing and framing.** The deposit is collected **before the trial begins**, and is **fully refundable if the business cancels during the trial**.

This should be sold as exactly that — "a refundable deposit, returned in full if you leave during the trial" — and **not as a free trial with a deposit attached.** A business that hears "free trial" and then encounters a payment request at signup experiences a bait\-and\-switch at the worst possible moment, with a product they haven't yet seen work. The honest framing keeps the filtering benefit (unserious signups drop out) without the credibility cost.

*Tension worth monitoring:* Sections 30 and 30.2 establish that target businesses are often new to software of this kind, that setup friction is where trials die, and that the insights need weeks of data before they impress. Money upfront works against all three. The counter\-argument is real — deposits and annual terms are ordinary commercial practice in the GCC, and a business unwilling to place a refundable deposit was unlikely to convert. This is a judgement call, not an error, but **early trial\-to\-paid conversion should be watched closely**\: if signups stall at the deposit step, that is the first thing to change.

**Deposit applies to all businesses, including SaaS\-only.** For businesses taking platform bookings it covers chargeback exposure. For SaaS\-only businesses (Section 29.4), which take no customer payments and therefore generate no chargebacks, it covers **unpaid subscription fees** — a genuine risk with or without bookings.

The deposit is therefore best understood as **general credit protection**, not a chargeback\-specific mechanism. That framing also keeps the terms uniform and simple to explain, which has its own value.

**Chronic problems.** A business that repeatedly exhausts its deposit is **reviewed by the founders**, who either require a larger deposit or end the relationship. Repeated chargebacks generally indicate either fraud or genuinely poor service, and both warrant a decision rather than an indefinite cycle of automatic suspension and settlement.

## 42\. Legal Structure & Consent

**Contracting party — the business, not Loop Labs.** The business contracts with the customer for the wash; Loop Labs is an intermediary that facilitates discovery, booking, and payment collection on the business's behalf.

This is consistent with the rest of the design and should stay that way: businesses vet their own staff (Section 16cc), bear damage liability, manage their own employees, and set their own prices. It also means Loop Labs is not the service provider and does not carry liability for the quality or conduct of every wash — which would be an untenable position across hundreds of independent businesses.

*Where it must be visible:* the customer\-facing terms need to state this plainly. A customer who believes they contracted with Loop Labs and later discovers otherwise, mid\-complaint, is a trust problem and potentially a legal one.

**Revenue recognition — memberships are a liability until redeemed.** Money received for a membership is not revenue; it is an obligation to deliver future washes. Only Loop Labs' **commission** is revenue, recognised as each wash is redeemed and performed.

This is correct accounting and it clarifies the float question in Section 40.8: the unredeemed balance is money owed, not money earned. Confirm the exact treatment with an accountant alongside the VAT question — it also bears directly on the licensing position in Section 41.1, since prepaid obligations to customers are precisely what regulators examine.

**Employee consent obtained directly in\-app.** Employees consent to GPS tracking and performance monitoring **within the app at signup**, in addition to being informed by their employer.

*Why this matters:* consent obtained solely through an employer is legally weaker, because it is given under employment pressure — an employee asked by their boss to agree is not freely consenting in the way PDPL contemplates. Obtaining it directly, in the app they will use, in a language they read (Section 36), is a materially stronger position. Employee location tracking is among the more sensitive areas of data protection law, and it sits at the centre of this product rather than at its edges.

## 42a. Data Integrity & Incentive Design

**Externally\-logged jobs are excluded from all shared systems.** They count fully in the business's **own** insights — staff performance, revenue, demand patterns — which is what the business pays for and what makes the SaaS proposition work (Section 30). They never feed the **platform\-wide duration model**, the **benchmark pool**, or future occupancy\-based pricing.

*Why this matters:* external jobs are self\-reported and unverified. Allowing them into shared systems would let one business's inaccurate or invented data corrupt the ETA predictions every customer sees, the benchmarks other businesses paid for, and eventually the pricing mechanism. The split keeps complete data where it belongs (the business's own view) and verified data where it must be (anything shared).

**Two duration models, deliberately.**

- **Platform ETA model** — trained only on platform bookings, since that is what it predicts. Verified, complete, and safe to expose to customers.
- **Business\-internal estimates** — trained on all of a business's jobs including walk\-ins, used for the business's own scheduling and analytics.

An employee working mostly walk\-ins therefore has thin *platform* history, which is honest rather than a gap — the platform only needs to predict what it schedules.

**Photos on externally\-logged jobs — business\-level setting.** Each owner chooses whether staff must attach photos to logged jobs.

*Reasoning:* the three purposes photos serve on platform bookings do not apply here. There is no platform payment, so no chargeback to contest (Section 37); no platform customer, so no platform dispute; and no live job\-status flow to trigger (Section 16w), since a logged job is a record created after the fact. What photos would give is the business's own quality tracking and evidence in its own walk\-in disputes — real value, but value to the business rather than to Loop Labs. So the business decides, and Loop Labs adds no friction to the feature its adoption depends on.

### 42b. Incentive Design in Metrics

**Speed is never shown alone.** Employee speed is always presented alongside quality signals — **customer ratings on that employee's jobs** and **complaints or disputes raised against them**. An employee who is fast and well\-rated reads as good; one who is fast and poorly\-rated does not.

*This is not cosmetic.* A metric that rewards speed in isolation produces rushing, and rushing has a second\-order consequence unique to this system: the duration model learns from actual completion times, so systematically rushed jobs teach the model that washes take less time than they really do. ETAs then become unrealistic platform\-wide, customers are told providers will arrive sooner than they can, and the ranking that depends on honest durations degrades. The incentive design protects the model, not just the workers.

**Speed is withheld until quality data exists.** Ratings and complaints are both rare per individual, so many employees will have neither for weeks. Rather than showing an unpaired speed figure in the meantime, **the speed metric appears only once there is enough quality signal to pair it with.** Showing it early with a caveat would recreate exactly the rushing incentive this design exists to prevent — caveats do not change behaviour, visible metrics do.

**Accepted and not defended against:** businesses asking customers for high ratings in person, and businesses logging inaccurate walk\-in jobs. The first affects all businesses roughly equally and cannot be prevented; the second now only misleads the business itself, since external jobs no longer reach shared systems.

**Deferred:** whether businesses might move customers off\-platform using contact details they receive. The no\-commission model means they gain nothing by doing so today, but membership commission (Section 40.3) does create an incentive worth revisiting.

## 42c. Support Bot

An AI support bot is the customer's first point of contact, since there is no support team (Section 19b). **Customers first; businesses and employees possibly later** — business support is likely the higher\-volume need eventually, given owners new to software (Section 30).

**Authority — executes entitlements, escalates judgement.** This is the governing line, and it resolves what would otherwise be a contradiction between "can take actions" and "never commits to outcomes":

- **Executes automatically** what the rules already grant the customer: cancelling within the window, rescheduling, applying a refund the rules mandate (such as a business\-side cancellation, Section 16x), redeeming a membership wash.
- **Never decides** anything discretionary: exceptions to policy, goodwill gestures, disputed outcomes, "I'm unhappy, refund me" where the rules specify credit only. It explains what the policy is and escalates.

The bot may state rules; it may never make a promise. A commitment from the bot is one a customer will reasonably hold Loop Labs to, and the cost of a single wrong promise exceeds the time it saved.

**Rules come from a single source, not from the model.** The bot reads policy from one authoritative source rather than having rules embedded in its instructions or learned. Three consequences, all necessary given how intricate these rules are: a policy change updates the bot automatically, the bot cannot invent or misremember terms, and the bot can never contradict what the app itself displays.

**Data access — a product feature, not an agent exception.** The bot sees the booking, payment, and membership data of **the specific customer it is speaking to**, strictly scoped to that person.

*This does not breach Section 24f.* That rule governs the **development agents** building the platform — Backend, Data/ML, SRE — who have no legitimate need for customer records. The support bot is a **product feature acting on behalf of a customer, on that customer's own data**, which is the same basis on which the customer sees it themselves in the app. The distinction to preserve: development agents never see customer data; the bot sees only the data of whoever it is currently helping.

**Escalation.** Anything the bot cannot resolve goes to the founders' admin dashboard **with the full conversation attached**, so the founders arrive with context rather than asking the customer to explain again.

## 42d. Operational Scaling & Transparency

**Business approval automates once patterns are clear.** Founders approve manually at first; as the checks that matter become obvious, the process becomes fully automatic with spot checks.

*Worth watching:* manual approval was chosen originally as a quality gate (Section 16a). Full automation removes that gate, so what the automated checks actually verify — licence validity, duplicate detection, plausible details — determines whether quality is genuinely preserved or merely assumed. Automate when the patterns are understood, not when the volume becomes annoying.

**Duplicate detection — flag, don't block.** Matching addresses, licence numbers, bank details, or phone numbers across registrations are flagged for founder review rather than rejected. Shared premises are genuinely common and blocking them would reject legitimate businesses; the flag catches the case where one operator is running multiple accounts to game ratings or deposits.

**Rules surface at the moment they apply.** Cancellation terms appear when cancelling; membership expiry when purchasing; the dispatch fee before dispatch; credit\-not\-refund when the credit is issued.

*Why this is not optional:* the rules in this product are genuinely intricate — credit rather than cash refunds, no\-show fees, cancellation\-after\-dispatch charges, expiring membership washes, per\-occurrence price locking. Every one of them is defensible, and every one is a surprise if first encountered at the moment it costs someone money. Terms and conditions satisfy the legal requirement and change nobody's understanding. Surfacing each rule at its decision point is what makes the difference between a customer who feels informed and one who feels cheated — and it directly reduces the disputes that land on the founders.

## 42e. Founder\-Led Operations, Early On

**Founders handle business support and onboarding personally at first.** Businesses are paying customers, new to software of this kind, and few in number early on. A human matters more here than it does for consumers, and the support bot extends to businesses only when the same questions start repeating.

**Onboarding is founder\-led deliberately.** Walking each business through services, staff, shifts, pricing, and payment details does not scale — and should not, at this stage. It is how the founders learn exactly where people get stuck, which is what tells them what to automate and what the templates (Section 32) need to cover. Automating onboarding before understanding the friction would automate the wrong things.

## 42f. Validation Status — Honest Assessment

The strategy in Sections 29 and 30 rests on two claims. Both are **plausible and currently unverified**, and this is recorded plainly so it is not mistaken for settled fact.

**Claim 1 — existing software offers no operational insight.** Confidence is described as fair, but competitor products have not been examined closely. The entire positioning depends on this gap being real: if competitors already provide decent insights, Loop Labs is a better version of an existing category rather than the only entrant in a new one, which changes the pitch, the pricing, and the urgency.

*Action:* a competitor teardown — what existing tools genuinely offer businesses — is a natural early CEO task, and it either confirms the wedge or reshapes it before anything is built around it.

**Claim 2 — businesses will pay for this.** The evidence is that businesses *liked the idea when described.* That is the softest form of validation available: conversational agreement about something hypothetical and free. The gap between it and the actual commercial proposition — a monthly fee, a **refundable deposit paid before the trial**, and an **annual term** (Section 41.3) — is wide, and this product's terms make it wider than typical.

*The asset that de\-risks this:* the founders have **specific businesses ready to start.** That is materially stronger than most pre\-launch positions, and it is also the validation instrument. Taking the real proposition to three of them — actual price, actual deposit, actual terms — establishes whether the interest survives contact with money. It costs a conversation rather than a build.

**Why this belongs in the charter.** Fifteen agents and a substantial platform are about to be built on these two assumptions. Neither is unreasonable, and neither is confirmed. The cost of testing them now is a few conversations; the cost of discovering a problem after launch is the whole thing. This is not a recommendation to delay — it is a note that the cheapest available risk reduction has not yet been taken.

## 42g. Two Founders Operating Concurrently

Extending Section 26, which established authority but not concurrency.

**Both founders may work with the CEO simultaneously**, in separate conversations drawing on the same charter, memory, and sprint state. Decisions either founder makes are written to shared memory immediately (Section 17c), so neither is ever working from a stale picture.

**Live awareness, bounded.** The CEO tells each founder what the other is doing **when it affects what they are doing right now** — "your brother approved the payment change you are currently reviewing." Routine actions wait for the session\-opening brief rather than interrupting. Without the bound, two concurrent founders would generate a constant stream of notifications about each other.

**Session brief includes the other founder's activity.** The four\-line brief (Section 22a) covers what the other founder approved or directed since this founder last checked in. Alignment without either having to ask.

**Double approval — first wins.** If both approve the same item within moments, it proceeds once and the second founder sees that it was already handled, and by whom. Consistent with either founder having independent authority (Section 26).

**Adaptation — communication only, never judgement.** The CEO learns how each founder prefers to be communicated with — detail level, tone, what they care to hear about — and **gives both founders identical recommendations on identical decisions.**

*This distinction is load\-bearing.* Both founders can approve anything independently. If the CEO tailored its actual recommendations to each of them, the company's direction would depend on which founder happened to ask, and over months the two would drift toward different strategies without either noticing, since neither sees the other's version. Presentation adapts; judgement does not.

**Founder disagreements.** When the two founders give conflicting direction, the CEO **stops, surfaces the conflict to both, and presents the case for each side** — laying out the reasoning behind both positions to help them decide.

*The boundary to hold:* presenting both cases is assistance; recommending a winner is not. The CEO must not pick a side, propose a compromise as its own view, or act on either instruction until the founders have settled it between themselves. An agent that resolves disagreements between business partners becomes a party to the partnership, which is not a role it should ever occupy. Its job is to make the disagreement visible and well\-understood, then wait.

## 42h. The Founders

**Complementary backgrounds.** Faisal brings the technical and computer\-science side; his brother brings **direct carwash market experience.** Neither role is split formally — both founders work across everything, and either handles whatever comes up.

**What the CEO should understand about this.**

- **Communication.** Technical depth should be pitched differently to each founder — plainer for one, deeper for the other — consistent with the communication\-adaptation rule in Section 42g. Recommendations remain identical.
- **Domain authority.** When the brother makes a claim about how carwash operations actually work — how businesses staff, what owners care about, why something would or would not be adopted — that is **expert input, not a preference or a guess.** The CEO should weight it accordingly, and should actively seek it on operational questions rather than reasoning from first principles.

This is the one place where the two founders are genuinely not interchangeable, and it is an asset rather than an asymmetry to manage.

**Commercial terms are jointly agreed.** Both founders have discussed and agree on the deposit, annual term, and pricing model (Section 41.3). These are not one founder's decisions.

**Continuity if both are unavailable.** Undecided. Currently the auto\-pause applies (Section 22b): approved sprint work continues, new decisions wait for a founder to return. Whether any third party should ever hold limited authority is deferred.

### Effect on the validation assessment

Section 42f flagged the competitor\-gap claim as plausible but unverified. **That assessment should be read alongside this:** direct market experience is evidence, and better evidence than a desk\-based competitor review would produce alone. The foundation is firmer than "fairly confident" suggested.

Two things remain worth doing, for different reasons. Confirming what specific competitor tools actually provide turns market intuition into something the CEO can plan against concretely. And taking the real commercial proposition to the businesses already willing to start (Section 42f) tests willingness to pay, which domain experience cannot establish on its own — knowing a market well and knowing that its businesses will pay a particular price under particular terms are different kinds of knowledge.

## 42i. Market Reality — Domain Input

Provided by the founder with direct carwash market experience. This is the most operationally grounded input in the charter and several decisions should be re\-read in light of it.

### Staff are paid salary plus a per\-job or commission element

**This is the single most consequential finding in this section.** It means job records are not analytics — they are **payroll input**.

Consequences that change the product's value and risk profile:

- **The tooling becomes the source of truth for what staff get paid.** That moves it from "useful insight" to "operationally necessary," which is a materially stronger reason for a business to adopt and keep paying.
- **The accounting add\-on gains a far better proposition.** Automatic commission calculation from actual job records is a concrete, immediate benefit — considerably more compelling than reports and exports (Section 27.2), and arguably a better first version than full bookkeeping.
- **Employees gain a genuine reason to use the app correctly.** Their pay depends on accurate job records, which solves an adoption problem that would otherwise have to be enforced by their employer.
- **A new fraud risk appears.** Section 42a concluded that inaccurate external job logging "only misleads the business itself." That is **no longer true** where jobs drive pay: an employee logging phantom washes is inflating their own wages. The business needs protection — which strengthens the case for the business\-level photo requirement (Section 42a) and for surfacing anomalous logging patterns to the owner.
- **Pay disputes become platform\-adjacent.** If an employee disputes their commission, the app's records are the evidence. Accuracy and auditability matter more than they would for pure analytics.

### Owners' pain is broad, not narrow

Staffing, customer acquisition, and financial visibility are **all** significant concerns. This supports the all\-in\-one positioning (Section 29) rather than a single\-problem wedge, and it means no one add\-on is obviously the priority.

### Owners will use a dashboard — if it shows money and staff clearly

This validates the dashboard\-first delivery model (Section 31), with a specific instruction attached: **lead with money and staff.** Those are the two things owners already think about. Anything else is secondary and should not compete for the top of the screen.

### Mobile carwash is common and growing

This validates the substantial investment in GPS tracking, live dispatch, ETA ranking, and service radius. Mobile is not a speculative segment being built ahead of demand — it is an established and expanding part of the market, and the complexity it adds is justified.

## 42j. Practical Operations

**Legal entity — not yet registered, and it gates more than it appears to.** No company exists yet. This is on the critical path rather than an administrative afterthought: a payment gateway requires a registered business and a business bank account, and the gateway gates the entire booking and payment flow. Held customer and business funds (Section 41.1) and PDPL obligations across two markets also make the structure — which country, what entity type, operating across Bahrain and the UAE — more consequential than a typical first company. **Worth professional advice early**, alongside the VAT, residency, and wallet licensing questions already flagged.

*Practical consequence for planning:* work that does not depend on payments can proceed while this is arranged, but nothing customer\-facing can go live without it.

**API capacity — Anthropic API, pay\-as\-you\-go.** Agents run through the Claude Agent SDK against the API with usage billing.

*The thing to verify early:* rate limits are the real constraint on concurrency, regardless of what Section 18 says about unlimited parallel agents. The priority queue in Section 24a exists precisely because limits will be hit. Confirm actual rate limits and how they scale before the cockpit's orchestration is built, so the queue is designed against real numbers rather than assumed ones.

**Both founders full\-time.** This materially changes the throughput picture. The merge\-approval gate (Section 23.1) was flagged as a potential bottleneck; two full\-time approvers make it considerably less binding, and the concern in Section 43.2 about founders becoming the constraint is correspondingly reduced — though still worth measuring rather than assuming.

**Credentials shared between both founders.** Cloud accounts, payment gateway, API keys, and cockpit admin access are all held by both. Neither founder is a single point of failure, which matters because exclusive access means the company stops whenever that person is unavailable.

*One caveat worth observing:* shared credentials weaken the audit attribution in Section 26, which records which founder took which action. Where possible, use **individual accounts with equal privileges** rather than one shared login — same resilience, attribution preserved. This applies particularly to the cockpit itself, where founder attribution is explicitly part of the design.

## 42k. Infrastructure Setup & Working Rhythm

**Source control — GitHub, private, both founders as owners.** Best\-supported by CI tooling and by the Agent SDK's workflow. Three repositories: the product monorepo (Section 20b), the cockpit (Section 18b), and company memory living with the cockpit (Section 18d).

**Cockpit hosting — same GCC region, separate infrastructure.** Same region as the product for latency and operational simplicity, but **isolated from production infrastructure** so a product outage cannot take down the control plane needed to fix it. This is the practical expression of the cockpit circularity concern in Section 24c: shared region, separate blast radius, with the terminal fallback (Section 21c) as the final backstop if both are affected.

**Development environments — one, not two.** Faisal maintains a local development environment; his brother works entirely through the cockpit. Nothing in the approval, direction, or review workflow requires running code locally, and keeping his setup to a browser removes a whole category of things that can break or need maintaining. If he later wants to inspect the running app, a read\-only local setup can be added — it is not needed to operate.

**Daily rhythm.**

1. **Morning CEO session** — the four\-line brief (Section 22a): what shipped, what's blocked, what needs you, what's next. Sprint decisions, direction, and questions happen here.
2. **Approvals through the day** — merge approvals handled as gates clear them, rather than batched. With both founders full\-time, whichever is free takes what is pending (Section 26).
3. **No continuous monitoring.** The single status indicator (Section 24f) is the mechanism for *not* watching. Green means nothing needs attention; interruptions are bounded to blockers, incidents, and items requiring approval (Section 22a).

*Why this rhythm rather than fixed batch windows:* merge throughput is capped by founder availability (Section 23.1), and batching into two daily windows would idle finished work for hours. Handling approvals as they arrive keeps the pipeline moving without requiring constant attention, because the queue notifies rather than needing to be watched.

## 43\. Validation Strategy

Four risks sit outside the product itself: the charter being misread, the founders becoming the bottleneck, the CEO degrading unnoticed, and nobody knowing whether the whole approach is working. This section addresses each with something observable rather than hoped for.

### 43\.1 Two Documents, Not One

This charter records **how decisions were reached** — the reasoning, the trade\-offs, the things challenged and reversed. That history is valuable and should be preserved. But it now contains roughly fifteen places where a later section supersedes an earlier one, and an agent reading it linearly can follow a retired instruction.

**Therefore: two documents.**

- **This document** remains the decision record and audit trail. Founders read it when they want to know *why* something is the way it is.
- **A clean consolidated specification** is produced from it, with superseded material removed rather than annotated, and no internal contradictions. **This is what the CEO and all agents read.**

The consolidated version is the input to the system. This one is the reasoning behind it. Conflating them is how a 32,000\-word document that argues with itself becomes the foundation for every downstream decision.

### 43\.2 Merge Approval — Tiered by Risk

Founders approve every merge (Section 23.1), which is a real throughput constraint. The resolution is not to remove the gate but to right\-size the *effort* per approval:

- **Routine changes** — approved on the CEO's summary of what the change does and why. Gates have already verified it works; re\-reading the code duplicates QA, Security, and Performance and makes the founders the slowest component.
- **Sensitive changes** — anything touching payments, personal data, security, or wallet balances gets the summary **plus the actual diff**. These are the changes where a subtle error is expensive and where founder judgement adds something the gates cannot.

**Diagnostic worth tracking: your own rejection rate.** If founders approve essentially everything, the gate is ceremonial and the effort would be better spent elsewhere. If they reject frequently, the CEO's judgement or the specification is wrong and that is the thing to fix. Either extreme is informative; the rate itself is the signal.

### 43\.3 Detecting a Failing CEO

Metrics (Sections 22b, 25) catch gradual degradation but are slow, and HR monitoring is itself an agent. The sharpest instrument available is a founder's own judgement — but only while it remains independent.

**The first\-month practice: predict before reading.** For each significant proposal in the early weeks, form your own view *before* opening the CEO's recommendation, then compare. Frequent alignment means it has understood the business. Frequent divergence — especially where the founders were right — is the signal, and it appears far sooner than any metric.

**This instrument has a short life, deliberately.** Once founders begin deferring to the CEO's judgement (which is the point of having it), independent comparison stops being possible. Use it hard in the first month while it still works, then rely on metrics.

### 43\.4 What Success Looks Like at Thirty Days

Three signals, in ascending order of significance:

1. **The pipeline works.** Real changes moved from assignment through gates to merged, without founders having to intervene in mechanics. This is the minimum bar — it proves the machine runs.
2. **The CEO proposes things the founders had not considered.** Evidence it understands the business rather than executing instructions. This is the difference between an expensive automation layer and something that genuinely thinks.
3. **Progress exceeds what a founder achieved alone in Claude Code.** The original problem this was built to solve, measured directly against the alternative.

**And the failure signals, stated equally plainly:**

- Founders spend more time managing agents than they previously spent building.
- The approval queue is consistently the reason nothing ships.
- Rework is high — agents building the wrong thing correctly, which points at specification quality rather than agent quality.
- The CEO's proposals require heavy correction most weeks.

**If two or more failure signals hold at thirty days, the response is to reduce scope rather than push harder** — fewer active agents, narrower sprints, more founder direction — and diagnose from there. A fifteen\-agent organisation that is not working does not improve by adding a sixteenth.
