# Strategic Intelligence Project — Data and State Model

## 1. Purpose

This document defines how V1 represents information inside the system.

The goal is to keep data:

- Structured
- Traceable
- Validated
- Easy to test
- Local-first
- Cloud-ready

Core rule:

> **Important information must remain traceable from Source → Evidence → Claim → Analysis → Final Brief.**

---

# 2. Modeling Approach

V1 should use typed models.

Recommended Python approach:

- Pydantic models for application/domain data
- Typed LangGraph state for workflow execution
- Repository models for persistence

Do not pass large uncontrolled dictionaries or raw strings between components when a structured model is possible.

---

# 3. Main Data Relationships

```text
Case
 │
 ├── Company
 ├── Executive
 ├── Research Tasks
 │
 ├── Sources
 │     ↓
 │   Evidence
 │     ↓
 │   Claims
 │     ↓
 │   Verification Results
 │     ↓
 │   Strategic Analysis
 │     ↓
 │   Governance Decisions
 │     ↓
 └── Meeting Brief
```

Everything belongs to a Case.

---

# 4. Stable IDs

Important records receive stable IDs.

Examples:

- `case_id`
- `company_id`
- `executive_id`
- `research_task_id`
- `source_id`
- `evidence_id`
- `claim_id`
- `verification_id`
- `analysis_id`
- `governance_id`
- `brief_id`
- `audit_event_id`

IDs should not depend on display names.

A person's name can change format.

An ID should remain stable.

---

# 5. Case Model

The Case is the root object for one meeting-preparation workflow.

Example fields:

```text
Case
- case_id
- company_id
- executive_id
- meeting_goal
- extra_context
- company_website
- company_linkedin_url
- executive_linkedin_url
- status
- created_at
- updated_at
```

Possible status values:

- `CREATED`
- `RESEARCHING`
- `VERIFYING`
- `ANALYZING`
- `GOVERNING`
- `GENERATING_BRIEF`
- `COMPLETED`
- `PARTIAL`
- `FAILED`

The Case should not contain all research data directly.

It connects the other records.

---

# 6. Company Model

Represents the target organization.

Example:

```text
Company
- company_id
- name
- official_website
- linkedin_url
- country
- industry
- created_at
- updated_at
```

Only fields useful for V1 should be stored.

Do not build a large company-master-data system.

---

# 7. Executive Model

Represents the professional target person.

Example:

```text
Executive
- executive_id
- full_name
- current_title
- company_id
- linkedin_url
- public_profile_url
- created_at
- updated_at
```

Important:

This model is for professional meeting intelligence.

It should not become a personal-profile database.

---

# 8. Research Plan Model

The Research Plan represents what the Research Planner wants to investigate.

```text
ResearchPlan
- case_id
- tasks[]
- created_at
```

Each task is structured.

---

# 9. Research Task Model

Example:

```text
ResearchTask
- research_task_id
- case_id
- target_type
- category
- query
- priority
- status
- created_at
- completed_at
```

Possible `target_type`:

- `COMPANY`
- `EXECUTIVE`

Possible categories:

- `STRATEGY`
- `PROJECTS`
- `CLIENT_CASES`
- `AI_ACTIVITY`
- `PARTNERSHIPS`
- `HIRING`
- `NEWS`
- `EVENTS`
- `EXECUTIVE_ROLE`
- `EXECUTIVE_FOCUS`
- `PUBLICATIONS`
- `INTERVIEWS`
- `PUBLIC_ACTIVITY`

Possible task status:

- `PENDING`
- `RUNNING`
- `COMPLETED`
- `PARTIAL`
- `FAILED`

---

# 10. Raw Finding Model

Research components should return structured findings before verification.

Example:

```text
RawFinding
- finding_id
- case_id
- research_task_id
- source_url
- title
- extracted_content
- topic
- relevance
- discovered_at
```

Raw Findings are not trusted Facts.

They are research input for the Evidence Layer.

---

# 11. Source Model

A Source represents where information came from.

Example:

```text
Source
- source_id
- case_id
- url
- title
- publisher
- source_type
- publication_date
- retrieval_date
- quality_class
- access_status
```

Possible source types:

