# Strategic Intelligence Project — V1 Roadmap

## Purpose

This is the canonical 22-Card V1 Roadmap. It consolidates the original roadmap with the approved Harness modernization, validated-checkpoint, evaluation-baseline, pre-mortem, Entity Resolution, Research Coverage, Evidence Fidelity, Context Budget, performance-baseline, and Golden Case controls.

The Card IDs and order are frozen.

Core rule:

> Complete a small, trustworthy V1 before expanding the product.

## V1 Timebox

Target: maximum 3 weeks.

- Week 1 — Foundation + Research: C01–C08
- Week 2 — Evidence + Verification + Governance + Security: C09–C14
- Week 3 — Analysis + Brief + UI + Recovery + Observability + Golden Case + Hardening + Documentation: C15–C22

## Global Card Gate

A Card is COMPLETE only when its implementation, required tests/evaluation, regression checks, evidence, exact Exit Gate, diff/status review, and architecture/scope checks pass.

For Cards affecting AI behavior, routing, trust, quality, or recovery, relevant baseline/evaluation must run or be explicitly recorded as N/A with reason.

## V1 Scope Freeze

V1 delivers one local-first meeting-intelligence workflow from Company + Executive + Meeting Goal to Quick Brief + Full Brief.

Do not add continuous monitoring, alerts, CRM, multi-user/enterprise dashboard, automatic LinkedIn scraping, autonomous agent teams, multi-model routing, cloud deployment, MCP runtime dependency, automated outreach, or enterprise RBAC unless a formally approved scope change proves it necessary.

## V1-C01 — Repository Baseline

**Goal:** Create a clean, testable project foundation.

**Dependencies:** None

**Scope / Acceptance:** Project structure; Python environment/dependencies; central configuration; .env.example; .gitignore; logging; test structure; documentation placement; harness/evaluation artifact conventions.

**Required Tests / Evaluation:** Package import; configuration load; test runner; secrets ignored; repository/Git review; harness boundary documented.

**Exit Gate:** Foundation is stable enough for typed domain models.

## V1-C02 — Domain Models

**Goal:** Implement application-owned typed contracts for the V1 workflow.

**Dependencies:** V1-C01

**Scope / Acceptance:** Case, Company, Executive, WorkflowRun, ResearchPlan, ResearchTask, RawFinding, Source, Evidence, Claim, ClaimEvidenceLink, VerificationResult, StrategicAnalysis, GovernanceDecision, MeetingBrief, AuditEvent, WorkflowError; explicit enums, IDs, timestamps and serialization.

**Required Tests / Evaluation:** Valid/invalid construction; enum rejection; required fields; serialization; relationship identifiers.

**Exit Gate:** Later Cards can exchange structured application-owned data without free-form/provider-specific contracts.

## V1-C03 — Persistence Foundation

**Goal:** Implement local persistence behind repository interfaces.

**Dependencies:** V1-C02

**Scope / Acceptance:** SQLite; repository contracts/implementations; ArtifactStore; schema/migrations; Case/run and Source/Evidence/Claim persistence; transaction-safe writes; accepted-checkpoint metadata and validation.

**Required Tests / Evaluation:** CRUD; relationships; rollback; artifact read/write; path traversal; duplicate basics; persistence/invariant failure prevents checkpoint acceptance.

**Exit Gate:** Workflow state can survive process termination through safe persistence.

## V1-C04 — Provider Foundation

**Goal:** Create vendor-independent AI/search capability boundaries.

**Dependencies:** V1-C01, V1-C02

**Scope / Acceptance:** LLMProvider; SearchProvider; factory/composition; Ollama adapter; search adapter; fake providers; normalized errors/timeouts; narrow capability injection; provider observability metadata; no silent cloud fallback.

**Required Tests / Evaluation:** Contract/factory tests; error normalization; timeout; Ollama/search integration where configured; no-silent-fallback.

**Exit Gate:** Core components operate through provider interfaces without vendor coupling.

## V1-C05 — Case Input and Validation

**Goal:** Create the validated root Case and resolve target identity before research.

