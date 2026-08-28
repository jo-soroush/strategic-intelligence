# Strategic Intelligence Project — Components and Responsibilities

## 1. Purpose

This document defines the responsibility and boundary of every major V1 component.

The goal is to prevent:

- Duplicate logic
- Unclear ownership
- Agent overlap
- Hidden dependencies
- Uncontrolled AI behavior
- Architecture becoming unnecessarily complex

Core rule:

> **Each component should have one clear responsibility and a clear input/output contract.**

V1 uses specialized components inside a controlled workflow.

A component does not automatically mean an autonomous AI agent.

---

# 2. Responsibility Model

The V1 workflow is:

```text
Case Input
    ↓
Research Planner
    ↓
Company Research ──┐
                   ├──→ Evidence Layer
Executive Research ┘
                         ↓
                  Verification Gate
                         ↓
                  Governance Gate
                         ↓
                  Strategic Analysis
                         ↓
                  Brief Generator
                         ↓
                 Quick / Full Brief
```

Supporting components:

```text
Provider Layer
Repository Layer
Workflow State
Observability
Security
Configuration
```

---

# 3. Case Context Component

## Responsibility

Create and validate one Strategic Intelligence Case.

## Owns

- Company name
- Executive name
- Meeting goal
- Optional company website
- Optional company LinkedIn URL
- Optional executive LinkedIn URL
- Optional user context
- Case ID
- Creation timestamp
- Case status

## Must

Validate required inputs before research begins.

Create a stable Case ID used throughout the workflow.

## Must Not

- Perform web research
- Analyze the company
- Generate meeting recommendations
- Verify evidence

## Output

A validated:

**CaseContext**

---

# 4. Research Planner

## Responsibility

Translate the Case Context into focused research tasks.

## Owns

Research planning only.

Example task groups:

### Company

- Strategy
- Projects
- Client cases
- AI activity
- Partnerships
- Hiring
- Investments
- News
- Events

### Executive

- Role
- Responsibilities
- Professional focus
- Projects
- Articles
- Interviews
- Public posts
- Talks
- Recent professional activity

## Must

Use:

- Company
- Executive
- Meeting goal
- User context

to decide which research areas are relevant.

Prioritize research that can improve meeting preparation.

## Must Not

- Decide whether claims are true
- Perform final strategic analysis
- Generate the meeting brief
- Bypass source policies

## Output

Structured:

**ResearchPlan**

containing focused research tasks.

---

# 5. Company Research Component

## Responsibility

Discover relevant public information about the company.

## Research Areas

- Company overview
- Strategy
- Current projects
- Recent projects
- Client case studies
- AI initiatives
- GenAI initiatives
- Agentic AI activity
- Data and analytics activity
- AI governance activity
- Products and services
- Partnerships
- Investments
- Acquisitions
- Hiring signals
- Expansion signals
- Important news
- Events and conferences
- Relevant public LinkedIn signals

## Must

Follow the Research Plan.

Prefer relevant and high-quality sources.

Return structured findings.

Preserve source references.

## Must Not

- Decide that a finding is verified
- Turn weak information into Fact
- Perform final opportunity analysis
- Generate meeting advice
- Automatically scrape LinkedIn

## Output

**RawCompanyFindings**

---

# 6. Executive Research Component

## Responsibility

Discover relevant public professional information about the target executive.

## Research Areas

- Current role
- Responsibilities
- Relevant career background
- Professional focus
- Projects and initiatives
- Articles
- Publications
- Interviews
- Podcasts
- Talks
- Panels
- Conferences
- Public professional posts
- Repeated professional topics
- Recent professional activity
- Connection to company strategy

## Must

Collect only information relevant to professional meeting preparation.

Use publicly available professional information.

Preserve source references.

## Must Not

- Perform unnecessary personal profiling
- Collect irrelevant private information
- Infer sensitive personal characteristics
- Automatically scrape LinkedIn
- Present inferred priorities as confirmed facts

## Output

**RawExecutiveFindings**

---

# 7. Search Provider

## Responsibility

Provide a vendor-independent interface for web search and source discovery.

## Interface Concept

```text
Research Component
        ↓
SearchProvider
        ↓
Search Adapter
```

## Must

Accept structured search requests.

Return structured search results.

Normalize provider-specific responses.

Expose useful error information.

## Must Not

Contain:

- Company analysis
- Executive analysis
- Governance decisions
- Meeting strategy

## Benefit

Search vendors can change without rewriting core research logic.

---

# 8. Source Acquisition / Content Access

