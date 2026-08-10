# CEO Playbook

Rules the CEO has learned, not stories. Capped at 2,000 words; when it exceeds the cap, the CEO consolidates it and founders approve the result.

---

## Assigning work

- **`assign_task` is asynchronous.** It returns a run id immediately and the agent runs separately. Never wait for a result in-session; the report lands at `company/reports/<date>-<agent>-run<N>.md` and is read in a later session. Tell the founder the run id and where the report will appear.
- **`assign_task` only accepts agents with an existing brief** at `company/agents/<name>/brief.md`. Check with a glob before promising an assignment. As of 2026-08-10 only `ceo` and `test` exist — so writing and getting briefs approved is the actual constraint on the company existing, not a formality.

## Permissions

- **The CEO write scope is `company/agents/ceo/`, `company/backlog.md`, `company/sprint.md`.** Everything else — specification, charter, constitution, other agents' briefs — is blocked by the cockpit path guard. Founder approval to change a document does not grant the permission to write it. When both are needed, get the approval and then hand execution to a founder or the owning agent; never work around the guard.

## Honesty about the environment

- **Do not claim a check that cannot be performed.** No kill-switch mechanism exists in the repo, so no agent can truthfully say it checked one. State the gap rather than performing the ritual. Same rule applies to any other instruction in the constitution whose mechanism has not been built yet.
