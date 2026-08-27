# Strategic Intelligence Project — V1 Card Specifications

## Purpose

This is the canonical executable contract for all 22 V1 Cards. It consolidates the original complete Card Specifications with all approved modernization and pre-mortem amendments.

## Execution Rules

Before every Card, reconcile AGENTS.md, PROJECT_CONTROL.md, architecture documents, this Roadmap/Specification, Evidence Map, Codex Execution Protocol, Golden Case Contract when relevant, repository reality, tests and Git.

Only one Card may be active. Do not implement future Cards early. User approval is required to start each Card and for architecture/scope changes, destructive/sensitive actions, commit/push/PR/merge/deployment.

For every Card:
- inspect first;
- preserve approved architecture;
- implement only bounded scope;
- add/run required tests and relevant regressions;
- run relevant baseline/evaluation or record N/A with reason when applicable;
- update Evidence and PROJECT_CONTROL;
- review diff/status;
- prove the exact Exit Gate;
- STOP on failure.

Status values: NOT_STARTED / IN_PROGRESS / BLOCKED / COMPLETE.

## V1-C05+ Forward Card Contract

V1-C05 onward uses this compact contract in addition to the existing bounded
requirements below. The existing `Goal` is the **Engineering Goal**; it, Scope,
Out of Scope, Dependencies, Tests / Evaluation, and Exit Gate remain the
authoritative Card requirements and are not broadened by this format.

Before the first implementation write, the active Card must make explicit:

1. **Engineering Goal** — the existing Card Goal.
2. **Learning Goal** — the specific engineering, AI, or software practice the
   Card will teach through its bounded work.
3. **Why It Exists** — the problem or prerequisite the Card resolves.
4. **Architecture Concept / Ownership Boundary** — the responsible component
   boundary; this references approved architecture and does not redefine it.
5. **Current System Before Card** — repository facts established by the
   mandatory Contract / Risk Map, not pre-filled assumptions.
6. **Design Decision** — the minimal in-scope decision selected after mapping;
   alternatives outside the Card remain deferred.
7. **Implementation Scope** and **Out of Scope** — the existing sections.
8. **Dependencies**, **Tests / Evaluation**, and **Exit Gate** — the existing
   sections.
9. **Critical-Path Expectation** — the smallest expected composed path that
   proves the Card's primary owned capability. It must be derived from actual
   implementation at closure and must not create a second Critical-Path gate.

The following forward-looking map defines the intended learning, rationale,
ownership boundary, and Critical-Path expectation without asserting current
implementation state. It applies only when the named Card is authorized.

