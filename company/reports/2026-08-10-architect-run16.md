# Architect Report — 2026-08-10 (Run 16)

**Deliverable:** Ownership map — first and only task for this run.  
**Kill switch:** Clear. No kill-switch file found anywhere in the repository.  
**Pre-reading completed:** Constitution, architect brief, consolidated specification (full read, emphasis on §10 Conflict Prevention and §36–38 Technical Architecture), technical specification and implementation plan (Part One and all stages).

---

## Note on write access

The write restriction is still in place. This run can write to `company/reports/` and `company/agents/architect/` only. The ownership map is therefore delivered here, in final form, ready to be moved to `company/ownership.md` unchanged. If that restriction is lifted before the map is needed, I will write it directly and note that in the next report.

---

# Part 1 — The Ownership Map

*This section is the complete ownership map in its final form. Everything below the horizontal rule is `company/ownership.md` content.*

---

---

# Loop Labs — Ownership Map

*Every directory in the product monorepo has exactly one owning agent. New files inherit directory ownership automatically. Agents may read anything; they write only what they own. Where an agent needs a change in a directory they do not own, they file a change request to that directory's owner.*

*Last updated: 2026-08-10 by the Architect.*

---

## The Inheritance Rule

**When a new directory is created:**

1. Look it up in this map. If it is listed, that entry wins.
2. If it is not listed, the owner is the owner of the nearest ancestor directory in this map.
3. If no ancestor is listed, or the directory sits at the product monorepo root, the owner is **DevOps**.

An agent creating a subdirectory inside their own territory does so freely — no Architect consultation required. An agent who needs a new subdirectory inside another agent's territory files a change request to that territory's owner. If the new subdirectory's natural owner differs from its parent's owner, flag the Architect so the map can be updated; a gap in the map is where the next collision happens.

---

## Product Monorepo

The product repository holds the Python/FastAPI backend and the Flutter client together, so API contract changes can be made atomically. The cockpit lives in a separate repository.

### Core Assignment Table

| Directory | Owner | Notes |
|-----------|-------|-------|
| `backend/` | Backend Developer | All backend source, tests, migrations, and tooling |
| `backend/app/integrations/` | Integrations Engineer | **Exception inside backend/.** Third-party client wrappers: payments, Maps, SMS, Firebase Admin. Backend Developer files change requests here; Integrations Engineer files change requests to the rest of `backend/`. |
| `backend/migrations/` | Backend Developer | **Backend Developer is the sole author of all schema migrations.** Architect approves every migration before it merges. This is an explicit constraint from the specification, not just an ownership rule. |
| `client/` | Frontend Developer | Flutter application — customer, business, and employee app shells (mobile and web) |
| `design/` | UX/UI Designer | Flutter Dart package: theme, component widgets, design tokens. Referenced from `client/` as a local path dependency. |
| `ml/` | Data/ML Engineer | ETA engine, duration prediction models, training pipelines, inference layer |
| `analytics/` | Data/ML Engineer | Event schema definitions, data processing pipeline, insights aggregation |
| `firebase/` | Integrations Engineer | Firebase project configuration, Realtime Database and Storage security rules |
| `contracts/` | Architect | API contract — the authoritative seam between Backend and Frontend ownership. OpenAPI specification, versioned. |
| `docs/` | Architect | Architecture decision records, system overview. Root of documentation. |
| `docs/product/` | Product Manager | **Exception inside docs/.** Requirements, acceptance criteria, user stories co-located with the code they describe. |
| `infra/` | DevOps | All environment and infrastructure configuration: Docker, orchestration manifests, environment configs (dev/staging/production), CI scripts |
| `monitoring/` | SRE | Alerting rules, dashboards, SLO definitions, error budget policies, incident runbooks |
| `performance/` | Performance Engineer | Load test scripts, benchmark configurations, geospatial query benchmarks, results |
| `security/` | Security | Security policies, threat models, review checklists, penetration test configurations |
| `qa/` | QA | Test plans, edge-case scenario definitions, coverage checklists. QA's staged additions before filing change requests to backend or frontend. |
| `.github/` | DevOps | GitHub Actions workflows, branch protection, repository settings |
| `[root-level files]` | DevOps | `pyproject.toml`, `docker-compose.yml`, `.gitignore`, `.env.example`, root `README.md`, and any other file at the monorepo root |

