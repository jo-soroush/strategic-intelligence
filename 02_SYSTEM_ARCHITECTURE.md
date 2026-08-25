# Strategic Intelligence Project — V1 System Architecture

## 1. Architecture Goal

V1 should be:

- Simple enough to complete in **3 weeks**
- Useful for a real meeting
- Trustworthy
- Testable
- Maintainable
- Local-first
- Cloud-ready
- Easy to extend later

The architecture should avoid unnecessary multi-agent complexity.

Core principle:

**Controlled Workflow + Specialized Components + Evidence-First Governance**

---

# 2. High-Level Architecture

```text
Case Input
   ↓
Research Planner
   ↓
┌─────────────────────────────┐
│ Company Research            │
│ Executive Research          │
└─────────────────────────────┘
   ↓
Evidence Layer
   ↓
Verification Gate
   ↓
Strategic Analysis
   ↓
Governance Gate
   ↓
Brief Generator
   ↓
Quick Brief / Full Brief
```

Supporting the full workflow:

```text
Structured State
Persistent Storage
Provider Layer
Failure & Recovery
Observability & Audit
Security & Privacy
Testing & Evaluation
```

---

# 3. Architecture Style

V1 uses a **controlled deterministic workflow**.

The system does not rely on a large group of autonomous agents.

AI is used only where reasoning, interpretation, or summarization provides clear value.

Deterministic code should control:

- Workflow transitions
- Evidence requirements
- Verification status
- Governance rules
- Error handling
- Storage
- Traceability

AI components should not be able to bypass these controls.

---

# 4. Orchestration

V1 uses a structured workflow orchestrator.

LangGraph is the preferred orchestration framework for V1.

The workflow should have clear stages:

```text
START
  ↓
validate_case
  ↓
plan_research
  ↓
company_research
executive_research
  ↓
build_evidence
  ↓
verify_claims
  ↓
strategic_analysis
  ↓
governance_gate
  ↓
generate_brief
  ↓
persist_results
  ↓
END
```

Independent research branches may run in parallel where practical.

Workflow state must remain explicit and structured.

---

# 5. Component 1 — Input & Case Context

Each meeting or negotiation is represented as one **Case**.

Required input:

- Company name
- Executive name
- Meeting goal

Optional input:

- Company website
- Company LinkedIn URL
- Executive LinkedIn URL
- Extra meeting context

Each case receives:

- Case ID
- Creation date
- Status

Everything produced later belongs to this case.

Core principle:

**One Meeting → One Case → One Traceable Intelligence Workflow**

---

# 6. Component 2 — Research Layer

The Research Layer discovers relevant public information.

It contains three logical parts.

## 6.1 Research Planner

The planner converts the case into focused research tasks.

Example research areas:

### Company

- Strategy
- Projects
- Client case studies
- AI activity
- Partnerships
- Hiring
- Investments
- News
- Events

### Executive

- Current role
- Professional focus
- Articles
- Interviews
- Public posts
- Talks
- Projects
- Recent activity

The planner should avoid unnecessary research.

Every research task should support the meeting goal.

---

## 6.2 Research Workers

V1 uses two main research branches:

### Company Research

Researches company-related intelligence.

### Executive Research

Researches relevant public professional information about the target executive.

These may run in parallel.

They are specialized workflow components, not fully autonomous agents.

---

## 6.3 Search Provider

Research components should not directly depend on one search vendor.

Architecture:

```text
Research Component
      ↓
SearchProvider Interface
      ↓
Concrete Search Adapter
```

This allows search providers to change later without changing core business logic.

---

# 7. LinkedIn Boundary

LinkedIn is an important public intelligence source.

V1 may use:

- Public company LinkedIn information
- Public professional executive information
- Public posts
- Public articles
- Public events
- Public job information

The user may provide LinkedIn URLs.

V1 does **not** implement automatic LinkedIn scraping.

Blocked or unavailable LinkedIn content must not be bypassed.

Other public sources should be used when LinkedIn information is unavailable.

---

