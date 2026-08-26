# Strategic Intelligence Project — Codex Execution Protocol

## Modernized Execution Policy

## Canonical Git Workflow

The canonical Card-branch and integration workflow is defined in `AGENTS.md` §21. `main` is the latest approved integrated state; each newly authorized Card begins on a branch created from dynamically verified current `main` after confirming local `main` equals `github/main`, GitHub's default branch is `main`, and the tracked working tree is clean. PROJECT_CONTROL records the verification rule, not a self-referential exact current `main` SHA; exact SHAs remain historical Git/Card-Evidence/commit-report evidence.

The required ordered lifecycle is:

```text
Card authorization
→ Card branch creation
→ implementation
→ validation
→ Final Card Closure Gate
→ explicit commit authorization → commit
→ explicit push authorization → Card branch push
→ explicit integration authorization
→ fast-forward integration into main when valid → main push
→ Post-Integration Reconciliation Gate
→ PROJECT_CONTROL reconciliation
→ required control-only reconciliation commit/push when the integration authorization explicitly covers completion of this lifecycle
→ STOP
→ separate explicit authorization before the next Card starts
```

The Post-Integration Reconciliation Gate is mandatory before a next-Card branch can be created. It dynamically verifies canonical main, remote/default-branch consistency, approved-commit containment, Card-branch preservation, clean tracked state, completed-Card/closure status, absence of unexpected history changes, and PROJECT_CONTROL's durable semantic integration checkpoint. Reconcile every current operational field affected by integration so none still describes pre-integration delivery state. PROJECT_CONTROL must not state that its own reconciliation commit or push is pending; Git proves those transient facts dynamically. If the integration authorization does not explicitly cover the reconciliation commit/push, STOP after the gate verification and request that approval. This protocol does not authorize application changes, a subsequent Card, history rewriting, force-push, or branch deletion.

## V1-C05+ Card Evidence Lifecycle

The canonical C05+ Card contract is in `13_CARD_SPECIFICATIONS.md`; the actual
evidence model is in `14_CARD_EVIDENCE_MAP.md`. Do not create another quality,
Critical-Path, Closure, or Post-Integration gate.

The pre-delivery execution sequence is:

```text
Card authorization
→ inspect / Contract-Risk Map
→ Card contract confirmation
→ implementation
→ focused validation
→ meaningful incremental Evidence update
→ Critical-Path Validation
→ regression validation
→ final Evidence/Learning reconciliation
→ exact Exit Gate
→ Final Card Closure Gate
→ STOP
```

Evidence updates occur only when validated execution proves a meaningful new
fact. Card Specifications state the expected Critical Path; Evidence records
the actual proof. Historical Git traceability may be recorded in Evidence, but
Git remains the dynamic authority for operational state.


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

They must also pass the canonical Critical-Path Validation Gate in `AGENTS.md` §17: a Card-specific, minimum realistic composed path proving its primary owned capability at the real composition boundary, with external systems faked only when necessary. This is pre-commit closure validation, not a full-system test and not the post-integration Git/control gate. All previous Card tests, evidence, Git diff/status, security, Governance, and STOP rules remain mandatory.

The final completeness verdict is additionally governed by the canonical Final Card Closure Gate in `AGENTS.md` §17. A summary cannot override tests, exact Exit Gate, Evidence Map, PROJECT_CONTROL, Git, or scope/architecture evidence.

## Guiding Rule

**Harness controls execution. Persistence + validation create safe checkpoints. Evaluation proves improvement. Complexity requires evidence.**
