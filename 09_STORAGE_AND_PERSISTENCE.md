# Strategic Intelligence Project — Storage and Persistence

## 1. Purpose

This document defines how V1 stores structured data, artifacts, workflow progress, and generated briefs.

The storage design must be:

- Local-first
- Cloud-ready
- Traceable
- Recoverable
- Simple enough for a 3-week V1
- Independent from core business logic

Core principle:

> Domain logic depends on repository contracts, not directly on SQLite or file-system details.

---

# 2. V1 Storage Strategy

V1 uses two local persistence mechanisms:

1. **SQLite** for structured records
2. **Local files** for larger artifacts and exported briefs

Conceptually:

```text
Application
   ↓
Repository Interfaces
   ↓
SQLite

Application
   ↓
Artifact Storage Interface
   ↓
Local Files
```

Future migration:

```text
SQLite → PostgreSQL
Local Files → Object Storage
```

without rewriting domain logic.

---

# 3. What Goes Into SQLite

SQLite stores structured application data such as:

- Cases
- Companies
- Executives
- Workflow runs
- Research plans
- Research tasks
- Sources
- Evidence
- Claims
- Claim/evidence links
- Verification results
- Strategic analysis
- Governance decisions
- Brief metadata
- Audit events
- Errors
- Checkpoint metadata

SQLite should not become a raw-document warehouse.

---

# 4. What Goes Into Local Files

Local files are used for larger artifacts.

Examples:

- Source captures when permitted
- Extracted source text
- Intermediate research artifacts
- Full generated briefs
- Quick briefs
- Exported JSON/Markdown
- Debug artifacts when useful

Suggested structure:

```text
data/
  strategic_intelligence.db

  cases/
    <case_id>/
      runs/
        <workflow_run_id>/
          sources/
          artifacts/
          briefs/
          exports/
```

The database stores references to these artifacts.

---

# 5. Repository Pattern

Business components must not execute SQL directly.

Use repository interfaces.

Conceptually:

```text
Business Component
       ↓
Repository Interface
       ↓
SQLite Repository
```

Possible repositories:

- `CaseRepository`
- `CompanyRepository`
- `ExecutiveRepository`
- `WorkflowRunRepository`
- `ResearchRepository`
- `SourceRepository`
- `EvidenceRepository`
- `ClaimRepository`
- `VerificationRepository`
- `AnalysisRepository`
- `GovernanceRepository`
- `BriefRepository`
- `AuditRepository`

Do not create unnecessary repository classes if a simpler grouping keeps V1 cleaner.

---

# 6. Repository Responsibilities

Repositories own persistence operations only.

Examples:

- Create
- Read
- Update
- List
- Delete
- Transaction-safe writes

Repositories do not own:

- Strategic reasoning
- Verification logic
- Governance decisions
- Prompt construction
- Research planning

---

# 7. Artifact Storage Interface

Large-file access should also stay behind an interface.

Conceptually:

```text
Application
   ↓
ArtifactStore
   ↓
LocalArtifactStore
```

Future:

```text
ArtifactStore
   ↓
S3 / Azure Blob / GCS Adapter
```

This keeps cloud migration simple.

---

# 8. Core Persistent Entities

The minimum V1 persistent entities are:

```text
Case
Company
Executive
WorkflowRun
ResearchTask
Source
Evidence
Claim
ClaimEvidenceLink
VerificationResult
StrategicAnalysis
GovernanceDecision
MeetingBrief
AuditEvent
WorkflowError
```

These align with the Data and State Model.

---

# 9. Case Persistence

A Case is the main root for one meeting-preparation scenario.

Persist:

- `case_id`
- company reference
- executive reference
- meeting goal
- optional URLs
- extra context
- case status
- timestamps

A Case may have multiple workflow runs.

---

# 10. Workflow Run Persistence

Each execution gets a unique:

`workflow_run_id`

Example:

