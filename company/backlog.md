# Backlog

Running list of ideas and deferred work. Items noticed during a build step that go beyond that step land here instead of in the code.

- **Reload message history on page refresh** — refreshing the page starts a new session with an empty chat; prior messages exist in SQLite but aren't re-rendered. Fine for Step 1 plumbing; worth revisiting when the cockpit is used daily. (noticed 2026-08-10, Step 1)
- **Per-session queue eviction** — the in-memory session→queue dict grows forever; harmless for two local users, but a long-lived server would want cleanup on session end. (noticed 2026-08-10, Step 1)
- **`.gitignore` before the day-one GitHub push** — must cover `cockpit.db`, `.venv/`, `__pycache__/`. The build package calls for the off-site backup before the first CEO session, so this lands with `git init`. (noticed 2026-08-10, Step 1)
- **`add_dirs` for the product repo** — the CEO's `cwd` is `REPO_ROOT`; the path guard (`can_use_tool`) already allows reads under `PRODUCT_REPO`, but the CLI subprocess itself may need `PRODUCT_REPO` passed via `ClaudeAgentOptions.add_dirs` to actually read outside `cwd`. Not testable yet since `carwash-app` doesn't exist; revisit once it does. (noticed 2026-08-10, Step 3)
- **In-memory `_sdk_sessions` map doesn't survive a server restart** — a founder's cockpit session id would no longer resolve to a resumable SDK session after `uvicorn` restarts, silently starting a fresh (full-context) turn instead of resuming. Fine for local single-process use now; would need persisting the mapping (e.g. in SQLite) for anything longer-lived. (noticed 2026-08-10, Step 3)