| Card | Learning Goal / Why It Exists | Architecture Concept / Ownership Boundary | Critical-Path Expectation |
|---|---|---|---|
| C05 | Learn deterministic input and identity gates; prevent unsafe or ambiguous cases from entering research. | Case validation and entity-resolution boundary before research, with persistence through the repository owner. | Case input → validation → entity-resolution decision → persistence or blocked research entry. |
| C06 | Learn bounded, coverage-aware planning; turn a valid Case into explicit research work rather than ad hoc requests. | ResearchPlanner owns plan/task/coverage construction; providers only support its approved boundary. | Valid Case → bounded ResearchPlan → task/coverage validation. |
| C07 | Learn source-grounded company research; establish company findings without inventing later evidence/verification behavior. | Company-research component produces bounded findings through approved research/provider boundaries. | Company task → approved source/finding handling → typed research output or explicit gap. |
| C08 | Learn public, professional executive research with privacy limits. | Executive-research component owns executive findings and privacy filtering. | Executive task → public/professional boundary → typed output or explicit gap. |
| C09 | Learn Source → Evidence → Claim traceability. | Evidence layer owns the evidence/provenance foundation and preserves downstream fidelity inputs; C11 owns fidelity/verification judgment. | Finding/source → evidence validation → claim linkage or rejection. |
| C10 | Learn deterministic source-quality and freshness assessment. | Source-quality/freshness component owns classifications used by later verification. | Source → quality/freshness assessment → typed classification. |
| C11 | Learn claim verification without conflating it with research or governance. | Verification component owns Fidelity/Verification outcomes and gaps; C13 alone owns Governance restriction / RESTRICT. | Claim plus evidence → Fidelity/Verification result → VERIFIED/SUPPORTED/CONFLICTING/STALE/INSUFFICIENT_EVIDENCE or explicit gap. |
| C12 | Learn bounded correction research that terminates safely. | Follow-up orchestration owns attempt limits and terminal routing; research remains bounded. | Verification gap → bounded follow-up attempt → verified result, gap, or terminal limit. |
| C13 | Learn deterministic governance as a non-overridable trust boundary. | Governance owns PASS/RESTRICT/BLOCK decisions over verified inputs. | Candidate content → deterministic governance checks → allowed, restricted, or blocked output. |
| C14 | Learn enforcement of security/privacy boundaries around external input, providers, and artifacts. | Security controls own validation, redaction, permissions, and fail-closed outcomes. | Unsafe boundary input → deterministic rejection/redaction without unsafe downstream access. |
| C15 | Learn evidence-bounded strategic synthesis. | Strategic-analysis component consumes trusted compressed context, not raw uncontrolled sources. | Verified context → typed FACT/INFERENCE/RECOMMENDATION analysis with gaps preserved. |
| C16 | Learn brief generation that preserves governance, provenance, restrictions, and gaps. | Brief generator formats only approved governed material. | Governed analysis → brief generation → restriction/BLOCK visibility validation. |
| C17 | Learn a thin local UI boundary over validated application services. | UI adapts user input/output and owns no research, verification, or governance logic. | Valid local request → application boundary → safe Quick/Full/partial display. |
| C18 | Learn recovery from accepted persistence checkpoints only. | Recovery/orchestration owns resume selection; repository proves accepted state. | Interrupted run → accepted-checkpoint lookup → validated resume or safe fallback. |
| C19 | Learn safe, structured observability across the harness. | Observability/audit boundary records content-minimized events without altering authority. | Case/run/stage event → redacted structured audit trace. |
| C20 | Learn evaluation against owned Golden Case evidence rather than subjective quality claims. | Evaluation contract owns fixtures, rubric, and comparison results. | Golden Case input → measured pipeline outputs → rubric/traceability verdict. |
| C21 | Learn disciplined defect hardening and regression protection. | Each defect is repaired at its owning boundary with regression evidence. | Reproduced defect → bounded owning-boundary fix → focused and regression proof. |
| C22 | Learn reproducible engineering closure and accurate project communication. | Documentation/demo boundary reports verified behavior without changing runtime authority. | Clean setup/review path → documented commands/evidence → reproducibility verdict. |

The Card-specific **Current System Before Card** and **Design Decision** are
recorded from the active Card's inspect-first evidence; they cannot be inferred
or marked complete before that inspection. The actual Critical-Path execution,
commands, and result belong in `14_CARD_EVIDENCE_MAP.md`.

# V1-C01 — Repository Baseline

## Goal
Create a clean, testable project foundation.

## Dependencies
None

## Implementation Scope and Requirements
Project structure; Python environment/dependencies; central configuration; .env.example; .gitignore; logging; test structure; documentation placement; harness/evaluation artifact conventions.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Package import; configuration load; test runner; secrets ignored; repository/Git review; harness boundary documented.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Foundation is stable enough for typed domain models.

# V1-C02 — Domain Models

## Goal
Implement application-owned typed contracts for the V1 workflow.

## Dependencies
V1-C01

## Implementation Scope and Requirements
Case, Company, Executive, WorkflowRun, ResearchPlan, ResearchTask, RawFinding, Source, Evidence, Claim, ClaimEvidenceLink, VerificationResult, StrategicAnalysis, GovernanceDecision, MeetingBrief, AuditEvent, WorkflowError; explicit enums, IDs, timestamps and serialization.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Valid/invalid construction; enum rejection; required fields; serialization; relationship identifiers.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Later Cards can exchange structured application-owned data without free-form/provider-specific contracts.