### Runtime Permission Exceptions

These permissions are enforced by the cockpit runtime, not the ownership map. They are listed here so the map is a complete reference and agents do not need to check two places.

| Agent | Scope | Permission |
|-------|-------|-----------|
| QA | `backend/tests/` and `client/test/` | Write access to test files — for adding edge-case tests without a change request on every single addition. QA still owns `qa/` for staging and planning. |
| Security | All application code | Read-only. Security is a gate, not a code author. Application security code (auth middleware, rate limiting, secret handling) lives in `backend/` and is written by Backend Developer, reviewed and blocked by Security. |
| Performance | All application and infrastructure code | Read-only. Performance is a gate. Load test scripts live in `performance/`, which Performance Engineer owns and writes. |
| All agents | `company/reports/` (cockpit repo) | Write access for submitting run reports. |
| All agents | `company/agents/{own-role}/` (cockpit repo) | Write access for memory and playbook. |

---

## Cockpit Repository

**The cockpit repository as a whole is owned by DevOps.** DevOps maintains the repository infrastructure, CI/CD pipelines, and the cockpit application code that runs the agents.

Within the cockpit repository, the `company/` directory contains company memory with agent-specific ownership. DevOps owns the cockpit application code outside `company/`.

| Path | Owner | Notes |
|------|-------|-------|
| `company/ownership.md` | Architect | This file |
| `company/lessons.md` | HR | All agents have runtime write access — shared lessons belong to everyone |
| `company/reports/` | HR | All agents have runtime write access for submitting reports; HR monitors and reviews |
| `company/charter.md` | CEO | |
| `company/specification.md` | CEO | CEO proposes changes; founder approval required to change |
| `company/plan.md` | CTO | Technical specification and implementation plan; CTO maintains when active, CEO holds it until then |
| `company/sprint.md` | CEO | |
| `company/backlog.md` | CEO | |
| `company/constitution.md` | CEO | Founders change this; CEO proposes amendments |
| `company/build-package.md` | CEO | |
| `company/agents/ceo/` | CEO | |
| `company/agents/cto/` | CTO | |
| `company/agents/architect/` | Architect | |
| `company/agents/hr/` | HR | |
| `company/agents/product-manager/` | Product Manager | |
| `company/agents/ux-designer/` | UX/UI Designer | |
| `company/agents/backend/` | Backend Developer | |
| `company/agents/frontend/` | Frontend Developer | |
| `company/agents/data-ml/` | Data/ML Engineer | |
| `company/agents/integrations/` | Integrations Engineer | |
| `company/agents/qa/` | QA | |
| `company/agents/security/` | Security | |
| `company/agents/performance/` | Performance Engineer | |
| `company/agents/devops/` | DevOps | |
| `company/agents/sre/` | SRE | |

---

## Summary: All Fifteen Roles

| Role | Product Monorepo | Cockpit Repo |
|------|-----------------|--------------|
| CEO | None | `company/` root documents, `company/agents/ceo/` |
| CTO | None | `company/plan.md`, `company/agents/cto/` |
| Product Manager | `docs/product/` | `company/agents/product-manager/` |
| Architect | `contracts/`, `docs/` (excl. `docs/product/`) | `company/ownership.md`, `company/agents/architect/` |
| HR | None | `company/lessons.md`, `company/reports/`, `company/agents/hr/` |
| UX/UI Designer | `design/` | `company/agents/ux-designer/` |
| Backend Developer | `backend/` (excl. `backend/app/integrations/`) | `company/agents/backend/` |
| Frontend Developer | `client/` | `company/agents/frontend/` |
| Data/ML Engineer | `ml/`, `analytics/` | `company/agents/data-ml/` |
| Integrations Engineer | `backend/app/integrations/`, `firebase/` | `company/agents/integrations/` |
| QA | `qa/` (+ runtime write to test directories) | `company/agents/qa/` |
| Security | `security/` | `company/agents/security/` |
| Performance Engineer | `performance/` | `company/agents/performance/` |
| DevOps | `infra/`, `.github/`, root files; cockpit repo application code | `company/agents/devops/` |
| SRE | `monitoring/` | `company/agents/sre/` |