# 8. Component 3 — Evidence Layer

The Evidence Layer converts raw research into traceable information.

Core model:

```text
Source
   ↓
Evidence
   ↓
Claim
```

## 8.1 Source Record

Each source should contain:

- Source ID
- URL/reference
- Title
- Publisher
- Source type
- Publication date when available
- Retrieval date

---

## 8.2 Evidence Record

Evidence represents the useful information extracted from a source.

Each evidence record contains:

- Evidence ID
- Source ID
- Evidence content
- Topic
- Relevance to case

---

## 8.3 Claim Record

A claim represents something the system may use in analysis or output.

Each claim contains:

- Claim ID
- Claim text
- Claim type
- Verification status
- Linked evidence

Claim types:

- FACT
- INFERENCE
- RECOMMENDATION

---

## 8.4 Claim–Evidence Relationship

A claim may have:

- One supporting source
- Multiple supporting sources
- Conflicting sources

Important claims must remain traceable back to evidence.

---

# 9. Component 4 — Verification Layer

The Verification Layer decides whether a factual claim is trustworthy enough to use.

It performs:

- Source quality check
- Freshness check
- Evidence sufficiency check
- Cross-source verification
- Conflict detection
- Duplicate-source detection

Possible verification states:

- VERIFIED
- SUPPORTED
- CONFLICTING
- STALE
- INSUFFICIENT_EVIDENCE

Important rule:

A weak or unsupported claim must not silently become a Fact.

If evidence is missing:

**INSUFFICIENT_EVIDENCE**

is a valid system result.

---

# 10. Component 5 — Strategic Analysis Layer

The Strategic Analysis Layer uses:

- Verified claims
- Evidence
- Case context
- Meeting goal

It does not perform unrestricted new research.

It analyzes:

- Company direction
- Executive priorities
- Project meaning
- Strategic signals
- Opportunity areas
- User relevance
- Meeting topics
- Questions
- Risks
- Knowledge gaps

The system must separate:

### FACT

Supported by evidence.

### INFERENCE

Interpretation based on evidence.

### RECOMMENDATION

Suggested meeting action or discussion point.

The Analysis Layer must not create new unsupported facts.

---

# 11. Component 6 — Governance Gate

The Governance Gate is a deterministic control layer where practical.

Its role is different from Verification.

Verification asks:

> Is this information supported?

Governance asks:

> Is this information acceptable for final use?

The gate checks:

- Facts have evidence
- Fact / Inference / Recommendation are correctly separated
- Unsupported factual claims are blocked
- Uncertainty is visible
- Conflicts are visible
- Stale information is flagged
- Personal information remains relevant and professional
- Claims are traceable
- Failed claims are blocked or downgraded

Possible results:

- PASS
- RESTRICT
- BLOCK

AI components cannot override hard governance rules.

---

# 12. Component 7 — Brief Generator

The Brief Generator receives only governance-approved intelligence.

It does not:

- Search
- Verify
- Create new factual claims

Its job is:

**Select → Prioritize → Summarize → Present**

V1 produces two views.

## 12.1 Quick Brief

Designed for a 2–3 minute read before the meeting.

Contains:

- Most important facts
- Key signals
- Best opportunities
- Important risks
- Best questions

---

## 12.2 Full Brief

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

Both views use the same governed intelligence.

---

# 13. Component 8 — State & Storage

V1 separates workflow state from persistent storage.

## 13.1 Workflow State

LangGraph state represents the current execution.

Example state contains:

- Case
- Research plan
- Raw findings
- Sources
- Evidence
- Claims
- Verification results
- Analysis
- Governance results
- Brief

Workflow state is temporary execution context.

---

## 13.2 Persistent Storage

V1 should use:

**SQLite**

for structured local storage.

Possible entities:

- Cases
- Companies
- Executives
- Sources
- Evidence
- Claims
- Verification results
- Analysis
- Governance decisions
- Briefs
- Audit events

---

## 13.3 Local Files

Large or raw artifacts should be stored as files.

Example:

```text
data/
  cases/
    <case_id>/
      sources/
      artifacts/
      briefs/
```

The database stores metadata and references.

---

## 13.4 Repository Pattern

Core business logic must not directly depend on SQLite.

Architecture:

```text
Application
   ↓
Repository Interface
   ↓
SQLite Repository
```

Future:

```text
Application
   ↓
Same Repository Interface
   ↓
PostgreSQL / Cloud Database
```

This supports local-first and cloud-ready development.

---

# 14. Component 9 — Provider Layer

External AI and search vendors should remain outside core business logic.

V1 provider interfaces:

## LLMProvider

Used for:

- Analysis
- Classification
- Structured reasoning
- Brief generation

## SearchProvider

Used for:

- Web search
- Source discovery

## EmbeddingProvider

Only introduced if embeddings become clearly necessary for V1.

Do not add embeddings only because they are common in AI systems.

Architecture:

```text
Core Application
      ↓
Provider Interface
      ↓
Provider Adapter
```

Example:

```text
StrategicAnalysis
      ↓
LLMProvider
      ↓
OllamaAdapter
```

Later:

```text
LLMProvider
   ├── OllamaAdapter
   ├── OpenAIAdapter
   ├── AzureOpenAIAdapter
   └── OtherAdapter
```

Vendor SDKs must not spread across the application.

---

# 15. Local-First, Cloud-Ready

V1 runs locally first.

Local V1 may use:

- Local application
- Local SQLite
- Local files
- Local LLM where suitable
- External search provider where required

Cloud-specific logic must remain outside core business logic.

Future migration may include:

- PostgreSQL
- Object storage
- Hosted LLMs
- Cloud secrets
- Container deployment
- Managed observability

The core workflow should not require redesign for cloud deployment.

---

# 16. Component 10 — Failure, Retry & Recovery

Failures must be safe and visible.

## Search Failure

Retry a limited number of times.

If still unsuccessful:

- Record failure
- Continue when possible
- Expose the information gap

## Blocked Website

Do not bypass restrictions.

Use another source or record the gap.

## LLM Failure

Use controlled retries.

If unresolved:

- Save workflow status
- Stop the affected step safely

## Missing Publication Date

Keep the source if useful.

Mark freshness as:

**UNKNOWN**

## Weak Evidence

Return:

**INSUFFICIENT_EVIDENCE**

## Conflicting Sources

Store both.

Mark:

**CONFLICTING**

## Interrupted Workflow

Persist enough progress to allow safe recovery or resume.

Core principle:

> **Partial but trustworthy result is better than a complete unreliable result.**

---

# 17. Component 11 — Observability & Audit

V1 should provide lightweight observability.

Track:

- Case ID
- Workflow step
- Search tasks
- Sources discovered
- Provider calls
- Verification decisions
- Governance decisions
- Retries
- Failures
- Timestamps
- Execution duration where practical

Important intelligence should remain traceable through:

```text
Final Brief
   ↓
Analysis
   ↓
Claim
   ↓
Evidence
   ↓
Source
```

The architecture should allow future integration with tools such as LangSmith or cloud observability platforms without requiring core redesign.

---

# 18. Component 12 — Security & Privacy

V1 should implement basic security from the beginning.

## Secrets

- API keys must not be hardcoded
- Use environment/config management
- `.env` must not be committed

## Input Validation

Validate:

- URLs
- Required fields
- Data formats

## Public Information Boundary

Executive research should focus only on:

- Public
- Professional
- Relevant

information.

Avoid unnecessary personal profiling.

## Data Minimization

Store only information useful for the case.

## External Content Safety

Web content must be treated as untrusted input.

External webpages must not be allowed to change system instructions or workflow rules.

This is important protection against prompt injection from researched content.

---

# 19. Component 13 — Testing & Evaluation

V1 must be testable at component and system level.

Important test areas:

## Research Tests

- Correct search planning
- Relevant source discovery
- Company/executive separation

## Evidence Tests

- Source → Evidence links
- Evidence → Claim links
- Duplicate handling