## Responsibility

Access permitted public source content required by research.

This responsibility may initially remain small and may be implemented through provider/tool adapters.

## Must

Respect:

- Public accessibility
- Source restrictions
- Access failures
- Platform boundaries

## Must Not

- Bypass blocked content
- Circumvent authentication
- Circumvent platform restrictions
- Automatically scrape LinkedIn in V1

External content must always be treated as:

**Untrusted Input**

---

# 9. Evidence Layer

## Responsibility

Convert raw research findings into traceable evidence structures.

Core relationship:

```text
Source
  ↓
Evidence
  ↓
Claim
```

## Owns

### Source Records

- Source ID
- URL/reference
- Title
- Publisher
- Source type
- Publication date
- Retrieval date

### Evidence Records

- Evidence ID
- Source ID
- Evidence content
- Topic
- Case relevance

### Claim Records

- Claim ID
- Claim text
- Claim type
- Evidence links

## Must

Maintain traceability.

Support multiple evidence records per claim.

Support conflicting evidence.

Detect or flag obvious duplicates where possible.

## Must Not

Perform final strategic analysis.

It structures evidence; it does not decide business meaning.

## Output

Structured:

**Sources + Evidence + Claims**

---

# 10. Verification Component

## Responsibility

Evaluate whether factual claims have enough support to be trusted.

## Checks

### Source Quality

Evaluate whether evidence comes from:

- Primary source
- Strong secondary source
- Other source

### Freshness

Consider:

- Publication date
- Retrieval date
- Newer information

### Evidence Sufficiency

Determine whether the claim has meaningful supporting evidence.

### Cross-Source Verification

For important claims, seek or evaluate independent confirmation when practical.

### Conflict Detection

Detect disagreement between credible evidence.

### Duplicate Detection

Avoid treating copied information as independent confirmation.

## Verification Status

A claim may receive:

- `VERIFIED`
- `SUPPORTED`
- `CONFLICTING`
- `STALE`
- `INSUFFICIENT_EVIDENCE`

## Must Not

- Invent missing evidence
- Hide conflicts
- Automatically promote weak claims
- Generate strategic recommendations

## Output

**VerifiedClaims**

with verification metadata.

---

# 11. Strategic Analysis Component

## Responsibility

Turn verified intelligence into meeting-relevant strategic understanding.

## Inputs

Only:

- Case Context
- Verified Claims
- Evidence
- Meeting Goal
- User-provided context

## Analysis Areas

### Company Direction

What does the evidence suggest about current company direction?

### Executive Priorities

What appears professionally important to the executive?

### Project Meaning

What do projects and client cases tell us?

### Strategic Signals

What developments may be strategically meaningful?

### Opportunity Areas

Where may relevant opportunities exist?

### User Relevance

Where does user-provided experience/context connect with identified opportunities?

### Meeting Topics

What subjects may be valuable to discuss?

### Smart Questions

What evidence-based questions could improve the meeting?

### Risks

What should not be assumed?

### Knowledge Gaps

What could not be established?

## Must

Clearly classify outputs as:

- FACT
- INFERENCE
- RECOMMENDATION

## Must Not

- Invent user experience
- Invent company facts
- Perform unrestricted new research
- Convert inference into fact
- Override Verification results

## Output

**StrategicAnalysis**

---

# 12. Governance Gate

## Responsibility

Make the final policy decision about what intelligence is allowed into the user-facing output.

Verification and Governance are separate.

Verification asks:

> **Is the claim supported?**

Governance asks:

> **Can this information be used in this way?**

## Checks

- Factual claims have evidence
- Claim classification is valid
- Unsupported claims are blocked
- Uncertainty is visible
- Conflicts remain visible
- Stale information is flagged
- Relevant privacy boundaries are respected
- Professional-data boundary is respected
- Important claims remain traceable

## Decisions

Every governed item receives:

- `PASS`
- `RESTRICT`
- `BLOCK`

## PASS

The information may be used normally.

## RESTRICT

The information may be used only with uncertainty, limitation, or warning visible.

## BLOCK

The information must not appear as usable intelligence.

## Critical Rule

> **AI components cannot override hard Governance Gate rules.**

## Output

**GovernedIntelligence**

---

# 13. Brief Generator

## Responsibility

Transform Governed Intelligence into a useful meeting-preparation document.

## Input

Only:

- Governed Intelligence
- Case Context
- Meeting Goal

## Must

- Prioritize
- Organize
- Summarize
- Present

## Must Not

