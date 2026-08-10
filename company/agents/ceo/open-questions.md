# CEO Open Questions

What is waiting on a founder decision, and since when. Removed once answered — the answer itself goes to `decisions.md`, not here.

---

## Open

### Cockpit configuration — three gaps blocking the Architect (raised 2026-08-10)

Verified in `app/agents.py` and `app/config.py`, not assumed. Cockpit config is DevOps's, and DevOps does not exist, so it is a founder action.

1. **The Architect cannot write `company/ownership.md`.** `run_assigned_task` hardcodes an assigned agent's write scope to `[company/reports/, company/agents/<own-name>/]`. There is no per-agent write-path table for assigned agents as there is for the CEO. Its single most important deliverable is unwritable. *Workaround in place:* the brief instructs it to deliver the map as its report; a founder moves it. No code change strictly required.
2. **No `MODELS["architect"]` entry** — it would fall through to the faster default. The specification puts the Architect on the strongest tier alongside CEO and Security, because its blast radius is the widest of any technical role.
3. **No `TOOLS["architect"]` entry** — it gets `Write` without `Edit`, the same whole-file-rewrite content-loss risk that justified granting the CEO `Edit`.

### No agent can do web research — blocks the competitor teardown (raised 2026-08-10)

The specification allows web research to any agent whenever useful. **No agent has a web tool.** `TOOLS["ceo"]` is `Read, Glob, Grep, Write, Edit`; `TOOLS["default"]` is the same without `Edit`. Nothing can fetch or search.

Consequence: the competitor teardown the founders asked for cannot be run by me or by any agent I could assign it to. It also weakens the provisional-price proposal, which was to be based on Hasan's market knowledge *plus* the teardown. Hasan's knowledge alone can carry a provisional number, but I should say plainly that it is one input rather than two.

Needs a founder decision: add web tools to the CEO, wait and give them to a research-capable agent later, or the founders run the teardown themselves.

### Hasan's provisional numbers for the M5 pilot criteria (raised 2026-08-10)

The pilot failure criteria are written into `sprint.md` as approved, but two thresholds are mine rather than his and he is the domain authority:

- Typical daily job volume for a business of the size we are piloting with, so "logging completeness" has a real denominator.
- Whether 80% logging completeness by week three is a sensible bar or a naive one.

Not urgent — needed before the pilot starts, which is several milestones away. Do not let it hold up M1.

### Genuinely blocked, not awaiting a decision

- **Deposit sizing** — depends on the payment gateway's actual chargeback dispute windows, which depends on gateway selection, which depends on company registration. Founders have cut the circularity at the price link instead; this one stays blocked and must not hold up anything else.

---

## Answered

**2026-08-10 — the milestone breakdown.** Approved by Hasan: shape and ordering, M4 with its constraint, Security into M3. Contents of M6 onward deliberately not approved. Two founder additions (M5 failure criteria, founding-member positioning) implemented in `sprint.md`. See `decisions.md`.

**2026-08-10 — Architect brief and markdown rendering.** Brief approved and the Architect activated (run 16). Markdown rendering approved, option one, Faisal implementing. Registration and advisors confirmed unchanged — still not started, jurisdiction still open.

**2026-08-10 — permissions and tooling.** All three granted (brief writes, own reports, `Edit`), memory structure Option B approved. See `decisions.md`.

**2026-08-10 — the nine opening questions.** All answered by Hasan and Faisal jointly. Recorded in full in `decisions.md`. Summary of what is now settled:

- Lead with the business tooling, not the marketplace. Direction; the CEO proposes what it means concretely.
- Run the competitor teardown, alongside Hasan's market knowledge.
- Registration not started; advisors not started. Both on the critical path; plan around their absence.
- Take the real proposition to three businesses before building. CEO proposes a provisional price, marked provisional.
- Cockpit work stays minimal — fix what actively blocks, nothing speculative.
- Merge approvals in session: summary for routine, summary plus diff for payments, personal data, security, wallet.
- Hasan: plainer on technical matters, full detail on request. Faisal: depth directly. Communication only, never judgement.
- The CEO's reading of the business is accurate. Marketing add-on genuinely undefined. Thirty-day assessment runs from first product code. CEO reviews the Architect's first output, founders approve, reverts to CTO when it exists.
