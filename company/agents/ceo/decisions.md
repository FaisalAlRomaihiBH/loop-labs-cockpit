# CEO Decision Log

Append-only. Every decision the CEO makes, with its reasoning and date, recorded here as it happens. Never consolidated — this file must remain searchable permanently.

---

## 2026-08-10 — Weekly founder review fixed to Saturdays, 10:00 Bahrain time

**Decision.** The weekly founder review is held every Saturday at 10:00 Bahrain time (UTC+3). Sprint plans are approved or rejected in that meeting.

**Made by.** Both founders, jointly. Communicated by Founder A. Not a CEO proposal.

**Reasoning given.** None stated beyond the decision itself; recorded as a founder directive.

**Why it matters / consequences.**
- The weekly sprint review and the next sprint's plan for approval (spec §19c) now have a fixed slot rather than floating. Sprint approval is a scheduled event, not an ad-hoc one.
- I should arrive at each Saturday meeting with: the sprint review, the self-assessment ("what I would do differently"), and the next sprint plan ready — not produce them during the meeting.
- The daily rhythm is unchanged: morning CEO session, merge approvals handled through the day as gates clear. This decision governs the weekly cadence only.
- The three-day auto-pause on new decisions (spec §7a) interacts with this: a missed Saturday review means new sprint work waits, while already-approved sprint work continues.

**Status.** Active standing commitment. Supersedes nothing — no prior cadence had been set.

*Retroactive note (same day): "Founder A" in this entry resolves to **Hasan**, per the identity correction below.*

---

## 2026-08-10 — Founder identities corrected: Founder A is Hasan, Founder B is Faisal

**Directive.** Faisal corrected the placeholder naming carried through the founding documents. Founder A is **Hasan** — his brother, the carwash operations expert. Founder B is **Faisal**. Message tags now carry these names.

**Made by.** Faisal. Not a CEO proposal — a factual correction with an explicit instruction to record it immediately.

**Why it matters / consequences.**
- The charter, consolidated specification, and implementation plan all refer to "his brother" / "the brother". Those references resolve to **Hasan**.
- Domain authority (spec §20, charter §42h) attaches to **Hasan**: his claims about carwash operations are expert input, to be weighted as evidence and actively sought on operational questions.
- The founder-preferences file is now seeded with identities and the standing rules. Communication mapping (deeper technical detail for Faisal, plainer for Hasan) is recorded as an **inference from their backgrounds, not a stated preference** — flagged for confirmation.
- **Evidence boundary set:** no founder preferences are to be inferred from any session before this message. Earlier test messages were the cockpit builder verifying the system, not founders acting as founders. Preference-building starts here.

**Status.** Active and permanent.

---

## 2026-08-10 — Amendment of founding documents approved; execution blocked on write permission

**Decision.** Faisal approved amending the founding documents to replace the placeholder naming with **Hasan** — naming only, no substantive change. This clears the "change the specification" hard stop for this specific, bounded edit.

**Made by.** Faisal, approving the CEO's recommendation (option 2 of three presented: amend naming only, now, while it is a one-line change).

**Reasoning given / carried.** The specification is what every future agent reads. An agent encountering "his brother" must resolve it through a memory file that may not be in its context. Fixing it at source removes a recurring ambiguity from fifteen agents rather than from the CEO alone.

**Outcome: not executed.** The cockpit's path guard rejects CEO writes outside `company/agents/ceo/`, `company/backlog.md`, and `company/sprint.md`. Every target file is outside that scope. I did not attempt to work around it.

**Assessment.** The guard behaved correctly — these documents are not the CEO's to write, and a permission that cannot be exceeded is the point of the design (spec §12). The gap is that no owning agent exists yet to file a change request to, so the constitution's normal route (§Ownership) has no destination. Until DevOps or the Architect exists, founding-document edits are a founder action.

**Status.** Approval stands and does not need re-asking. Execution deferred to a founder edit or a widened CEO write scope. Full file-and-line list recorded in the backlog so whoever does it has an exact worklist.

---

## 2026-08-10 — CEO memory structure (Option B) and two write grants approved

**Decision.** Faisal approved all three CEO requests, effective immediately:

1. **Memory structure — Option B.** The three mandated files (`decisions.md` append-only and never consolidated, `playbook.md` capped and consolidated, `founders.md`) plus a standing `open-questions.md` and dated reports under `company/reports/`. Options A (three files only) and C (add metrics, competitor and index files) were presented and not chosen.
2. **Write access to `company/agents/*/brief.md`** — briefs only, explicitly **not** other agents' memory. Granted with the stated understanding that it **moves to HR when HR exists**.
3. **An `Edit` tool** scoped to the same paths as the CEO's `Write`.

**Made by.** Faisal, approving the CEO's recommendation. Enforcement layer updated and tested by him before granting.

**Reasoning carried.** Every CEO session is fresh, so anything not written to a file is lost — `open-questions.md` gives blocked decisions a durable home instead of a chat log, which had already proven interruptible. Brief-writing was the single blocker on the company existing at all: the CEO's first construction task is writing the organisation's briefs, and it could not perform it. `Write`-only meant correcting one line of a memory file required reproducing the whole file — wasteful and a real content-loss risk.

**Verified in source, not assumed.** `app/config.py` now sets `TOOLS["ceo"] = ["Read", "Glob", "Grep", "Write", "Edit"]`, and adds `CEO_WRITE_GLOBS` = `company/agents/*/brief.md` and `company/reports/*-ceo-*.md`. `app/agents.py` applies the same path guard to `Edit` as to `Write`. The reports grant is scoped **by filename convention** — `*-ceo-*.md` — so the CEO can write its own reports and not other agents'.

**Consequences.**
- The blocker on building the organisation is cleared. The Architect's brief is now writable, and drafting it is the next construction step once the founders answer the open questions — in particular the shadow-period question, since the CTO who would normally review a new agent's first work does not exist.
- Brief-writing carries an acknowledged risk: the CEO can also rewrite an existing agent's brief. This is why it is temporary and hands to HR. Until then, treat any brief edit to an agent other than a brand-new one as needing founder approval.
- Off-site backup is satisfied (private GitHub push, `.gitignore` verified), so memory now has real durability behind it.

**Status.** Active. Grant 2 is explicitly temporary and expires to HR.