---

*End of ownership map.*

---

---

# Part 2 — Reasoning and Flags

*This section is for the shadow-period review. It explains the genuine judgment calls, options I rejected, and boundaries I am not fully confident about. It does not travel to `company/ownership.md`.*

---

## Judgment calls

### 1. `design/` as a top-level Flutter package rather than `client/lib/design/`

**Options considered:**

- *A:* `design/` at the monorepo root — a separate Flutter Dart package, referenced from `client/` as a local path dependency.
- *B:* `client/lib/design/` — a subdirectory inside the Frontend Developer's territory, with UX/UI Designer owning that subdirectory.

**Why A:**  
Option B creates a subdirectory exception inside `client/` — the ownership map needs to list `client/lib/design/` explicitly as UX/UI Designer's, while everything else in `client/` is Frontend Developer's. That works mechanically but the seam is less visible.

Option A gives each role a clean top-level home. The UX/UI Designer owns everything in `design/` without any inheritance confusion, and the Frontend Developer owns everything in `client/` with the same clarity. The tradeoff is a cross-package dependency that Flutter handles natively through local path references in `pubspec.yaml`.

**What would make me revisit it:** if the UX/UI Designer role turns out to produce design specifications that Frontend Developer implements (rather than writing Flutter widgets directly), then there is no Flutter package to own at all and UX/UI's output belongs in `docs/product/` or similar. The spec says "delivered as Flutter theme and component specs" — I read "Flutter theme and component specs" as actual Flutter code, not Figma exports. If I have read that wrong, Option B or no `design/` directory at all is correct.

---

### 2. `backend/app/integrations/` as Integrations Engineer's territory inside Backend Developer's directory

**Options considered:**

- *A:* Integrations Engineer owns `backend/app/integrations/` as a subdirectory exception inside `backend/`.
- *B:* Backend Developer owns all of `backend/`, Integrations Engineer files change requests for integration code.
- *C:* `integrations/` at the monorepo root, owned by Integrations Engineer — a peer of `backend/` rather than a child.

**Why A:**  
The integration code is Python that runs in the same FastAPI process. It imports from and is imported by `backend/app/services/`. A top-level `integrations/` package (Option C) would be a Python package imported by the backend — technically possible but creates awkward import paths and blurs the boundary between application code and library code.

Option B gives Integrations Engineer no code territory at all and makes every line of integration code a change request. Integrations Engineer's mandate is ownership and maintenance of these adapters, not just authoring one batch and handing off.

Option A creates one sub-directory exception but a visible seam: `backend/app/integrations/` is consistently where all third-party adapters live. Backend Developer and Integrations Engineer have one well-defined interface between them.

**What I rejected:** I considered `integrations/` at the top level (Option C) more seriously. The objection is practical: in Python, a package at the monorepo root used by `backend/` requires either installing it as a development dependency or adding it to the Python path in `pyproject.toml`. That is manageable but it adds complexity. The sub-directory approach keeps imports natural (`from app.integrations.payments import PaymentClient`).

**What would make me revisit it:** if the payment gateway, Maps, SMS, and Firebase adapters turn out to be large enough codebases that they each deserve their own package — with versioning, separate test suites, and separate release cycles — then top-level packages per integration makes more sense. At that point, `integrations/` or `integrations/payments/`, `integrations/maps/` etc. at the root would be right.

---

### 3. `contracts/` owned by the Architect, not the Backend Developer

**The question:** the API contract is intimately connected to the backend implementation. Backend Developer understands what the API can actually do. Who should own the OpenAPI spec?

**Why Architect:**  
The contract is the seam between Backend and Frontend. If Backend Developer owns it, they can change it unilaterally — which is precisely the failure mode contract tests exist to catch. Architect ownership makes the ownership map itself enforce what the delivery pipeline already requires: any API contract change needs Architect design sign-off. Having the file and the approval gate owned by the same agent is consistent and removes the possibility that a Backend Developer edits the spec as a "documentation update" without triggering the design gate.

There is no extra friction here. The spec already says API contract changes require design sign-off. Architect owning `contracts/` means that rule is mechanically enforced at the file-write level, not just at the review stage.

