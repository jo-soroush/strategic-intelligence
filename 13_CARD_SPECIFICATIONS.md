# Strategic Intelligence Project — V1 Card Specifications

## Purpose

This is the canonical executable contract for all 22 V1 Cards. It consolidates the original complete Card Specifications with all approved modernization and pre-mortem amendments.

## Execution Rules

Before every Card, reconcile AGENTS.md, architecture documents, this Roadmap,
the relevant Card Specification and Evidence record, Git Workflow, Golden Case
Contract when relevant, repository reality, tests, and Git.

Only one Card may be active. Do not implement future Cards early. User approval is required to start each Card and for architecture/scope changes, destructive/sensitive actions, commit/push/PR/merge/deployment.

For every Card:
- inspect first;
- preserve approved architecture;
- implement only bounded scope;
- add/run required tests and relevant regressions;
- run relevant baseline/evaluation or record N/A with reason when applicable;
- update canonical Evidence;
- review diff/status;
- prove the exact Exit Gate;
- STOP on failure.

Status values: NOT_STARTED / IN_PROGRESS / BLOCKED / COMPLETE.

## Planned-Contract Rule

Each detailed Card section below is its one authoritative planned contract.
Its Goal is the Engineering Goal; its Scope, Out of Scope, Dependencies, Tests
/ Evaluation, and Exit Gate are exact. For C05 onward, the compact duplicate
overlay has been consolidated into the Card's own planned learning, ownership,
and expected Critical-Path fields. Current-system facts, design decisions, and
actual Critical-Path execution belong only in the Card's Evidence record.

## Cross-Card Composition Rule

When a Card creates, consumes, or changes a trust, security, provider,
persistence, or cross-Card boundary, its planned contract must identify the
material composition surface and require an executable Critical Path or
regression for it. The scope is risk-proportionate and does not create a new
delivery stage.

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

## Planned Learning, Ownership, and Critical Path
Learn deterministic input and identity gates; Case validation/entity resolution owns the boundary before research and persistence; Case input → validation → entity-resolution decision → persistence or blocked research entry.

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

## Planned Learning, Ownership, and Critical Path
Learn bounded, coverage-aware planning; ResearchPlanner owns plan/task/coverage construction while providers only support its approved boundary; Valid Case → bounded ResearchPlan → task/coverage validation.

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

## Planned Learning, Ownership, and Critical Path
Learn source-grounded company research; the company-research component owns bounded findings through approved research/provider boundaries; Company task → approved source/finding handling → typed research output or explicit gap.

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

## Planned Learning, Ownership, and Critical Path
Learn public, professional executive research with privacy limits; executive research owns findings and privacy filtering; Executive task → public/professional boundary → typed output or explicit gap.

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

## Planned Learning, Ownership, and Critical Path
Learn Source → Evidence → Claim traceability; the Evidence layer owns provenance and downstream fidelity inputs while C11 owns fidelity/verification judgment; Finding/source → evidence validation → claim linkage or rejection.

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

## Planned Learning, Ownership, and Critical Path
Learn deterministic source-quality/freshness assessment; this component owns classifications used by later verification; Source → quality/freshness assessment → typed classification.

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

## Planned Learning, Ownership, and Critical Path
Learn verification without conflating it with research or governance; Verification owns Fidelity/Verification outcomes and gaps while C13 alone owns Governance restriction / RESTRICT; Claim plus evidence → Fidelity/Verification result → VERIFIED/SUPPORTED/CONFLICTING/STALE/INSUFFICIENT_EVIDENCE or explicit gap.

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

## Planned Learning, Ownership, and Critical Path
Learn bounded correction research that terminates safely; follow-up orchestration owns attempt limits and terminal routing; Verification gap → bounded follow-up attempt → verified result, gap, or terminal limit.

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

## Planned Learning, Ownership, and Critical Path
Learn deterministic governance as a non-overridable trust boundary; Governance owns PASS/RESTRICT/BLOCK decisions over verified inputs; Candidate content → deterministic governance checks → allowed, restricted, or blocked output.

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

## Planned Learning, Ownership, and Critical Path
Learn enforcement of security/privacy boundaries; security controls own validation, redaction, permissions, and fail-closed outcomes; Unsafe boundary input → deterministic rejection/redaction without unsafe downstream access.

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

## Planned Learning, Ownership, and Critical Path
Learn evidence-bounded strategic synthesis; Strategic Analysis consumes trusted compressed context rather than raw uncontrolled sources; Verified context → typed FACT/INFERENCE/RECOMMENDATION analysis with gaps preserved.

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

## Planned Learning, Ownership, and Critical Path
Learn brief generation that preserves governance, provenance, restrictions, and gaps; the Brief generator formats only approved governed material; Governed analysis → brief generation → restriction/BLOCK visibility validation.

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