# V1-C03 — Persistence Foundation

## Goal
Implement local persistence behind repository interfaces.

## Dependencies
V1-C02

## Implementation Scope and Requirements
SQLite; repository contracts/implementations; ArtifactStore; schema/migrations; Case/run and Source/Evidence/Claim persistence; transaction-safe writes; accepted-checkpoint metadata and validation.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
CRUD; relationships; rollback; artifact read/write; path traversal; duplicate basics; persistence/invariant failure prevents checkpoint acceptance.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Workflow state can survive process termination through safe persistence.

# V1-C04 — Provider Foundation

## Goal
Create vendor-independent AI/search capability boundaries.

## Dependencies
V1-C01, V1-C02

## Implementation Scope and Requirements
LLMProvider; SearchProvider; factory/composition; Ollama adapter; search adapter; fake providers; normalized errors/timeouts; narrow capability injection; provider observability metadata; no silent cloud fallback.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Contract/factory tests; error normalization; timeout; Ollama/search integration where configured; no-silent-fallback.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Core components operate through provider interfaces without vendor coupling.

# V1-C05 — Case Input and Validation

## Goal
Create the validated root Case and resolve target identity before research.

## Dependencies
V1-C02, V1-C03

## Implementation Scope and Requirements
Required company/executive/meeting goal; optional URLs/context; safe URL validation; persistence; Entity Resolution Gate for company, executive and executive↔company relationship; ambiguity blocks unrestricted deep research.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Valid/missing fields; invalid URL; persistence; same-name executive; moved executive; conflicting URL; ambiguous company/business unit.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Invalid or unresolved/unsafe Cases cannot enter unrestricted research.

# V1-C06 — Research Planner

## Goal
Convert a valid Case into a bounded meeting-focused ResearchPlan with explicit coverage.

## Dependencies
V1-C04, V1-C05

## Implementation Scope and Requirements
Company/executive tasks; meeting-goal intent; priorities; approved categories; task/attempt budgets; Research Coverage Contract with COVERED/PARTIAL/NOT_FOUND/UNAVAILABLE/NOT_RELEVANT; privacy boundary.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Valid plan; task separation; limits; invalid task/privacy rejection; fake LLM structured output; coverage/high-priority gap behavior.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Research receives a valid bounded plan and completion is coverage-aware, not result-count driven.

# V1-C07 — Company Research

## Goal
Produce structured source-linked company intelligence.

## Dependencies
V1-C04, V1-C06

## Implementation Scope and Requirements
Overview; strategy; projects/case studies; AI activity; products/services; partnerships; investments/acquisitions; hiring; news/events; permitted professional signals; source preservation; relevance and blocked-source handling.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Structured findings; empty/duplicate/blocked results; relevance filtering; project discovery; source-reference preservation.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Company research reliably produces traceable meeting-relevant findings.

# V1-C08 — Executive Research

## Goal
Produce relevant public professional intelligence about the target executive.

## Dependencies
V1-C04, V1-C06

## Implementation Scope and Requirements
Role/responsibilities; relevant background/focus; articles/interviews/events/projects; professional activity; company-strategy connection; identity disambiguation; LinkedIn optional; no sensitive inference/scraping.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Structured findings; ambiguous identity; missing LinkedIn; personal-data rejection; source preservation; fact/inference behavior.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Executive research is useful while preserving the public-professional-relevant boundary.

# V1-C09 — Evidence Layer

## Goal
Create a traceable Source → Evidence → Candidate Claim foundation with fidelity inputs.

## Dependencies
V1-C03, V1-C07, V1-C08

## Implementation Scope and Requirements
Source normalization; Evidence extraction; candidate Claims; ClaimEvidenceLink SUPPORTS/CONTRADICTS/CONTEXT; duplicates; preserve enough Evidence→Candidate Claim context for Fidelity evaluation.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Evidence requires Source; many-to-many links; multiple/contradictory evidence; duplicates; broken traceability; fidelity input preservation.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Important findings are traceable to Sources and ready for fidelity/verification.

# V1-C10 — Source Quality and Freshness