**Dependencies:** V1-C02, V1-C03

**Scope / Acceptance:** Required company/executive/meeting goal; optional URLs/context; safe URL validation; persistence; Entity Resolution Gate for company, executive and executive↔company relationship; ambiguity blocks unrestricted deep research.

**Required Tests / Evaluation:** Valid/missing fields; invalid URL; persistence; same-name executive; moved executive; conflicting URL; ambiguous company/business unit.

**Exit Gate:** Invalid or unresolved/unsafe Cases cannot enter unrestricted research.

## V1-C06 — Research Planner

**Goal:** Convert a valid Case into a bounded meeting-focused ResearchPlan with explicit coverage.

**Dependencies:** V1-C04, V1-C05

**Scope / Acceptance:** Company/executive tasks; meeting-goal intent; priorities; approved categories; task/attempt budgets; Research Coverage Contract with COVERED/PARTIAL/NOT_FOUND/UNAVAILABLE/NOT_RELEVANT; privacy boundary.

**Required Tests / Evaluation:** Valid plan; task separation; limits; invalid task/privacy rejection; fake LLM structured output; coverage/high-priority gap behavior.

**Exit Gate:** Research receives a valid bounded plan and completion is coverage-aware, not result-count driven.

## V1-C07 — Company Research

**Goal:** Produce structured source-linked company intelligence.

**Dependencies:** V1-C04, V1-C06

**Scope / Acceptance:** Overview; strategy; projects/case studies; AI activity; products/services; partnerships; investments/acquisitions; hiring; news/events; permitted professional signals; source preservation; relevance and blocked-source handling.

**Required Tests / Evaluation:** Structured findings; empty/duplicate/blocked results; relevance filtering; project discovery; source-reference preservation.

**Exit Gate:** Company research reliably produces traceable meeting-relevant findings.

## V1-C08 — Executive Research

**Goal:** Produce relevant public professional intelligence about the target executive.

**Dependencies:** V1-C04, V1-C06

**Scope / Acceptance:** Role/responsibilities; relevant background/focus; articles/interviews/events/projects; professional activity; company-strategy connection; identity disambiguation; LinkedIn optional; no sensitive inference/scraping.

**Required Tests / Evaluation:** Structured findings; ambiguous identity; missing LinkedIn; personal-data rejection; source preservation; fact/inference behavior.

**Exit Gate:** Executive research is useful while preserving the public-professional-relevant boundary.

## V1-C09 — Evidence Layer

**Goal:** Create a traceable Source → Evidence → Candidate Claim foundation with fidelity inputs.

**Dependencies:** V1-C03, V1-C07, V1-C08

**Scope / Acceptance:** Source normalization; Evidence extraction; candidate Claims; ClaimEvidenceLink SUPPORTS/CONTRADICTS/CONTEXT; duplicates; preserve enough Evidence→Candidate Claim context for Fidelity evaluation.

**Required Tests / Evaluation:** Evidence requires Source; many-to-many links; multiple/contradictory evidence; duplicates; broken traceability; fidelity input preservation.

**Exit Gate:** Important findings are traceable to Sources and ready for fidelity/verification.

## V1-C10 — Source Quality and Freshness

**Goal:** Provide deterministic source-quality/freshness metadata for Verification.

**Dependencies:** V1-C09

**Scope / Acceptance:** PRIMARY/STRONG_SECONDARY/OTHER; publication/retrieval dates; freshness/unknown; origin/duplicate signals.

**Required Tests / Evaluation:** Primary/secondary classification; missing date; stale evidence; publication/retrieval separation; duplicate-origin.

**Exit Gate:** Verification receives reliable source-quality and freshness inputs.

## V1-C11 — Verification Engine

**Goal:** Evaluate factual Claims against Evidence after Evidence Fidelity checking.

**Dependencies:** V1-C09, V1-C10