```text
Case A
 ├── Run 1
 ├── Run 2
 └── Run 3
```

Persist:

- run ID
- case ID
- start time
- end time
- status
- last completed stage
- provider metadata where useful
- brief version reference

This supports reruns, debugging, and future comparison.

---

# 11. Stable IDs

Use stable generated IDs for persistent records.

Recommended:

- UUID-style IDs
- application-generated IDs

Do not use display names as primary keys.

Examples:

- `case_id`
- `source_id`
- `claim_id`

Names may change; IDs should not.

---

# 12. Relationships

Important relationships include:

```text
Case
 ↓
WorkflowRun
 ↓
ResearchTask
 ↓
Source
 ↓
Evidence
 ↓
Claim
 ↓
Verification
 ↓
StrategicAnalysis
 ↓
GovernanceDecision
 ↓
MeetingBrief
```

Also:

```text
Claim ↔ Evidence
```

is many-to-many.

---

# 13. Claim–Evidence Link Table

Use a relationship structure such as:

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

This is essential for traceability and conflict handling.

---

# 14. Transactions

Writes that must stay consistent should use transactions.

Example:

When creating a Claim with Evidence links:

```text
Create Claim
+
Create ClaimEvidenceLinks
```

should succeed together or fail together.

Avoid partially persisted trust chains.

---

# 15. Persistence Boundaries

Persistence should happen at meaningful workflow stages.

Examples:

- Case creation
- Research completion
- Evidence creation
- Verification completion
- Analysis completion
- Governance completion
- Brief generation

Do not write every tiny temporary model state to permanent storage unless useful.

---

# 16. Checkpoints

Workflow checkpoints and domain persistence are related but not identical.

Recommended safe checkpoints:

- `CASE_VALIDATED`
- `RESEARCH_PLANNED`
- `RESEARCH_COMPLETED`
- `EVIDENCE_BUILT`
- `VERIFICATION_COMPLETED`
- `ANALYSIS_COMPLETED`
- `GOVERNANCE_COMPLETED`
- `BRIEF_GENERATED`

The implementation may use LangGraph checkpoint support, database metadata, or both.

---

# 17. Resume Behavior

If a workflow stops unexpectedly:

```text
Load Case
↓
Load WorkflowRun
↓
Read last safe checkpoint
↓
Restore required state
↓
Resume from next valid stage
```

Resume must not blindly rerun the whole Case unless necessary.

---

# 18. Safe Reruns

A user may rerun research later.

A rerun should create a new WorkflowRun instead of silently replacing the previous run.

Example:

```text
Case A
  Run 1 → Brief v1
  Run 2 → Brief v2
```

This preserves history.

---

# 19. Brief Versioning

Every generated Brief should include a version.

Example:

```text
brief_version = 1
brief_version = 2
```

The system should not silently overwrite old Briefs.

The latest version may be marked as current.

---

# 20. Brief Storage

Briefs can be stored in both:

- Structured database form
- Rendered artifact form such as Markdown

Example:

```text
briefs/
  quick_brief_v1.md
  full_brief_v1.md
```

Database metadata links each artifact to:

- Case
- Workflow run
- Brief version
- generation timestamp

---

# 21. Raw Source Storage

Do not store complete external pages unless necessary and permitted.

Prefer:

- Source metadata
- Short relevant evidence
- Minimal extracted content

If larger source content is temporarily useful, store it as an artifact with clear Case/Run ownership.

---

# 22. Data Minimization

Persistence follows the same privacy rule as research:

> Store only what the Case needs.

Do not persist unnecessary personal data simply because it was publicly accessible.

---

# 23. Deduplication

The storage layer should support duplicate protection.

Possible duplicate keys/signals:

- canonical URL
- source-content hash
- evidence hash
- normalized title + publisher
- Claim/evidence relationship uniqueness

V1 does not need perfect semantic deduplication.