## Goal
Provide deterministic source-quality/freshness metadata for Verification.

## Dependencies
V1-C09

## Implementation Scope and Requirements
PRIMARY/STRONG_SECONDARY/OTHER; publication/retrieval dates; freshness/unknown; origin/duplicate signals.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Primary/secondary classification; missing date; stale evidence; publication/retrieval separation; duplicate-origin.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Verification receives reliable source-quality and freshness inputs.

# V1-C11 — Verification Engine

## Goal
Evaluate factual Claims against Evidence after Evidence Fidelity checking.

## Dependencies
V1-C09, V1-C10

## Implementation Scope and Requirements
Fidelity statuses SUPPORTED_BY_EVIDENCE/PARTIALLY_SUPPORTED/NOT_SUPPORTED/AMBIGUOUS; verification VERIFIED/SUPPORTED/CONFLICTING/STALE/INSUFFICIENT_EVIDENCE; source independence/conflict/sufficiency; labeled baseline fixtures.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Fidelity fixtures; overstrong/not-supported claims; strong primary/secondary; independent confirmation; duplicate origin; conflict; stale; missing evidence; expected-vs-actual baseline.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Unsupported/overstrong facts cannot be promoted to trusted factual intelligence and baseline evidence is recorded.

# V1-C12 — Bounded Follow-Up Research

## Goal
Allow Verification to request targeted additional research without autonomous loops.

## Dependencies
V1-C07, V1-C08, V1-C11

## Implementation Scope and Requirements
Important weak Claim → focused ResearchTask → Evidence → reverification; configurable attempts; audit trail; abstention after limit.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Follow-up strengthens; finds nothing; max attempts; termination; persisted attempt/audit state.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Research-more behavior is bounded and deterministic at workflow level.

# V1-C13 — Governance Gate

## Goal
Implement the deterministic non-overridable trust boundary before user-facing intelligence.

## Dependencies
V1-C11

## Implementation Scope and Requirements
PASS/RESTRICT/BLOCK; FACT requires Evidence; Evidence requires Source; fidelity/trust invariants; inference cannot silently become fact; BLOCK excluded; RESTRICT preserved; privacy; external content no authority; fail closed; reason codes/persistence.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
FACT without Evidence; Evidence without Source; misclassified inference; conflict/stale restriction; personal-data block; governance failure blocks Brief; reason-code persistence.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Trust rules are demonstrably stronger than model output and cannot be overridden by AI.

# V1-C14 — Security Boundaries

## Goal
Implement V1 controls for safely researching untrusted public sources.

## Dependencies
V1-C04, V1-C05, V1-C07, V1-C08, V1-C13

## Implementation Scope and Requirements
Secret isolation; URL validation; SSRF/redirect protection where fetching exists; safe paths; prompt-injection isolation; least privilege; log redaction; no silent cloud fallback; no access-control bypass.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Malformed/unsupported/private URL; redirect-to-private; path traversal; prompt injection; secret leakage; no silent fallback; personal-data filtering.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: External research cannot bypass application security/governance boundaries.

# V1-C15 — Strategic Analysis

## Goal
Convert governed intelligence into meeting-relevant strategic reasoning using controlled context.

## Dependencies
V1-C11, V1-C13

## Implementation Scope and Requirements
Company direction; executive priorities; project meaning; signals; opportunities; user relevance; topics/questions/risks/gaps; FACT/INFERENCE/RECOMMENDATION; Context Budget/Compression from ranked verified/restricted Claims and Evidence summaries; preserve provenance/conflicts/freshness/restrictions.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Controlled fixture; no invented facts/user background; conflict/gap preservation; meeting relevance; compression retains critical restricted/conflicting evidence.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Strategic reasoning adds value without destroying evidence/trust boundaries.

# V1-C16 — Brief Generator

## Goal
Generate trustworthy Quick and Full Briefs from governed intelligence.

## Dependencies
V1-C13, V1-C15