**Scope / Acceptance:** Fidelity statuses SUPPORTED_BY_EVIDENCE/PARTIALLY_SUPPORTED/NOT_SUPPORTED/AMBIGUOUS; verification VERIFIED/SUPPORTED/CONFLICTING/STALE/INSUFFICIENT_EVIDENCE; source independence/conflict/sufficiency; labeled baseline fixtures.

**Required Tests / Evaluation:** Fidelity fixtures; overstrong/not-supported claims; strong primary/secondary; independent confirmation; duplicate origin; conflict; stale; missing evidence; expected-vs-actual baseline.

**Exit Gate:** Unsupported/overstrong facts cannot be promoted to trusted factual intelligence and baseline evidence is recorded.

## V1-C12 — Bounded Follow-Up Research

**Goal:** Allow Verification to request targeted additional research without autonomous loops.

**Dependencies:** V1-C07, V1-C08, V1-C11

**Scope / Acceptance:** Important weak Claim → focused ResearchTask → Evidence → reverification; configurable attempts; audit trail; abstention after limit.

**Required Tests / Evaluation:** Follow-up strengthens; finds nothing; max attempts; termination; persisted attempt/audit state.

**Exit Gate:** Research-more behavior is bounded and deterministic at workflow level.

## V1-C13 — Governance Gate

**Goal:** Implement the deterministic non-overridable trust boundary before user-facing intelligence.

**Dependencies:** V1-C11

**Scope / Acceptance:** PASS/RESTRICT/BLOCK; FACT requires Evidence; Evidence requires Source; fidelity/trust invariants; inference cannot silently become fact; BLOCK excluded; RESTRICT preserved; privacy; external content no authority; fail closed; reason codes/persistence.

**Required Tests / Evaluation:** FACT without Evidence; Evidence without Source; misclassified inference; conflict/stale restriction; personal-data block; governance failure blocks Brief; reason-code persistence.

**Exit Gate:** Trust rules are demonstrably stronger than model output and cannot be overridden by AI.

## V1-C14 — Security Boundaries

**Goal:** Implement V1 controls for safely researching untrusted public sources.

**Dependencies:** V1-C04, V1-C05, V1-C07, V1-C08, V1-C13

**Scope / Acceptance:** Secret isolation; URL validation; SSRF/redirect protection where fetching exists; safe paths; prompt-injection isolation; least privilege; log redaction; no silent cloud fallback; no access-control bypass.

**Required Tests / Evaluation:** Malformed/unsupported/private URL; redirect-to-private; path traversal; prompt injection; secret leakage; no silent fallback; personal-data filtering.

**Exit Gate:** External research cannot bypass application security/governance boundaries.

## V1-C15 — Strategic Analysis

**Goal:** Convert governed intelligence into meeting-relevant strategic reasoning using controlled context.

**Dependencies:** V1-C11, V1-C13

**Scope / Acceptance:** Company direction; executive priorities; project meaning; signals; opportunities; user relevance; topics/questions/risks/gaps; FACT/INFERENCE/RECOMMENDATION; Context Budget/Compression from ranked verified/restricted Claims and Evidence summaries; preserve provenance/conflicts/freshness/restrictions.

**Required Tests / Evaluation:** Controlled fixture; no invented facts/user background; conflict/gap preservation; meeting relevance; compression retains critical restricted/conflicting evidence.

**Exit Gate:** Strategic reasoning adds value without destroying evidence/trust boundaries.

## V1-C16 — Brief Generator

**Goal:** Generate trustworthy Quick and Full Briefs from governed intelligence.

**Dependencies:** V1-C13, V1-C15

**Scope / Acceptance:** Rank/select/summarize/organize only; no research/new unsupported facts; no BLOCK reintroduction; preserve RESTRICT and fact/inference; Quick Brief; Full Brief with evidence/sources and gaps.

**Required Tests / Evaluation:** BLOCK leakage=0; RESTRICT preserved; unsupported fact test; gaps/sources; Quick/Full structure.

**Exit Gate:** Both Briefs are trustworthy, traceable and useful.

## V1-C17 — Minimal Local UI

**Goal:** Make V1 usable locally without direct Python invocation.

**Dependencies:** V1-C05, V1-C16

