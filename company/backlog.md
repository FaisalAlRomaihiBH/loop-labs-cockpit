# Backlog

Running list of ideas and deferred work. Items noticed during a build step that go beyond that step land here instead of in the code.

- **Reload message history on page refresh** — refreshing the page starts a new session with an empty chat; prior messages exist in SQLite but aren't re-rendered. Fine for Step 1 plumbing; worth revisiting when the cockpit is used daily. (noticed 2026-08-10, Step 1)
- **Per-session queue eviction** — the in-memory session→queue dict grows forever; harmless for two local users, but a long-lived server would want cleanup on session end. (noticed 2026-08-10, Step 1)
- **`.gitignore` before the day-one GitHub push** — must cover `cockpit.db`, `.venv/`, `__pycache__/`. The build package calls for the off-site backup before the first CEO session, so this lands with `git init`. (noticed 2026-08-10, Step 1)