- `OFFICIAL_COMPANY`
- `OFFICIAL_REPORT`
- `CASE_STUDY`
- `EXECUTIVE_DIRECT`
- `NEWS`
- `BUSINESS_PUBLICATION`
- `CONFERENCE`
- `PUBLIC_LINKEDIN`
- `JOB_POSTING`
- `OTHER`

Possible quality classes:

- `PRIMARY`
- `STRONG_SECONDARY`
- `OTHER`

Possible access states:

- `AVAILABLE`
- `PARTIAL`
- `BLOCKED`
- `FAILED`

---

# 12. Evidence Model

Evidence is a specific useful piece of information taken from a Source.

Example:

```text
Evidence
- evidence_id
- case_id
- source_id
- content
- topic
- relevance
- publication_date
- extracted_at
```

Evidence must always reference a Source.

Evidence should contain only the relevant content needed to support claims.

Do not store unnecessarily large copied pages as Evidence.

---

# 13. Claim Model

A Claim is a statement the system may use.

Example:

```text
Claim
- claim_id
- case_id
- text
- claim_type
- topic
- evidence_ids[]
- verification_status
- created_at
```

Possible claim types:

- `FACT`
- `INFERENCE`
- `RECOMMENDATION`

Important:

A `FACT` requires Evidence.

An `INFERENCE` must be based on available Evidence.

A `RECOMMENDATION` must connect to the meeting goal and available intelligence.

---

# 14. Claim–Evidence Relationship

One Claim may use several Evidence records.

Example:

```text
Claim
    ↓
Evidence A
Evidence B
Evidence C
```

One Evidence record may also support multiple Claims.

For clean persistence, V1 should support a many-to-many relationship.

Conceptually:

```text
ClaimEvidenceLink
- claim_id
- evidence_id
- relationship_type
```

Possible relationship types:

- `SUPPORTS`
- `CONTRADICTS`
- `CONTEXT`

This allows conflict detection without destroying evidence.

---

# 15. Verification Result Model

Verification should be stored separately from the Claim.

Example:

```text
VerificationResult
- verification_id
- claim_id
- status
- source_quality
- freshness_status
- independent_source_count
- conflict_detected
- duplicate_risk
- notes
- verified_at
```

Possible status values:

- `VERIFIED`
- `SUPPORTED`
- `CONFLICTING`
- `STALE`
- `INSUFFICIENT_EVIDENCE`

Possible freshness status:

- `CURRENT`
- `AGING`
- `STALE`
- `UNKNOWN`

This separation is important.

The Claim says:

> What are we saying?

Verification says:

> How well is it supported?

---

# 16. Strategic Analysis Model

The analysis should be structured, not only one large LLM-generated report.

Example:

```text
StrategicAnalysis
- analysis_id
- case_id
- company_direction[]
- executive_priorities[]
- project_meaning[]
- strategic_signals[]
- opportunity_areas[]
- user_relevance[]
- meeting_topics[]
- smart_questions[]
- risks[]
- knowledge_gaps[]
- created_at
```

Each analysis item should contain enough information to remain traceable.

Example:

```text
AnalysisItem
- item_id
- text
- type
- related_claim_ids[]
- rationale
```

Possible type:

- `FACT`
- `INFERENCE`
- `RECOMMENDATION`

Important:

Strategic Analysis should reference Claims rather than raw web content.

---

# 17. Opportunity Model

Opportunities are important enough to represent clearly.

Example:

```text
Opportunity
- opportunity_id
- case_id
- title
- description
- related_claim_ids[]
- relevance_to_goal
- confidence
- assumptions[]
```

Opportunity does not mean confirmed business opportunity.

It may be an AI-supported strategic inference.

It must be presented accordingly.

---

# 18. Meeting Question Model

Questions should also remain connected to intelligence.

Example:

```text
MeetingQuestion
- question_id
- case_id
- question
- reason
- related_claim_ids[]
- priority
```

This prevents the system from generating generic questions unrelated to research.

---

# 19. Governance Decision Model

Governance decisions should be stored separately.

Example:

```text
GovernanceDecision
- governance_id
- case_id
- target_type
- target_id
- decision
- reason_codes[]
- notes
- decided_at
```

Possible decisions:

- `PASS`
- `RESTRICT`
- `BLOCK`

Possible reason codes:

- `MISSING_EVIDENCE`
- `UNVERIFIED_FACT`
- `STALE_INFORMATION`
- `CONFLICTING_EVIDENCE`
- `UNCERTAINTY_NOT_VISIBLE`
- `PRIVACY_BOUNDARY`
- `PERSONAL_DATA_NOT_RELEVANT`
- `UNTRACEABLE_CLAIM`
- `MISCLASSIFIED_INFERENCE`

Hard Governance rules should be deterministic where practical.

---

# 20. Brief Model

The final brief should be structured before being rendered.

Example:

```text
MeetingBrief
- brief_id
- case_id
- version
- executive_summary
- company_situation
- strategy_direction
- projects_client_cases
- ai_activity
- executive_intelligence
- strategic_signals
- opportunity_map
- user_relevance
- meeting_strategy
- questions
- do_not_assume
- knowledge_gaps
- source_references
- generated_at
```

The Brief Generator should receive only Governance-approved content.

---

# 21. Quick Brief Model

Quick Brief can be produced from the same governed data.

Example:

```text
QuickBrief
- brief_id
- case_id
- key_facts[]
- key_signals[]
- top_opportunities[]
- top_questions[]
- major_risks[]
- generated_at
```

Quick Brief and Full Brief should not perform separate research.

They are two presentations of the same trusted intelligence.

---

# 22. Audit Event Model

Important workflow actions should produce Audit Events.

Example:

```text
AuditEvent
- audit_event_id
- case_id
- event_type
- component
- target_id
- status
- timestamp
- metadata
```

Example event types:

- `CASE_CREATED`
- `RESEARCH_STARTED`
- `SOURCE_DISCOVERED`
- `EVIDENCE_CREATED`
- `CLAIM_CREATED`
- `CLAIM_VERIFIED`
- `CLAIM_REJECTED`
- `CONFLICT_FOUND`
- `GOVERNANCE_RESTRICTED`
- `GOVERNANCE_BLOCKED`
- `BRIEF_GENERATED`
- `PROVIDER_FAILED`
- `RETRY_OCCURRED`
- `WORKFLOW_COMPLETED`

Audit Events should explain system behavior without storing sensitive secrets.

---

# 23. Error Model

Errors should be structured.

Example:

```text
WorkflowError
- error_id
- case_id
- component
- error_code
- message
- retryable
- occurred_at
```

Possible error codes:

- `INVALID_INPUT`
- `SEARCH_FAILED`
- `SOURCE_UNAVAILABLE`
- `PROVIDER_UNAVAILABLE`
- `INVALID_PROVIDER_RESPONSE`
- `PERSISTENCE_FAILED`
- `INSUFFICIENT_EVIDENCE`
- `GOVERNANCE_BLOCKED`
- `WORKFLOW_FAILED`

---

# 24. Workflow State Model

LangGraph Workflow State is different from permanent database data.

It represents the current execution.

Conceptually:

```text
WorkflowState
- case_context
- research_plan
- company_findings
- executive_findings
- sources
- evidence
- claims
- verification_results
- strategic_analysis
- governance_decisions
- quick_brief
- full_brief
- errors
- current_stage
```

The workflow should pass IDs and structured records rather than uncontrolled free text when possible.

---

# 25. Workflow State vs Persistent Storage

These are separate responsibilities.

## Workflow State

Used while a workflow is running.

Questions:

- What stage are we at?
- What data does the next node need?
- Did something fail?
- Can we resume?

## Persistent Storage

Used after execution.

Questions:

- What Cases exist?
- What Evidence did we collect?
- What Claims were used?
- What Governance decisions were made?
- What Brief was generated?

Core rule:

> **LangGraph State is not the database.**

---

# 26. State Size Rule

Workflow State should not become a container for every raw web page.

Prefer:

```text
Workflow State
→ structured objects / IDs
→ persistent artifact storage
```

Large raw source content should remain in artifact storage when needed.

This keeps workflow execution easier to manage.

---

# 27. Checkpointing

The workflow should support checkpoints at important stages.

Recommended checkpoints:

```text
Case Validated
      ↓
Research Completed
      ↓
Evidence Built
      ↓
Verification Completed
      ↓
Analysis Completed
      ↓
Governance Completed
      ↓
Brief Generated
```

This supports:

- Resume
- Failure recovery
- Debugging
- Auditability

The exact LangGraph checkpoint implementation can be decided during implementation.

---

# 28. Persistence Model

V1 uses:

