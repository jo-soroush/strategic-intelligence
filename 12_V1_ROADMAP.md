# Strategic Intelligence Project — V1 Roadmap

## Purpose

This roadmap owns V1 Card sequence and phase intent. It is not a live-status
dashboard or a duplicate Card contract. `13_CARD_SPECIFICATIONS.md` owns each
Card's dependencies, scope, tests, ownership boundary, learning goal, Critical
Path expectation, and exact Exit Gate. `14_CARD_EVIDENCE_MAP.md` owns actual
Card status and execution evidence.

## V1 Scope Freeze

V1 delivers one local-first meeting-intelligence workflow from Company +
Executive + Meeting Goal to Quick Brief + Full Brief. It excludes continuous
monitoring, alerts, CRM, multi-user/enterprise dashboard, automated LinkedIn
scraping, autonomous agent teams, multi-model routing, cloud deployment, MCP
runtime dependency, automated outreach, and enterprise RBAC unless a formally
approved scope change proves it necessary.

## Phase 1 — Foundation and Research (C01–C08)

| Card | High-level delivery intent |
|---|---|
| V1-C01 — Repository Baseline | Establish a clean, testable project foundation. |
| V1-C02 — Domain Models | Establish application-owned typed workflow contracts. |
| V1-C03 — Persistence Foundation | Provide safe local persistence and resumable state. |
| V1-C04 — Provider Foundation | Establish vendor-independent AI/search boundaries. |
| V1-C05 — Case Input and Validation | Validate the root Case and resolve target identity. |
| V1-C06 — Research Planner | Create bounded, meeting-focused research plans. |
| V1-C07 — Company Research | Produce traceable company findings. |
| V1-C08 — Executive Research | Produce useful public-professional executive findings. |

## Phase 2 — Evidence, Verification, Governance, and Security (C09–C14)

| Card | High-level delivery intent |
|---|---|
| V1-C09 — Evidence Layer | Establish Source → Evidence → Claim traceability. |
| V1-C10 — Source Quality and Freshness | Classify source quality and freshness deterministically. |
| V1-C11 — Verification Engine | Evaluate factual Claims against Evidence after Fidelity checking. |
| V1-C12 — Bounded Follow-Up Research | Request targeted additional research without autonomous loops. |
| V1-C13 — Governance Gate | Apply deterministic non-overridable trust decisions. |
| V1-C14 — Security Boundaries | Enforce external-input, provider, and artifact boundaries. |

## Phase 3 — Product Completion and Hardening (C15–C22)

| Card | High-level delivery intent |
|---|---|
| V1-C15 — Strategic Analysis | Produce evidence-bounded strategic synthesis. |
| V1-C16 — Brief Generator | Produce trustworthy, traceable meeting briefs. |
| V1-C18 — Workflow Execution and Recovery | Provide the application workflow boundary, then resume only from accepted safe checkpoints. |
| V1-C17 — Minimal Local UI | Provide a thin local interface over the completed workflow boundary. |
| V1-C19 — Observability and Audit | Explain what happened, why, and how a run performed. |
| V1-C20 — Golden Case | Evaluate real meeting-preparation value against trust invariants. |
| V1-C21 — Hardening and Regression | Repair known defects and protect quality baselines. |
| V1-C22 — Documentation and Demo Readiness | Make V1 reproducible and explainable without chat reconstruction. |

Execution order follows this table. C18 deliberately precedes C17 because the
UI must invoke C18's application-owned workflow boundary; Card identifiers are
preserved for traceability.

## Final V1 Intent

V1 is complete only when its Cards have delivered the approved local-first
workflow and the final V1 contract is proven. Actual completion evidence is
recorded only in `14_CARD_EVIDENCE_MAP.md`.

## V1.2 — Persistent Intelligence Memory and GraphRAG

V1.2 is an authorized extension after V1 completion. It preserves V1/V1.1
trust, governance, local-first, and evidence semantics. The eight Cards are
strictly sequential; no later Card may start before its predecessor completes:

| Card | High-level delivery intent | Dependency |
|---|---|---|
| V1.2-G01 — Graph Intelligence Contract | Bound entities, relations, memory/refresh, temporal provenance, conflicts, query categories, evaluation, and non-goals. | None |
| V1.2-G02 — Persistent Company Memory | Persist user-selected companies in order, reusable research artifacts, exact/normalized company duplicates, and memory-first explicit Refresh behavior. | G01 |
| V1.2-G03 — Entity Resolution | Create stable identities and conservative alias/ambiguity handling for Company, Person, Technology, Project, and Event. | G02 |
| V1.2-G04 — Governed Relationship Extraction | Extract only bounded, evidence-backed relations with Source→Evidence→Claim→Verification→Governance provenance, temporal support, and conflict handling. | G03 |
| V1.2-G05 — Knowledge Graph Persistence | Persist an incremental, idempotent, restart-safe graph projection without creating a second trust store. | G04 |
| V1.2-G06 — Evidence-backed GraphRAG | Resolve question entities, retrieve bounded graph paths, assemble supporting evidence/context, and generate qualified answers without automatic web research. | G05 |
| V1.2-G07 — Graph Intelligence UI | Expose ordered memory, company intelligence, connections, graph inspection, provenance, Ask Graph, and explicit Refresh. | G06 |
| V1.2-G08 — Evaluation and Portfolio Evidence | Evaluate GraphRAG against a truthful non-graph baseline and produce reproducible technical/portfolio evidence. | G07 |

G02 reuses existing V1 Source, Evidence, Claim, Verification, Governance,
WorkflowRun, checkpoint, and audit records. G03/G04 add entity/relationship
projections; G05 owns only graph projection storage. New relationship records
use `relationship_id`, `research_run_id`, `created_at`, optional `valid_from`,
`valid_to`, `superseded_by`, and `temporal_status` (`CURRENT`, `STALE`,
`CONFLICTING`, `SUPERSEDED`). BLOCK content is never usable graph knowledge.

V1.2 completion requires all eight Cards and their recorded Exit Gates. Actual
status and execution evidence remain owned exclusively by
`14_CARD_EVIDENCE_MAP.md`.