**Scope / Acceptance:** Thin local UI for Case input, workflow status, Quick/Full Brief, errors and Knowledge Gaps; no business logic/polish expansion.

**Required Tests / Evaluation:** Valid submission; validation error; completed/partial/failed result.

**Exit Gate:** A user can execute the approved V1 workflow locally.

## V1-C18 — Workflow Recovery

**Goal:** Prove safe recovery from validated accepted checkpoints.

**Dependencies:** V1-C03, V1-C16

**Scope / Acceptance:** Stage action → required persistence → invariant/schema validation → checkpoint acceptance → recovery; accepted-only resume; fallback from invalid latest checkpoint; no trust-stage skip; bounded counters; duplicate/idempotent safety.

**Required Tests / Evaluation:** Persistence failure; invariant failure; recovery from accepted checkpoint; invalid latest fallback; resume after Research/Evidence/Verification/Governance; idempotent/duplicate-safe resume.

**Exit Gate:** Interrupted work resumes from the last accepted safe checkpoint without corrupting trust state.

## V1-C19 — Observability and Audit

**Goal:** Make Harness execution reconstructable and measurable.

**Dependencies:** V1-C03, V1-C04, V1-C13

**Scope / Acceptance:** Structured run/case/stage/node/attempt/provider/tool/checkpoint/verification/governance/duration/failure/evaluation identifiers; performance baseline: total/stage duration, searches, provider calls, retries/follow-ups, retained sources/claims; redaction.

**Required Tests / Evaluation:** Audit/verification/governance/retry/error events; secret redaction; checkpoint accept/reject trace; performance metrics recorded.

**Exit Gate:** A developer can answer what happened, why, and how the run performed without exposing secrets.

## V1-C20 — Golden Case

**Goal:** Prove V1 on one real company, executive and meeting goal using the Golden Case Contract.

**Dependencies:** V1-C07 through V1-C19

**Scope / Acceptance:** Complete pipeline; Ground Truth; entity resolution; coverage/recall; fidelity; verification; governance; context preservation; strategic insight; Quick/Full Brief; performance baseline; accumulated baseline comparison.

**Required Tests / Evaluation:** Golden Case Contract manual/automated checks; traceability; usefulness rubric; runtime/performance; regressions.

**Exit Gate:** Golden Case passes mandatory trust invariants and demonstrates real meeting-preparation value.

## V1-C21 — Hardening and Regression

**Goal:** Fix confirmed integration/Golden Case defects without feature expansion.

**Dependencies:** V1-C20

**Scope / Acceptance:** Bugs; governance/research/verification/security/recovery/duplicate/error/Brief defects only; root-cause fixes; one-variable changes where practical; compare quality-affecting fixes to baseline.

**Required Tests / Evaluation:** Relevant full regression; critical-bug tests; governance/security regressions; baseline comparison.

**Exit Gate:** No known critical V1 defect remains and relevant quality baselines do not regress.

## V1-C22 — Documentation and Demo Readiness

**Goal:** Make V1 reproducible, self-explanatory and portfolio/demo ready.

**Dependencies:** V1-C21

**Scope / Acceptance:** README; setup/local run; architecture index; provider config; tests; limitations; V1 scope; security/governance; Golden Case/demo; current status; V2 parking lot; reproducible final evidence.

**Required Tests / Evaluation:** Fresh-environment instructions reviewed; commands/links verified; limitations accurate; final tests/tree/evidence reviewed.

**Exit Gate:** A future developer/Codex session can reproduce and understand V1 without reconstructing decisions from chat history.

## Final V1 Exit Gate

After C22, V1 is COMPLETE only if the full automated suite and relevant provider, persistence, recovery, Governance, security/prompt-injection and Golden Case checks pass; important factual claims are traceable; known unsupported factual claims and BLOCK leakage are zero; RESTRICT qualifications and Knowledge Gaps remain visible; local-first execution works; logs/audit and documentation match reality; no critical issue remains; and V1 scope was not silently expanded.

If any mandatory gate fails:

`V1 STATUS = BLOCKED`
