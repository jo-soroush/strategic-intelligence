# Strategic Intelligence Project — Workflow and Orchestration

## 1. Purpose

This document defines how V1 executes one Strategic Intelligence Case from start to finish.

The workflow is explicit, controlled, testable, recoverable, observable, evidence-first, governance-enforced, local-first, and cloud-ready.

> The workflow controls the AI. The AI does not control the workflow.


## Modernization Decision — Harness, Validated Checkpoints, Evaluation Baseline

V1 adopts three implementation principles before V1-C01:

1. **Harness Engineering** — the product is treated as a controlled AI execution harness, not merely a chain of prompts or agents. The harness owns orchestration, typed state, provider/tool boundaries, permissions, retry limits, persistence/checkpoints, governance, observability, and evaluation hooks.
2. **Validated Checkpoints (Shepherd-style recovery)** — a stage becomes resumable only after its required outputs are persisted and validation succeeds. Recovery resumes from the last accepted checkpoint; invalid or partially persisted state is never promoted.
3. **Evaluation Before Complexity** — V1 establishes a small measurable evaluation baseline early and compares meaningful model, prompt, provider, retrieval, verification, and workflow changes against it. The Golden Case remains the final real-world acceptance case, but evaluation is no longer postponed until C20.

These are architecture-strengthening changes, not new user-facing features. They do not expand V1 into autonomous multi-agent, multi-model, monitoring, or cloud infrastructure work.

## Harness Architecture

LangGraph is the V1 orchestrator inside a broader application harness.

```text
                         STRATEGIC INTELLIGENCE HARNESS
┌────────────────────────────────────────────────────────────────────┐
│ Case / typed state                                                 │
│ Orchestration + routing                                            │
│ Tool/provider permissions                                          │
│ Retry / timeout / loop budgets                                     │
│ Persistence + validated checkpoints                                │
│ Verification + deterministic Governance                            │
│ Observability / audit / evaluation hooks                           │
└───────────────────────────┬────────────────────────────────────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        LLMProvider    SearchProvider    Repositories
             │              │              │
        Local Ollama   Permitted Web   SQLite / Files
```

Business reasoning remains in dedicated components. The harness coordinates execution and enforces boundaries; it does not absorb domain logic.

## High-Level Workflow

```text
START
→ Validate Case
→ Plan Research
→ Company Research + Executive Research
→ Build Evidence
→ Build Claims
→ Verify
→ bounded Follow-Up Research when required
→ Strategic Analysis
→ Governance Gate
→ Brief Generator
→ Persist Results
→ Determine Case Status
→ END
```

## Harness Responsibilities

The harness owns:

- typed workflow state;
- node routing and termination;
- provider/tool capability injection;
- retry, timeout, and follow-up budgets;
- persistence coordination;
- validated checkpoint acceptance;
- recovery;
- audit/trace events;
- evaluation hooks;
- deterministic security and Governance boundaries.

The harness does **not** decide business facts or replace Verification/Strategic Analysis.

## Validated Checkpoint Protocol

A checkpoint is not merely “the node ran.”

```text
Stage action
→ typed output validation
→ required persistence succeeds
→ stage invariants pass
→ checkpoint accepted
```

Only then may the workflow advance or later resume from that checkpoint.

If persistence or validation fails:

```text
checkpoint = NOT ACCEPTED
→ preserve previous safe checkpoint
→ controlled failure / retry / recovery
```

Recommended checkpoints remain:

- CASE_VALIDATED
- RESEARCH_PLANNED
- RESEARCH_COMPLETED
- EVIDENCE_BUILT
- VERIFICATION_COMPLETED
- ANALYSIS_COMPLETED
- GOVERNANCE_COMPLETED
- BRIEF_GENERATED
- CASE_COMPLETED

## Recovery

Recovery loads the last **accepted** checkpoint, validates its persisted state, and resumes from the next required stage.

Recovery must:

- not skip trust stages;
- not trust half-written state;
- avoid uncontrolled duplicate records;
- preserve retry/follow-up counters;
- emit recovery audit events.

Rollback is required only where a state mutation must be reversed; V1 should prefer transaction-safe writes and resume from the last accepted checkpoint over complex compensating workflows.

## Evaluation Hooks

Important harness stages should expose structured evaluation inputs/outputs without coupling runtime logic to a specific evaluation framework.

Evaluation hooks should make it possible to compare:

- research relevance/coverage;
- source quality;
- verification status accuracy;
- Governance leakage;
- unsupported claims;
- Brief usefulness;
- latency and provider failures.

No external evaluation framework is mandatory for V1.

## Core Invariants

- AI never controls the harness.
- Every loop is bounded.
- Every tool/provider capability is explicitly granted.
- External content remains untrusted.
- FACT requires traceable Evidence/Source.
- Governance is deterministic and non-overridable.
- A checkpoint is safe only after persistence + validation.
- Recovery resumes only from an accepted checkpoint.
- Evaluation must measure changes before complexity is added.
- No silent cloud fallback.

## Final Principle

**Controlled Harness → Typed State → Evidence → Verification → Governance → Validated Checkpoints → Observable/Evaluable Brief**


# Pre-Mortem Hardening Addendum

## Entity Resolution Gate

Deep research must not start until the target Company and Executive are sufficiently disambiguated.

```text
Case Input
→ Entity Resolution
   ├── CONFIRMED → Research Planner
   ├── PARTIAL → limited research / explicit warning
   └── AMBIGUOUS → stop deep research
```

Entity Resolution should use deterministic/user-supplied identifiers where possible:

- official company domain;
- country/business unit;
- executive current company;
- current role;
- supplied public professional URL.

The workflow must not silently merge similarly named people or organizations.

## Research Coverage State

Workflow state should carry structured research coverage:

- category;
- status;
- number/quality of retained sources;
- missing/unavailable reason.

Research completion depends on coverage + value + configured limits, not merely “search returned results.”

## Evidence Fidelity Stage

Insert an explicit trust step:

```text
Build Evidence
→ Build Candidate Claims
→ Evidence Fidelity Check
→ Verification
```

A candidate FACT that is not faithfully supported by its evidence is blocked/reclassified before normal Verification.

## Context Budget / Compression

Strategic Analysis should not receive all raw sources.

Preferred runtime context:

```text
Verified/Restricted Claims
+ ranked Evidence summaries
+ strategic signals
+ Case Context
```

Raw source content remains retrievable by ID if deeper inspection is needed.

The harness should enforce configurable context budgets and prioritize:

1. meeting relevance;
2. source quality;
3. freshness;
4. verification status;
5. diversity/non-duplication.

## Performance Baseline Hooks

Every run should measure where practical:

- total Case duration;
- research duration;
- LLM duration;
- verification duration;
- Governance duration;
- number of searches;
- number of provider calls;
- follow-up attempts;
- retained sources/claims.

No artificial SLA is required before baseline data exists.

Performance optimization must not reduce trust quality without measured justification.

## Added Workflow Invariants

- Deep research requires resolved target identity.
- Research completion requires explicit coverage state.
- Candidate FACTs pass Evidence Fidelity before Verification.
- Strategic Analysis uses compressed trusted context, not uncontrolled raw-source dumps.
- Performance is measured from early V1 runs.
