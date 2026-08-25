# Strategic Intelligence Project — Golden Case Evaluation Contract

## Purpose
The Golden Case is the real-world proof that V1 produces trustworthy and useful strategic meeting intelligence.

It must prove:

`Correct Entity → Research → Source → Evidence → Fidelity → Verification → Governance → Strategic Insight → Meeting Brief`

## Golden Case Inputs
- Real Company
- Real Executive
- Real Meeting Goal
- Public/professional research boundary
- Manually reviewed Ground Truth Set
- Quick Brief
- Full Brief

The specific company/executive can be selected later.

## Ground Truth
Before final evaluation, manually establish approximately 15–30 important, publicly supportable facts/signals.

Each item records:
- ID
- category
- statement
- importance: HIGH / MEDIUM
- supporting source
- publication date if known
- notes

Ground Truth must itself be source-supported.

## Evaluation Dimensions

### 1. Entity Accuracy
Did the system research the correct company and executive?

**Mandatory target: wrong confirmed entity = 0.**

Ambiguity must be surfaced instead of silently accepted.

### 2. Research Recall
Measure:

`important Ground Truth items discovered / important Ground Truth items available`

Report HIGH-importance recall separately.

### 3. Research Coverage
Each expected category is:
- COVERED
- PARTIAL
- NOT_FOUND
- UNAVAILABLE
- NOT_RELEVANT

Important gaps remain visible.

### 4. Source Quality
Prefer primary sources, then strong independent secondary sources. Syndicated copies do not count as independent confirmation.

### 5. Evidence Fidelity
Does the Claim faithfully represent the Evidence?

Statuses:
- SUPPORTED_BY_EVIDENCE
- PARTIALLY_SUPPORTED
- NOT_SUPPORTED
- AMBIGUOUS

**Known unsupported or overstrong factual Claims entering the governed Brief = 0.**

### 6. Verification Quality
Compare expected vs actual:
- VERIFIED
- SUPPORTED
- CONFLICTING
- STALE
- INSUFFICIENT_EVIDENCE

Record mismatches, not only aggregate accuracy.

### 7. Governance Quality
Mandatory:
- FACT without Evidence reaching Brief = 0
- Evidence without Source reaching Brief = 0
- BLOCK leakage = 0
- known unsupported factual Brief claims = 0
- RESTRICT qualification preservation = 100%

A mandatory Governance failure means Golden Case FAIL.

### 8. Traceability
Every important factual Brief statement must support:

`Brief → Claim → Verification/Governance → Evidence → Source`

**Target: 100% for important factual Brief statements.**

### 9. Strategic Insight Quality
Score important INFERENCE items:

| Score | Meaning |
|---|---|
| 0 | Unsupported / irrelevant |
| 1 | Obvious summary |
| 2 | Useful connection between verified facts |
| 3 | Strong meeting-relevant strategic insight |

V1 should produce multiple insights scoring 2 or 3 without inventing facts.

### 10. Meeting Usefulness
Human review, 1–5:
- relevance to meeting goal
- company understanding
- executive understanding
- strategic opportunities
- meeting questions
- clarity / scanability
- trust / source transparency

**Final target: average ≥ 4.0/5; no critical dimension below 3.**

## Performance Baseline
Record:
- total Case runtime
- research runtime
- model runtime
- verification runtime
- Governance runtime
- search count
- provider calls
- retries/follow-ups
- retained Sources
- generated Claims
- blocked/restricted Claims

Do not invent an SLA before baseline data exists.

## Context Quality
Confirm context compression:
- retains important verified Claims
- retains conflicts
- retains RESTRICT qualifications
- retains provenance
- removes low-value duplicates
- prevents raw-source overload

## Knowledge Gaps
Valid outputs include:
- Not found
- Could not verify
- Source unavailable
- Conflicting information
- Insufficient evidence

A visible gap is preferable to fabrication.

## Quick Brief Evaluation
A user should understand the most important meeting intelligence in roughly one minute of reading:
- executive summary
- strategic signals
- important projects
- executive priorities
- opportunities
- meeting questions
- risks
- knowledge gaps

FACT / INFERENCE / RECOMMENDATION remain distinct.

## Full Brief Evaluation
Review:
- Company Intelligence
- Executive Intelligence
- Projects / Case Studies
- Strategic Analysis
- Opportunity Map
- Meeting Strategy
- Knowledge Gaps
- Sources / Evidence

## Progressive Use Across V1

`Early V1 → Ground Truth + fixtures`

`Research Cards → Recall + Coverage`

`Evidence/Verification Cards → Fidelity + Verification`

`Governance Cards → leakage + traceability`

`Analysis/Brief Cards → strategic value + usefulness`

`C20 → complete Golden Case evaluation`

`C21 → measured hardening/regression`

`C22 → reproducible final demo evidence`

## Change Comparison
For quality-affecting changes:

`Baseline Before → bounded change → Candidate After → regression review → Accept/Reject`

Do not call a change better merely because one output looks better.

## V1 Golden Case PASS Gate

| Requirement | Target |
|---|---|
| Wrong confirmed entity | 0 |
| High-priority research categories | attempted + status recorded |
| Important Ground Truth recall | measured + reviewed |
| Unsupported/overstrong FACT leakage | 0 known |
| BLOCK leakage | 0 |
| RESTRICT preservation | 100% mandatory fixtures |
| Important factual Brief traceability | 100% |
| Verification fixtures | meet approved baseline |
| Context compression trust preservation | PASS |
| Strategic insight | multiple useful evidence-based insights |
| Meeting usefulness | average ≥ 4.0/5 |
| Knowledge gaps visible | PASS |
| Performance baseline | recorded |
| End-to-end workflow | PASS |

Failure of a mandatory trust invariant:

`GOLDEN_CASE_STATUS = FAIL`

## Final Evidence Record
Record:
- Case
- Company
- Executive
- Meeting Goal
- Ground Truth Version
- Evaluation Date
- Model / Provider
- Search Provider
- Configuration
- Entity Accuracy
- Research Recall
- Research Coverage
- Evidence Fidelity
- Verification
- Governance
- Traceability
- Strategic Insight
- Meeting Usefulness
- Performance
- Knowledge Gaps
- Regressions
- Known Limitations
- GOLDEN_CASE_STATUS: PASS / FAIL

## Card Integration
No new Card is created.

This Contract strengthens:
- C05 — Entity Resolution
- C06/C07/C08 — Research Coverage / Recall
- C09 — Evidence traceability
- C11 — Fidelity + Verification
- C13 — Governance
- C15 — Strategic Insight
- C16 — Brief usefulness
- C19 — Performance / observability
- C20 — full Golden Case evaluation
- C21 — measured hardening/regression
- C22 — reproducible final demo evidence

## Final Principle
The portfolio claim should not merely be:

“I built a multi-agent research app.”

The evidence-backed claim should be:

“I built and evaluated a governed strategic-intelligence system that discovers important public information, preserves evidence fidelity and traceability, blocks unsupported factual claims, and converts verified intelligence into useful meeting preparation.”

**Golden Case proves the product value.**
