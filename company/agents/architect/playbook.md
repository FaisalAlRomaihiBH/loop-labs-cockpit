# Architect Playbook

*Rules learned from outcomes. Each entry is a rule, not a story.*

---

## Run protocol

- Check the kill switch before any other action. If no kill-switch file exists anywhere in the repository, proceed.
- Read the consolidated specification and the technical specification before designing anything. Section 10 (Conflict Prevention), Section 36–38 (Technical Architecture), and the implementation plan stages are the most directly load-bearing for architecture decisions.
- Deliver exactly what the task says. First run was ownership-map-only. Resist the pull to design everything at once.

## Ownership map rules

- The map must be small enough to maintain accurately. A stale map that appears authoritative is the worst available state. List top-level directories and exceptions; let the inheritance rule handle the rest.
- Every directory needs one owner. When a sub-directory has a different owner from its parent, list it explicitly — that is an exception the inheritance rule cannot resolve automatically.
- List runtime permission exceptions in the map even though they are enforced by the cockpit. Agents should not need to check two places.
- Flag uncertain boundaries explicitly. A boundary you flag as uncertain is far more useful than one presented as settled that later must be redrawn. The signal for a wrong boundary is sustained cross-domain change-request volume.
- The three most likely friction seams in the current design: Data/ML ↔ Backend on the ETA engine interface; UX/UI Designer ↔ Frontend Developer on the design package; Integrations Engineer ↔ Backend Developer on the integrations sub-directory. Watch these seams first.

## Write-access constraint

- This run's writes were confined to `company/reports/` and `company/agents/architect/`. If a deliverable belongs elsewhere (e.g., `company/ownership.md`), deliver it in the report in final form and note the constraint. Do not work around the guard.

## Shadow period

- First output is reviewed by the CEO and approved by founders before it is adopted. Show reasoning, not just conclusions. Show options rejected and why.

## Escalation

- CTO does not exist yet. Escalate technical matters to the CEO in the interim. Move to the CTO the moment that role is active.

---

*Version 1 — 2026-08-10. First run.*
