# Strategic Intelligence Project — Governance and Trust

## 1. Purpose

Governance is a runtime trust boundary, not only documentation.

Core principle:

> Evidence before Fact. Uncertainty before fabrication.

---

## 2. Trust Flow

```text
Source
→ Evidence
→ Candidate Claim
→ Evidence Fidelity Gate
→ Verification
→ Strategic Analysis
→ Governance Gate
→ Final Brief
```

No important factual claim should bypass this chain.

---

## 3. Intelligence Types

- `FACT` — supported statement
- `INFERENCE` — interpretation based on evidence
- `RECOMMENDATION` — suggested meeting action or question

These types must remain distinct.

---

## 4. Evidence Fidelity Gate

This gate addresses a critical failure mode:

> The source may be real, but the AI may extract a Claim that is stronger or different from what the source actually supports.

Before a candidate FACT can proceed to normal Verification, the system must check whether the Evidence actually supports the Claim.

Possible fidelity states:

- `SUPPORTED_BY_EVIDENCE`
- `PARTIALLY_SUPPORTED`
- `NOT_SUPPORTED`
- `AMBIGUOUS`

---

## 5. Fidelity Rule

For a candidate FACT:

```text
Evidence span
→ Candidate Claim
→ Fidelity check
```

If:

`NOT_SUPPORTED`

the Claim must not proceed as a FACT.

If:

`PARTIALLY_SUPPORTED` or `AMBIGUOUS`

the Claim must be weakened, reclassified, restricted, or rejected.

AI cannot strengthen the wording beyond the source.

---

## 6. Evidence Fidelity Requirements

Where practical, retain:

- Source ID
- Evidence ID
- Evidence excerpt/structured evidence
- Candidate Claim
- Fidelity status
- Fidelity notes/reason

This creates traceability from original source meaning to final Claim.

---

## 7. Deterministic Trust Rules

Mandatory:

```text
FACT without Evidence → BLOCK
Evidence without Source → BLOCK
FACT with NOT_SUPPORTED fidelity → BLOCK
INFERENCE cannot silently become FACT
BLOCK cannot enter Brief
RESTRICT qualification must remain visible
Missing evidence → abstain
Governance failure → no final Brief
```

---

## 8. Verification Status

After Fidelity, Verification may assign:

- `VERIFIED`
- `SUPPORTED`
- `CONFLICTING`
- `STALE`
- `INSUFFICIENT_EVIDENCE`

Verification evaluates support quality; Governance decides final use.

---

## 9. Source Quality

Source classes:

- `PRIMARY`
- `STRONG_SECONDARY`
- `OTHER`

Primary does not automatically mean true.

Independent context may still be valuable.

---

## 10. Freshness

Freshness is contextual.

Current-state claims require stronger recency than historical context.

Unknown publication dates must remain unknown.

---

## 11. Conflict

Credible conflicts remain visible.

The system must not silently select one source when uncertainty remains.

---

## 12. Uncertainty

Valid output includes:

- Evidence suggests...
- Available information indicates...
- Could not be independently confirmed...
- Insufficient evidence...
- Conflicting public information exists...

Avoid fake confidence percentages unless a calibrated method exists.

---

## 13. Governance Decisions

- `PASS`
- `RESTRICT`
- `BLOCK`

`BLOCK` is non-overridable by AI.

`RESTRICT` must preserve the reason/qualification into the final Brief.

---

## 14. Context Budget / Compression Trust Rule

Raw web content should not flow directly into final Strategic Analysis at scale.

Preferred trust-preserving compression:

```text
Raw Sources
→ Relevant Evidence
→ Fidelity-checked Claims
→ Verified Claims
→ Ranked Strategic Signals
→ Strategic Analysis
→ Brief
```

Compression must preserve:

- Claim IDs
- Evidence links
- conflict/stale/uncertainty metadata
- Governance restrictions

Do not summarize away uncertainty or provenance.

---

## 15. Strategic Inference

Inference is valuable and allowed.

But important inference must reference verified/restricted Claims.

Never:

```text
LLM imagination → strategic conclusion
```

Prefer:

```text
Verified Claims → explicit reasoning → INFERENCE
```

---

## 16. Recommendation Governance

Recommendations must connect to:

- meeting goal;
- governed intelligence;
- approved user context.

Recommendations must not invent supporting facts.

---

## 17. Privacy

Executive intelligence is:

`Public + Professional + Relevant`

Unnecessary personal information is BLOCKED or excluded.

Sensitive personal inference is prohibited.

---

## 18. Prompt Injection

External source content remains untrusted.

It cannot override:

- Governance
- system instructions
- tool permissions
- provider configuration
- workflow routing
- secrets boundaries

---

## 19. Audit

Important trust decisions should be reconstructable:

```text
Source
→ Evidence
→ Fidelity
→ Claim
→ Verification
→ Analysis
→ Governance
→ Brief
```

---

## 20. Mandatory Tests

Minimum:

1. FACT without Evidence → BLOCK
2. Evidence without Source → BLOCK
3. Evidence does not entail Claim → BLOCK/reclassify
4. Partially supported Claim cannot remain overstrong
5. INFERENCE cannot become FACT
6. CONFLICT remains visible
7. STALE current claim is restricted
8. BLOCK cannot enter Brief
9. RESTRICT survives Brief
10. prompt injection cannot change trust rules
11. context compression preserves provenance/restrictions
12. missing evidence produces abstention

---

## 21. Final Principle

> A real source is not enough. The Claim must faithfully represent what the source supports.

V1 therefore protects both:

**provenance** and **semantic fidelity**.