**SQLite + Local Files**

SQLite stores structured records.

Local files store larger artifacts.

Conceptual local structure:

```text
data/
  strategic_intelligence.db

  cases/
    <case_id>/
      sources/
      artifacts/
      briefs/
```

---

# 29. Repository Boundary

Domain components should not directly run SQLite queries.

Use repository interfaces.

Example:

```text
ClaimRepository
- create()
- get()
- list_for_case()
- update()
```

Possible repositories:

- `CaseRepository`
- `SourceRepository`
- `EvidenceRepository`
- `ClaimRepository`
- `VerificationRepository`
- `GovernanceRepository`
- `BriefRepository`
- `AuditRepository`

Do not create separate repositories if implementation becomes unnecessarily complex.

The final implementation should stay practical for V1.

---

# 30. Cloud-Ready Data Boundary

Domain models should remain independent from SQLite.

Future infrastructure may use:

```text
SQLite
   ↓ later
PostgreSQL
```

and:

```text
Local Files
   ↓ later
S3 / Azure Blob / Cloud Storage
```

Business logic should continue using the same domain and repository contracts.

---

# 31. Data Validation

Typed models should validate important rules.

Examples:

A Case cannot start without:

- Company
- Executive
- Meeting goal

A FACT cannot be approved without:

- Evidence reference

A Governance Decision must use:

- PASS
- RESTRICT
- BLOCK

A Source URL should have a valid structure when URL-based.

Validation should happen at clear system boundaries.

---

# 32. Immutability and History

Important evidence and governance decisions should not be silently overwritten.

Prefer preserving history.

Example:

If a Claim changes:

```text
Claim v1
Claim v2
```

or record the modification through Audit Events.

For V1, full enterprise event sourcing is unnecessary.

But important decision history should remain understandable.

---

# 33. Timestamps

Important records should include timestamps.

Recommended:

- `created_at`
- `updated_at`
- `retrieval_date`
- `publication_date`
- `verified_at`
- `decided_at`
- `generated_at`

Internally, timestamps should use a consistent timezone-aware format.

Presentation can later convert timestamps for the UI.

---

# 34. Publication Date vs Retrieval Date

These must not be confused.

**Publication Date**

When the source was published.

**Retrieval Date**

When our system accessed it.

Example:

```text
Published: 2026-05-01
Retrieved: 2026-08-24
```

Both are important for Freshness analysis.

---

# 35. Source Independence

Several websites may repeat the same original source.

Therefore verification must not simply count URLs.

Example:

```text
Company Press Release
       ↓
News Site A
News Site B
News Site C
```

These may represent only one original information source.

Data models should allow source relationships or duplicate-group metadata if needed.

For V1, simple duplicate/origin tracking is enough.

---

# 36. Confidence

V1 should avoid fake mathematical precision.

Do not automatically produce values like:

`Confidence = 87.4%`

unless we have a real calibrated method.

Prefer understandable states such as:

- High support
- Moderate support
- Weak support
- Insufficient evidence

or verification statuses already defined.

---

# 37. User Context Model

The system may need user-provided context to identify relevance.

Example:

```text
UserContext
- case_id
- professional_background
- capabilities
- meeting_objective
- constraints
- notes
```

Important:

The system should use only information explicitly provided or approved for the Case.

It must not invent user experience.

For V1 this model can remain small.

---

# 38. Privacy and Data Minimization

The data model itself should support privacy.

Executive records should contain only relevant professional information.

Avoid fields for unnecessary personal information.

Do not create fields for:

- Family
- Private relationships
- Sensitive characteristics
- Home address
- Personal lifestyle information

unless a future valid product requirement requires redesign and governance review.

For V1, they are out of scope.

---

# 39. External Content Boundary

Raw external content is untrusted.

It should never become:

- System configuration
- Prompt instructions
- Governance rules
- Provider settings

without explicit application logic.

External content enters through:

```text
Source
   ↓
Evidence Extraction
```

not:

```text
External Website
   ↓
System Instructions
```

---

# 40. Data Lifecycle

Simple V1 lifecycle:

```text
Case Created
   ↓
Research Data Collected
   ↓
Evidence Created
   ↓
Claims Created
   ↓
Claims Verified
   ↓
Analysis Created
   ↓
Governance Decisions Applied
   ↓
Brief Generated
   ↓
Case Completed
```