## Verification Tests

- Unsupported facts rejected
- Conflicts detected
- Stale information flagged
- Weak evidence handled safely

## Governance Tests

- Facts require evidence
- Inferences cannot appear as Facts
- Blocked claims stay out of final brief
- Privacy rules are respected

## Recovery Tests

- Search failure
- Provider failure
- Missing dates
- Interrupted workflow

## Brief Tests

- Uses approved intelligence only
- No new unsupported facts
- Important claims remain traceable

## End-to-End Test

At least one real:

**Company + Executive + Meeting Goal**

case should be tested from input through final brief.

---

# 20. Architecture Boundaries

V1 should not introduce architecture for features we are not building.

Do not design unnecessary systems for:

- Continuous monitoring
- Alerts
- CRM
- Teams
- Multi-user permissions
- Enterprise dashboards
- Large-scale crawling
- Automatic LinkedIn scraping
- Autonomous outreach
- Large agent teams

These can be designed later if needed.

---

# 21. V1 Architecture Principles

## 1. Simplicity First

Do not add complexity without clear business value.

## 2. Evidence Before Analysis

Strategic conclusions should start from traceable information.

## 3. Deterministic Controls

Critical verification and governance rules should not depend entirely on LLM judgment.

## 4. Modular Components

Each component has one clear responsibility.

## 5. Provider Independence

Core business logic should not depend on one AI or search vendor.

## 6. Local First

V1 should run locally and remain easy to develop.

## 7. Cloud Ready

Infrastructure choices must not trap the application locally.

## 8. Safe Failure

Missing information is acceptable.

Invented information is not.

## 9. Human Judgment

The system supports preparation and decision-making.

It does not replace the user's judgment.

## 10. Build Only What V1 Needs

The architecture should support the product.

The product should not exist to demonstrate architectural complexity.

---

# 22. Final V1 Architecture

```text
┌────────────────────────────────────┐
│            User / UI               │
│ Company + Executive + Goal         │
└─────────────────┬──────────────────┘
                  ↓
┌────────────────────────────────────┐
│        Case Context / Validation   │
└─────────────────┬──────────────────┘
                  ↓
┌────────────────────────────────────┐
│          Research Planner          │
└──────────┬────────────────┬────────┘
           ↓                ↓
┌──────────────────┐  ┌──────────────────┐
│ Company Research │  │Executive Research│
└──────────┬───────┘  └─────────┬────────┘
           └──────────┬─────────┘
                      ↓
┌────────────────────────────────────┐
│          Evidence Layer            │
│ Source → Evidence → Claim          │
└─────────────────┬──────────────────┘
                  ↓
┌────────────────────────────────────┐
│         Verification Gate          │
│ Quality / Freshness / Conflict     │
└─────────────────┬──────────────────┘
                  ↓
┌────────────────────────────────────┐
│       Strategic Analysis           │
│ Direction / Opportunity / Meeting  │
└─────────────────┬──────────────────┘
                  ↓
┌────────────────────────────────────┐
│          Governance Gate           │
│ PASS / RESTRICT / BLOCK            │
└─────────────────┬──────────────────┘
                  ↓
┌────────────────────────────────────┐
│          Brief Generator           │
└──────────┬────────────────┬────────┘
           ↓                ↓
     Quick Brief        Full Brief
```

Supporting architecture:

```text
LangGraph Structured State
        +
Repository Interfaces
        +
SQLite / Local Files
        +
Provider Interfaces
        +
Retry / Recovery
        +
Observability / Audit
        +
Security / Privacy
        +
Testing / Evaluation
```

---

# 23. Final Architecture Statement

V1 is a:

> **Local-first, cloud-ready, evidence-first strategic intelligence system built around a controlled LangGraph workflow, modular AI components, deterministic verification and governance gates, structured state, traceable evidence, and provider-independent infrastructure.**

The architecture intentionally avoids unnecessary autonomous multi-agent complexity.

The priority is:

**Useful → Trustworthy → Explainable → Maintainable → Extendable**