## Implementation Scope and Requirements
Rank/select/summarize/organize only; no research/new unsupported facts; no BLOCK reintroduction; preserve RESTRICT and fact/inference; Quick Brief; Full Brief with evidence/sources and gaps.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
BLOCK leakage=0; RESTRICT preserved; unsupported fact test; gaps/sources; Quick/Full structure.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Both Briefs are trustworthy, traceable and useful.

# V1-C17 — Minimal Local UI

## Goal
Make V1 usable locally without direct Python invocation.

## Dependencies
V1-C05, V1-C16

## Implementation Scope and Requirements
Thin local UI for Case input, workflow status, Quick/Full Brief, errors and Knowledge Gaps; no business logic/polish expansion.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Valid submission; validation error; completed/partial/failed result.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: A user can execute the approved V1 workflow locally.

# V1-C18 — Workflow Recovery

## Goal
Prove safe recovery from validated accepted checkpoints.

## Dependencies
V1-C03, V1-C16

## Implementation Scope and Requirements
Stage action → required persistence → invariant/schema validation → checkpoint acceptance → recovery; accepted-only resume; fallback from invalid latest checkpoint; no trust-stage skip; bounded counters; duplicate/idempotent safety.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Persistence failure; invariant failure; recovery from accepted checkpoint; invalid latest fallback; resume after Research/Evidence/Verification/Governance; idempotent/duplicate-safe resume.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Interrupted work resumes from the last accepted safe checkpoint without corrupting trust state.

# V1-C19 — Observability and Audit

## Goal
Make Harness execution reconstructable and measurable.

## Dependencies
V1-C03, V1-C04, V1-C13

## Implementation Scope and Requirements
Structured run/case/stage/node/attempt/provider/tool/checkpoint/verification/governance/duration/failure/evaluation identifiers; performance baseline: total/stage duration, searches, provider calls, retries/follow-ups, retained sources/claims; redaction.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Audit/verification/governance/retry/error events; secret redaction; checkpoint accept/reject trace; performance metrics recorded.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: A developer can answer what happened, why, and how the run performed without exposing secrets.

# V1-C20 — Golden Case

## Goal
Prove V1 on one real company, executive and meeting goal using the Golden Case Contract.

## Dependencies
V1-C07 through V1-C19

## Implementation Scope and Requirements
Complete pipeline; Ground Truth; entity resolution; coverage/recall; fidelity; verification; governance; context preservation; strategic insight; Quick/Full Brief; performance baseline; accumulated baseline comparison.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Golden Case Contract manual/automated checks; traceability; usefulness rubric; runtime/performance; regressions.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: Golden Case passes mandatory trust invariants and demonstrates real meeting-preparation value.

# V1-C21 — Hardening and Regression

## Goal
Fix confirmed integration/Golden Case defects without feature expansion.

## Dependencies
V1-C20

## Implementation Scope and Requirements
Bugs; governance/research/verification/security/recovery/duplicate/error/Brief defects only; root-cause fixes; one-variable changes where practical; compare quality-affecting fixes to baseline.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Relevant full regression; critical-bug tests; governance/security regressions; baseline comparison.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: No known critical V1 defect remains and relevant quality baselines do not regress.

# V1-C22 — Documentation and Demo Readiness

## Goal
Make V1 reproducible, self-explanatory and portfolio/demo ready.

## Dependencies
V1-C21

## Implementation Scope and Requirements
README; setup/local run; architecture index; provider config; tests; limitations; V1 scope; security/governance; Golden Case/demo; current status; V2 parking lot; reproducible final evidence.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Any feature not required by this Card or the approved V1 scope; future-Card implementation; silent architecture expansion.

## Required Tests / Evaluation
Fresh-environment instructions reviewed; commands/links verified; limitations accurate; final tests/tree/evidence reviewed.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: A future developer/Codex session can reproduce and understand V1 without reconstructing decisions from chat history.

# Final V1 Gate

C22 does not itself authorize V1 COMPLETE. Final status also requires the mandatory gates in the Test & Evaluation Plan, Roadmap, Evidence Map, Golden Case Contract, AGENTS.md and PROJECT_CONTROL.md to agree with repository reality.