Important Case data persists after completion.

Temporary execution data may be cleaned when no longer needed.

---

# 41. Deletion

V1 should make it possible to delete a Case and its associated stored data.

Conceptually:

```text
Delete Case
   ↓
Structured Records
   +
Case Artifacts
```

Deletion behavior should be designed carefully during persistence implementation.

---

# 42. Versioning

At minimum, generated Briefs should have a version.

Example:

```text
brief_version = 1
```

If research is rerun later:

```text
brief_version = 2
```

Old Briefs should not necessarily be silently replaced.

This becomes useful for future change tracking.

---

# 43. Serialization

Important domain models should support clean serialization.

Recommended format for internal interchange:

**JSON-compatible structured data**

This helps:

- LangGraph
- Testing
- API development
- Cloud migration
- Debugging
- Export

---

# 44. Database Schema Principle

The database should reflect domain relationships, but should not become over-normalized for V1.

Priorities:

- Clear relationships
- Traceability
- Easy querying
- Maintainability

Avoid building a complex enterprise data platform for a single-user V1.

---

# 45. Core Traceability Chain

The most important relationship in the project is:

```text
Source
  ↓
Evidence
  ↓
Claim
  ↓
Verification
  ↓
Strategic Analysis
  ↓
Governance
  ↓
Meeting Brief
```

This chain must survive:

- Workflow execution
- Persistence
- Brief generation
- Debugging
- Future cloud migration

---

# 46. Example

Example source:

```text
Source:
Capgemini official announcement
```

Evidence:

```text
Capgemini announced a new AI-related initiative.
```

Claim:

```text
FACT:
Capgemini launched initiative X.
```

Verification:

```text
VERIFIED
Primary source
Current
```

Analysis:

```text
INFERENCE:
This may indicate increased investment in this capability.
```

Governance:

```text
PASS
```

Recommendation:

```text
RECOMMENDATION:
Ask the executive how this initiative connects to the team's current priorities.
```

Final Brief:

```text
Strategic Signal:
Capgemini recently launched X.

Why it matters:
This may indicate increased focus on Y.

Meeting Question:
How does X affect your team's priorities this year?

Source:
Official company announcement.
```

This is the behavior the data model must support.

---

# 47. V1 Data Principles

## 1. Structured First

Use typed data instead of uncontrolled text.

## 2. Evidence First

Claims should remain connected to evidence.

## 3. Traceability

Important outputs must be explainable.

## 4. Separate State and Storage

Workflow execution and permanent data are different concerns.

## 5. Keep Models Small

Do not model future enterprise features prematurely.

## 6. Provider Independent

Domain data should not depend on LLM or search vendors.

## 7. Storage Independent

Domain models should not depend on SQLite.

## 8. Cloud Ready

Persisted models should migrate cleanly to future infrastructure.

## 9. Privacy by Design

Do not collect fields V1 does not need.

## 10. Human-Understandable Trust

Avoid fake confidence precision.

---

# 48. Final Data Architecture

```text
                         CASE
                          │
          ┌───────────────┼───────────────┐
          ↓               ↓               ↓
       Company         Executive      ResearchPlan
                                          │
                                          ↓
                                    ResearchTasks
                                          │
                                          ↓
                                      Findings
                                          │
                                          ↓
                                       Sources
                                          │
                                          ↓
                                      Evidence
                                          │
                                          ↓
                                       Claims
                                          │
                                          ↓
                                  VerificationResults
                                          │
                                          ↓
                                  StrategicAnalysis
                                          │
                                          ↓
                                  GovernanceDecision
                                          │
                                          ↓
                                     MeetingBrief
                                          │
                                          ↓
                                     AuditEvents
```

Execution:

```text
LangGraph WorkflowState
        ↓
Domain Models
        ↓
Repository Interfaces
        ↓
SQLite + Local Artifacts
```

Future:

```text
Same Domain Models
        ↓
Same Repository Contracts
        ↓
PostgreSQL + Cloud Object Storage
```

---

# 49. Final Statement

The V1 data model is designed around:

> **Structured intelligence with full traceability from original public source to the final meeting recommendation.**

The model should remain simple enough for the three-week V1 while creating strong boundaries for:

- Governance
- Verification
- Testing
- Local development
- Cloud migration
- Future product growth