**What I rejected:** co-ownership (Backend writes, Architect approves). The ownership map has one owner per directory, full stop. Co-ownership is not available as a concept.

---

### 4. Roles with no product monorepo directories (CEO, CTO, HR)

CEO, CTO, and HR have no product monorepo directories. Their work product — decisions, coordination, agent lifecycle management — lives in the cockpit repository's `company/` directory.

This is not an oversight. CTO coordinates work but does not write application code. CEO directs but does not build. HR manages agents but does not write product code. Giving them empty directories in the product monorepo would add noise to the map without adding value.

The risk: if the CTO role is ever asked to produce a technical decision that needs version-controlling alongside the product code (e.g., a formal RFC document), there is nowhere to put it without filing a change request. I have noted `company/plan.md` as CTO-owned in the cockpit repo; if the CTO needs a `docs/architecture/decisions/` folder that overlaps with Architect territory, that boundary should be revisited.

---

### 5. `firebase/` owned by Integrations Engineer, not DevOps

Firebase sits between integration and infrastructure. The rule configuration (Realtime Database security rules, Storage rules) is security-critical and closely tied to the application's data model. The Firebase project configuration is set up by whoever integrates Firebase.

I assigned `firebase/` to Integrations Engineer because: they define the security rules (which restrict access to location paths by job and by role), they configure the storage buckets for photos, and they write the Firebase Admin SDK adapter in `backend/app/integrations/`. These are integration concerns, not infrastructure concerns in the way that K8s manifests and CI pipelines are.

DevOps needs to deploy Firebase rules as part of the deployment pipeline. That is a change request to the Integrations Engineer for the rules files, and a DevOps-owned CI task that fires the `firebase deploy` command. The deployment mechanism lives in `.github/workflows/` (DevOps), the deployed artifacts live in `firebase/` (Integrations Engineer). This seam is clean.

**What would make me revisit it:** if the Firebase security rules become a point of frequent change-request friction between DevOps and Integrations, or if Security legitimately needs to own the access control rules (since they are security policy, not just integration config). Security's read-only runtime permission is the current answer; if that proves insufficient, Security could own `firebase/rules/` as a sub-directory exception.

---

### 6. `monitoring/` owned by SRE, not DevOps

DevOps sets up the monitoring infrastructure (installs Prometheus, Grafana, configures the log aggregator). SRE configures it (writes alerting rules, builds dashboards, defines SLOs). The distinction is: DevOps provides the platform, SRE operates on it.

Alert rules and dashboard definitions are SRE's operational judgment expressed as code. They need to own and evolve these without filing change requests to DevOps for every threshold change. `monitoring/` → SRE preserves that autonomy.

If SRE needs new monitoring infrastructure (a new exporter, a new scrape target), they file a change request to DevOps. That flow is correct: infrastructure decisions belong to DevOps, operational configuration belongs to SRE.

---

## Uncertain boundaries

These are the three boundaries I am least confident about. I flag them rather than present them as settled, because a stale-but-confident map is worse than an honest uncertain one.

**Uncertain 1: Data/ML Engineer ↔ Backend Developer on the ETA engine**

The ETA engine (`ml/`) produces predictions that the matching service (`backend/app/services/`) calls during every discovery request. The flow is: Backend Developer writes the matching service → it calls into `ml/eta_engine/` → Data/ML Engineer improves the model → Backend Developer benefits.

The risk: during Stage 4 development (discovery and booking), the matching service and ETA engine will evolve in lockstep. If Backend Developer needs to change the inference interface to support a new input (say, vehicle size as a duration factor), they must file a change request to Data/ML Engineer. If Data/ML Engineer changes the output shape of the ETA result, they must file a change request to Backend Developer. If this cross-direction flow is frequent, it signals the interface is inside the wrong seam.

**What would decide it:** if the ETA engine interface stabilises quickly after Stage 4 and changes are rare (good), this boundary is correct. If Backend Developer files multiple change requests per sprint to Data/ML Engineer throughout Stages 4–7, the ETA engine's inference interface should move into `backend/app/services/` (Backend Developer) with the model itself remaining in `ml/`. The model trains independently; the interface serves the backend.