Simple deterministic duplicate protection is enough.

---

# 24. Source Canonicalization

When practical, normalize URLs before duplicate checks.

Examples:

- Remove tracking parameters
- Normalize trailing slash
- Preserve meaningful query parameters

Canonicalization must not accidentally merge different pages.

---

# 25. Idempotent Writes

Where practical:

```text
Same source + same Case + same canonical URL
```

should not create uncontrolled duplicate records.

Likewise for exact Evidence or relationship records.

This helps safe retries.

---

# 26. Audit Persistence

Audit events are append-oriented.

Important past decisions should not be silently rewritten.

Examples:

- Claim verified
- Claim restricted
- Claim blocked
- Retry triggered
- Provider failed
- Brief generated

Audit records should support reconstruction of system behavior.

---

# 27. Error Persistence

Errors should be stored when they matter to workflow recovery or audit.

Persist:

- component
- error code
- message
- retryable flag
- timestamp
- related run
- related task/claim when available

Do not store secrets in error messages.

---

# 28. Deletion

V1 should support deleting a Case.

Deleting a Case should remove or safely orphan-clean:

- Case records
- Workflow runs
- Research data
- Sources
- Evidence
- Claims
- Analysis
- Governance decisions
- Briefs
- Case artifacts

Deletion must not leave hidden artifact files behind.

---

# 29. Deletion Safety

Deletion should be explicit and deliberate.

Avoid accidental cascading deletion from unrelated records.

V1 may implement a service-level Case deletion operation that coordinates:

```text
Database deletion
+
Artifact deletion
```

---

# 30. Database Migrations

Even with SQLite, schema changes should be controlled.

Use a migration tool or a simple migration discipline suitable for the chosen ORM/database layer.

Possible future tools:

- Alembic
- SQLModel/SQLAlchemy migrations

Exact implementation can be selected during build.

Do not manually change production-like schema without tracked migration logic.

---

# 31. ORM / Database Access

V1 may use a lightweight ORM or typed database layer.

Good options include:

- SQLAlchemy
- SQLModel

The exact choice should prioritize:

- Simplicity
- Typed models
- Migration support
- Testability
- PostgreSQL compatibility

Avoid a custom database abstraction that duplicates mature libraries.

---

# 32. SQLite Configuration

V1 uses SQLite because:

- Single-user
- Local-first
- Easy setup
- No external database service
- Enough for current scale

SQLite is not a statement that the future product must remain single-node.

---

# 33. SQLite Limitations

Be aware of:

- Limited write concurrency
- Local-file deployment model
- Not ideal for larger multi-user cloud workloads

These limits are acceptable for V1.

Do not solve future distributed-database problems now.

---

# 34. PostgreSQL Migration Path

Future:

```text
Repository Interfaces
       ↓
PostgreSQL Repository
```

Domain logic should not change.

A PostgreSQL migration may become useful for:

- Multi-user deployment
- Cloud service
- Higher concurrency
- More advanced querying
- Managed backups

---

# 35. Object Storage Migration Path

Future artifact storage:

```text
LocalArtifactStore
        ↓
ObjectStorageAdapter
        ↓
S3 / Azure Blob / GCS
```

Artifact references should use application-owned identifiers/URIs rather than assuming fixed local paths everywhere.

---

# 36. Path Handling

Core business logic must not hardcode absolute local machine paths.

Use configured storage roots.

Example concept:

```text
DATA_ROOT
ARTIFACT_ROOT
DATABASE_URL
```

The application resolves paths through infrastructure/configuration code.

---

# 37. Local Backup

V1 backup can remain simple.

Important local assets:

- SQLite database
- `data/cases/` artifacts

A simple backup should copy both consistently.

Full enterprise backup infrastructure is outside V1.

---

# 38. Recovery

Recovery should be possible from:

- Database
- Case artifacts
- workflow checkpoint metadata

The system should not depend only on in-memory state.

