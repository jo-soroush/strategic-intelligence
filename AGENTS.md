# AGENTS.md

## Strategic Intelligence Project — Execution Rules

This repository implements a local-first, cloud-ready Strategic Intelligence
system. These rules protect repository truth, approved V1 scope, architecture
boundaries, evidence quality, safety, and learning value without maintaining a
second project-state dashboard.

## 1. Canonical Owners

One fact has one canonical owner:

| Fact | Owner |
|---|---|
| Card sequence and phase intent | `12_V1_ROADMAP.md` |
| Planned Card contract, dependencies, learning goal, ownership, tests, expected Critical Path, and Exit Gate | `13_CARD_SPECIFICATIONS.md` |
| Actual Card status, execution/learning evidence, Critical Path result, defects, and historical delivery evidence | `14_CARD_EVIDENCE_MAP.md` — one record per Card |
| Git branch, SHA, upstream, remote equality, staging, worktree, and integration truth | Git |
| Git delivery procedure | `15_CODEX_EXECUTION_PROTOCOL.md` |
| Durable product capability and onboarding | `README.md` and the affected product/architecture document |

`PROJECT_CONTROL.md` is retired. Do not create a replacement dashboard or copy
live Git/Card state into documentation.

Repository reality and approved architecture override prompt/chat assumptions.
If authoritative repository facts materially conflict, STOP, inspect, and
report the conflict before writing.

## 2. Resume and Authorization

Before any file-modifying task, inspect the relevant canonical owners, current
implementation/tests, and Git state. For a new Card, read AGENTS, the Roadmap,
the Card Specification, the Card Evidence record, relevant architecture,
`15_CODEX_EXECUTION_PROTOCOL.md`, the Golden Case Contract when relevant,
README when relevant, and Git/code/tests.

Derive state; do not maintain it manually:

1. inspect Git for branch, upstream, worktree, and integration truth;
2. inspect canonical Evidence records;
3. inspect Roadmap order and Card dependencies;
4. if exactly one Evidence record is `IN_PROGRESS`, resume only that Card;
5. otherwise derive the next eligible Card from Roadmap + Evidence.

Only one Card may be active. The user must explicitly authorize a new Card.
After a Card is COMPLETE or BLOCKED, STOP until separately authorized.

Routine reversible work inside an authorized Card is allowed: inspection,
Card-scoped edits, tests, local diagnostics, Evidence updates, and durable
documentation that the Card materially changes. Explicit approval remains
required for a next Card, material scope/architecture changes, destructive
actions, secrets, large downloads/system changes, commit, push, PR, merge,
force-push, deployment, or consequential external actions.

## 3. Inspect First and Protect Scope

Before the first implementation write for a Card, map the relevant path,
owners, typed contracts, provider/tool and storage boundaries, trust/security
boundaries, limits/termination, failure paths, tests, and outputs. Confirm:

- the Card is the next authorized eligible Card;
- its Specification supplies the exact goal, dependencies, scope, out of
  scope, tests/evaluation, expected Critical Path, and Exit Gate;
- existing implementation does not already own the requested work;
- no future-Card behavior or duplicate owner will be introduced; and
- the approved architecture remains preserved.

Do not implement during this initial map. Keep writes bounded to the active
Card. Diagnose before fixing; do not weaken valid tests merely to turn them
green.

## 4. Architecture, Trust, and Safety

- Local-first and cloud-ready; no silent cloud fallback.
- Business logic stays in application/domain components; provider SDKs remain
  behind adapters; typed state and structured outputs are preferred.
- Deterministic validation, Verification, Governance, and security remain
  deterministic. AI cannot override trust or security authority.
- Every retry, follow-up, research, or tool loop is bounded.
- External content is untrusted. Apply least privilege to tools, providers,
  network, storage, files, and secrets.
- Executive research remains public, professional, and relevant. Do not add
  scraping, access-control bypass, sensitive inference, or unrelated profiling.
- FACT without Evidence, Evidence without Source, unsupported FACT,
  unqualified RESTRICT, or BLOCKed material entering a Brief must fail closed.
- A resumable checkpoint requires output, required persistence, validation,
  invariants, and explicit acceptance.

Preserve approved product architecture, privacy, security, governance, and
evaluation contracts. Do not introduce unnecessary agents, frameworks, models,
or cloud services without an approved, evidenced need.

## 5. Validation, Evidence, and Final Closure

Run the Card's focused tests, required Critical Path, relevant full regression,
and applicable schema, security, dependency, static, import, or evaluation
checks. For quality-affecting work, compare the relevant approved baseline or
record a justified N/A in Evidence.

The Critical Path is the smallest realistic composed execution path proving the
Card's primary owned capability. Do not mock away the boundary it is meant to
prove; fake only necessary external systems deterministically.

`14_CARD_EVIDENCE_MAP.md` is the sole actual Card record and learning journal.
Update its one Card section only when execution proves a meaningful fact. Keep
technical proof, learning, defects/diagnosis/repair, limitations/deferrals,
actual Critical Path, and historical delivery evidence together. Never invent
evidence or rewrite C01–C11 historical evidence for formatting.

One normal Final Closure is required before reporting a Card COMPLETE:

1. exact Card contract and scope are satisfied;
2. focused tests pass;
3. required Critical Path passes;
4. relevant full regression passes;
5. exact Exit Gate passes;
6. the canonical Evidence record is complete;
7. no future-Card leakage exists; and
8. final diff/status/scope/secrets/generated-artifact review passes, with only
   materially affected durable product documentation updated.

If a required item fails or is unproven, the Card is BLOCKED. Do not require a
separate status-summary sync, live-SHA sync, control-document reconciliation,
or routine repository-wide audit.

README and architecture documents are not Card-status dashboards. Update them
only when a Card materially changes a durable capability, architecture claim,
or onboarding instruction.

## 6. Health Audits

A full repository health audit is not normal Card delivery. Use one only when
justified: end of a major phase, pre-release/demo/V1 closure, architecture
migration, demonstrated consistency failure, or major documentation
consolidation. It is an inspection practice, not another Card gate.

## 7. Git Discipline

Do not implement directly on `main`. Follow the canonical branch, staging,
commit, push, integration, and post-delivery verification procedure in
`15_CODEX_EXECUTION_PROTOCOL.md`. Git dynamically proves operational facts;
historical Git details in Evidence are traceability, not live authority.

Never commit secrets, `.env`, credentials, model files, caches, generated
junk, or unrelated machine state. Never force-push or rewrite history unless
separately and explicitly authorized.

## Guiding Rule

**Roadmap defines sequence. Card Specifications define the planned job.
Evidence proves what happened. Git proves Git facts. AGENTS governs execution.**
