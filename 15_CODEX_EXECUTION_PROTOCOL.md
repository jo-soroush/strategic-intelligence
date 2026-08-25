# Strategic Intelligence Project — Codex Execution Protocol

## Modernized Execution Policy

## Canonical Git Workflow

The canonical Card-branch and integration workflow is defined in `AGENTS.md` §21. `main` is the latest approved integrated state; each newly authorized Card begins on a branch created from dynamically verified current `main` after confirming local `main` equals `github/main`, GitHub's default branch is `main`, and the tracked working tree is clean. PROJECT_CONTROL records the verification rule, not a self-referential exact current `main` SHA; exact SHAs remain historical Git/Card-Evidence/commit-report evidence. Card integration remains gated by validation, Evidence Map and Project Control updates, exact Exit Gate proof, diff/status review, and explicit user approval. This protocol does not authorize commits, pushes, merges, history rewriting, or starting a subsequent Card.


## Modernization Decision — Harness, Validated Checkpoints, Evaluation Baseline

V1 adopts three implementation principles before V1-C01:

1. **Harness Engineering** — the product is treated as a controlled AI execution harness, not merely a chain of prompts or agents. The harness owns orchestration, typed state, provider/tool boundaries, permissions, retry limits, persistence/checkpoints, governance, observability, and evaluation hooks.
2. **Validated Checkpoints (Shepherd-style recovery)** — a stage becomes resumable only after its required outputs are persisted and validation succeeds. Recovery resumes from the last accepted checkpoint; invalid or partially persisted state is never promoted.
3. **Evaluation Before Complexity** — V1 establishes a small measurable evaluation baseline early and compares meaningful model, prompt, provider, retrieval, verification, and workflow changes against it. The Golden Case remains the final real-world acceptance case, but evaluation is no longer postponed until C20.

These are architecture-strengthening changes, not new user-facing features. They do not expand V1 into autonomous multi-agent, multi-model, monitoring, or cloud infrastructure work.

## Harness-Aware Contract / Risk Map

For Cards touching runtime behavior, the inspect-first map must identify:

- harness/orchestrator owner;
- state owner;
- provider/tool capabilities;
- permission boundary;
- retry/timeout/follow-up budgets;
- persistence boundary;
- checkpoint candidate and acceptance conditions;
- Governance/security boundary;
- observability hooks;
- relevant evaluation baseline.

## Evaluation Alignment Gate

Before a quality-affecting write, Codex must answer:

```text
Relevant baseline exists: YES / NO
Baseline artifact: <path/id or N/A>
Metric/rubric affected: <name>
Expected improvement: <specific hypothesis>
Regression risk: <specific risk>
```

If no baseline exists but the Card is responsible for establishing one, that becomes part of the Card acceptance evidence.

Do not introduce a new model, prompt strategy, provider, framework, or agent pattern merely because it appears more modern.

## Validated Checkpoint Rule

Codex must distinguish:

```text
node/stage execution success
```

from:

```text
safe resumable checkpoint
```

A safe checkpoint requires:

1. required output produced;
2. typed/schema validation passed;
3. required persistence succeeded;
4. stage invariants passed;
5. checkpoint explicitly accepted.

Failure at steps 2–4 means the checkpoint is rejected.

## Recovery Validation

Recovery changes must prove:

- exact last accepted checkpoint;
- invalid/partial newer state is not trusted;
- resume does not skip trust stages;
- retry/follow-up limits survive restart;
- duplicate persistence is controlled;
- recovery event is observable.

## Harness Observability

Where relevant, evidence should correlate:

```text
Case
→ Run
→ Stage
→ Attempt
→ Provider/Tool capability
→ Checkpoint decision
→ Verification/Governance decision
→ Output
```

Do not log secrets or unnecessary raw personal/source data.

## Quality-Change Discipline

When changing prompts, models, search behavior, Verification logic, routing, or Brief behavior:

1. state the hypothesis;
2. run relevant baseline;
3. change one bounded thing where practical;
4. rerun;
5. compare;
6. record regressions;
7. accept/reject based on evidence.

## Framework Adoption Rule

MCP, DeepEval, Kitesurf, DeepCrawl, Agent-Reach, multi-model routing, or similar tooling is not implicitly approved by this modernization.

Adopt only after:

- a concrete project problem is demonstrated;
- current architecture cannot solve it cleanly;
- measurable benefit is defined;
- scope/dependency impact is reviewed;
- user approves the architecture/scope change when required.

## Card Quality Gate Addition

Before COMPLETE, relevant Cards must include:

```text
Harness boundary: PASS
Validated checkpoint behavior: PASS / N/A
Relevant evaluation baseline: PASS / N/A with reason
Regression comparison: PASS / N/A with reason
```

All previous Card tests, evidence, Git diff/status, security, Governance, and STOP rules remain mandatory.

## Guiding Rule

**Harness controls execution. Persistence + validation create safe checkpoints. Evaluation proves improvement. Complexity requires evidence.**