---

# 39. Corruption / Persistence Failure

If persistence fails during a critical trust stage:

- Record/log the failure where possible
- Do not pretend the stage completed
- Do not advance the workflow checkpoint incorrectly

For example:

```text
Governance completed in memory
but persistence failed
→ do not mark GOVERNANCE_COMPLETED checkpoint
```

---

# 40. Atomic Stage Completion

A stage should be considered safely complete only when its required outputs are persisted successfully.

Example:

```text
Verification logic succeeds
↓
Verification results saved
↓
Checkpoint = VERIFICATION_COMPLETED
```

This supports correct resume behavior.

---

# 41. Storage and Governance

Blocked content may remain in internal audit storage when needed for traceability, but must be marked clearly and never become user-facing usable intelligence.

Storage status does not equal permission to display.

---

# 42. Storage and Privacy

Data lifecycle must support:

- Minimal collection
- Case-level deletion
- Future retention policy
- Clear ownership
- Traceability

V1 does not need a complex enterprise retention engine.

---

# 43. Storage and Prompt Injection

External content stored as artifacts remains untrusted data.

Persisted source text must never become:

- Application configuration
- Governance policy
- Tool permissions
- System instructions

The trust boundary survives persistence.

---

# 44. Testing Repositories

Repository contracts should be testable.

Minimum tests:

1. Create/read/update Case
2. Persist WorkflowRun
3. Persist Source/Evidence/Claim chain
4. Persist many-to-many ClaimEvidenceLink
5. Persist VerificationResult
6. Persist GovernanceDecision
7. Store/retrieve Brief metadata
8. Case deletion cleans related records
9. Duplicate protection works
10. Transaction rollback preserves consistency

---

# 45. Artifact Store Tests

Minimum tests:

1. Create Case directory
2. Write Brief artifact
3. Read artifact
4. Stable artifact reference
5. Prevent invalid path traversal
6. Delete Case artifacts
7. Missing artifact returns structured error

---

# 46. Resume Tests

Test:

```text
Run stops after EVIDENCE_BUILT
↓
Restart application
↓
Load Case
↓
Resume at Verification
```

Also test recovery after:

- Research completion
- Verification completion
- Governance completion

---

# 47. Migration Readiness Test

Core component tests should use repository interfaces rather than assuming SQLite.

This proves the application can later swap storage implementations.

---

# 48. V1 Persistence Invariants

S1. Every persistent record belongs to the correct Case or shared entity.

S2. Evidence always references a valid Source.

S3. Claim/evidence relationships remain intact.

S4. Governance and Verification history is not silently lost.

S5. A checkpoint is written only after required stage data persists successfully.

S6. Reruns create new WorkflowRun records.

S7. New Briefs do not silently overwrite old versions.

S8. Core business logic does not issue raw SQLite queries.

S9. Absolute machine-specific paths do not leak into domain logic.

S10. Case deletion removes associated persistent data and artifacts.

S11. Secrets are never stored in domain tables or artifacts.

S12. Stored web content remains untrusted data.

---

# 49. Final V1 Persistence Architecture

```text
                       DOMAIN / WORKFLOW
                              │
              ┌───────────────┴────────────────┐
              │                                │
       Repository Interfaces              ArtifactStore
              │                                │
       SQLite Repositories               LocalArtifactStore
              │                                │
 strategic_intelligence.db             data/cases/<case_id>/
```

Future:

```text
                       DOMAIN / WORKFLOW
                              │
              ┌───────────────┴────────────────┐
              │                                │
       Repository Interfaces              ArtifactStore
              │                                │
        PostgreSQL                       Object Storage
                                         S3 / Blob / GCS
```

---

# 50. Final Principle

V1 persistence should be simple enough for one local user while preserving the boundaries required for a future cloud product.

The storage design priority is:

**Consistency → Traceability → Recovery → Simplicity → Portability → Scale Later**
