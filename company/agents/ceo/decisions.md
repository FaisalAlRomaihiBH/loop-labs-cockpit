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