I am not moving this now because the right placement is only knowable from observed change-request patterns. I am flagging it so the CTO and Architect know where to watch.

**Uncertain 2: UX/UI Designer's Flutter skill level**

The `design/` directory is only coherent if the UX/UI Designer writes Flutter Dart code. The spec says "delivered as Flutter theme and component specs." If "specs" means design documentation that Frontend Developer implements — rather than actual Dart files — then `design/` either does not exist or belongs to Frontend Developer, with UX/UI Designer owning only documentation in `docs/product/` or a separate design-assets directory.

I cannot resolve this from the spec alone. It depends on the brief written for the UX/UI Designer role, which does not exist yet.

**What would decide it:** the UX/UI Designer's brief. If that brief says they produce Figma files and component specifications that Frontend translates into code, `design/` should either be removed from the map or assigned to Frontend Developer. If the brief says they produce Flutter code, the current assignment stands.

**Uncertain 3: Product Manager's product monorepo presence**

I assigned `docs/product/` in the product monorepo to the Product Manager on the grounds that requirements and acceptance criteria should live near the code they describe. The alternative is that Product Manager's work lives entirely in `company/agents/product-manager/` in the cockpit repo — which is where the spec implies most non-coding agent output lands.

If the Product Manager's acceptance criteria are tracked in the cockpit repo alongside tasks and sprint planning, `docs/product/` in the product monorepo may be empty forever, and empty directories in the ownership map are noise that will drift.

I will flag this as pending the Product Manager's brief. If that brief says they write to the cockpit repo only, remove `docs/product/` from the product monorepo. If they produce living requirement documents that belong alongside the code, keep it.

---

## Held dependencies

**Data/ML Engineer's `company/agents/` path:** I have used `company/agents/data-ml/` in this map. The actual path depends on the naming convention chosen when the agent is created. The rule is `company/agents/{role-identifier}/`. The Architect does not own `company/` structure; HR or the cockpit setup process does. If the naming differs from `data-ml/`, update accordingly.

**UX/UI Designer's `company/agents/` path:** same issue — I used `company/agents/ux-designer/`. Verify against actual creation.

**`company/plan.md` interim ownership:** I assigned this to CTO because it is the technical specification and implementation plan. The CTO does not exist yet. Until the CTO exists, the CEO holds this document (as noted in the Architect brief's escalation section). The map reflects the intended steady-state, not the current interim.

**Geospatial approach:** the technical specification lists PostGIS versus Redis geo index versus hybrid as a decision deferred to Stage 1. That decision may add or alter directories in `backend/` (a PostGIS-heavy approach might warrant a `backend/app/services/geo/` directory) or in `infra/` (Redis configuration). The ownership map does not change — the directories land where the inheritance rule dictates — but it is worth noting that the geospatial decision is the next pending item with map implications.

---

## Open questions

1. **UX/UI Designer brief**: needed to confirm whether `design/` as a Flutter code package is correct, or whether the designer produces specifications that Frontend Developer implements.

2. **Product Manager's output location**: does the Product Manager write to the product monorepo (`docs/product/`), the cockpit repo only, or both? The brief will settle this.

3. **`company/agents/` naming convention**: what are the exact identifiers for each role's memory directory? The map uses guesses (`data-ml`, `ux-designer`). HR or DevOps should confirm and the map should be updated before agents are created.

4. **Voice provider for Stage 4b**: the spec notes that the in-progress additions escalation chain requires a voice provider not yet in the stack. When selected, its adapter will live in `backend/app/integrations/` → Integrations Engineer. No action needed now, but the Integrations Engineer brief should note this as a coming addition.

---

## What I would flag to the CEO

The map is internally consistent and covers all fifteen roles. The three uncertain boundaries above are the parts most likely to need redrawing within the first two sprints of Stage 4 development (specifically the ETA engine boundary). The CTO, once active, should watch the change-request volume on the `ml/` ↔ `backend/app/services/` seam and flag it to the Architect if it becomes high.

The UX/UI Designer boundary needs resolution before that agent is briefed and activated, because the brief either grants them write access to a `design/` Flutter package or it does not.

---

*End of report.*
