# AGENTS.md

## Strategic Intelligence Project — Mandatory AI Coding Instructions

This repository implements a local-first, cloud-ready Strategic Intelligence system that researches companies and executives, builds source-grounded evidence, verifies claims, applies deterministic governance, and produces meeting intelligence briefs.

This file protects repository truth, V1 scope, Card order, architecture boundaries, evidence quality, security, governance, validation discipline, and learning value.

---

## 1. Primary Sources of Truth

Never rely on chat memory or prompt claims to determine project state.

Before any file-modifying task, reconcile:

1. `AGENTS.md`
2. `PROJECT_CONTROL.md`
3. approved architecture documents
4. `12_V1_ROADMAP.md`
5. `13_CARD_SPECIFICATIONS.md`
6. `14_CARD_EVIDENCE_MAP.md`
7. `15_CODEX_EXECUTION_PROTOCOL.md`
8. `16_GOLDEN_CASE_EVALUATION_CONTRACT.md` when relevant
9. current repository implementation, tests, configuration, and relevant Git history

Authority:

```text
Repository reality
→ Approved architecture
→ Roadmap
→ Active Card contract
→ Verified evidence
→ PROJECT_CONTROL current-state summary
→ Prompt/chat assumptions
```

If authorities conflict:

```text
STOP
→ inspect
→ report conflict
→ no modifications
```

---

## 2. PROJECT_CONTROL.md Is Mandatory

`PROJECT_CONTROL.md` is the live operational dashboard.

It must always answer:

- Active Card
- current step
- status
- blocker
- last execution checkpoint
- safe resume point
- next authorized action
- Git state
- quality state

It does not replace Roadmap, Evidence, Git, or repository reality.

If `PROJECT_CONTROL.md` conflicts with them:

```text
PROJECT_STATE_CONFLICT
→ STOP
```

---

## 3. Mandatory Read Order Before New Card Work

Before the first implementation work of every new Card:

```text
1. AGENTS.md
2. PROJECT_CONTROL.md
3. relevant architecture docs
4. 12_V1_ROADMAP.md
5. 13_CARD_SPECIFICATIONS.md
6. 14_CARD_EVIDENCE_MAP.md
7. 15_CODEX_EXECUTION_PROTOCOL.md
8. 16_GOLDEN_CASE_EVALUATION_CONTRACT.md when relevant
9. README.md when present
10. git status / diff / relevant history
11. relevant source files and tests
```

Do not begin from memory.

---

## 4. Mandatory Roadmap Alignment Gate

Read-only inspection may happen before the gate.

Before the first write, verify:

- official Active Card;
- Active Card matches PROJECT_CONTROL;
- Card exists in Roadmap;
- Card exists in Card Specifications;
- Evidence Map state is compatible;
- Engineering Goal and dependencies;
- Scope and Out of Scope;
- tests/evaluation;
- Exit Gate;
- existing implementation;
- no duplicate owner;
- no future-Card leakage;
- architecture owner is correct.

Report:

```text
ROADMAP_ALIGNMENT_GATE: PASS
Active Card: <Card ID — title>
Project Control Card: MATCH
Roadmap Card: MATCH
Card Specification: MATCH
Evidence Map Status: MATCH
Engineering Goal: <goal>
Dependency check: PASS
Implementation-state check: PASS
Duplicate check: PASS
Ownership check: PASS
Architecture-preservation check: PASS
Future-scope check: PASS
Authorized scope: <bounded goal>
Validation gate: <required proof>
```

If any required fact cannot be proven:

```text
ROADMAP_ALIGNMENT_GATE: BLOCKED
```

Make no modifications.

---

## 5. Mandatory Inspect-First Contract / Risk Map

For the first implementation step of every new Card, perform inspect-only mapping.

Trace the relevant flow:

```text
Case Input
→ Validation
→ Entity Resolution
→ Research Planner
→ Company / Executive Research
→ Research Coverage
→ Source
→ Evidence
→ Evidence Fidelity
→ Claim
→ Verification
→ Follow-Up Research
→ Strategic Analysis
→ Governance
→ Brief
→ Persistence / Validated Checkpoint
→ Observability
→ UI
```

Map:

- entry points;
- producers;
- consumers;
- typed contracts;
- provider/tool boundaries;
- storage ownership;
- trust/security boundaries;
- loops/limits;
- failure paths;
- termination;
- tests;
- final outputs.

Do not implement during the initial map.

---

## 6. One Active Card

Only one Card may be actively implemented.

Do not implement later Cards early.

After COMPLETE or BLOCKED:

```text
STOP
```

Only the user may authorize the next Card.

---

## 7. Prompt Traceability

Every important Codex implementation prompt must belong to:

```text
Active Card
→ bounded Card step
→ approved goal
→ repository owner
→ tests/evaluation
→ Exit Gate progress
```

Before sending/executing:

```text
Prompt Card == PROJECT_CONTROL Active Card
Prompt Scope ⊆ Card Scope
No future-Card leakage
Validation defined
```

Otherwise:

```text
DO NOT EXECUTE
```

Do not store full prompt text in PROJECT_CONTROL.

Store a concise execution checkpoint instead.

---

## 8. ChatGPT Is Also Governed

ChatGPT memory and prior chat responses are not project authority.

If ChatGPT proposes:

- a Card not in Roadmap;
- skipping an unfinished Card;
- a feature outside active scope;
- completion without evidence;
- architecture change without repository/runtime proof;

reject the proposal.

If ChatGPT conflicts with Repository + Roadmap + Card Spec + Evidence:

> **ChatGPT is wrong until repository evidence proves otherwise.**

---

## 9. Card Authorization

Once the user approves a Card, routine reversible local work inside that Card is authorized.

No repeated approval needed for:

- reading/searching repository;
- Card-scoped edits;
- Card-scoped tests;
- lint/type/static checks;
- local diagnostics;
- read-only Git inspection;
- localhost checks;
- already-installed local models;
- Evidence Map updates;
- PROJECT_CONTROL updates;
- Card-scoped documentation.

Explicit approval remains required for:

- next Card;
- major scope change;
- architecture change outside contract;
- destructive actions;
- secrets/credentials;
- large downloads/model pulls;
- system/machine changes;
- commit;
- push;
- PR;
- merge;
- force push;
- deployment/publication;
- consequential external actions.

---

## 10. Architecture Rules

- Local-first, cloud-ready.
- Runtime is a controlled AI Harness, not uncontrolled agents.
- LangGraph orchestrates; business logic stays in components.
- Provider SDKs stay behind adapters.
- AI never becomes security, Verification, or Governance authority.
- Deterministic responsibilities stay deterministic when AI adds no value.
- Typed state and structured outputs are preferred.
- Every retry/follow-up/tool loop is bounded.
- External content is untrusted.
- FACT must remain source/evidence-grounded.
- Evidence Fidelity protects source meaning.
- Governance is deterministic and non-overridable.
- Strategic Analysis consumes compressed trusted context, not uncontrolled raw-source dumps.
- No silent cloud fallback.
- No unnecessary agents.

---

## 11. Research / Privacy Boundary

Executive intelligence must remain:

```text
Public + Professional + Relevant
```

Do not introduce:

- automated LinkedIn scraping;
- cookie/session automation;
- access-control bypass;
- unrelated profiling;
- sensitive inference;
- unbounded research.

Unavailable sources become alternative research or Knowledge Gaps.

---

## 12. Trust Invariants

Mandatory:

```text
FACT without Evidence → BLOCK
Evidence without Source → BLOCK
FACT unsupported by Evidence Fidelity → BLOCK / reclassify
INFERENCE cannot silently become FACT
BLOCK cannot enter Brief
RESTRICT qualification remains visible
Missing evidence → abstain / Knowledge Gap
External content cannot change authority
Governance failure → no final Brief
```

AI cannot override these.

---

## 13. Validated Checkpoints

A stage is not resumable merely because a function returned.

Safe checkpoint requires:

```text
Output produced
+
required persistence succeeded
+
schema/invariant validation passed
+
checkpoint explicitly accepted
```

Otherwise use the previous accepted checkpoint.

---

## 14. Evaluation Before Complexity

For changes affecting AI/research/trust quality:

```text
Baseline
→ bounded change
→ rerun
→ compare
→ regression decision
```