- Perform new research
- Invent new facts
- Bypass governance
- Upgrade uncertain claims
- Remove important uncertainty

## Outputs

### Quick Brief

Designed for approximately a 2–3 minute review.

Contains:

- Critical facts
- Important signals
- Main opportunities
- Main risks
- Best meeting questions

### Full Brief

Contains:

1. Executive Summary
2. Company Situation
3. Strategy & Direction
4. Projects & Client Cases
5. AI / Technology Activity
6. Executive Intelligence
7. Strategic Signals
8. Opportunity Map
9. User Relevance
10. Meeting Strategy
11. Questions to Ask
12. Do Not Assume
13. Knowledge Gaps
14. Evidence & Sources

---

# 14. Workflow Orchestrator

## Responsibility

Control execution order and workflow state.

LangGraph is the preferred V1 orchestrator.

## Owns

- Workflow transitions
- Branching
- Parallel research execution
- Retry routing
- Failure routing
- State progression
- Resume/recovery coordination

## Must

Keep workflow transitions explicit.

Example:

```text
validate
   ↓
plan
   ↓
research
   ↓
evidence
   ↓
verify
   ↓
analyze
   ↓
govern
   ↓
brief
```

## Must Not

Contain business logic that belongs to individual components.

The orchestrator coordinates.

It should not become a giant service containing the whole application.

---

# 15. Workflow State

## Responsibility

Represent the current execution state of one case.

Possible state fields:

- Case Context
- Research Plan
- Company Findings
- Executive Findings
- Sources
- Evidence
- Claims
- Verification Results
- Strategic Analysis
- Governance Results
- Briefs
- Errors
- Workflow status

## Rule

Workflow State is not the same as permanent storage.

---

# 16. Repository Layer

## Responsibility

Provide storage access without exposing database implementation details to business logic.

Architecture:

```text
Business Component
       ↓
Repository Interface
       ↓
Repository Implementation
```

V1:

```text
Repository Interface
       ↓
SQLite
```

Future:

```text
Repository Interface
       ↓
PostgreSQL / Cloud Database
```

## Must

Handle:

- Create
- Read
- Update
- Persistence
- Data relationships

## Must Not

Contain strategic analysis or AI reasoning.

---

# 17. File / Artifact Storage

## Responsibility

Store larger case artifacts that should not live directly inside database rows.

Possible structure:

```text
data/
  cases/
    <case_id>/
      sources/
      artifacts/
      briefs/
```

## Possible Content

- Raw source artifacts
- Extracted content
- Generated reports
- Exported briefs

Database records should reference these artifacts when needed.

---

# 18. LLM Provider

## Responsibility

Provide a vendor-independent interface to language models.

Used by components that genuinely need model reasoning.

Possible uses:

- Structured extraction
- Analysis
- Classification
- Brief generation

Architecture:

```text
Component
   ↓
LLMProvider
   ↓
Provider Adapter
```

Example V1:

```text
LLMProvider
   ↓
OllamaAdapter
```

Possible future:

```text
LLMProvider
   ├── OllamaAdapter
   ├── OpenAIAdapter
   ├── AzureOpenAIAdapter
   └── OtherAdapter
```

## Must Not

Contain business rules.

---

# 19. Embedding Provider

Embeddings are **not automatically required for V1**.

An `EmbeddingProvider` should only be introduced if a confirmed V1 requirement needs semantic retrieval or similarity search.

Do not add vector infrastructure only because it is common in AI applications.

If introduced, it must follow the same provider-abstraction pattern.

---

# 20. Configuration Component

## Responsibility

Manage application configuration centrally.

Examples:

- Provider selection
- Model configuration
- Search limits
- Retry limits
- Database location
- Artifact location
- Logging level
- Governance thresholds

Secrets must come from secure environment/configuration mechanisms.

## Must Not

Contain business logic.

---

# 21. Observability Component

## Responsibility

Make system execution understandable.

Track:

- Case ID
- Workflow run
- Component execution
- Search operations
- Provider calls
- Verification decisions
- Governance decisions
- Errors
- Retries
- Duration
- Cost/token information when available

## Core Requirement

A developer should be able to understand:

> **What happened during this case and where did something go wrong?**

V1 can use lightweight local logging.

The architecture should allow future integration with:

- OpenTelemetry
- LangSmith
- Cloud observability platforms

without redesigning business logic.

---

# 22. Audit Component

## Responsibility

Maintain important decision history.

Important chain:

```text
Brief
 ↓
Strategic Analysis
 ↓
Claim
 ↓
Evidence
 ↓
Source
```

