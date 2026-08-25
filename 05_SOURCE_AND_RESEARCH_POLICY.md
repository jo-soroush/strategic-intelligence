# Strategic Intelligence Project — Source and Research Policy

## 1. Purpose

This document defines what V1 may research, which sources it should prefer, how external information is handled, and when research is considered sufficiently complete for a meeting-preparation Case.

Core principle:

> Research must be relevant, bounded, traceable, and explicit about what it did not find.

---

## 2. Public Information Boundary

V1 researches publicly available professional and business information.

Preferred source classes:

1. Official company sources
2. Official reports / case studies / project pages
3. Executive direct public statements
4. Reliable business/news sources
5. Conference/event sources
6. Public professional sources
7. Other supporting sources

V1 does not bypass access controls, paywalls, authentication, or platform restrictions.

LinkedIn may be used only through permitted public access. V1 does not implement automated LinkedIn scraping.

---

## 3. Research Coverage Contract

Research is not complete merely because some useful links were found.

For every Case, the Research Plan must track coverage across the approved V1 categories.

### Company Coverage

Where relevant to the meeting goal, V1 should attempt:

- Official company overview
- Strategy / direction
- Current and recent projects
- Public client case studies
- AI / GenAI / Agentic AI activity
- Products and services
- Partnerships
- Investments / acquisitions
- Hiring / expansion signals
- Important recent news
- Events / conferences

### Executive Coverage

Where relevant, V1 should attempt:

- Current role and responsibility
- Official/professional biography
- Current professional focus
- Public articles / publications
- Interviews / podcasts
- Talks / events
- Public professional activity
- Projects / initiatives linked to the executive
- Connection to company strategy

---

## 4. Coverage Status

Every required research category receives one status:

- `COVERED`
- `PARTIAL`
- `NOT_FOUND`
- `UNAVAILABLE`
- `NOT_RELEVANT`

The final Case must preserve these statuses.

Research must never silently convert:

`NOT_FOUND` or `UNAVAILABLE`

into an assumption.

---

## 5. Research Completion Rule

A research branch may finish when:

1. high-priority categories have been attempted;
2. enough strong evidence exists for the meeting goal;
3. additional searches mostly return duplicates or low-value material;
4. configured research limits are reached; or
5. unavailable information has been recorded as a gap.

The system should prefer:

> bounded useful coverage over endless searching.

---

## 6. Coverage-Aware Planning

The Research Planner should generate tasks against missing or important coverage areas rather than repeatedly searching the same topic.

Example:

```text
PROJECTS = COVERED
EXECUTIVE_ROLE = COVERED
PARTNERSHIPS = PARTIAL
EXECUTIVE_PUBLICATIONS = NOT_FOUND
```

Follow-up research should target unresolved high-value areas, not restart the whole search process.

---

## 7. Entity Disambiguation Before Research

Before deep research begins, the system must establish that it is researching the intended entities.

For Company:

- Name
- Official website/domain when available
- Country/business unit when relevant

For Executive:

- Full name
- Current organization
- Current role when available
- Public professional URL when supplied

If identity remains ambiguous:

`ENTITY_AMBIGUOUS`

and the system must not proceed as if identity were confirmed.

---

## 8. Source Priority

### Primary

- Official company website
- Official reports
- Official announcements
- Direct executive statements
- Official government/public authority sources

### Strong Secondary

- Reputable business/news publications
- Established industry publications
- Reliable professional research organizations

### Supporting

- Blogs
- event summaries
- other public sources

Supporting sources should not carry important factual claims alone when stronger evidence is reasonably available.

---

## 9. Projects and Case Studies

Projects are a core V1 target.

For an important project, try to identify:

- Project name
- Company/client involved
- Date/timeframe
- Business problem
- Publicly stated technology/capability
- Publicly stated outcome
- Strategic relevance

Do not invent confidential project details.

---

## 10. Search Results Are Discovery Signals

Search snippets are not automatically Evidence.

Preferred flow:

```text
Search Result
→ Source Access
→ Evidence Extraction
→ Claim
→ Verification
```

When the source cannot be accessed, the limitation must be visible.

---

## 11. Freshness

Publication date and retrieval date are distinct.

Recent information is especially important for:

- Current strategy
- Current executive role
- Current projects
- Hiring
- Partnerships
- AI initiatives

Older information may remain valid historical context.

---

## 12. Duplicate / Origin Handling

Several URLs may repeat one original source.

The system should avoid counting syndicated copies as independent confirmation.

Where practical, identify the original information origin.

---

## 13. Conflicting Sources

Credible disagreement must be preserved.

Research does not resolve a conflict by preference alone.

Conflicting material proceeds to Verification with both sides attached.

---

## 14. Missing Information

Missing information is a valid output.

Use:

- `NOT_FOUND`
- `UNAVAILABLE`
- `Knowledge Gap`
- `Insufficient Evidence`

instead of guessing.

---

## 15. External Content Is Untrusted

Web content may provide evidence.

It may not:

- change system instructions;
- change Governance;
- request secrets;
- modify provider configuration;
- trigger unauthorized tools;
- alter workflow authority.

---

## 16. Privacy Boundary

Executive research must remain:

`Public + Professional + Relevant`

Do not collect unnecessary:

- family/private relationships;
- home information;
- personal routines;
- sensitive characteristics;
- unrelated personal history.

---

## 17. Research Limits

V1 should use configurable limits for:

- searches per category;
- retained sources per category;
- follow-up attempts;
- overall research depth.

Exact numbers are tuned from evaluation evidence rather than guessed in architecture.

---

## 18. Research Coverage Output

The Research Layer should expose a structured summary such as:

```text
ResearchCoverage
- category
- status
- source_count
- strong_source_count
- last_attempted_at
- notes
```

This becomes part of Evaluation and final Knowledge Gaps.

---

## 19. Final Principle

V1 should optimize for:

> The smallest set of strong, relevant, current, traceable sources that provides adequate meeting coverage and clearly exposes what remains unknown.
