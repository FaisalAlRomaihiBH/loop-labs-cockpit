# CEO Playbook

Rules the CEO has learned, not stories. Capped at 2,000 words; when it exceeds the cap, the CEO consolidates it and founders approve the result.

---

## Assigning work

- **`assign_task` is asynchronous.** It returns a run id immediately and the agent runs separately. Never wait for a result in-session; the report lands at `company/reports/<date>-<agent>-run<N>.md` and is read in a later session. Tell the founder the run id and where the report will appear.
- **`assign_task` only accepts agents with an existing brief** at `company/agents/<name>/brief.md`. Check with a glob before promising an assignment. As of 2026-08-10 only `ceo` and `test` exist — so writing and getting briefs approved is the actual constraint on the company existing, not a formality.

## Permissions

- **The CEO write scope is `company/agents/ceo/`, `company/backlog.md`, `company/sprint.md`.** Everything else — specification, charter, constitution, other agents' briefs — is blocked by the cockpit path guard. Founder approval to change a document does not grant the permission to write it. When both are needed, get the approval and then hand execution to a founder or the owning agent; never work around the guard.
- **The CEO has no `Edit` tool — only `Write`, which overwrites whole files.** Read a memory file before rewriting it, and reproduce the parts that are not changing. Budget for this when updating memory mid-session.

## Honesty about the environment

- **Verify environment claims in the cockpit source before recording them as fact.** A rule written from "I could not find it" is a guess, not a finding. Grep `app/` first.
- **The kill switch exists and is enforced by the runtime, not by the agent.** It is the file `company/KILL`. `app/agents.py` checks it before any run starts (refusing it) and again on every message mid-run (interrupting it). Consequence: an agent cannot meaningfully "check" it — if it were set, the run would not be happening. The honest statement is that the mechanism is structural and a running session is itself the proof it is clear. Do not perform a fake check, and do not claim the mechanism is missing.
