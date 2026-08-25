# Strategic Intelligence Project — Test and Evaluation Plan

## Modernized V1 Evaluation Policy


## Modernization Decision — Harness, Validated Checkpoints, Evaluation Baseline

V1 adopts three implementation principles before V1-C01:

1. **Harness Engineering** — the product is treated as a controlled AI execution harness, not merely a chain of prompts or agents. The harness owns orchestration, typed state, provider/tool boundaries, permissions, retry limits, persistence/checkpoints, governance, observability, and evaluation hooks.
2. **Validated Checkpoints (Shepherd-style recovery)** — a stage becomes resumable only after its required outputs are persisted and validation succeeds. Recovery resumes from the last accepted checkpoint; invalid or partially persisted state is never promoted.
3. **Evaluation Before Complexity** — V1 establishes a small measurable evaluation baseline early and compares meaningful model, prompt, provider, retrieval, verification, and workflow changes against it. The Golden Case remains the final real-world acceptance case, but evaluation is no longer postponed until C20.

These are architecture-strengthening changes, not new user-facing features. They do not expand V1 into autonomous multi-agent, multi-model, monitoring, or cloud infrastructure work.

## Evaluation Baseline Starts Early

The evaluation system begins during foundation work rather than waiting for the final Golden Case.

Two complementary assets are used:

### 1. V1 Evaluation Baseline

A small deterministic/labeled suite established incrementally as relevant Cards land.

It measures stable system properties such as:

- research relevance;
- source traceability;
- verification accuracy;
- unsupported-claim rate;
- Governance BLOCK leakage;
- RESTRICT preservation;
- recovery correctness;
- bounded-loop behavior.

### 2. Golden Case

The real public end-to-end Case remains the final product-quality benchmark and demo asset.

The Golden Case should not use brittle exact-wording assertions.

## Baseline Metrics

Track where meaningful:

| Dimension | V1 Baseline Signal |
|---|---|
| Traceability | important factual outputs with valid Claim → Evidence → Source chain |
| Verification | agreement with manually labeled verification fixtures |
| Unsupported claims | known unsupported factual claims; target 0 in governed Brief |
| Governance leakage | BLOCK items reaching user-facing Brief; target 0 |
| Restriction preservation | RESTRICT qualifications preserved; target 100% in mandatory fixtures |
| Research relevance | labeled relevant findings / reviewed findings |
| Recovery | resumes from last accepted checkpoint without skipping trust stages |
| Loop safety | all retry/follow-up loops terminate at configured limits |
| Brief usefulness | structured manual rubric on Golden Case |
| Reliability | controlled handling of provider/source/persistence failures |

Do not create fake precision where the evaluation set is too small. Store counts, labels, and rubric results alongside derived percentages.

## Change Comparison Rule

Meaningful changes to prompts, models, search adapters, verification logic, routing, or retrieval behavior must be compared against the available baseline when they can affect evaluated behavior.

A change is not “better” merely because one example looks better.

Record:

```text
change
→ baseline before
→ candidate result
→ regressions
→ decision
```

## Evaluation Fixtures

Create reusable deterministic fixtures incrementally for:

- Cases
- Sources
- Evidence
- Claims
- verification labels
- Governance decisions
- fake provider responses
- prompt-injection cases
- recovery/checkpoint cases

## Validated Checkpoint Tests

For each checkpoint-capable stage:

```text
stage work succeeds
+ persistence succeeds
+ validation succeeds
→ checkpoint accepted
```

Failure cases:

```text
stage succeeds + persistence fails → checkpoint rejected
stage persists + invariant fails → checkpoint rejected
recovery sees invalid checkpoint → fall back to prior accepted checkpoint
```

## Harness Tests

Test the harness independently from semantic model quality:

- routing;
- capability boundaries;
- timeout/retry budgets;
- bounded follow-up;
- checkpoint acceptance;
- recovery;
- partial success;
- provider failure;
- audit events;
- Governance fail-closed behavior.

## Evaluation Framework Policy

V1 does not require DeepEval or another external framework.

First establish the project-owned baseline and schemas. An evaluation framework may be adopted later only if it materially improves regression automation without becoming the source of truth.

## Final V1 Evaluation Gate

V1 cannot complete unless:

- automated tests pass;
- evaluation baseline has real results;
- Verification labeled fixtures pass the accepted threshold;
- BLOCK leakage = 0;
- known unsupported factual Brief claims = 0;
- RESTRICT preservation passes mandatory fixtures;
- validated-checkpoint recovery passes;
- Golden Case passes manual review;
- changes with quality impact have recorded comparison evidence.

## Final Principle

**Measure first → change one thing → compare → preserve trust → add complexity only when evidence justifies it.**


# Pre-Mortem Evaluation Addendum

## Entity Resolution Tests

Required:

- exact company/executive match;
- two executives with same/similar name;
- executive moved companies;
- ambiguous company/business unit;
- supplied URL conflicts with discovered entity.

Expected:

- ambiguous identity never silently passes as confirmed.

## Research Coverage Evaluation

For labeled Cases, record category coverage:

- COVERED
- PARTIAL
- NOT_FOUND
- UNAVAILABLE
- NOT_RELEVANT

Evaluate whether high-priority categories were actually attempted and whether additional search adds meaningful new information.

## Evidence Fidelity Evaluation

Create labeled source/evidence/claim fixtures:

- fully supported Claim;
- overstrong Claim;
- partially supported Claim;
- contradicted Claim;
- ambiguous Claim.

Measure agreement with expected fidelity status.

A real URL/source does not count as success if the Claim misrepresents it.

## Context Compression Tests

Given a controlled set of sources/claims:

- low-value duplicates should be excluded;
- important verified claims retained;
- conflicts retained;
- restrictions retained;
- provenance IDs retained;
- final analysis must not depend on removed raw wording unless explicitly retrieved.

## Performance Baseline

From early executable Cards, record:

- total runtime;
- research time;
- model-call time;
- verification time;
- Governance time;
- search count;
- provider-call count;
- retry/follow-up count.

Do not define a hard SLA until baseline runs exist.

Use the baseline to detect severe regressions.

## New Mandatory V1 Trust Metrics

- Wrong-entity acceptance: target 0 in mandatory fixtures.
- Important category coverage status recorded: 100%.
- Known overstrong factual claims passing Fidelity: 0.
- Important final facts with valid Source → Evidence → Fidelity → Claim chain: 100%.
- BLOCK leakage: 0.
- Context compression losing mandatory restriction/provenance: 0 in fixtures.

## Performance Decision Rule

A quality improvement that creates major runtime regression must be explicitly reviewed.

Do not optimize latency by skipping Verification, Governance, or Fidelity gates.
