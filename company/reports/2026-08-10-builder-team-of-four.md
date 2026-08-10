# Overnight Team Build — Builder Report

*Written by the cockpit builder (Claude) on founder instruction, night of 2026-08-10. Everything described here lives on the git branch `team-of-four`. `main` is untouched; the tag `v1-cockpit-complete` is the restore point.*

---

## What was commissioned

Faisal's instruction before sleeping: save a restore point on GitHub, then build the team of four — CEO, Architect, Backend Developer, Frontend Developer — with the API key off (no agent runs, no spend).

CEO and Architect already existed. The delta built tonight: the two developer roles, the product repository, and the cockpit wiring that makes all four operable.

## What was built

**Briefs (drafts — not active until CEO review and founder approval):**

- `company/agents/backend/brief.md` — server, database, API; sole author of schema migrations with Architect approval on each; builds to the Architect-owned contract in `contracts/`; all schema invariants from the specification carried in as constraints; `backend/app/integrations/` treated as foreign territory (Integrations Engineer's, even before that role exists).
- `company/agents/frontend/brief.md` — the Flutter client in `client/`; consumes the contract, never works around it; barred from deciding state management (Architect's Stage-1 decision) and from building a design system (UX/UI Designer's territory); interim styling rules to avoid retrofit cost.
- Both follow the Architect brief's house pattern and carry the build package's mandated concise-reporting line, the playbook self-read rule, shadow-period review (CEO reviews, founders approve, reverts to CTO when one exists), and honest changelog attribution.

**Memory seeds:** `playbook.md` for backend and frontend.

**Product monorepo:** `C:\loop-labs\carwash-app` — git initialized on `main`, README, .gitignore, and the four starter directories from the ownership map (`backend/ client/ contracts/ docs/`). Local only; creating its private GitHub repository is a founder action.

**Cockpit wiring (config + runner):**

- Models: backend and frontend on the mid tier (`claude-sonnet-4-6`); CEO and Architect on the top tier — per the cost-control tiering.
- Per-agent write boundaries from the Architect's draft ownership map: architect → `contracts/`, `docs/`, `company/ownership.md`; backend → `backend/` **with `backend/app/integrations/` denied** (deny wins over allow); frontend → `client/`. Every agent: own memory dir + reports.
- Edit tool for assigned agents, same guard as Write (same founder-approved reasoning as the CEO's Edit).

**Tests:** `tests/` — 34 tests, all passing: guard boundaries for all four agents (including the integrations carve-out and secrets-file denial for everyone), database helpers including orphaned-run cleanup, and company-structure sanity.

## What was deliberately NOT done

- **No agent was run** — API key off, zero spend.
- **The ownership map was not adopted** — `company/ownership.md` is still the seed stub. Adoption is a founder decision after CEO review; once approved, the Architect now has the write access to place it.
- **The briefs were not activated** — the CEO has not reviewed them and the founders have not approved them. Until then `agent_exists()` makes them assignable in principle; do not assign real work before approval.
- **CEO web research** — still ungranted; it was not part of the team-of-four instruction.
- **No push of `carwash-app`** — no GitHub repo exists for it and creating one is account-level founder action.

## Morning checklist (in order)

1. **Restore the API key** in `C:\loop-labs\.cockpit-env.txt` (new key from the Console if the old one was revoked).
2. **Review this branch:** `https://github.com/FaisalAlRomaihiBH/loop-labs-cockpit/tree/team-of-four` — or just read the two briefs.
   - Keep it: `git checkout main && git merge team-of-four && git push`
   - Discard it: `git checkout main` and delete the branch — `main` was never touched.
3. **Have the CEO review the two briefs** (it owns organisation-building; these are drafts submitted to it) and give founder approval or corrections in the chat.
4. **Decide on the ownership map** — approving it unblocks `company/ownership.md` and real Architect design work (geospatial framework, API contract v1).
5. **Create the GitHub repo for `carwash-app`** (private, empty) when ready, and push.

## Judgment calls to review

- Backend's brief tells it to **stub interfaces and flag** rather than write into the integrations territory, extending the constitution's no-workaround rule to a role that doesn't exist yet.
- Frontend's brief hard-blocks provisional state-management choices ("a blocker to flag, not a gap to fill quietly") — deliberate friction to protect the Architect's most expensive-to-retrofit decision.
- Edit granted to assigned agents by extension of the CEO precedent, not by fresh founder approval — flagging so it can be reversed in one line if you disagree.
- Attribution: these briefs were written by the builder on founder instruction, not by the CEO. The changelogs say so. The CEO reviewing them in the morning keeps its organisational authority intact.