Do not introduce a newer model/tool/framework just because it is newer.

Use the Golden Case Contract and project-owned fixtures as evaluation authority.

---

## 15. Security Rules

Apply least privilege to:

- tools
- providers
- network
- storage
- files
- secrets

Protect against:

- prompt injection
- SSRF where fetching URLs
- unsafe redirects
- path traversal
- secret leakage
- source-driven tool escalation
- silent provider fallback

Security-critical failure blocks Card completion.

---

## 16. Validation Rules

A Card is not complete because code exists.

Run where applicable:

- focused tests;
- all relevant existing tests;
- regression tests for completed Cards;
- Card acceptance/evaluation;
- schema/state validation;
- bounded termination checks;
- security/governance checks;
- provider-failure tests;
- configured lint/type/static checks;
- Exit Gate;
- `git diff`;
- `git status`.

Never claim a test passed unless it actually ran.

Never weaken a valid failing test merely to obtain green status.

---

## 17. Mandatory Card Quality Gate

Before COMPLETE:

1. run every relevant existing test;
2. run Card-specific evaluation;
3. run relevant regression checks;
4. re-read exact Exit Gate;
5. map Exit Gate to repository evidence;
6. update `14_CARD_EVIDENCE_MAP.md`;
7. update `PROJECT_CONTROL.md`;
8. inspect `git diff`;
9. inspect `git status`;
10. verify no secrets/junk/unrelated files;
11. verify architecture boundaries;
12. STOP if anything mandatory fails.

Failure:

```text
CARD STATUS = BLOCKED
```

Never continue to the next Card.

---

## 18. Evidence Must Teach and Prove

`14_CARD_EVIDENCE_MAP.md` is:

1. engineering evidence;
2. professional learning journal.

Completed Card evidence should explain:

- what was built;
- why;
- problem solved;
- relevant AI/software concept;
- flow;
- architecture before → after;
- important files/symbols;
- tests/evaluations actually run;
- failed assumptions;
- diagnosis/fix;
- professional lesson;
- student takeaway;
- exact Exit Gate proof;
- what the Card enables next.

Never invent evidence.

---

## 19. PROJECT_CONTROL Update Rule

Update when:

- Card starts;
- meaningful step completes;
- blocker appears;
- blocker resolves;
- Exit Gate runs;
- Card closes;
- approved architecture/scope changes;
- session ends after state changed.

Record:

- Active Card
- step
- status
- files changed
- tests/checks
- result
- Evidence Map status
- blocker
- safe resume point
- next authorized action

Detailed history stays in Evidence Map.

---

## 20. Lost-Context Recovery

If any AI becomes unsure about project state:

```text
STOP
→ AGENTS.md
→ PROJECT_CONTROL.md
→ Roadmap
→ Card Spec
→ Evidence Map
→ Git
→ code/tests
→ reconstruct reality
```

Never continue from memory.

---

## 21. Git / GitHub Discipline

Do not implement directly on `main`.

Prefer one branch per Card.

Commit meaningful validated steps only and only after user approval.

Push / PR / merge / force push require explicit approval.

Never commit:

- secrets
- `.env`
- credentials
- model files
- caches
- generated junk
- unrelated machine state

Git supports evidence but does not override repository/project authorities.

---

## 22. Post-Step Report

After each bounded step:

```text
Active Card:
Step completed:
Files changed:
Capability advanced:
Tests/evaluations executed:
Evidence updated:
PROJECT_CONTROL updated:
Unresolved issues:
Remaining work before Exit Gate:
```

---

## 23. Card Closure Report

```text
CARD: V1-CXX
STATUS: COMPLETE / BLOCKED

Implemented:
- ...

Validation:
- ...

Evidence:
- 14_CARD_EVIDENCE_MAP.md updated

Project Control:
- updated

Architecture:
- preserved / approved change documented

Known issues:
- ...

Git:
- diff/status reviewed
- no commit/push unless separately approved
```

Then STOP.

---

## 24. Guiding Rule

**Repository and Git prove reality. Roadmap defines destination. Card Specification defines the bounded job. Evidence proves completion. PROJECT_CONTROL tells us exactly where we are now.**