## Planned Learning, Ownership, and Critical Path
Learn a thin local UI boundary over validated application services; UI adapts
input/output and owns no workflow sequencing, research, verification, or
governance logic; Valid local request → C18 application workflow boundary →
typed workflow result → safe Quick/Full/partial display.

## Dependencies
V1-C05, V1-C16, V1-C18

## Implementation Scope and Requirements
Thin local UI for Case input, C18 workflow invocation/status, Quick/Full Brief,
typed errors, Knowledge Gaps, restrictions, and omission disclosure; no
business logic/polish expansion.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Workflow sequencing, retry/resume, repository coordination, provider calls,
Case-validation rules, Verification, Governance, Strategic Analysis, Brief
generation, and any future-Card implementation.

## Required Tests / Evaluation
Valid submission; validation error; completed/partial/failed result.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: A user can execute the approved V1 workflow locally.

# V1-C18 — Workflow Execution and Recovery

## Goal
Provide an application-owned bounded workflow boundary and prove safe recovery
from validated accepted checkpoints.

## Planned Learning, Ownership, and Critical Path
Learn bounded first-run execution and recovery from accepted persistence
checkpoints; the workflow orchestrator sequences existing typed services,
owns routing/termination and resume selection, and the repository proves
accepted state. First run: validated Case → research → Evidence/Claims →
Verification → bounded Follow-Up as required → Governance → Strategic Analysis
→ Brief Generator → typed workflow result. Recovery: interrupted run →
accepted-checkpoint lookup → validated resume or safe fallback.

## Dependencies
V1-C03, V1-C05, V1-C16

## Implementation Scope and Requirements
Application-owned first-run workflow entry point; explicit stage action →
required persistence → invariant/schema validation → checkpoint acceptance;
accepted-only resume; fallback from invalid latest checkpoint; no trust-stage
skip; bounded counters; duplicate/idempotent safety. It sequences existing
authorities and preserves their typed outputs/states without a trust upgrade.

All implementation must use application-owned typed contracts, deterministic controls where behavior is objectively checkable, bounded retries/loops, least-privilege capabilities, safe failure, and existing architecture owners. Provider-specific objects must not leak into domain contracts. External content remains untrusted.

## Out of Scope
Case-validation rules, research semantics, provenance, source quality/freshness,
Verification, Follow-Up decision authority, Governance decisions, security
policy, Strategic Analysis, Brief generation, UI presentation, and any
future-Card implementation.

## Required Tests / Evaluation
Real composed first-run path through the implemented application services;
persistence failure; invariant failure; recovery from accepted checkpoint;
invalid latest fallback; resume after Research/Evidence/Verification/Governance;
idempotent/duplicate-safe resume; and proof that orchestration preserves C05,
C03, C09–C16 authority boundaries. BLOCK is proved at the owning C13→C15→C16
trust boundary when upstream controls intentionally prevent an unsafe BLOCK input
from reaching normal C18 first-run candidate flow; C18 must prove no bypass,
reinterpretation, or recovery resurrection. C12 routing is proved across its
legitimate lifecycle states: unresolved eligible Verification invokes C12, while
a persisted/resumed resolved-current state does not; C12 never authorizes use.

Run relevant existing regression tests. For AI/routing/trust/recovery/quality-affecting Cards, execute the applicable baseline/evaluation or explicitly record N/A with reason.

## Evidence Required
Record actual implementation locations, tests/commands and results, relevant evaluation/baseline identifiers/results, known issues/blockers, diff/status review, and exact Exit Gate proof in `14_CARD_EVIDENCE_MAP.md`. Never invent evidence.

## Exit Gate
PASS only when: An application-owned workflow boundary safely executes the
approved first-run V1 path and interrupted work resumes from the last accepted
safe checkpoint without corrupting trust state.

# V1-C19 — Observability and Audit

## Goal
Make Harness execution reconstructable and measurable.

## Planned Learning, Ownership, and Critical Path
Learn safe structured observability; the observability/audit boundary records content-minimized events without altering authority; Case/run/stage event → redacted structured audit trace.

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

## Planned Learning, Ownership, and Critical Path
Learn evaluation against owned Golden Case evidence rather than subjective quality claims; the evaluation contract owns fixtures, rubric, and comparisons; Golden Case input → measured pipeline outputs → rubric/traceability verdict.

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

## Planned Learning, Ownership, and Critical Path
Learn disciplined defect hardening and regression protection; each defect is repaired at its owning boundary with regression evidence; Reproduced defect → bounded owning-boundary fix → focused and regression proof.

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

## Planned Learning, Ownership, and Critical Path
Learn reproducible engineering closure and accurate project communication; documentation/demo reports verified behavior without changing runtime authority; Clean setup/review path → documented commands/evidence → reproducibility verdict.

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

C22 does not itself authorize V1 COMPLETE. Final status also requires the
applicable Test & Evaluation Plan, Card Specifications, Evidence Map, Golden
Case Contract, AGENTS.md, and Git reality to agree.