Governance and Verification decisions should also be traceable.

Auditability is part of the product's trust model.

---

# 23. Security Boundary

## Responsibility

Protect the application from unsafe input and configuration mistakes.

V1 requirements include:

- No hardcoded secrets
- `.env` excluded from Git
- Input validation
- URL validation
- Safe file paths
- Controlled provider configuration
- External content treated as untrusted

---

# 24. Prompt-Injection Boundary

Web content may contain instructions intended to manipulate an AI system.

Research content is **data**, not system instruction.

External content must never be allowed to:

- Change system rules
- Change Governance rules
- Request secrets
- Trigger unauthorized tools
- Modify provider configuration
- Override workflow logic

Core rule:

> **Web content can provide evidence. It cannot control the application.**

---

# 25. Privacy Boundary

Executive intelligence is limited to information that is:

- Public
- Professional
- Relevant to the meeting

The system should avoid unnecessary collection of:

- Private life information
- Family information
- Sensitive personal characteristics
- Irrelevant personal history
- Unnecessary personal identifiers

Data minimization applies throughout the workflow.

---

# 26. Error & Recovery Responsibility

Each component should return structured failure information.

The orchestrator decides workflow recovery.

Examples:

```text
SEARCH_FAILED
SOURCE_UNAVAILABLE
PROVIDER_UNAVAILABLE
INVALID_RESPONSE
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
UNKNOWN_FRESHNESS
GOVERNANCE_BLOCKED
```

Components should not silently hide errors.

---

# 27. Component Communication Rule

Components should communicate using structured models.

Avoid passing large uncontrolled strings between components.

Preferred:

```text
ResearchPlan
RawFinding
SourceRecord
EvidenceRecord
ClaimRecord
VerificationResult
StrategicAnalysis
GovernanceDecision
MeetingBrief
```

Structured contracts improve:

- Testing
- Validation
- Debugging
- Provider independence
- Cloud migration
- Maintainability

---

# 28. AI vs Deterministic Code

Use AI when the task requires:

- Semantic understanding
- Interpretation
- Reasoning
- Summarization
- Strategic analysis

Use deterministic code when the task requires:

- IDs
- Validation
- Workflow transitions
- Storage
- Evidence presence checks
- Governance enforcement
- Status management
- Retry limits
- Configuration
- Audit records

Core rule:

> **Do not ask an LLM to do something normal code can do more reliably.**

---

# 29. Component Independence

A component should know as little as possible about unrelated components.

Example:

Company Research should not know how SQLite stores claims.

Strategic Analysis should not know which search API discovered a source.

Brief Generator should not know which LLM provider produced an inference.

Governance should not depend on the UI.

This allows components to evolve independently.

---

# 30. Local-First / Cloud-Ready Responsibility

Infrastructure dependencies must remain behind interfaces.

V1:

```text
Local UI
Local Application
LangGraph
SQLite
Local Files
Ollama where suitable
External Search Provider where needed
```

Future:

```text
Cloud UI/API
Containerized Application
Managed Workflow Runtime if needed
PostgreSQL
Object Storage
Hosted LLM
Managed Search
Cloud Observability
```

Core business logic should survive this migration without major redesign.

---

# 31. V1 Component Ownership Summary

| Component | Owns | Does Not Own |
|---|---|---|
| Case Context | Meeting input | Research |
| Research Planner | Research tasks | Verification |
| Company Research | Company discovery | Strategy decisions |
| Executive Research | Executive discovery | Personal profiling |
| Search Provider | Search access | Business logic |
| Evidence Layer | Source/evidence/claim structure | Strategic meaning |
| Verification | Evidence trust | Meeting advice |
| Strategic Analysis | Strategic interpretation | New unsupported facts |
| Governance Gate | Final policy controls | Research |
| Brief Generator | Presentation | New intelligence |
| Orchestrator | Workflow execution | Component business logic |
| Repository | Persistence | AI reasoning |
| LLM Provider | Model access | Business rules |
| Observability | Execution visibility | Workflow decisions |
| Audit | Decision trace | Analysis |
| Security | Application boundaries | Strategic analysis |

---

# 32. Final Responsibility Principle

Every V1 component should be explainable with one sentence.

If a component begins doing several unrelated jobs, its boundary should be reviewed.

The architecture should remain:

**Focused → Modular → Testable → Traceable → Replaceable**

The system is not designed around the number of agents.

It is designed around clear responsibilities required to produce:

> **Trustworthy, evidence-backed strategic intelligence for a real executive meeting.**
