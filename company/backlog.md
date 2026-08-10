# Backlog

Running list of ideas and deferred work. Items noticed during a build step that go beyond that step land here instead of in the code.

## Cockpit

- **Per-session queue eviction** — the in-memory session→queue dict grows forever; harmless for two local users, but a long-lived server would want cleanup on session end. (noticed 2026-08-10, Step 1)
- **`add_dirs` for the product repo** — the CEO's `cwd` is `REPO_ROOT`; the path guard (`can_use_tool`) already allows reads under `PRODUCT_REPO`, but the CLI subprocess itself may need `PRODUCT_REPO` passed via `ClaudeAgentOptions.add_dirs` to actually read outside `cwd`. Not testable yet since `carwash-app` doesn't exist; revisit once it does. (noticed 2026-08-10, Step 3)
- **No `Edit` tool for the CEO** — memory updates require rewriting whole files with `Write`. Costs tokens and risks losing content on a partial rewrite. Requested from founders 2026-08-10; under consideration. (noticed 2026-08-10, first founder session)

## Company / documents

- **Founder-identity naming amendment — approved by Faisal, blocked on write permission.** Placeholder "his brother" / "the brother" must become **Hasan** in: `constitution.md` L7, `specification.md` L13 + L380, `charter.md` L1201/1841/1857/1862/1926, `build-package.md` L27 (currently *inverted* — says Founder A is Faisal, Founder B is his brother; the truth is the reverse) + L35/L200/L254, `agents/ceo/brief.md` L90. `plan.md` L219 needs no change. Naming only, no substantive edits. CEO path guard blocks all of these; needs a founder edit or a widened write scope. (2026-08-10)
- **No owning agent exists to receive change requests.** The constitution routes any needed change in a file you don't own to the owning agent. Until the Architect publishes the ownership map and DevOps exists, that route has no destination and every such change becomes a founder action. Expect this to bite repeatedly during company construction. (noticed 2026-08-10)

## Closed

- ~~No kill-switch mechanism found in the repo~~ — **wrong, and corrected 2026-08-10.** The mechanism exists: `company/KILL`, checked by `app/agents.py` before a run starts and on every message mid-run. Enforced by the runtime rather than by agent instruction, which is stronger. The original entry was written from a failed search rather than from reading the cockpit source.
- ~~Reload message history on page refresh~~ — **fixed 2026-08-10 by Faisal.** Conversations now survive page navigation and cockpit restarts.
- ~~In-memory session→client map doesn't survive a server restart~~ — **addressed 2026-08-10, by a different mechanism than the one I proposed.** `_clients` still holds the live SDK client in memory per cockpit session, so a server restart does drop it — but `_first_user_message` then replays the stored message history from SQLite into the first prompt of the reconnected session. Verified live: this session was restarted mid-conversation and the full prior exchange came back verbatim. Continuity comes from the database rather than from persisting the client, which is the more robust of the two.
- ~~`.gitignore` before the day-one GitHub push~~ — **done, verified 2026-08-10.** Repository pushed to a private GitHub repo, which satisfies the specification's requirement that company memory be backed up off-site from the first session. `.gitignore` correctly excludes `cockpit.db`, `.venv/`, `__pycache__/`, `*.pyc`, and carries `*.env` / `cockpit-env*` backstops; secrets live outside the repository by design.
