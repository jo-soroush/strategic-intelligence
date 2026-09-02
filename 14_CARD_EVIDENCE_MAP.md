# Strategic Intelligence Project — V1 Card Evidence Map

## Purpose

This is the canonical evidence ledger for all 22 V1 Cards.

Evidence is written only from actual repository execution. `TBD` and `PENDING` are intentional before implementation.

A Card may be COMPLETE only when its mandatory requirements, tests/evaluation,
regressions, exact Exit Gate, diff/status review, and canonical Evidence record
all agree.

Card-level `Git Status Review` entries are historical closure evidence captured
at the time of final pre-commit review. They do not replace dynamically
verified live Git state.

## Status Values

NOT_STARTED / IN_PROGRESS / BLOCKED / COMPLETE

## V1-C05+ Evidence Model

For V1-C05 onward, each active Card updates this ledger at meaningful validated
milestones: completed Contract / Risk Map, validated implementation milestone,
Critical-Path execution, defect diagnosis or validated repair, Exit Gate proof,
and approved Git delivery/integration. It is not a chronological command diary.
Every entry remains repository-execution evidence only; record `N/A` where a
required field has no meaningful applicable fact.

At closure, the Card's evidence must concisely contain:

1. **Implementation Evidence** — exact files/components and actual behavior.
2. **Validation Evidence** — exact commands, results, and relevant regressions.
3. **Contract / Risk Map Outcome** — concise inspected outcome, without copying
   the full map.
4. **Critical-Path Evidence** — expected and actual path, owned composition
   boundary, exact command/test, and result.
5. **Architecture Before → After** — the actual ownership/boundary change.
6. **Problem → Diagnosis → Fix** — actual issue/failed assumption, diagnosis,
   and solution; explicit `N/A` if no meaningful issue occurred.
7. **Known Limitations / Deferrals** — remaining facts and future Card owner
   where known.
8. **Professional Engineering Lesson** and **Learner Takeaway** — concise,
   Card-grounded lessons rather than generic theory.
9. **What This Enables Next** — one concise next-capability explanation.
10. **Historical Git Evidence** — Card branch, relevant Card commit(s), and
    completed push/integration status when known. This is historical evidence,
    never live Git authority.
11. **Exact Exit Gate Proof** — requirement-to-actual-proof mapping.

Post-delivery defects and validated repairs belong chronologically in the
canonical record for the Card whose owned boundary exposed them. Record the
cross-Card composition proof where material; do not create a second status
authority or rewrite unrelated historical records.

The existing per-Card requirement table remains the authoritative detailed
requirement map. Do not duplicate architecture documents, copy raw test logs,
or use this section to store live branch, current `main` SHA, upstream, pending
delivery, or worktree state; Git proves those facts dynamically.

# V1-C01 — Repository Baseline

**Status:** COMPLETE
**Dependencies:** None
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Project/config/test foundation | `pyproject.toml`; `src/strategic_intelligence/config.py`; `tests/unit/test_foundation.py` | `.venv/bin/python -m pytest` | PASS — 2 passed | Python 3.11.15 venv; editable package install; safe defaults validated |
| Secrets excluded | `.gitignore`; `.env.example` | `git check-ignore -v` for `.env`, `.venv`, generated data/logs, caches, and artifacts | PASS | `.env.example` intentionally not ignored; no real secret added |
| Harness ownership boundary | `README.md`; `src/strategic_intelligence/` package layout | Package import and documented ownership review | PASS | Reserved boundaries for application, domain, harness, providers, infrastructure, security, governance, observability, and UI |
| Evaluation fixture/evidence convention | `tests/fixtures/`; `evaluations/fixtures/`; `evaluations/artifacts/` | Documentation and ignore-rule review | PASS | Fixtures are versioned; generated artifacts are ignored except `.gitkeep` |

**Baseline Before:** N/A — C01 introduces no model, prompt, provider, routing, trust, or recovery behavior.
**Candidate After:** N/A — foundation-only Card.
**Regression Decision:** N/A — no quality-affecting runtime baseline exists or is required for C01.
**Known Issues / Blockers:** No blocker. Pip reported a disabled user cache due to ownership; installation and validation succeeded.
**Diff Review:** PASS — `git diff --check` passed; new untracked foundation files were inspected.
**Git Status Review:** PASS — repository initialized on `card/v1-c01-repository-baseline`; no commit created.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — reproducible Python 3.11 virtual environment, package/config/test foundation, safe ignore rules, documented Harness ownership, and documented evaluation conventions are present and validated.

### Retrospective Enrichment

This section was reconstructed on 2026-08-26 from the preserved Card record,
commit history, current repository files, and approved authorities. It is not
an assertion that these learning fields were recorded during C01 execution.

**Engineering Goal / Why It Existed:** C01 established the repository,
installable package, non-secret configuration, test layout, ignore rules, and
Harness/documentation placement needed before any bounded runtime Card could be
implemented safely.

**Architecture Before → After:** Before C01, the pre-C01 audit records a
documentation-only directory without a Git repository, application package,
tests, or configuration. Commit `cb0e428` established the project-owned
package boundaries and the configuration/test/evaluation conventions; it did
not add product workflow behavior.

**Implementation / Validation Evidence:** `pyproject.toml`, `.gitignore`,
`.env.example`, `src/strategic_intelligence/config.py`, package boundary
directories, `tests/unit/test_foundation.py`, and fixture/artifact `.gitkeep`
files are introduced by `cb0e428`. The contemporaneous evidence records
`.venv/bin/python -m pytest` passing 2 tests, package/config validation,
`pip check`, ignore-rule review, and `git diff --check`.

**Critical Path / Real Execution Evidence:** Not evidenced as a distinct
Critical-Path run. C01 closed before the later Critical-Path gate; its recorded
foundation checks are not retrospectively relabelled as that gate.

**Problem → Diagnosis → Fix:** No meaningful implementation defect is
evidenced. The only recorded environmental observation was a disabled user pip
cache caused by ownership; installation and validation still succeeded.

**Known Limitations / Deferrals:** C01 intentionally left domain contracts,
persistence, providers, and application workflow to later Cards. Runtime
behavior was not proven by this foundation-only Card.

**Professional Engineering Lesson:** A usable AI system begins with explicit
package, configuration, test, artifact, and ignore boundaries; otherwise later
runtime proof is difficult to reproduce or review.

**Learner Takeaway:** Before building intelligence behavior, make the project
safe to install, test, configure, and inspect. That foundation is an
engineering capability, not administrative overhead.

**What This Enabled Next:** C02 could define application-owned typed contracts
inside an installable, tested package rather than inventing structures ad hoc.

**Historical Git Evidence:** C01 implementation commit `cb0e428` (`chore(c01):
establish repository baseline`) is preserved in Git history. The retained C01
branch later received control reconciliation commit `61de4a9`; these are
historical references, not live Git-state assertions.

**Exact Exit Gate Proof:** The preserved Exit Gate evidence remains PASS: the
repository contains the reproducible foundation, safe ignore policy, documented
Harness ownership, and evaluation conventions validated during C01.


# V1-C02 — Domain Models

**Status:** COMPLETE
**Dependencies:** V1-C01
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Typed domain models | `src/strategic_intelligence/domain/models.py` | `.venv/bin/python -m pytest` | PASS — 11 passed | Pydantic contracts cover Case through WorkflowError, plus typed supporting/state models |
| Enums/IDs/timestamps | `src/strategic_intelligence/domain/models.py` | Construction/invariant tests | PASS | Opaque UUID IDs, timezone-aware timestamps, and explicit domain enums |
| Serialization | `src/strategic_intelligence/domain/models.py`; `tests/unit/test_domain_models.py` | JSON model dump/validate round trips | PASS | Nested research, traceability, analysis/brief, audit, run, context, and workflow-state round trips |
| Provider-independent contracts | `src/strategic_intelligence/domain/` | Source and dependency review | PASS | No provider SDK objects or provider-specific dependencies; Pydantic is the typed validation/serialization dependency |

**Baseline Before:** N/A — C02 introduces no model, prompt, provider, routing, trust, or recovery behavior.
**Candidate After:** N/A — contract-only Card.
**Regression Decision:** N/A — no quality-affecting runtime baseline applies to C02.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — C02 changes are limited to the Pydantic dependency, domain contracts, contract tests, Evidence Map, and Project Control.
**Git Status Review:** PASS — branch `card/v1-c02-domain-models`; C02 changes are uncommitted; `REPAIR_INSTRUCTIONS.md` remains untracked and outside Card scope.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — later Cards can exchange explicit application-owned, provider-independent typed contracts with IDs, timestamps, enums, relationship IDs, deterministic validation, and JSON-compatible serialization.

### Retrospective Enrichment

This section was reconstructed on 2026-08-26 from the preserved Card record,
commit `17bb25c`, current domain code/tests, and approved architecture. It is
not a contemporaneous C02 learning record.

**Engineering Goal / Why It Existed:** C02 established typed,
application-owned data contracts so subsequent storage, providers, research,
verification, governance, and briefs could exchange validated state instead of
free-form or vendor-specific objects.

**Architecture Before → After:** C01 supplied package boundaries but no domain
model layer. C02 added `domain/models.py` and domain exports as the shared
contract boundary, with Pydantic validation/JSON serialization and no provider
SDK objects in the domain layer.

**Implementation / Validation Evidence:** Commit `17bb25c` adds the 447-line
model module and `tests/unit/test_domain_models.py`. The preserved evidence
records `.venv/bin/python -m pytest` passing 11 tests, covering required and
unknown fields, enum/non-negative invariants, evidence requirements, aware
timestamps, nested contracts, and JSON round trips.

**Critical Path / Real Execution Evidence:** Not evidenced as a separately
recorded composed Critical-Path run. The documented construction and JSON
round-trip tests prove contract behavior but are not retroactively claimed as
the later Critical-Path gate.

**Problem → Diagnosis → Fix:** N/A — no meaningful C02 defect, failed
assumption, or repair is recorded in the preserved Evidence or commit history.

**Known Limitations / Deferrals:** The contracts define data, not persistence,
provider execution, research, verification, governance, or UI behavior. Those
owners remain with C03 and later Cards.

**Professional Engineering Lesson:** Shared contracts should be owned by the
application and validated at boundaries before adapters or workflows depend on
them; this prevents vendor coupling from becoming a domain concern.

**Learner Takeaway:** Typed models make important system state explicit. IDs,
enums, validation, and serialization let independent components communicate
without guessing at strings or provider response shapes.

**What This Enabled Next:** C03 could persist Case, Source, Evidence, Claim,
and WorkflowRun values using stable application-owned schemas.

**Historical Git Evidence:** C02 implementation commit `17bb25c`
(`feat(c02): add typed domain models`) is preserved on the retained C02 branch
and in the linear project history. This is historical traceability only.

**Exact Exit Gate Proof:** The existing PASS proof is preserved: later Cards
have provider-independent typed data with deterministic validation and
JSON-compatible serialization.


# V1-C03 — Persistence Foundation

**Status:** COMPLETE
**Dependencies:** V1-C02
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Repository/SQLite/ArtifactStore | `application/persistence.py`; `infrastructure/sqlite_repository.py`; `infrastructure/artifacts.py` | `tests/unit/test_persistence.py` | PASS — 7 passed | Application protocols isolate SQLite/files; SQLite schema migration table and LocalArtifactStore are local-first adapters |
| Transactions | `SqliteRepository.save_claim_with_links` | rollback test | PASS | Claim and exact ClaimEvidenceLinks execute in one SQLite transaction; missing referenced Evidence rolls back the Claim |
| Safe paths | `LocalArtifactStore` | artifact path/read/delete tests | PASS | Configured root containment, generated IDs, traversal rejection, structured missing-artifact failure, and case deletion |
| Validated checkpoint persistence/acceptance | `SqliteRepository.accept_checkpoint` | checkpoint acceptance/rejection test | PASS | Accepted checkpoint row is written only after required persisted records are verified; rejected input leaves no accepted checkpoint |

**Baseline Before:** N/A — C03 establishes storage infrastructure, not an AI/research/trust-quality baseline.
**Candidate After:** N/A — deterministic local persistence foundation.
**Regression Decision:** PASS — full suite remains green (18 passed).
**Known Issues / Blockers:** None.
**Diff Review:** PASS — scope is application persistence interfaces, SQLite/local artifact adapters, safe configuration properties, C03 tests, and control evidence only.
**Git Status Review:** PASS — branch `card/v1-c03-persistence-foundation`; C03 work is uncommitted; `REPAIR_INSTRUCTIONS.md` remains untracked and outside Card scope.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — Case and WorkflowRun survive repository reopen; Source/Evidence/Claim traceability persists; Claim+links are atomic; artifact storage is path-safe; accepted checkpoints require persisted records.

### Retrospective Enrichment

This section was reconstructed on 2026-08-26 from the preserved Card record,
commit `734aa45`, current persistence code/tests, and approved storage
architecture. It is not a contemporaneous C03 learning record.

**Engineering Goal / Why It Existed:** C03 created the local persistence
foundation needed for durable Cases/runs, traceability records, artifacts, and
accepted checkpoints before later workflow stages can safely resume or audit
their work.

**Architecture Before → After:** C02 supplied serializable domain values but
no storage adapter. C03 added application persistence protocols, a SQLite
repository behind that boundary, and a local artifact store; domain models do
not issue SQLite queries or own filesystem paths.

**Implementation / Validation Evidence:** Commit `734aa45` adds
`application/persistence.py`, `infrastructure/sqlite_repository.py`,
`infrastructure/artifacts.py`, configuration support, and
`tests/unit/test_persistence.py`. The preserved evidence records 7 focused
persistence tests, 18 full-suite tests, transaction rollback, artifact
read/write/delete/traversal checks, checkpoint rejection, `pip check`,
compile/import, and diff/status review.

**Critical Path / Real Execution Evidence:** Not evidenced as a separately
recorded Critical-Path execution. The reopen, atomic-link, artifact, and
checkpoint tests demonstrate persistence invariants, but this enrichment does
not relabel them as a later gate.

**Problem → Diagnosis → Fix:** N/A — no meaningful C03 defect or repair is
recorded. The checkpoint-rejection and rollback cases are intentional safety
tests, not evidence of a production failure.

**Post-Delivery Repair Chronology:** The final C01–C15 composition audit found
F001 (IMPORTANT): `append_claim_evidence` could accept a direct Case-B Evidence
attachment to a Case-A Claim. C11 and C15 already rejected the resulting
provenance mismatch at consumption, but the C03 persistence boundary lacked
the invariant. The repair rejects mismatched Claim/Evidence Case IDs before
the transaction. A direct cross-Case append now fails, leaves valid existing
links unchanged, and remains absent after repository reopen; same-Case append
and the C12 follow-up path continue to pass.

**Known Limitations / Deferrals:** C03 establishes accepted-checkpoint storage,
not the later workflow recovery/resume behavior owned by C18. It also does not
implement research, verification, governance, or cloud database behavior.

**Professional Engineering Lesson:** Persistence is a boundary, not a side
effect. Transactional linkage, path containment, and explicit checkpoint
acceptance make durable state trustworthy enough for later recovery.

**Learner Takeaway:** Saving data is not the same as creating a safe resume
point. A checkpoint becomes usable only after the required data exists and its
invariants have passed.

**What This Enabled Next:** C05 and later Cards can persist validated Cases and
traceability records; C18 can later build recovery on accepted checkpoint
evidence rather than partial execution state.

**Historical Git Evidence:** C03 implementation commit `734aa45`
(`feat(c03): add persistence foundation`) is preserved on the retained C03
branch and in linear project history. This is historical traceability only.

**Exact Exit Gate Proof:** The existing PASS proof is preserved: Case and
WorkflowRun reopen successfully; traceability persists; Claim/evidence links
are atomic; artifacts remain contained; and checkpoints require persisted
records.


# V1-C04 — Provider Foundation

**Status:** COMPLETE
**Dependencies:** V1-C01, V1-C02
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| LLM/Search provider contracts | `providers/contracts.py` | `tests/unit/test_providers.py` | PASS — 9 passed | Application-owned request/response/result contracts and protocols contain no vendor objects |
| Adapters/factory/fakes | `providers/ollama.py`; `providers/search.py`; `providers/factory.py`; `providers/fakes.py` | factory/fake/default-composition tests | PASS | Ollama and DuckDuckGo details remain isolated; construction is explicit; deterministic fakes require no live service |
| Narrow capability injection | `providers/contracts.py`; `providers/factory.py` | protocol/factory review | PASS | Consumers receive only LLMProvider/SearchProvider protocols through composition |
| Timeout/error normalization | `providers/ollama.py`; `providers/search.py` | timeout/unavailable tests | PASS | External failure becomes a secret-safe ProviderError with normalized code and retryability; workflow retry remains future orchestrator ownership |
| No silent cloud fallback | `config.py`; `providers/factory.py` | cloud/unknown-provider tests | PASS | Default is explicit local Ollama; unapproved cloud/unknown selections fail rather than falling back |

**Baseline Before:** N/A — C04 establishes deterministic provider boundaries, not a quality/routing change.
**Candidate After:** N/A — no live provider evaluation is required; fakes cover contracts deterministically.
**Regression Decision:** PASS — full suite remains green (27 passed).
**Known Issues / Blockers:** Resolved — an independent audit reproduced `build_providers(Settings.from_environment())` failing with `AttributeError` because the factory expected `Settings.ollama_base_url` while centralized Settings did not provide it.
**Repair Evidence:** Added documented `OLLAMA_BASE_URL` parsing with local default `http://127.0.0.1:11434` and basic HTTP(S) base-URL validation, plus deterministic default-composition and invalid-scheme tests. Construction does not call the provider network.
**Critical Path:** `Settings.from_environment()` → `build_providers(...)` → default local provider → `OllamaAdapter` construction. `test_default_settings_construct_local_ollama_provider_without_network` passes without mocking the Settings/factory/adapter boundary or making a provider network call.
**Diff Review:** PASS — repair is limited to centralized provider configuration, `.env.example`, C04 tests, and control/evidence records; no future workflow behavior.
**Git Status Review:** Historical closure evidence: repair branch `card/v1-c04-provider-foundation-repair` contains the validated, uncommitted C04 repair; `REPAIR_INSTRUCTIONS.md` remains outside Card scope.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — provider consumers can depend on stable application protocols while vendor HTTP details remain isolated and cloud use cannot occur silently. `.venv/bin/python -m pytest tests/unit/test_providers.py` passed 9 tests; full suite passed 27 tests; `pip check`, compile/import checks, and `build_providers(Settings.from_environment())` passed.

### Retrospective Enrichment

This section was reconstructed on 2026-08-26 from the preserved C04 Evidence,
commits `8da3f52` and `cb882e2`, current provider code/tests, PROJECT_CONTROL,
and Git history. It preserves the original implementation and the later repair
as distinct phases.

**Engineering Goal / Why It Existed:** C04 established application-owned LLM
and search capability boundaries so later components can use local providers
without vendor objects, credentials, or silent cloud fallback entering domain
or application contracts.

**Architecture Before → After:** Before C04, C01–C03 had package, domain, and
persistence foundations but no provider implementation. Original commit
`8da3f52` introduced provider contracts, factory composition, Ollama and
DuckDuckGo adapters, deterministic fakes, normalized errors, and explicit
local-first selection. Repair commit `cb882e2` completed the centralized
configuration path needed by the factory.

**Implementation / Validation Evidence:** Original C04 files are
`providers/contracts.py`, `factory.py`, `fakes.py`, `ollama.py`, `search.py`,
configuration, `.env.example`, and `tests/unit/test_providers.py`. The repair
added `Settings.ollama_base_url`, HTTP(S) base-URL validation, documented
`OLLAMA_BASE_URL`, and two deterministic regression tests. The preserved C04
record documents 9 focused provider tests, 27 full-suite tests, `pip check`,
compile/import checks, and no-network default factory construction after repair.

**Critical Path / Real Execution Evidence:** This is later repair validation,
not a claim about the original C04 closure. The independently exercised path is
`Settings.from_environment()` → `build_providers(...)` → default local provider
→ `OllamaAdapter` construction. Test
`test_default_settings_construct_local_ollama_provider_without_network` proves
that composition boundary without mocking Settings/factory/adapter or contacting
the provider network.

**Problem → Diagnosis → Fix:** The original factory accessed
`settings.ollama_base_url`, but original `Settings` did not define it. An
independent audit reproduced `AttributeError` for the real default composition
path, showing that passing provider unit tests had not proven that path. Repair
commit `cb882e2` centralized the missing setting and URL validation, then added
the default-composition and invalid-scheme regressions. The preserved Evidence
and PROJECT_CONTROL record the repaired validation result.

**Known Limitations / Deferrals:** C04 owns the provider boundary, not provider
orchestration, retries, research behavior, verification, governance, UI, or
concrete cloud adapters. Live provider quality evaluation is not evidenced by
this deterministic construction-focused repair.

**Professional Engineering Lesson:** Unit tests can validate isolated adapters
while still missing the real composition path. Exercise default configuration
through the factory before declaring an integration boundary complete.

**Learner Takeaway:** A provider boundary is more than an interface. It also
includes the configuration and factory path that creates the provider safely;
test that composed path without requiring a live network call.

**What This Enabled Next:** C05+ components can receive provider capabilities
through application-owned contracts, with deterministic fakes and explicit
local-first construction available at the composition boundary.

**Historical Git Evidence:** Original provider implementation commit `8da3f52`
(`feat(c04): add provider foundation`) remains on the preserved C04 branch.
Repair commit `cb882e2` (`fix(c04): repair provider composition and closure
validation`) remains on the preserved repair branch; subsequent project history
records its approved integration. These are historical references, not live Git
state assertions.

**Exact Exit Gate Proof:** The existing PASS proof is preserved and clarified:
provider consumers use stable application protocols; vendor HTTP details stay
in adapters; unapproved cloud/unknown selection fails; and the later real
default-composition regression closes the configuration/factory evidence gap.


# V1-C05 — Case Input and Validation

**Status:** COMPLETE
**Dependencies:** V1-C02, V1-C03
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Case validation/persistence | `domain/models.py` (`Case`); `application/case_input.py` (`CaseIntakeService`); C03 `PersistenceRepository` | `tests/unit/test_case_input.py`; full suite | PASS | Valid typed input creates one Case only after confirmation and retrieves it from real SQLite persistence |
| URL safety | `application/case_input.py` (`_normalize_public_url`) | Invalid URL tests | PASS | Only absolute credential-free HTTP(S) URLs pass; whitespace, `file:`, localhost, and non-global IP literals are rejected before persistence |
| Company identity | `application/case_input.py` (`CompanyIdentityCandidate`, `_resolve`) | Conflicting URL and business-unit ambiguity tests | PASS | A company must have a unique candidate or a supplied public URL / country-plus-business-unit anchor; conflicts reject |
| Executive identity | `application/case_input.py` (`ExecutiveIdentityCandidate`, `_resolve`) | Same-name and moved-executive tests | PASS | An executive must have a unique candidate or professional URL/current-title anchor; multiple candidates reject |
| Executive↔Company relation | `application/case_input.py` (`_resolve`) | Moved-executive test | PASS | A matched executive associated with another company produces a structured conflict and no Case |
| Ambiguity handling | `application/case_input.py` (`EntityResolution`, `CaseIntakeResult`) | Insufficient-anchor and same-name/company ambiguity tests | PASS | Unresolved, conflicting, or ambiguous identity returns a structured rejection before Case persistence |

### C05 Start / Contract-Risk Map

**Engineering Goal / Why It Exists:** Create one validated root Case and
confirm the intended company, executive, and relation before any later Card can
conduct unrestricted research.

**Learning Goal:** Practice placing deterministic validation, normalization,
identity ambiguity, and safe persistence behind an application-owned typed
boundary rather than allowing downstream research to infer identity.

**Implementation Scope / Out of Scope:** C05 owns required company, executive,
and meeting-goal input; optional URLs/context; safe URL handling; deterministic
entity resolution; and root-Case persistence. It does not own network lookup,
provider use, research planning/execution, Case-update policy, verification,
governance, UI, or orchestration.

**Dependencies / Evaluation / Exit Gate:** C02 supplies typed domain contracts;
C03 supplies the Case repository. Required valid/missing, invalid-URL,
persistence, same-name executive, moved-executive, conflicting-URL, and
ambiguous-company/business-unit cases are executed below. The Exit Gate is
that invalid or unresolved/unsafe Cases cannot enter unrestricted research.

**Inspected Before State:** C02 provides typed `Case`, `Company`, and
`Executive` contracts; C03 can persist a Case through the application-owned
repository. Neither provides a Case-submission boundary or deterministic entity
resolution.

**Owned Boundary and Design Decision:**
`application/case_input.py` owns strict intake validation, URL normalization,
and deterministic resolution. It composes the completed C02 domain contracts
with the completed C03 `PersistenceRepository`; it performs no network lookup,
provider call, research, workflow orchestration, verification, governance, or
UI work. Unresolved or conflicting identity data yields a non-persisted,
structured rejection.

**C05 Critical Path:** typed raw submission → application validation and URL
normalization → company/executive/relation confirmation → C02 Case creation →
real C03 SQLite `create_case` persistence. Invalid or ambiguous input stops
before Case persistence and therefore before later research.

**Validated Implementation Milestone:**
`tests/unit/test_case_input.py` executes the critical path against a real
`SqliteRepository`: accepted input is normalized, confirmed, and retrieved from
persisted storage. The same test module also proves required-field, unsafe URL,
same-name executive, moved-executive, conflicting-company URL,
business-unit ambiguity, and insufficient-anchor rejections. Result: PASS — 6
passed.

### Closure Evidence

**Implementation Evidence:** Added required human-readable company and executive
names to the C02 `Case` contract and added the application-owned
`CaseIntakeService` with strict submission, candidate, resolution, error, and
result contracts. It creates a Case only after deterministic validation and
identity confirmation, then uses the completed C03 repository boundary for
persistence.

**Validation Evidence:** `.venv/bin/python -m pytest tests/unit/test_case_input.py`
passed 6 tests. `.venv/bin/python -m pytest` passed 33 tests. `.venv/bin/python
-m pip check`, `.venv/bin/python -m compileall -q src`, and the Case-input
package import check passed. `git diff --check` passed.

**Contract / Risk Map Outcome:** The implemented critical path matches the
inspected ownership: strict raw submission → deterministic application gate →
C02 contracts → real C03 SQLite persistence. Candidate lookup is deliberately
input-only and deterministic; C05 adds no network lookup or future workflow.

**Critical-Path Evidence:**
`test_critical_path_validates_normalizes_resolves_and_persists_with_real_repository`
uses the real `SqliteRepository`, validates and normalizes a submission,
confirms identity, persists a Case, and reads the identical Case back. Result:
PASS.

**Architecture Before → After:** Before C05, typed records and Case storage
existed independently. After C05, the application layer owns their controlled
composition at a validated intake boundary; domain code remains independent of
SQLite and no provider, research, governance, UI, or orchestration code was
introduced.

**Problem → Diagnosis → Fix:** N/A — no meaningful implementation defect was
observed during C05 validation. The design explicitly avoids treating missing
identity anchors as sufficient evidence.

**Known Limitations / Deferrals:** C05 does not fetch, research, update Cases,
or persist separate company/executive records; the existing C03 Case update
operation remains its storage concern. Research planning, external source
handling, verification, governance, and UI remain owned by later Cards.

**Professional Engineering Lesson:** An intake boundary is a trust boundary:
validation and deterministic identity resolution must occur before a durable
checkpoint can unlock more capable downstream work.

**Learner Takeaway:** Represent rejection as typed data, not an exception-only
side effect. That makes ambiguity visible, testable, and impossible for a
future workflow to ignore accidentally.

**What This Enables Next:** C06 can receive a bounded, persisted Case only
after C05 has made its target identity explicit and safe.

**Historical Git Evidence:** At the final pre-delivery diff/status review, only
C05 tracked work plus recognized untracked artifacts outside Card scope were
present. No C05 commit, push, or integration had then been authorized or
performed. After approval, commit `46e857a` (`feat(c05): add validated case
intake`) was pushed on the preserved C05 Card branch and fast-forward integrated
into `main` without a merge commit or history rewrite. These are historical
delivery facts; Git remains the live authority for reference equality.

**Baseline Before:** N/A — this deterministic validation/persistence Card does
not alter an AI, routing, trust-quality, or recovery baseline.
**Candidate After:** N/A — no AI-quality candidate was introduced.
**Regression Decision:** PASS — all prior regression tests remain green.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — C05 changes are limited to typed Case intake, its
domain/test adjustments, and required Evidence/Project Control state.
**Git Status Review:** PASS — no secret, `.env`, cache, generated artifact, or
future-Card implementation is in the C05 tracked set; recognized untracked
artifacts remain untouched and outside scope.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — malformed/unsafe submissions fail validation;
unresolved, ambiguous, and conflicting identities return structured rejections;
only confirmed input reaches Case persistence. Therefore no invalid or
unresolved/unsafe Case can enter the later unrestricted-research path.


# V1-C06 — Research Planner

**Status:** COMPLETE
**Dependencies:** V1-C04, V1-C05
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Bounded ResearchPlan | `domain/models.py` (`ResearchPlan`, `ResearchTask`); `application/research_planning.py` (`ResearchPlanner`) | Critical-path test; full suite | PASS | Plan has a maximum 13 task budget and a maximum per-task attempt budget; tasks are unique, ordered, typed, and pending |
| Company/executive separation | `application/research_planning.py` task templates | Critical-path test | PASS | Separate company and executive templates create only their matching typed targets/categories |
| Coverage statuses | `domain/models.py` (`ResearchCoverage`, `ResearchCoverageStatus`) | Coverage and incomplete-plan tests | PASS | Typed statuses preserve covered, partial, missing, unavailable, and not-relevant state with explainable incomplete coverage |
| High-priority gap behavior | `application/research_planning.py` (`plan`, `is_completion_ready`) | Coverage-aware planning test | PASS | Covered work is skipped; partial high-priority work remains planned; completion requires all required categories to be covered or not relevant |
| Privacy boundary | `application/research_planning.py` (`_guidance`, `_validate_coverage`) | Fake LLM private-category test | PASS | Optional provider guidance can only emphasize approved public-professional categories; unknown/private categories reject before plan creation |

### C06 Start / Contract-Risk Map

**Engineering Goal / Why It Exists:** Convert a C05-validated Case into a
meeting-focused, bounded ResearchPlan so later research follows explicit work
rather than uncontrolled discovery.

**Learning Goal:** Practice separating a business objective into typed,
prioritized machine-executable research work while keeping coverage gaps and
boundedness visible.

**Inspected Before State:** C02 supplies `ResearchPlan` and `ResearchTask`
contracts, C04 supplies an optional normalized LLM provider boundary, and C05
supplies a confirmed root Case. No application planner, task budget, or
coverage-aware planning behavior exists.

**Owned Boundary and Design Decision:** The C06 application planner owns task
selection, ordering, per-task attempt budgets, and coverage-aware gap
selection. Deterministic templates establish the safe baseline; any optional
C04 structured-LLM guidance is validated and cannot create categories, exceed
budgets, invoke search, or override the privacy boundary.

**Contract / Risk Map:** Producer: a validated C05 Case. Inputs: company,
executive, meeting goal, optional context, and prior typed coverage. Invariants:
typed allowed categories, company/executive separation, unique ordered tasks,
bounded task/attempt counts, and no private-personal research. Failures:
malformed guidance or invalid coverage returns a structured rejection; an
unresolved high-priority coverage status remains an explicit task rather than a
completion claim. Consumers: C07/C08 research only. Deferred: web/search
execution, source/evidence collection, verification, orchestration,
checkpoint persistence, and UI.

**C06 Critical-Path Expectation:** C05 Case → real C06 planner → typed
ResearchPlan with bounded, separated pending ResearchTasks → deterministic plan
validation. The critical path uses real C05 intake and local C03 SQLite; a fake
C04 LLM is used only for the provider-guidance validation test, never to mock
the planner itself.

### Closure Evidence

**Implementation Evidence:** Extended the application-owned domain contracts
with typed `ResearchCoverageStatus`, `ResearchCoverage`,
`ResearchCoverageRequirement`, plan task/attempt budgets, and plan consistency
invariants. Added `ResearchPlanner`, which turns a C05 Case into ordered
company/executive tasks and validates optional C04 structured-LLM guidance.
The planner never invokes search or fetches external content.

**Validation Evidence:** `.venv/bin/python -m pytest
tests/unit/test_research_planning.py` passed 6 tests. `.venv/bin/python -m
pytest` passed 39 tests. `.venv/bin/python -m pip check`, `.venv/bin/python
-m compileall -q src`, the research-planning import check, and `git diff
--check` passed.

**Contract / Risk Map Outcome:** The implemented boundary matches the inspected
flow: C05 validated Case → application planner → C02 typed plan/task/coverage
contracts. It uses deterministic templates as the default and treats an
optional C04 provider only as bounded category emphasis. No planning result can
become research execution, evidence, a claim, or a workflow checkpoint.

**Critical-Path Evidence:**
`test_critical_path_builds_a_bounded_separated_typed_plan` composes real C05
Case intake and local C03 SQLite persistence with the real C06
`ResearchPlanner`. It proves 13 ordered bounded pending tasks,
company/executive separation, explicit required coverage, meeting-goal queries,
and no remote dependency. Result: PASS.

**Architecture Before → After:** Before C06, C02 held passive plan/task
records, but nothing constructed or assessed them. After C06, the application
layer owns deterministic, coverage-aware planning while the domain remains
provider-independent and C07/C08 still own research execution.

**Problem → Diagnosis → Fix:** The first provider-guidance implementation let a
malformed fake structured response raise Pydantic validation directly. The
diagnosis was an unnormalized provider-boundary failure. C06 now converts both
normalized provider failures and structured-validation failures into a typed
`INVALID_GUIDANCE` rejection; the focused regression test passes.

**Known Limitations / Deferrals:** C06 does not persist plans or accept a
`RESEARCH_PLANNED` checkpoint, execute searches, record sources/coverage
results, or implement workflow orchestration. C07/C08 own research execution;
later persistence/workflow Cards own durable plan/checkpoint coordination.

**Professional Engineering Lesson:** A research planner is a control surface,
not a search loop. Its value is making work explicit, prioritized, bounded, and
reviewable before any external capability is granted.

**Learner Takeaway:** A meeting goal becomes machine-executable research by
mapping it to typed questions with target, category, priority, and attempt
limits—then using coverage outcomes, not a count of links, to decide what is
still needed.

**What This Enables Next:** C07 and C08 can consume explicit, bounded,
separated tasks rather than inventing their own search scope.

**Historical Git Evidence:** At the final pre-delivery diff/status review, only
C06 tracked work plus recognized untracked artifacts outside Card scope were
present. No C06 commit, push, or integration had then been authorized or
performed. After approval, commit `d784694` (`feat(c06): add bounded research
planner`) was pushed on the preserved C06 Card branch and fast-forward
integrated into `main` without a merge commit or history rewrite. These are
historical delivery facts; Git remains the live authority for reference equality.

**Baseline Before:** N/A — C06 adds deterministic planning behavior, not an
AI-quality/routing/recovery baseline candidate.
**Candidate After:** N/A — optional fake-provider guidance is contract-tested,
not evaluated for model quality.
**Regression Decision:** PASS — C01–C05 regression tests remain green.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — changes are limited to C06 domain planning contracts,
the application planner, focused tests, and required Evidence/Project Control.
**Git Status Review:** PASS — no secret, `.env`, cache, generated artifact, or
C07+ implementation is in the C06 tracked set; recognized untracked artifacts
remain untouched and outside scope.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — planning produces typed bounded tasks with
explicit coverage requirements, skips covered work, retains unresolved
high-priority gaps, and reports completion only when coverage—not result
count—proves every required category is covered or not relevant.

# V1-C07 — Company Research

**Status:** COMPLETE
**Dependencies:** V1-C04, V1-C06
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Company intelligence | `application/company_research.py` (`CompanyResearchService`) | Focused tests; composed critical path | PASS | Only matching pending C06 COMPANY tasks produce typed `RawFinding` discovery output |
| Project/case discovery | `application/company_research.py` (`research`) | Composed critical-path test | PASS | A C06 `PROJECTS` task produces source-linked project discovery output with the original task ID and category |
| Source references | `application/company_research.py` (`_to_finding`) | Critical path; deterministic-output test | PASS | Each retained raw finding preserves a validated HTTP(S) source URL, title, snippet, topic, and discovery relevance; C09 still owns Source/Evidence records |
| Relevance | `application/company_research.py` (`_is_relevant`) | Empty/duplicate/blocked/irrelevant-result test | PASS | Deterministic company, goal, or category term matching rejects unrelated discovery results before retention |
| Blocked/unavailable handling | `application/company_research.py` (`research`, `_provider_failure`) | Blocked, malformed, timeout, and empty-result tests | PASS | Blocked, malformed, timeout, duplicate, and empty outcomes remain typed gaps or rejections; there is no retry or fallback |

### C07 Start / Contract-Risk Map

**Engineering Goal / Why It Exists:** Execute the C06 company portion of a
bounded ResearchPlan and turn normalized discovery results into traceable,
meeting-relevant raw company findings without treating discovery as verified
evidence.

**Learning Goal:** Separate planning research from executing source discovery,
and separate discovery signals from the later evidence, claim, and verification
decisions that make information trustworthy.

**Inspected Before State:** C02 provides typed `ResearchTask` and
`RawFinding` contracts. C04 provides the vendor-independent `SearchProvider`,
normalized `SearchResult`, typed provider failures, a deterministic fake, and
an optional DuckDuckGo adapter. C06 produces bounded pending company and
executive tasks but never performs search. There is no C07 application service.

**Owned Boundary and Design Decision:** C07 will consume only a pending,
case-matching C06 COMPANY task from the existing approved company categories;
it will call the C04 search contract once within the task's explicit attempt
budget and retain validated, meeting-relevant discovery results as
`RawFinding`. C07 does not fetch pages, persist records, construct C09
`Source`/`Evidence` objects, produce claims, assess truth, update coverage, or
orchestrate workflow recovery.

**Contract / Risk Map:** Producer: a C05-validated Case and a C06 pending
company `ResearchTask`. Provider boundary: C04 `SearchProvider`; its vendor
objects remain outside application/domain contracts. External search snippets
are untrusted discovery data. Invariants: case/task identity and COMPANY target
must match; task budget allows at most one explicit call in the current C06
plan; retained results have HTTP(S) provenance, nonblank title/snippet, unique
URLs, and deterministic meeting-goal relevance. Failure paths: unsupported
task, provider timeout/unavailability, malformed result, blocked access, and
empty result return typed outcomes/gaps without retry or fallback. Persistence
and accepted checkpoints are deferred because C03 has no RawFinding repository
operation and C09 owns source/evidence normalization. Consumers: C09 Evidence
Layer and later workflow orchestration. C08 executive research, page retrieval,
verification, claims, analysis, governance, UI, and cloud behavior are
explicitly deferred.

**C07 Critical-Path Expectation:** validated C05 Case → real C06
`ResearchPlanner` → selected pending COMPANY task → real C07 company-research
service → C04 deterministic `FakeSearchProvider` as the necessary external
adapter double → validated, deduplicated, relevant `RawFinding` output. This
does not claim live internet behavior; the C07 Exit Gate does not require an
unreliable external smoke test.

### Closure Evidence

**Implementation Evidence:** Added the application-owned
`CompanyResearchService` and typed result/error contracts. The service accepts
only a pending, case-matching COMPANY task from the approved C06 company
categories, calls the normalized C04 `SearchProvider` once, caps retained
results, validates public HTTP(S) provenance, filters relevance, removes
duplicate URLs, and constructs `RawFinding` records. It deliberately imports
neither `Evidence` nor Claim/verification/governance components and makes no
persistence write.

**Validation / Regression Evidence:** `.venv/bin/python -m pytest
tests/unit/test_company_research.py` passed 5 tests. `.venv/bin/python -m
pytest` passed 44 tests. `.venv/bin/python -m pip check`, `.venv/bin/python
-m compileall -q src`, the company-research import check, and `git diff
--check` passed.

**Contract / Risk Map Outcome:** The actual path is C05 Case → C06 plan → C07
company task service → C04 provider contract → raw discovery findings or a
typed gap. It retains only company-task discovery data and preserves the
untrusted-boundary distinction: a search snippet is neither C09 Evidence nor a
FACT. C03 persistence/checkpoint ownership, C08 executive research, page
access, coverage-state updates, C09 Source/Evidence/Claims, verification,
analysis, governance, orchestration, UI, and cloud behavior remain deferred.

**Critical-Path Evidence:**
`test_critical_path_executes_a_real_company_service_from_c05_and_c06` composes
the real C05 `CaseIntakeService` with local C03 SQLite, the real C06
`ResearchPlanner`, a selected C06 `PROJECTS` task, and the real C07
`CompanyResearchService`. `FakeSearchProvider` replaces only the external C04
search adapter so the primary C07-owned composition boundary is not mocked
away. It proves one bounded query, structured project finding, task linkage,
source URL preservation, topic, and discovery-only relevance. Result: PASS.

**Live External Smoke Test:** NOT_REQUIRED — C07's exact Exit Gate requires
reliable traceable company findings, not public-network availability. The
actual DuckDuckGo adapter remains an optional C04 external boundary; no live
network request was made, and the deterministic fake is not presented as live
internet proof.

**Architecture Before → After:** Before C07, a C06 plan could name bounded
company work but nothing consumed it through search. After C07, the application
layer has a narrow company-discovery boundary that turns normalized results into
raw, source-linked findings while Evidence Layer ownership remains untouched.

**Problem → Diagnosis → Fix:** Initial malformed individual provider entries
would be discarded without a typed error. Diagnosis: the failure was safe but
not explicit enough for a provider-boundary contract. The service now records
`INVALID_PROVIDER_RESULT` and returns `REJECTED` when no validated result can
be retained; the focused test passes.

**Known Limitations / Deferrals:** C07 does not retrieve pages, bypass blocked
content, persist findings, mark plan coverage complete, create `Source` or
`Evidence` records, create claims, assess truth, or run executive research.
Search result snippets remain untrusted discovery signals. C08 owns executive
research; C09 owns source/evidence/claim normalization; later Cards own
coverage progression, verification, workflow, and presentation.

**Professional Engineering Lesson:** Planning a search is not research
execution, and a returned snippet is not verified intelligence. A narrow
research component makes those transitions explicit, bounded, and observable
instead of allowing a provider response to silently acquire more authority.

**Learner Takeaway:** A typed plan tells the system what question is allowed;
company research runs that question once and preserves raw provenance; only
later source access, evidence extraction, and verification can support a fact.

**What This Enables Next:** C08 can implement the separate public-professional
executive path using the same bounded provider discipline, while C09 can later
normalize C07 raw findings into traceable Sources and Evidence.

**Historical Git Evidence:** After closure approval, commit `4c6dcd4`
(`feat(c07): add bounded company research`) was pushed on preserved branch
`card/v1-c07-company-research` and fast-forward integrated into `main` without
a merge commit or history rewrite. These are historical delivery facts; Git
remains the live authority for branch, reference equality, and worktree state.

**Baseline Before:** N/A — C07 establishes deterministic, provider-independent
discovery behavior rather than an AI-quality, routing, or recovery baseline.
**Candidate After:** N/A — no model, prompt, or live-provider quality claim was
introduced.
**Regression Decision:** PASS — C01–C06 regression tests remain green in the
44-test full suite.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — C07 changes are limited to its application research
service, focused tests, and required Evidence/Project Control updates.
**Git Status Review:** PASS — no secret, `.env`, cache, generated artifact,
machine-specific path, or C08+ implementation is in the C07 tracked set;
`REPAIR_INSTRUCTIONS.md` and `eference/` remain recognized untouched untracked
artifacts outside scope.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — the composed path proves that an approved C06
company task reliably produces a bounded, traceable, meeting-relevant raw
finding with preserved source provenance; empty, duplicate, blocked,
irrelevant, malformed, and unavailable outcomes remain explicit rather than
being promoted to verified Evidence.


# V1-C08 — Executive Research

**Status:** COMPLETE
**Dependencies:** V1-C04, V1-C06
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Professional executive intelligence | `application/executive_research.py` (`ExecutiveResearchService`) | Focused tests; composed critical path | PASS | Only matching pending C06 EXECUTIVE tasks produce typed RawFinding discovery output |
| Identity handling | `application/executive_research.py` (`_to_finding`) | Privacy/identity test; critical path | PASS | All normalized executive-name terms must match before a result is retained; similarly named people are explicitly rejected |
| Public/professional boundary | `application/executive_research.py` (`_contains_excluded_personal_data`, `_is_professionally_relevant`) | Privacy/data-minimization test | PASS | Family/private and sensitive-characteristic material, unrelated personal activity, and ambiguous relevance are rejected before retention |
| LinkedIn optionality | C05 → C06 → C08 critical path | Critical-path test | PASS | A validated current-title identity with no LinkedIn URL reaches C08; C08 performs no LinkedIn-specific fetch or scrape |
| Fact/inference separation | `application/executive_research.py` (`ExecutiveResearchResult`) | Deterministic raw-finding test | PASS | Discovery remains raw source-linked data; the result exposes neither Evidence nor Claim construction |

### C08 Start / Contract-Risk Map

**Engineering Goal / Why It Exists:** Execute the C06 executive portion of a
bounded ResearchPlan to discover useful public professional information for
meeting preparation, while refusing private, sensitive, irrelevant, or
identity-ambiguous material.

**Learning Goal:** Practice data minimization as executable behavior: public
information gains no automatic right to be collected merely because a search
provider exposes it.

**Inspected Before State:** C05 produces a confirmed Case with an executive
identity boundary; C06 creates bounded pending EXECUTIVE tasks; C04 supplies
the vendor-independent normalized search contract; C07 demonstrates bounded
company discovery and raw-finding provenance. No C08 executive-research
application service exists.

**Owned Boundary and Design Decision:** C08 will consume only a pending,
case-matching EXECUTIVE task from the approved executive categories. It will
make one bounded C04 search call, retain only results that identify the named
executive and are professionally relevant to the task/meeting goal, and reject
the excluded personal-data categories explicitly named by the Security and
Privacy policy. It will preserve validated provenance in `RawFinding` but will
not fetch pages, scrape LinkedIn, persist records, create C09 Source/Evidence
objects or claims, infer attributes, update coverage, or orchestrate workflow.

**Contract / Risk Map:** Producer: a C05-validated Case and C06 pending
EXECUTIVE `ResearchTask`. Identity invariant: all normalized executive-name
terms must appear in retained discovery text; a similarly named or unrelated
person is rejected. Privacy invariant: home/address, family/private
relationships, routines, sensitive characteristics, and unrelated personal
activity are excluded even if public. Trust boundary: provider results/snippets
are untrusted discovery data, never facts or Evidence. Failure paths:
unsupported/mismatched task, provider timeout/unavailability, malformed or
unsafe result, identity mismatch, privacy rejection, duplicate, and empty
result produce typed gaps/rejections without retry or fallback. C03 persistence
does not own RawFinding storage; C09 owns Source/Evidence/Claim normalization.
Consumers are C09 and later orchestration. C07 company research, C09+ trust
stages, analysis, governance, UI, and cloud behavior are deferred.

**C08 Critical-Path Expectation:** validated C05 Case → real C06
`ResearchPlanner` → selected pending EXECUTIVE task → real C08
executive-research service → C04 deterministic `FakeSearchProvider` as the
necessary external-adapter double → privacy-filtered, identity-constrained,
source-linked `RawFinding`. The service and privacy boundary must be real; the
fake is not live-internet proof.

### Closure Evidence

**Implementation Evidence:** Added the application-owned
`ExecutiveResearchService` with typed result/error contracts. It accepts only
a pending, case-matching C06 EXECUTIVE task, makes one explicit C04 provider
call, caps results, validates public HTTP(S) provenance, requires complete
executive-name matching, applies professional-meeting relevance, removes
duplicate URLs, and constructs only `RawFinding` discovery records.

**Validation / Regression Evidence:** `.venv/bin/python -m pytest
tests/unit/test_executive_research.py` passed 4 tests. `.venv/bin/python -m
pytest` passed 48 tests. `.venv/bin/python -m pip check`, `.venv/bin/python
-m compileall -q src`, the executive-research import check, and `git diff
--check` passed.

**Privacy / Data-Minimization Evidence:** The real C08 service rejects fixture
content containing family details/children and religion/personal-routine
material before it can become a `RawFinding`. It also rejects a different
person with a shared first name and an identity-matching but professionally
irrelevant cooking result. C05's current-title identity path proves that a
missing LinkedIn URL is non-blocking; C08 has no LinkedIn fetch or scrape.
These deterministic controls enact the public + professional + relevant rule,
rather than treating public availability as sufficient.

**Contract / Risk Map Outcome:** The implemented path is C05 confirmed
executive identity → C06 typed executive task → C08 privacy-aware discovery
service → C04 provider contract → raw finding or explicit gap. Discovery
snippets remain untrusted; C08 creates neither C09 Evidence/Claims nor a fact
or inferred priority. C03 persistence/checkpoints, C07 company research, C09
Source/Evidence/Claim normalization, verification, analysis, governance,
workflow, UI, and cloud behavior remain deferred.

**Critical-Path Evidence:**
`test_critical_path_uses_c05_c06_and_real_privacy_aware_executive_research`
composes real C05 intake and local C03 SQLite with no LinkedIn URL, the real
C06 `ResearchPlanner`, a selected C06 `EXECUTIVE_ROLE` task, and the real C08
`ExecutiveResearchService`. `FakeSearchProvider` replaces only the external
C04 search adapter. The actual C08 identity, professional-relevance, and
privacy controls run before a source-linked raw finding is returned. Result:
PASS.

**Live External Smoke Test:** NOT_REQUIRED — the C08 Exit Gate requires useful
public-professional-relevant executive research, not unreliable public-network
availability. No live request was made; the deterministic provider fake is not
represented as live-internet proof.

**Architecture Before → After:** Before C08, C06 could plan executive work but
there was no component to execute it under a data-minimization boundary. After
C08, the application owns a narrow, typed executive-discovery boundary while
the C04 provider abstraction and C09 evidence ownership remain intact.

**Problem → Diagnosis → Fix:** An initial relevance heuristic treated a company
name token shared with the executive surname as company context, allowing an
unrelated personal result to pass. Diagnosis: identity tokens must not also
establish professional relevance. C08 now subtracts executive-name terms from
company-context terms; the privacy/identity regression test passes.

**Known Limitations / Deferrals:** C08 does not access profile pages, scrape
LinkedIn, persist findings, update coverage, create Source/Evidence/Claims,
verify facts, infer priorities, or perform strategic analysis. Search snippets
remain untrusted discovery signals. C09 owns traceable Source/Evidence/Claim
normalization; later Cards own verification, workflow, governance, and briefs.

**Professional Engineering Lesson:** Privacy is not a source filter alone. A
safe executive-research boundary must prove identity, professional relevance,
and data minimization independently, because a public result can still be
about the wrong person or contain inappropriate detail.

**Learner Takeaway:** “Publicly available” means a result may be visible; it
does not mean the system should retain it. The system first asks whether it is
about the confirmed executive, professionally relevant to the meeting, and free
of excluded personal detail.

**What This Enables Next:** C09 can later turn C07/C08 raw findings into
normalized Sources, Evidence, and candidate Claims without inheriting an
unbounded or privacy-blind discovery step.

**Historical Git Evidence:** After closure approval, commit `89712a7`
(`feat(c08): add privacy-bounded executive research`) was pushed on preserved
branch `card/v1-c08-executive-research` and fast-forward integrated into `main`
without a merge commit or history rewrite. These are historical delivery facts;
Git remains the live authority for branch, reference equality, and worktree
state.

**Baseline Before:** N/A — C08 establishes deterministic privacy and identity
controls, not a model, prompt, live-provider, routing, or recovery baseline.
**Candidate After:** N/A — no AI model or external-network quality claim was
introduced.
**Regression Decision:** PASS — C01–C07 regression tests remain green in the
48-test full suite.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — changes are limited to C08 executive discovery, focused
tests, and required Evidence/Project Control updates.
**Git Status Review:** PASS — no secret, `.env`, cache, generated artifact,
machine-specific path, or C09+ implementation is in the C08 tracked set;
`REPAIR_INSTRUCTIONS.md` and `eference/` remain recognized untouched untracked
artifacts outside scope.
**PROJECT_CONTROL Updated:** YES
**Exit Gate Evidence:** PASS — a validated C06 executive task reliably produces
a bounded, traceable, public-professional-meeting-relevant raw finding or an
explicit gap. Privacy, identity, personal-data, malformed, duplicate, empty,
and unavailable outcomes cannot become Evidence, a verified Claim, or an
inferred executive priority.


# V1-C09 — Evidence Layer

**Status:** COMPLETE
**Dependencies:** V1-C03, V1-C07, V1-C08
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Source normalization | `application/evidence_layer.py` | `test_critical_path_persists_complete_provenance_chain` | PASS | Valid source-linked RawFinding creates and persists a Source before Evidence |
| Evidence→Source | `application/evidence_layer.py`; C03 repository | real SQLite save/read-back | PASS | Persisted Evidence retains the saved Source ID and read-back returns the same typed records |
| Claim→Evidence | `application/evidence_layer.py` | focused C09 tests | PASS | Candidate Claim retains one or more explicit ClaimEvidenceLinks with SUPPORTS, CONTRADICTS, and CONTEXT semantics; verification remains unset |
| Contradictions/duplicates | `application/evidence_layer.py`; C03 repository | `test_duplicate_source_is_reused_and_conflicting_evidence_is_preserved` | PASS | Repeated URL reuses Source identity; distinct contradictory excerpts are retained as separate Evidence/links |
| Evidence Fidelity input preservation | `application/evidence_layer.py` | focused C09 tests and code review | PASS | URL, title, Source ID, excerpt, topic, relevance, candidate claim text, and relationship context are retained for later judgment |

### C09 Start / Contract-Risk Map

**Engineering Goal / Why It Exists:** Convert raw C07/C08 discovery into a
persistent, traceable Source → Evidence → candidate Claim foundation without
promoting a candidate to a verified fact.

**Contract / Risk Map:** Producers are source-linked `RawFinding` records from
C07/C08. C09 owns source normalization, evidence extraction, candidate Claim
and ClaimEvidenceLink construction, duplicate handling, and existing C03
persistence/read-back. Invariants: a finding needs case/task/source URL/title
and excerpt; Source is saved before Evidence; Evidence is linked to Source;
candidate Claims retain link semantics SUPPORTS/CONTRADICTS/CONTEXT and no
verification status. Duplicate source URLs reuse C03's Source identity;
duplicate finding content is deterministic. Contradictions remain separate
Evidence/links. C10 quality/freshness classification and C11 fidelity/
verification are deferred. No network/provider, analysis, governance, UI, or
workflow behavior belongs here.

**C09 Critical-Path Expectation:** C07/C08-style `RawFinding` → real C09
service → persisted Source → persisted Evidence → candidate Claim with explicit
link → C03 read-back proving provenance. Network is not required.

### C09 Closure Evidence

**Implementation Evidence:** `EvidenceLayerService` is the C09 application
boundary. It validates source-linked `RawFinding` provenance, normalizes and
persists `Source`, persists `Evidence`, then creates a candidate `Claim` with
an explicit `ClaimEvidenceLink`. Results are typed and fail closed with
`INVALID_FINDING`, `INVALID_CLAIM`, or `PERSISTENCE_FAILED`; no candidate is
assigned a verification status.

**Validation / Regression Evidence:** `.venv/bin/python -m pytest
tests/unit/test_evidence_layer.py` passed 4 tests; the full suite, `pip check`,
`compileall -q src`, the evidence-layer import check, and `git diff --check`
passed at closure. The focused suite proves the real SQLite provenance path,
deterministic duplicate-source reuse, preserved contradictory material,
non-conflated SUPPORTS/CONTRADICTS/CONTEXT links, a real multi-evidence
candidate Claim, and malformed/blank input rejection.

**Contract / Risk Map Outcome:** C07/C08 remain RawFinding producers; C09 owns
only the typed traceability transformation and uses the existing C03
persistence boundary. A valid persisted C05 Case is required by the repository
foreign-key invariant. External content remains untrusted. C10 source
quality/freshness and C11 Evidence Fidelity/verification are explicitly
deferred; no provider, network, analysis, governance, UI, or workflow behavior
was added.

**Provenance / Traceability Evidence:** The critical-path test proves
`RawFinding(case/task/source URL/title/excerpt) → Source(url/title) →
Evidence(source ID/content/topic/relevance) → candidate Claim(text/topic,
verification_status=None) → ClaimEvidenceLink`. It saves and reads the Source
and Evidence through the real C03 SQLite repository, proving the persisted
Evidence references its Source. `originating_finding_id` is retained in the C09
typed result; the existing domain persistence contract does not add a new
stored RawFinding foreign key.

**Critical-Path Evidence:** Expected and actual path are the same: a
C07/C08-style deterministic fixture enters the real C09 service, exercises C03
SQLite Source/Evidence/Claim-link persistence, then reads Source and Evidence
back. Persistence boundary: YES. Mocks/fakes: only the deterministic input
fixture, because C09 owns no network fetch. Network used: NO. Command:
`.venv/bin/python -m pytest tests/unit/test_evidence_layer.py`; result: PASS
(4 passed).

**Architecture Before → After:** Before C09, C07/C08 could produce
source-linked RawFindings but had no application boundary that constructed a
persisted evidence chain. After C09, that chain is explicit and typed while
C02 domain ownership and C03 repository ownership remain unchanged.

**Problem → Diagnosis → Fix:** The first critical-path test attempted to write
records for an unpersisted Case and correctly hit C03's foreign-key protection.
The test now creates the valid C05 Case first, proving C09 composes with rather
than bypasses the existing persistence invariant.

**Known Limitations / Deferrals:** C09 neither fetches sources nor classifies
quality/freshness; it does not score fidelity, verify/adjudicate truth, resolve
contradictions, or produce strategic/governance/UI output.

**Evidence Fidelity Preparation:** Exact source reference and title, excerpt,
topic, relevance, candidate wording, and relationship semantics survive for
C10/C11. Later fidelity judgment—whether wording overstates the evidence,
whether sources are independent, and whether a claim is verified—remains with
its owning Cards.

**Professional Engineering Lesson:** Provenance is a concrete system property:
make the relationship objects and persisted references explicit before asking a
later component to judge trust.

**Learner Takeaway:** Finding something produces a RawFinding. Having evidence
means preserving the source and excerpt in a traceable record. Proving a claim
true requires the later Fidelity and Verification work; C09 deliberately does
not make that leap.

**What This Enables Next:** C10 can add quality/freshness metadata and C11 can
evaluate fidelity and verification from retained, linked evidence rather than
unstructured research output.

**Baseline Before:** N/A — C09 adds a deterministic traceability boundary, not
an AI-quality change.
**Candidate After:** N/A — no model/provider/routing evaluation applies.
**Regression Decision:** PASS — all existing tests remain green.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — C09-only application service, focused tests, Evidence,
and Project Control; no C10+ runtime behavior.
**Git Status Review:** PASS — historical final pre-commit review found only C09
changes on `card/v1-c09-evidence-layer`; recognized
`REPAIR_INSTRUCTIONS.md` and `eference/` were untracked and outside scope.
**PROJECT_CONTROL Updated:** YES
**Historical Git Evidence:** C09 branch was created from integrated `main` at
`c5ff36c`; approved commit `92a3e074bca8ada18d3f6ee02868b5b1f9fdad66`
(`feat(c09): add traceable evidence layer`) was pushed on the preserved Card
branch and fast-forward integrated into canonical `main` without a merge
commit, rebase, or force-push.
**Exact Exit Gate Proof:** PASS — important RawFindings enter a real typed,
persisted Source → Evidence → candidate Claim/link chain and are traceable to
their Sources, with the fidelity and verification inputs retained for later
Cards.


# V1-C10 — Source Quality and Freshness

**Status:** COMPLETE
**Dependencies:** V1-C09
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Source quality | `application/source_quality.py` | `test_primary_and_strong_secondary_classification_is_deterministic` | PASS | Existing SourceType maps deterministically to PRIMARY, STRONG_SECONDARY, or OTHER |
| Publication/retrieval dates | `application/source_quality.py` | `test_publication_and_retrieval_dates_remain_distinct_with_staleness` | PASS | Publication date remains distinct from the Source's retrieval date in typed output |
| Freshness | `application/source_quality.py` | focused C10 tests | PASS | Explicit policy returns CURRENT/AGING/STALE/UNKNOWN; missing or future publication date is UNKNOWN |
| Duplicate-origin signal | `application/source_quality.py` | `test_duplicate_origin_signal_is_preserved_and_self_reference_fails_closed` | PASS | origin_source_id yields a duplicate-origin signal; self-origin is rejected |

### C10 Start / Contract-Risk Map

**Engineering Goal / Why It Exists:** Supply the source-quality, date, freshness,
and origin metadata that C11 needs to evaluate evidence without allowing source
labels to become proof of a Claim.

**Learning Goal:** Separate deterministic source metadata from later trust
judgment: classification and date arithmetic can be tested without pretending
to verify factual support.

**Contract / Risk Map:** C09's persisted `Source` is the producer and C11
Verification is the consumer. C10 owns a deterministic application boundary
that classifies existing `SourceType` values as PRIMARY, STRONG_SECONDARY, or
OTHER; preserves publication and retrieval dates as distinct facts; emits
CURRENT/AGING/STALE/UNKNOWN freshness from publication date and an explicit
reference date; and exposes whether `origin_source_id` marks a duplicate
origin. Inputs must be typed Sources; malformed or self-referential origin
metadata fails closed. C10 does not fetch URLs, alter evidence/claims, assign
VerificationStatus, judge Evidence Fidelity, resolve conflicts, or make
Governance decisions. Persistence remains C03-owned; network and providers are
not part of this Card's Critical Path.

**C10 Critical-Path Expectation:** persisted C03 Source → real C10 metadata
service → typed quality/freshness/origin result → read-back of the unchanged
persisted Source, proving metadata is derived from real source provenance with
no network or verification boundary.

### C10 Closure Evidence

**Implementation Evidence:** `SourceQualityService` derives typed source
metadata without mutating a persisted Source: SourceType maps to
PRIMARY/STRONG_SECONDARY/OTHER; `SourceFreshnessPolicy` maps publication date
against an explicit reference date to CURRENT/AGING/STALE/UNKNOWN; and
`origin_source_id` becomes an explicit duplicate-origin signal. A source cannot
identify itself as its own origin, and an inverted freshness-policy window is
rejected.

**Validation / Regression Evidence:** `.venv/bin/python -m pytest
tests/unit/test_source_quality.py` passed 6 tests; `.venv/bin/python -m pytest`
passed 58 tests; `pip check`, `compileall -q src`, the source-quality import
check, and `git diff --check` passed. The focused suite covers primary/strong
secondary/other classification, date separation, CURRENT/STALE/UNKNOWN,
duplicate-origin preservation, self-reference rejection, and policy invariants.

**Contract / Risk Map Outcome:** C09 Source records are the only input, and C11
Verification is the downstream consumer. C10 remains deterministic and
offline: it does not acquire sources, alter Evidence or Claims, judge Evidence
Fidelity, assign VerificationStatus, resolve conflict, or make Governance
decisions. C03 remains the persistence owner.

**Critical-Path Evidence:** Expected and actual path: real C03 SQLite
repository saves and reads a Source → real `SourceQualityService` assesses that
persisted typed Source → typed PRIMARY/CURRENT metadata is returned while the
repository read-back proves the stored Source is unchanged. Persistence
boundary: YES. Mocks/fakes: none at the owned metadata/persistence boundary;
the test Case and Source are deterministic fixtures. Network used: NO. Command:
`.venv/bin/python -m pytest tests/unit/test_source_quality.py`; result: PASS
(6 passed).

**Architecture Before → After:** C09 retained Source type, publication date,
retrieval date, and origin fields but did not produce deterministic quality or
freshness inputs. C10 adds an application-owned metadata boundary; C02 domain
contracts and C03 persistence remain unchanged.

**Problem → Diagnosis → Fix:** N/A — no implementation defect was found. The
explicit reference-date policy and validation prevent hidden clock-dependent
tests and inverted freshness windows.

**Known Limitations / Deferrals:** C10 does not infer publisher reputation,
fetch dates or content, prove source independence, decide whether evidence
supports a Claim, or resolve conflicts. Those are source-acquisition or C11
Verification/Fidelity responsibilities.

**Professional Engineering Lesson:** Source quality and freshness are useful
inputs, not truth labels. Keeping them deterministic and separate from
Verification makes later trust decisions explainable and testable.

**Learner Takeaway:** A recent official Source may be stronger metadata than an
old supporting Source, but neither proves a Claim. First preserve dates and
origin, then let the later Verification layer assess support.

**What This Enables Next:** C11 can consume consistent quality, freshness, and
duplicate-origin signals while evaluating Evidence Fidelity and Claim
verification.

**Baseline Before:** N/A — deterministic metadata introduces no model/provider
quality comparison.
**Candidate After:** N/A — no model/provider/routing evaluation applies.
**Regression Decision:** PASS — all existing tests remain green.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — C10-only metadata service, focused tests, Evidence, and
Project Control; no C11+ behavior.
**Git Status Review:** PASS — C10 changes are uncommitted on
`card/v1-c10-source-quality-freshness`; recognized
`REPAIR_INSTRUCTIONS.md` and `eference/` remain untracked and outside scope.
**PROJECT_CONTROL Updated:** YES
**Historical Git Evidence:** C10 branch was created from integrated `main` at
`8cff3c8`; approved commit `2c2868910c5bd433f76d38e7e2641dc237626220`
(`feat(c10): add source quality and freshness`) was pushed on the preserved
Card branch and fast-forward integrated into canonical `main` without a merge
commit, rebase, or force-push.
**Exact Exit Gate Proof:** PASS — Verification now has deterministic typed
PRIMARY/STRONG_SECONDARY/OTHER, publication/retrieval-date,
CURRENT/AGING/STALE/UNKNOWN, and duplicate-origin inputs from Source records.


# V1-C11 — Verification Engine

**Status:** COMPLETE
**Dependencies:** V1-C09, V1-C10
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Evidence Fidelity labels | `domain/models.py`; `application/verification.py` | `tests/unit/test_verification.py` | PASS | Typed direct, partial, unsupported, and ambiguous outcomes derive from persisted SUPPORTS/CONTEXT Evidence rather than Evidence availability alone. |
| Verification statuses | `application/verification.py`; typed `VerificationResult` | focused C11 tests | PASS | VERIFIED, SUPPORTED, CONFLICTING, STALE, and INSUFFICIENT_EVIDENCE are deterministic, explainable results; C11 neither mutates Claims nor governs. |
| Source independence/conflict | `application/verification.py`; C03 repository read | focused C11 tests | PASS | Actual links are read with Evidence/Source, C10 quality/freshness is assessed, duplicate origins are counted, and contradictions remain visible. |
| Baseline fixture version | `evaluations/fixtures/c11_verification_baseline.json` | labeled expected-vs-actual baseline test | PASS | `c11-verification-v1` independently labels direct, partial, ambiguous, unsupported, conflicting, stale, duplicate-origin, unknown-freshness, and missing-provenance outcomes. |
| Expected vs actual/regression | `tests/unit/test_verification.py` | focused 13 passed; full suite 71 passed | PASS | Static expected Fidelity/Verification labels match the real C11 service; completed-C01–C10 tests remain green. |

### C11 Start / Contract-Risk Map

**Engineering Goal / Why It Exists:** Evaluate factual candidate Claims against
their linked Evidence after Fidelity checking, so provenance alone cannot
promote a Claim to trusted factual intelligence.

**Learning Goal:** Separate deterministic fidelity/support judgment from source
collection, metadata classification, and later Governance. Evidence exists does
not mean the Claim is supported strongly enough to verify.

**Current System Before Card:** C09 persists a Source → Evidence → candidate
Claim chain with SUPPORTS/CONTRADICTS/CONTEXT links and leaves verification
unset. C10 deterministically provides quality, freshness, and duplicate-origin
metadata for typed Sources. C03 owns repository reads/writes; no Verification
application boundary exists.

**Design Decision:** C11 will add an application-owned, deterministic
Fidelity/Verification service. It will read C09 provenance through the C03
repository boundary, use real C10 metadata, retain contradiction/duplicate
signals, return typed fidelity plus VerificationResult outcomes, and never
mutate the candidate Claim or make Governance decisions.

**Contract / Risk Map:** Producers: persisted C09 Claim, ClaimEvidenceLink,
Evidence, and Source records; C10 provides source-quality/freshness assessment.
Inputs: all links must resolve to the Claim's Evidence and their Sources.
SUPPORTS may contribute only after fidelity comparison; CONTRADICTS preserves a
conflict; CONTEXT never becomes support. Missing provenance, no supporting
Evidence, unsupported/overstated wording, stale/unknown metadata, weak quality,
and duplicate origins fail closed to typed non-verified outcomes. C11 may
conclude VERIFIED, SUPPORTED, CONFLICTING, STALE, or INSUFFICIENT_EVIDENCE with
explainable fidelity status; it must never conclude Governance PASS/RESTRICT/
BLOCK, fetch/research, alter Claim type/status, start C12 follow-up, or hide
conflict/uncertainty. Governance is the downstream C13 consumer.

**C11 Critical-Path Expectation:** persisted C05 Case → real C09 candidate
Claim plus explicit links → C03 read-back of Claim/Evidence/Source/link data →
real C10 quality/freshness assessment → real C11 Fidelity/Verification service
→ typed VerificationResult without Claim mutation. Persistence reads: YES;
providers/network: NO.

**Implementation Evidence:** C11 adds `FidelityStatus` and requires it in the
typed `VerificationResult`; `VerificationService` owns deterministic judgment.
It reads ClaimEvidenceLinks through the application-owned persistence protocol
and C03 SQLite implementation, resolves linked Evidence/Source provenance,
uses C10 `SourceQualityService`, returns accepted/rejected typed assessments,
and does not persist/mutate a Claim's `verification_status`.

**Critical-Path Evidence:** Expected and actual path: persisted C05 Case → real
C09 `EvidenceLayerService` candidate Claim plus SUPPORTS link → real C03 SQLite
Claim/Evidence/Source/link read-back → real C10 metadata assessment → real C11
`VerificationService` → typed `VerificationResult`. The focused test
`test_critical_path_reads_real_c09_candidate_without_promoting_it` passed with
direct fidelity but `INSUFFICIENT_EVIDENCE` for C09's OTHER/unknown metadata;
the persisted candidate remains unmutated. No provider/network or C12 workflow
was faked or used.

**Baseline Before:** N/A — C11 establishes the first deterministic
Fidelity/Verification judgment baseline; no earlier verification behavior
exists for comparison.

**Candidate After / Expected vs Actual:** PASS — static labeled fixture
`c11-verification-v1` records direct-primary VERIFIED, overstrong
INSUFFICIENT_EVIDENCE, ambiguous CONTEXT-only, unsupported, conflicting, stale,
duplicate-origin SUPPORTED, unknown-freshness INSUFFICIENT_EVIDENCE, and
missing-provenance rejection outcomes. The test reads these declared labels and
compares them to real C11 results; it does not generate expected labels from
the service.

**Regression Decision:** PASS — after the independent pre-finalization audit
found and C11 repaired four defects, `.venv/bin/python -m pytest` executed 71
tests with 71 passed. Focused C11 tests: 13 passed. C03/C09/C10 regression
coverage remains included in the full suite.

**Architecture Before → After:** Before C11, C09 held provenance and C10 held
metadata but no component owned the support judgment. After C11, application
code owns a deterministic Fidelity/Verification boundary over those completed
contracts; C13 still owns PASS/RESTRICT/BLOCK Governance and C12 still owns
follow-up research.

**Problem → Diagnosis → Fix:** An independent pre-finalization audit invalidated
the earlier local closure. F001: C11 could evaluate `INFERENCE` or
`RECOMMENDATION` as factual; repair rejects non-FACT Claims. F002: it checked
Evidence→Source case consistency but not Claim→Evidence; repair rejects
cross-case Evidence. F003: punctuation-only or non-ASCII-only Claim text could
normalize to an empty string and match every Evidence item; repair rejects an
unusable normalized Claim before fidelity. F004: the versioned baseline omitted
required scenarios; repair added static ambiguous, unsupported, duplicate,
unknown-freshness, and missing-provenance oracles. New regression tests prove
each repair; 13 focused and 71 full tests pass.

**Known Limitations / Deferrals:** Verification results are returned, not yet
persisted as a separate record or used by workflow/Governance. C11 rejects
non-FACT Claims rather than governing them. C12 owns bounded follow-up
research; C13 owns final trust policy; C15+ owns consumption.

**Professional Engineering Lesson:** Provenance, source metadata, fidelity, and
Governance are distinct trust layers. Separating them makes conservative
judgments inspectable and prevents a convenient but unsafe “evidence exists”
shortcut.

**Learner Takeaway:** A factual candidate becomes useful only after its words,
relationships, source quality, freshness, independence, and conflicts are
evaluated. A typed non-verified outcome is a successful safety result.

**What This Enables Next:** C12 can request bounded additional research for a
specific weak Claim, while C13 can later apply non-overridable governance to
the explicit C11 result.

**Diff Review:** PASS — C11-only domain/application/persistence/test/baseline
and durable-documentation changes; no provider, Governance, orchestration, UI,
or C12+ behavior.

**Git Status Review:** PASS — only C11 tracked changes plus recognized
untracked `REPAIR_INSTRUCTIONS.md` and `eference/`; no staged files, commit,
push, merge, rebase, or force-push.

**PROJECT_CONTROL Updated:** YES

**Historical Git Evidence:** C11 implementation commit
`f3bca2f9e031da2b319f87be0cba745bb6448bd2`
(`feat(c11): add governed verification engine`) was pushed to the preserved
`card/v1-c11-verification-engine` branch and fast-forward integrated into
canonical `main` without a merge commit, rebase, or force-push. This is
historical delivery evidence; Git remains the live authority.

**Exact Exit Gate Proof:** PASS — after F001–F004 repair, FACT-only entry,
same-Case Claim→Evidence→Source provenance, unusable-normalization rejection,
overstrong, unsupported, context-only, missing-provenance, stale,
unknown-freshness, duplicate-origin, conflicting, and independent-confirmation
cases exercise deterministic non-promotion. The versioned baseline has static
expected labels matching actual C11 results; no unsupported or overstrong FACT
is emitted as VERIFIED/SUPPORTED.


# V1-C12 — Bounded Follow-Up Research

**Status:** COMPLETE
**Dependencies:** V1-C07, V1-C08, V1-C11
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Focused follow-up | `application/follow_up_research.py` | `test_follow_up_research.py` | PASS | Deterministic C12 orchestration accepts only unresolved C11 assessments and terminates on no progress, resolution, or budget exhaustion. |
| Attempt limit | `FollowUpResearchService.run` | focused tests | PASS | Iteration is bounded by `ResearchTask.max_attempts` (1–3); no implicit retry exists. |
| Reverification | C09 Evidence + C11 Verification | focused tests | PASS | Retained follow-up provenance is appended to the existing Claim before deterministic C11 re-evaluation. |
| Abstention | `FollowUpResult` | focused tests | PASS | Missing/insufficient follow-up remains NO_PROGRESS or EXHAUSTED, never VERIFIED. |
| Audit/persisted counters | `FollowUpResearchAttempt`; SQLite repository | focused tests | PASS | Each executed attempt persists count, evidence IDs, verification status, terminal flag, and reason. |

**Baseline Before:** N/A — C12 did not exist; C11 correctly stopped at typed unresolved outcomes.
**Candidate After:** PASS — C07/C08 preserve optional provider publisher/publication metadata in the application-owned `RawFinding`; C09 persists it to `Source` and `Evidence`; bounded C12 retains provenance, re-runs C11, and persists each terminal attempt without Governance behavior.
**Regression Decision:** PASS — C07–C12 focused composition/regression tests: 36 passed; full suite: 75 passed; `pip check`, compile, package/config imports, and diff check passed.
**Known Issues / Blockers:** None. The confirmed C07/C08 → `RawFinding` → C09 metadata-propagation gap was repaired without altering C10 freshness policy or C11 verification policy: missing publication dates remain UNKNOWN, and retrieval date is not substituted or fabricated.
**Critical Path:** PASS — deterministic C04-style `SearchResult(publisher="Example Co", published_at=2026-08-20)` → real C07 `CompanyResearchService` → metadata-bearing `RawFinding` → real C09 `EvidenceLayerService` → C03 SQLite persistence → C10 CURRENT freshness assessment at 2026-08-27 → C11 VERIFIED Claim → real C12 bounded follow-up RESOLVED after one persisted attempt. C08 has a focused equivalent propagation proof. The fake replaces only external provider/network discovery; application, evidence, persistence, C10, and C11 boundaries are real. No network use.
**Technical Learning / Learner Takeaway:** Bounded follow-up is orchestration, not a truth or Governance authority. Provenance metadata must survive each application-owned boundary so deterministic quality and verification decisions can remain conservative when metadata is missing and can resolve only when retained evidence warrants it.
**Known Limitations / Deferrals:** C13 remains the sole owner of PASS/RESTRICT/BLOCK; no Governance decision, silent provider fallback, or autonomous loop was added.
**Diff Review:** PASS — C12 application/domain/persistence/test/Evidence changes plus directly-required C07/C08 → C09 metadata propagation and regression coverage only; no C13+ implementation.
**Git Status Review:** PASS — tracked changes reviewed; protected untracked repair/reference materials remain outside scope.
**Exit Gate Evidence:** PASS — workflow-level research-more is deterministic and bounded by `ResearchTask.max_attempts` (1–3); the real composed resolved path and terminal no-progress paths are both proven, with every executed attempt persisted for audit.


# V1-C13 — Governance Gate

**Status:** COMPLETE
**Dependencies:** V1-C11
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| FACT without Evidence BLOCK | C02 `Claim` invariant; `GovernanceService.evaluate` | `test_governance.py` | PASS | A FACT without Evidence cannot deserialize as a valid Claim; Governance rejects that invalid persisted input before final use rather than weakening the C02 invariant. |
| Evidence without Source BLOCK | `GovernanceService._evaluate_fact` | focused tests | PASS | Invalid provenance from C11 becomes a persisted BLOCK with `UNTRACEABLE_CLAIM`. |
| Inference separation | `GovernanceService.evaluate` | focused tests | PASS | Traceable INFERENCE stays INFERENCE and receives RESTRICT with `INFERENCE_REQUIRES_QUALIFICATION`; it is never verified as FACT. |
| BLOCK leakage=0 | `GovernanceDecision` only | focused tests | PASS | BLOCK is a typed, persisted terminal Governance result; C16 Brief behavior was not implemented or invoked. |
| RESTRICT preservation | `GovernanceDecision.reason_codes` and `notes` | focused tests | PASS | Conflict, stale, inference, and recommendation restrictions preserve an explicit reason and qualification in persistence. |
| Fail closed/reason codes | `GovernanceService`; C03 repository | focused tests | PASS | Unsupported, untraceable, and private-personal Claims BLOCK; deterministic repeated evaluation preserves decision/reason semantics and audit records. |

**Baseline Before:** N/A — C11 supplied deterministic verification outcomes but no final-use Governance decision or persisted restriction record.
**Candidate After:** PASS — C13 deterministically consumes persisted Claim provenance and C11 assessment, produces one typed PASS/RESTRICT/BLOCK decision with reason codes/notes, and persists it through the application-owned C03 repository boundary.
**Regression Decision:** PASS — focused C13: 8 passed; C09–C13 evidence/source-quality/verification/follow-up/governance regression: 35 passed; full suite: 84 passed; `pip check`, compile, governance import, and diff checks passed.
**Known Issues / Blockers:** None. During C13 testing, a valid RECOMMENDATION with no Evidence exposed an over-strict C03 link-set check. The bounded correction permits an empty link set only when the Claim has no evidence IDs, while still requiring every supplied link to match the Claim and exactly match its evidence IDs. FACT/INFERENCE evidence invariants remain enforced by C02; invalid persisted FACT data is rejected fail-closed.
**Critical Path:** PASS — persisted C03 Source/Evidence/FACT Claim with unresolved C11 quality → real C12 `FollowUpResearchService` → deterministic C04-style fake `SearchResult` → real C07 Company Research → C09 retained provenance → C10 freshness inside real C11 → C12 RESOLVED → real C13 `GovernanceService` → PASS `GovernanceDecision` → C03 `list_governance_decisions` read-back. The fake replaces only external search/network discovery; no network use.
**Technical Learning / Learner Takeaway:** Verification asks whether a Claim is supported; Governance separately decides whether it may be used. Keeping the decision typed, deterministic, reason-coded, and persisted makes conflict, staleness, uncertainty, non-factual content, and privacy boundaries visible rather than silently normalized away.
**Known Limitations / Deferrals:** C14 security controls, C15 strategic analysis, C16 Brief routing, orchestration, and provider/network enforcement remain out of scope. C13 performs no research, source-quality classification, fidelity re-evaluation, or AI override.
**Diff Review:** PASS — C13 Governance/domain/repository/test/Evidence changes plus the directly-required valid no-evidence RECOMMENDATION persistence correction only; no C14+ implementation.
**Git Status Review:** PASS — tracked C13 changes reviewed; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside scope; no staged files.
**Exit Gate Evidence:** PASS — deterministic PASS/RESTRICT/BLOCK rules block unsupported, untraceable, and private-personal Claims; preserve stale/conflict/non-factual qualification; and cannot be overridden by model output because no model path exists in the Governance engine.


# V1-C14 — Security Boundaries

**Status:** COMPLETE
**Dependencies:** V1-C04, V1-C05, V1-C07, V1-C08, V1-C13
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| URL / SSRF / redirect | `security/boundaries.py`; C05/C07/C08/C09 ingress; C04 DuckDuckGo adapter | `test_security_boundaries.py` | PASS | One application-owned policy accepts syntactically valid public HTTP(S) URLs and permits only public-unicast destinations. It rejects malformed authority encoding, credentials, loopback, private, link-local, unspecified, multicast, reserved, known internal, and resolver-supported numeric destinations. The owned network opener resolves and checks every address before opening; every redirect repeats that check. |
| Safe source retention | `application/evidence_layer.py` | unsafe literal and malformed-host persistence tests | PASS | Unsafe and malformed RawFindings are rejected before `save_source`, `save_evidence`, or Claim persistence; C14 rejection cannot become trusted Evidence. |
| Prompt-injection isolation | C07/C08 RawFinding data flow; C09 evidence; C13 Governance | `test_untrusted_source_text_remains_data_and_cannot_override_governance` | PASS | Malicious source instructions remain persisted source data only. They receive no provider, tool, configuration, or Governance capability; deterministic C13 returns BLOCK for the unsupported Claim. |
| Artifact path safety | C03 `LocalArtifactStore` | `test_artifact_paths_allow_safe_components_and_reject_traversal` | PASS | Generated-safe identifiers and containment under the configured root allow a safe artifact while rejecting traversal in identifiers and suffixes. |
| Secrets / logging | `observability/logging.py` | message and formatted-exception redaction tests | PASS | The application logger redacts configured secret values plus bearer and credential-shaped fragments from messages, stack information, and pre-rendered exception text without mutating the underlying exception. No secret is hardcoded or added to domain/persistence contracts. |
| Least privilege / no silent fallback | C04 provider factory; C07 Company Research | `test_provider_configuration_and_failure_do_not_silently_fallback`; `test_providers.py` | PASS | Provider selection remains explicit. Unsupported configuration fails and a failing provider produces one visible UNAVAILABLE result with no substitution, retry, or bypass. |
| Privacy regression | C08 Executive Research | `test_executive_research.py` | PASS | The completed C08 public-professional/personal-data filtering boundary remains green and is not re-owned by C14. |

**Baseline Before:** C05/C07/C08 had three similar public-URL normalizers and C03 already contained artifacts, but C09 accepted any HTTP(S) finding, the DuckDuckGo adapter auto-followed redirects, and logging had no secret-redaction filter.
**Candidate After:** PASS — C14 centralizes deterministic external-URL normalization in `security/boundaries.py`, applies it at C05 user intake, C07/C08 discovery retention, C09 evidence retention, and the only owned external network opener. The lexical boundary admits only ASCII DNS reg-names or IP literals and rejects encoded authority text. At the network boundary, `getaddrinfo` results are checked before opening and before every redirect continuation; every resolved address must meet the public-unicast invariant. The same fail-closed policy protects redirects; logging redacts secrets; existing C03, C04, and C13 boundaries remain owned by their Cards.
**Regression Decision:** PASS — focused C14: 27 passed; C04/C05/C07/C08/C09/C13 security regression: 36 passed; full suite: 111 passed; `pip check`, compile, package/config imports, `git diff --check`, and `git diff --cached --check` passed.
**Known Issues / Blockers:** Resolved before final closure. The first pre-delivery audit invalidated the initial closure: F001 found decimal/hex numeric IPv4 forms (`2130706433`, `0x7f000001`) passed textual validation but resolved to loopback; F002 found `SecretRedactionFilter` redacted a log message but not formatter-appended `exc_info`. F001 was repaired with literal numeric parsing plus fail-closed resolved-address validation at the owned opener and redirect boundary. F002 was repaired by redacting pre-rendered exception and stack text on the LogRecord while retaining the original exception. The second adversarial audit found F003: multicast addresses were accepted because `is_global` was treated as permitted public access; this was repaired with an explicit public-unicast invariant. It also found F004: percent-encoded authority hosts passed lexical C05/C09 validation; this was repaired with ASCII DNS-reg-name/IP-literal host syntax validation. The earlier C13 BLOCK-versus-RESTRICT test expectation was corrected to prove stronger existing Governance behavior; no production defect was found there.
**Critical Path:** PASS — multicast `http://224.0.0.1/discovery` → real C14 public-unicast policy → `INTERNAL_DESTINATION` rejection → mocked `build_opener` proves no network opener/action occurs. Malformed `http://%31%32%37.0.0.1/internal` → shared lexical policy → `MALFORMED` rejection → real C05 validation and C09 EvidenceLayer reject before persistence, with no network opener. The F001 numeric-loopback and resolved-private redirect paths remain rejected; a mocked public resolver result permits the HTTPS/public-unicast control URL. Separately, an exception carrying a configured secret → real `SecretRedactionFilter` → standard final formatter emits `[REDACTED]` while the original exception remains unchanged. Mocks replace only DNS/network I/O to make safety deterministic; the C14 policy, redirect hook, C05/C09 boundaries, and logging formatter path are real. No network use.
**Technical Learning / Learner Takeaway:** Security is strongest when the component holding a dangerous capability enforces a narrow deterministic policy itself. Centralizing URL policy eliminates inconsistent ingress validation, while capability separation means untrusted text can be retained as evidence data without becoming instructions, tool access, secrets, or Governance authority.
**Known Limitations / Deferrals:** The standard-library opener performs its own resolution after C14's `getaddrinfo` preflight, so the bounded V1 implementation rejects all addresses observed immediately before each owned open/redirect but does not claim DNS-pinning or perfect DNS-rebinding immunity without a larger custom HTTP stack. Resolution failures fail closed. C15 analysis, C16 Brief behavior, UI, cloud/enterprise security, crawlers, and access-control bypass remain out of scope. C09 provenance, C10 freshness, C11 verification, C12 follow-up, and C13 Governance ownership are unchanged.
**Diff Review:** PASS — centralized C14 security policy, resolved-destination/redirect repair, public-unicast/malformed-host adversarial repair, logging exception-redaction repair, ingress wiring, provider protection, focused tests, and canonical C14 Evidence only; no C15+ implementation, architecture expansion, dependency, or new control dashboard.
**Git Status Review:** PASS — all tracked C14 changes reviewed; no staged files; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside scope.
**Exit Gate Evidence:** PASS — external research URLs are deterministically validated at application ingress and, immediately before the owned network access path, against every address then resolved. Malformed authority, unsafe literal/numeric, resolved-private, multicast, and redirect destinations are rejected before downstream network/evidence actions. Source text cannot override the separate deterministic C13 authority, artifact traversal is rejected, provider failure does not bypass policy, and message/exception secret-bearing log content is redacted. Therefore external research cannot bypass application security/Governance boundaries within the documented standard-library DNS preflight limitation.


# V1-C15 — Strategic Analysis

**Status:** COMPLETE
**Dependencies:** V1-C11, V1-C13
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Controlled strategic reasoning | `application/strategic_analysis.py` | `test_critical_path_builds_bounded_governed_context_and_typed_analysis` | PASS | A Case's governed C11/C13 intelligence is compressed into typed `StrategicAnalysis`; C15 performs no research, verification judgment, or Governance decision. A provider result requires at least one grounded analytical contribution. |
| Context retrieval and isolation | `application/persistence.py`; `infrastructure/sqlite_repository.py` | `test_cross_case_claim_references_fail_closed_and_retrieval_is_isolated` | PASS | The narrow C03 extension lists Claims only by Case. C15 re-checks every linked Evidence and Source against that Case and rejects cross-Case output references. |
| Deterministic context budget | `application/strategic_analysis.py` | budget and `test_restriction_overflow_is_visible_and_deterministic` | PASS | Only latest Case-matching C13 PASS/RESTRICT decisions are eligible; bounded synthesis orders PASS before RESTRICT, then C11 state, Evidence relevance, and opaque Claim ID. A separately bounded restriction channel retains selected gaps and records `omitted_restriction_count`; an automatic restricted knowledge gap discloses incomplete coverage without exposing omitted Claim content. |
| Trust preservation | `application/strategic_analysis.py`; `domain/models.py` | A01–A11 adversarial focused tests | PASS | BLOCK Claims, Evidence summaries, and metadata are excluded before provider access. FACT requires one eligible PASS FACT Claim and Unicode-safe canonical equality. INFERENCE/RECOMMENDATION remain non-FACT and Case/Claim-bound; RECOMMENDATION cannot become INFERENCE. RESTRICT-derived AnalysisItems, Opportunities, and MeetingQuestions carry deterministic structured restriction flags/reason codes and qualifications; nested Case IDs must match. |
| User/context and source safety | `application/strategic_analysis.py` | provider user-background and prompt-injection tests | PASS | Provider-generated user relevance is rejected; C15 derives it only from the supplied Case meeting goal. Evidence text enters a bounded JSON data envelope and cannot authorize Claims, override C13, or become instructions. |
| Provider failure handling | `application/strategic_analysis.py` | malformed provider-output test | PASS | Schema-invalid/provider-failed output is rejected without accepting partial analysis. |
| Provider-output bounds | `application/strategic_analysis.py` | `test_provider_output_bounds_fail_closed_and_accept_valid_boundary` | PASS | C15 rejects over-limit section items, Opportunities, MeetingQuestions, free-text fields, and Claim-reference cardinality rather than truncating potentially meaningful output. |

**Baseline Before:** C01–C14 supplied typed Case, provenance, Verification, Governance, and provider contracts, plus future-oriented domain output models, but no Case-scoped governed-context retrieval or strategic-analysis application service.
**Candidate After:** PASS — C15 introduces a bounded application-owned synthesis boundary. It consumes only Case-scoped C13 PASS/RESTRICT Claims, recomputes C11 metadata through the existing Verification service, truncates Evidence summaries, and validates provider output before acceptance. FACT permits formatting-only Unicode NFKC/case/whitespace canonical equivalence with one permitted supported PASS FACT Claim; it does not claim semantic paraphrase validation. The provider receives no BLOCK Claim, Evidence, or metadata. A bounded restriction channel carries selected restrictions and explicitly reports omitted coverage; final output adds structured restriction metadata, qualifications, and gaps. User relevance remains derived only from the Case meeting goal.
**Regression Decision:** PASS — focused C15: 20 passed; relevant C09–C15 regression: 82 passed; C13: 8 passed; C14: 27 passed; affected persistence/domain: 17 passed; full suite: 131 passed; `pip check`, compile, package/config imports, `git diff --check`, and `git diff --cached --check` passed in the final repair validation.
**Known Issues / Blockers:** F001 (TEST, resolved) — the first budget test used a fixed provider response referencing one randomly generated Claim ID, while deterministic budget ordering could exclude that Claim. C15 correctly rejected the out-of-context reference. The test was repaired to use a provenance-free empty provider analysis for ranking/budget proof. The first independent adversarial audit found A01–A05 and they were repaired: invented FACT/copied BLOCKed text via unrelated PASS ID, nested Case mismatch, restriction loss at PASS-heavy cutoff, classification escalation/unqualified restricted derivatives, and empty analysis. A second audit found A06–A11: ASCII-loss Unicode FACT equality, semantic BLOCK-paraphrase overclaim, structural-only restricted metadata, silent restriction overflow, low-value generic recommendation acceptance, and unbounded output. A06 is repaired with formatting-only Unicode canonicalization; A07 is repaired by the actual provider-context boundary, not a claim of arbitrary paraphrase detection; A08/A09/A11 are repaired with structured restriction metadata, overflow disclosure, and fail-closed output bounds. A10 remains a non-blocking residual: C15 rejects empty/structurally vacuous output but does not judge open-ended strategic usefulness.
**Critical Path:** PASS — persisted Case + real C03 Case-scoped Claim retrieval + real C11 verification + real C13 PASS/RESTRICT/BLOCK decisions → C15 excludes all BLOCK content before a bounded PASS/RESTRICT provider context → selected restriction gaps plus explicit overflow count → fake C04-style structured provider returns bounded `StrategicAnalysis` → C15 rejects unsupported Unicode FACT changes, out-of-context references, cross-Case output, classification escalation, malformed/oversized output, and empty analysis → accepted non-FACT reasoning remains typed/provenanced while RESTRICT-derived fields are structurally marked and qualified. The fake replaces only provider generation; repository, Verification, Governance evidence, C15 policy, and output validation are real. No network use.
**Technical Learning / Learner Takeaway:** Strategic value can be added without handing an LLM raw authority: let deterministic controls decide what is eligible, give the model a small typed data envelope, and reject output that cannot prove its links back to permitted Claims.
**Known Limitations / Deferrals:** C15 does not persist StrategicAnalysis, generate a Brief, orchestrate a workflow, or judge open-ended semantic usefulness; those remain C16+ work and later evaluation. FACT is deliberately constrained to Unicode NFKC/case/whitespace-equivalent Claim reuse rather than semantic paraphrase. INFERENCE/RECOMMENDATION retain model-authored language but are Case/Claim-bound, explicitly non-FACT, and structurally marked/qualified when RESTRICT; C15 cannot deterministically detect arbitrary semantic paraphrases a hostile provider knows independently of its bounded input. C13 remains final-use authority. A generic provenance-bearing recommendation can satisfy C15's intentionally non-semantic minimum-value invariant; Golden Case/evaluation owns usefulness judgment.
**Diff Review:** PASS — C15 application service, narrow Case-scoped Claim retrieval, small optional qualification fields on existing analysis outputs, focused adversarial tests, and the canonical C15 Evidence record only; no research, verification, Governance, security, Brief, UI, or C16+ implementation.
**Post-Delivery Repair Chronology:** The C01–C15 hard audit found P01: a historical C13 PASS could be reused after the real C11 assessment became stale; repaired by persisting a semantic C11 fingerprint with C13’s decision and requiring C15’s final-use context to match it. S01: a configured remote Ollama endpoint could bypass C14’s owned network boundary; repaired by loopback-only local configuration, explicit remote enablement, and C14 validation for enabled remote requests. D01: four durable architecture/workflow documents incorrectly placed Strategic Analysis before Governance; corrected to the implemented `Verification → Governance → Strategic Analysis` order. Focused C11/C13/C15 and C04/C14 regressions plus composed tests prove the repairs; C13 remains the sole final-use Governance authority.
**Git Status Review:** PASS — no files staged; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside scope.
**Exit Gate Evidence:** PASS — controlled strategic reasoning uses only bounded Case-scoped governed intelligence; BLOCK material is excluded before provider access; FACT allows only formatting-equivalent reuse of one eligible PASS FACT Claim; all model reasoning remains typed and in-context; RESTRICT derivations are structurally visible downstream; restriction overflow is explicitly disclosed; and malformed, oversized, cross-Case, unsupported-FACT, classification-escalating, and empty provider output fails closed. This is a bounded-input/non-FACT reasoning guarantee, not semantic detection of arbitrary BLOCK paraphrases.


# V1-C16 — Brief Generator

**Status:** COMPLETE
**Dependencies:** V1-C13, V1-C15
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Deterministic Quick/Full Briefs | `application/brief_generator.py`; `domain/models.py` | `tests/unit/test_brief_generator.py` | PASS | C16 deterministically projects only accepted C15 analysis; QuickBrief carries gaps and restriction-overflow disclosure. |
| Cross-Card trust composition | C03/C11/C13/C15 → C16 | real composed C13 → C15 → C16 test | PASS | PASS is visible, RESTRICT is qualified in both Briefs, BLOCK is absent, and related Claim IDs remain traceable. |
| Provenance and Case isolation | `BriefGeneratorService` | cross-Case/unknown Claim and persistence-reload tests | PASS | Case, Claim, Evidence, and Source ownership are validated before presentation; inconsistent provenance fails closed. |
| Classification/restrictions/gaps | `BriefGeneratorService` | altered FACT and removed-restriction adversarial tests | PASS | Unsupported FACT rewrite and removed C15 restriction metadata are rejected; knowledge gaps and omitted restrictions remain visible. |
| Provider/security boundary | existing C04/C14 adapters | C14/provider regression | PASS | C16 adds no provider, SDK, socket, or direct network path. |

**Baseline Before:** C15 provided accepted Case-scoped StrategicAnalysis but no Brief-generation service or Brief-specific trust validation.
**Candidate After:** PASS — deterministic QuickBrief and MeetingBrief presentation consumes accepted C15 output, validates same-Case provenance, preserves typed classification/restrictions/gaps, and exposes traceable source references without a new provider path.
**Regression Decision:** PASS — focused C16 plus C13/C14/C15/persistence/domain regression passed; full suite and dependency/compile/import/diff checks passed.
**Cross-Card Composition Surface:** C13 → C15 → C16 preserves PASS/RESTRICT/BLOCK semantics; currentness remains owned by C15; C03 reload retains same-Case provenance; C14 remains the sole external-provider boundary; C16 rejects unknown/cross-Case Claim/Evidence/Source references.
**Critical Path:** PASS — persisted Case + traceable Source/Evidence/Claim + real C11/C13 PASS/RESTRICT/BLOCK decisions → C15 accepted StrategicAnalysis → deterministic C16 QuickBrief + MeetingBrief → FACT/INFERENCE/RECOMMENDATION provenance, restriction metadata, gaps, source references, and BLOCK exclusion validated. The provider is fake only for C15 structured analysis; persistence and trust services are real.
**Hard-Audit Chronology:** The pre-delivery C16 hard audit initially failed. F001 found QuickBrief silently truncated material gaps after five items; repaired with independent `omitted_knowledge_gap_count`, separate from C15's upstream `omitted_restriction_count`. F002 found MeetingBrief reduced restricted gaps to plain strings; repaired with typed `knowledge_gap_details` retaining `is_restricted` and reason codes. F003 found no independent C16 presentation bounds for typed adversarial input; repaired with deterministic section, gap, text, Claim-reference, duplicate-reference, and source-reference limits. Boundary/one-over tests and the C13→C15→C16, currentness, persistence/reload, Quick/Full consistency, and adversarial re-audit proofs passed.
**Known Issues / Blockers:** None. C16 intentionally does not detect arbitrary semantic paraphrase attacks beyond C15's bounded provenance controls, nor does it persist Briefs or orchestrate workflow; later Cards own those capabilities.
**Diff Review:** PASS — C16 service, minimal QuickBrief trust-display fields, focused C16/composition tests, and canonical C16 Evidence only; no C17/UI, research, verification, Governance, security-policy, provider-adapter, or workflow-recovery implementation.
**Git Status Review:** PASS — no files staged; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside C16 scope.
**Exit Gate Evidence:** PASS — both Briefs are generated only from accepted C15 governed analysis, are traceable through valid same-Case Claim/Evidence/Source records, retain restrictions/gaps and classification, reject provenance or trust destruction, and contain meaningful governed material. C17 remains NOT_STARTED.


# V1-C17 — Minimal Local UI

**Status:** COMPLETE
**Dependencies:** V1-C05, V1-C16, V1-C18
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Case input | `ui/local_app.py` | `tests/unit/test_local_ui.py` | PASS | C05-compatible core, identity-support, and optional fields map unchanged through the public facade. |
| C18 workflow invocation | `ui/local_app.py` | local UI → `WorkflowApplication` adapter proof | PASS | UI imports only `WorkflowApplication` and presentation models; it constructs no lower-level runtime service. |
| Quick/Full display | `ui/local_app.py` | focused rendering tests | PASS | Existing typed Brief fields, gaps, restrictions, and omission disclosures render escaped. |
| Partial/failure display | `ui/local_app.py` | focused rendering tests | PASS | Terminal state, typed error code/message/stage, and only returned safe material render without tracebacks. |

**Baseline Before:** C18 exposed a typed workflow result but no local browser interface.
**Candidate After:** PASS — loopback-only standard-library WSGI UI accepts C05 payloads, delegates only to `WorkflowApplication`, and safely renders existing typed terminal results.
**Regression Decision:** PASS — focused UI, C05, C14, C16, C18, WorkflowApplication, and full regressions passed.
**Critical Path:** PASS — local form submission → `WorkflowApplication.execute(...)` → C18 typed result → escaped local browser presentation; deterministic fake providers prove the path without external network access.
**Known Issues / Blockers:** None. Resume controls remain intentionally absent because C17 does not own recovery interaction.
**Diff Review:** PASS — thin standard-library UI, C17 focused tests, README launch guidance, and C17 Evidence only; no provider, persistence, workflow, trust, or security authority moved into UI.
**Git Status Review:** PASS — no files staged; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside scope.
**Exit Gate Evidence:** PASS — `python -m strategic_intelligence.ui` starts a loopback-only server at `127.0.0.1:8765`; a C05-compatible controlled submission produces and safely presents a typed C18 result. C18 remains authoritative for workflow execution and all trust semantics.
**Git Delivery:** PASS — C17 commit `dc224bf172f68685e430d5e6804cf681fb34e85b` was pushed on `card/v1-c17-minimal-local-ui` and fast-forward integrated into canonical `main`.


# V1-C18 — Workflow Execution and Recovery

**Status:** COMPLETE
**Dependencies:** V1-C03, V1-C05, V1-C16
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| First-run application workflow boundary | `harness/workflow_executor.py` | C18 focused composition | PASS | C05→C16 typed terminal result |
| Accepted-checkpoint protocol | workflow run snapshots + SQLite checkpoints | focused recovery tests | PASS | accepted-only resume/fallback |
| Persistence/invariant rejection | executor checkpoint boundary | controlled repository fault | PASS | no false advancement |
| Trust/currentness preservation | C18 routing to C11/C13/C15 | trust-side resume | PASS | resumes at `EVIDENCE_BUILT` |
| Bounded counters | `WorkflowRun.retry_count` | retry/reload tests | PASS | one retry, persisted |
| Idempotent/duplicate-safe resume | durable Claim reuse | research resume tests | PASS | stable provenance IDs |

**Critical Path:** PASS — valid Case → planned/researched traceable Claim → Verification → eligible bounded C12 Follow-Up → current Governance → C15 → C16 → typed terminal result; persisted intermediate recovery reuses durable provenance and re-establishes current trust.
**Cross-Card Composition:** PASS — C03 preserves Case integrity; C07/C08 normalize retryability; C09 provenance remains traceable; C10/C11/C13 own trust; C12 is bounded and non-authorizing; C15/C16 exclude BLOCKed authority; C18 owns only orchestration/recovery.
**BLOCK / C12 Proof Surface:** Upstream C07/C08/C09/C03 intentionally prevent unsafe first-run BLOCK material. BLOCK is therefore proven at its C13→C15→C16 owner boundary; C18 has no bypass or resurrection path. Unresolved first-run Verification invokes C12; a persisted/resumed resolved-current state does not create another attempt.
**Validation:** `tests/unit/test_workflow_executor.py` (16 passed); C13/C15/C16 BLOCK owner-boundary regression command (52 tests passed, including BLOCK exclusion coverage); full suite (158 passed); `pip check`, compile/import, and Git diff checks passed.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — C18 executor, typed persistence/retry surface, focused tests, narrow C07/C08 retryability propagation, and C18 contract/evidence only; no C17 work.
**Git Status Review:** PASS — no staged files; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside scope.
**Exit Gate Evidence:** PASS — first-run execution and accepted-checkpoint recovery are bounded, typed, Case-safe, idempotent for durable artifacts, and cannot corrupt or bypass current trust authority.
**Post-Integration Composition Repair:** PASS — `application/workflow_application.py` now wires the existing approved local repository, configured providers, and C05–C16 services into the C18 executor. A future UI can execute or resume only through this typed facade; no trust, security, retry, persistence, or recovery semantics moved from their existing owners.


# V1-C19 — Observability and Audit

**Status:** COMPLETE
**Dependencies:** V1-C03, V1-C04, V1-C13
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Structured harness trace | `observability/audit.py`; C03 repository | `tests/unit/test_observability.py` | PASS | Typed, ordered, content-minimized events persist and reload by workflow run. |
| Verification/Governance events | C18 observer hooks | real governed workflow composition | PASS | Existing C11/C13 outcomes are recorded without reinterpretation. |
| Checkpoint decisions | C18 `_checkpoint` observation | controlled C03 rejection composition | PASS | Accepted and rejected owner outcomes are observed; no false acceptance is emitted. |
| Retry/error events | C04 provider observer + C18 retry hook | real retryable C18 provider path | PASS | Existing single retry, provider failure, terminal result, and sanitized metadata are reconstructed. |
| Observer-failure isolation | `AuditTrail.record(...)` | real C18 execution with controlled audit-write failure | PASS | An audit-store failure cannot convert an accepted checkpoint or C18 terminal outcome into a different workflow result; the incomplete trace makes no false terminal claim. |
| Secret redaction | existing `redact_secrets` | adversarial secret-bearing provider/checkpoint paths | PASS | Persisted events and reports contain no controlled secret, raw provider content, or traceback. |
| Performance baseline telemetry | `AuditReport` | trace/report and reload assertions | PASS | Total/stage durations plus provider, retry, error, checkpoint, Verification, and Governance counts reconcile to persisted events. |

**Baseline Before:** C18 persisted workflow/checkpoint state but no structured run audit trace or application-owned reconstruction report.
**Candidate After:** PASS — C19 observes existing C03/C04/C11/C13/C18 outcomes through typed, redacted persisted events and `WorkflowApplication.audit_report(...)`.
**Regression Decision:** PASS — C19 focused (7), C03/C04/C11/C12/C13/C14/C18/WorkflowApplication regression (98), and full suite (174) passed.
**Critical Path:** PASS — real governed workflow → ordered persisted C19 trace/report → close/reopen → same reconstructed metrics and terminal outcome, without secrets.
**Known Issues / Blockers:** None.
**Diff Review:** PASS — C19 audit model/persistence/observer/report surface, focused proofs, and canonical C19 Evidence only; no authority moved from C03/C04/C11/C13/C18.
**Git Status Review:** PASS — no files staged; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside C19 scope.
**Exit Gate Evidence:** PASS — a developer can retrieve persisted/reloaded ordered events, bounded decision/retry/checkpoint/error context, terminal outcome, and performance metrics without secret or raw provider-content exposure.
**Git Delivery:** PASS — C19 implementation commit `8397c3e4b11ac335e2a8fcd916c8e5e7fc1c5d77` was pushed on `card/v1-c19-observability-audit` and fast-forward integrated into canonical `main`.


# V1-C20 — Golden Case

**Status:** COMPLETE
**Dependencies:** V1-C07 through V1-C19
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Real Case/Ground Truth | `evaluations/fixtures/c20_capgemini_invent_arash_afsarian_v1.json` | Official Capgemini source review; `test_golden_case.py` | PASS | Versioned evaluation-only fixture: 20/20 manually reviewed, official-source-backed GT items; no fixture import or input path exists in C18 runtime composition. |
| Evaluation isolation and reconstruction | `src/strategic_intelligence/evaluation/golden_case.py`; `application/workflow_application.py` | Deterministic C05→C18→C03/C11/C13/C15/C16/C19 composition and close/reopen test | PASS | Post-run-only, human-mapped Claim comparison; no lexical answer-key matching. Application-owned snapshot reconstructs persisted Case/run/Source/Evidence/Claim/Verification/Governance/audit truth. |
| Brave public-web provider | `providers/brave.py`; `providers/factory.py`; `config.py` | Typed C05 adapter/factory/error/redaction tests; real C05-provider probe | PASS | Brave Web Search is selected only by `SEARCH_PROVIDER=brave` and reads its credential only from the environment-only `BRAVE_SEARCH_API_KEY` value. It uses the C14 request boundary, preserves typed results, has bounded timeouts, and maps authentication, rate-limit, timeout/network, malformed-response, and generic failures without returning a failure as empty results. The real query `Arash Afsarian Capgemini` returned 5 normalized results in 1.011 seconds, including `www.capgemini.com`; no credential was recorded in C20 runtime truth. |
| Entity accuracy | Final run `bb68d5b2-adda-4f68-a34f-da484f73931f` | `WorkflowApplication` → C18 → C20 reviewed evaluation | PASS | The final completed run established the selected Capgemini Invent / Arash Afsarian professional-meeting context; prior failed runs remain preserved below as historical measurements. |
| Research recall/coverage | `evaluation/golden_case.py` | Explicit reviewed `FOUND`/`PARTIAL`/`NOT_FOUND`/`CONTRADICTED` mapping over verified GT only | PASS | Post-run manual GroundTruthMatch review found 12 of 20 verified facts (60.0%); coverage was not inferred from keyword overlap. |
| Governance/traceability | `evaluation/golden_case.py` | Final persisted/reloaded Golden Case trace and C15→C16 revalidation | PASS | Source→Evidence→Claim, current C11/C13 outcomes, BLOCK exclusion, RESTRICT qualification, and Brief provenance remained traceable after reload. |
| Strategic insight/usefulness | `MeetingValueReview`; C16/C17 meeting-ready projection | Regenerated Full Brief from persisted accepted C15 analysis; explicit offline human-review model | PASS | Five bounded, traceable non-FACT meeting takeaways appear ahead of unchanged detailed canonical FACT evidence. The offline review scored relevance 4, company understanding 4, executive understanding 3, strategic opportunities 4, meeting questions 4, clarity 4, and traceability 5. |
| Performance/baseline comparison | C19 `AuditReport` through `WorkflowApplication.golden_case_snapshot` | Final real persisted/reloaded Golden Case trace | PASS | Final run: 51,369 ms total, 20 provider calls, 0 retries, 0 errors, 8 accepted checkpoints, and 84 events. Close/reopen reconstructed the terminal audit record. |

**Baseline Before:** C19 integrated baseline: 174 tests passing.
**Candidate After:** Final C20 closure: focused C16/C17 meeting-ready projection tests passed, the full suite passed at 307 tests, and compile/import, `pip check`, and diff checks passed. The final Golden Case completed through C18/C15/C16 with a separately reviewed 12/20 (60.0%) Ground Truth result and PASS MeetingValueReview.
**Regression Decision:** PASS for deterministic C20 surfaces, public-web adapter parsing/error transparency, C15/C16 provenance/currentness/restriction preservation, bounded Brave-provider composition, and meeting-ready C16/C17 presentation.
**Known Issues / Blockers:** BLOCKING — the real Golden Case planning timeout was resolved within existing C04/C06 boundaries: schema-constrained, non-reasoning structured generation and explicit typed approved-category guidance complete the isolated planning request in about 2.3 seconds. The original DuckDuckGo run `6b298ad4-7b19-4afa-af04-10d3446fd861` reached 13 C07/C08 search calls and correctly returned `PARTIAL / INSUFFICIENT_EVIDENCE` with 0 Sources, Evidence, Claims, Verification/Governance outcomes, and Briefs; its persisted reload preserved the same trace. Root-cause inspection found the former DuckDuckGo adapter used the Instant Answer endpoint rather than public-web results; C04 now uses the public HTML endpoint through the same C14 URL boundary and parses bounded title/URL/snippet results. Four representative public queries receive HTTP 202 and are surfaced as retryable `PROVIDER_RATE_LIMITED`, not silently converted to empty results. The environment-supplied Brave key enabled a real C05 probe and the real run `0f10b6b3-d57e-4a2d-a90f-2bcdac02342d`: it retrieved 131 Sources/Evidence records and produced 27 Claims, but C11 judged all 27 as `INSUFFICIENT_EVIDENCE` and C13 retained all 27 as `RESTRICT`. The 27-way diagnostic was exact: 24 were fidelity-supported with `OTHER` quality plus `UNKNOWN` freshness, and 3 were fidelity-supported with `PRIMARY` quality plus `UNKNOWN` freshness; none had a fidelity, ClaimEvidenceLink, contradiction, or C11 matching defect. The explicitly authorized repair adds bounded public HTML acquisition at C07/C08 through the existing C14 network boundary, preserves discovery provenance and distinguishes `PUBLIC_PAGE` content from snippets, extracts only deterministic metadata dates, and records content-minimized retrieval observations in C19. A real Brave-discovered `www.capgemini.com` probe retrieved 21,713 normalized characters with a machine-readable date. The form/control-text normalization repair eliminated the two C13 `PRIVACY_BOUNDARY` BLOCKs that occurred when whole public pages included contact-form text; C13 remains unchanged. In run `10265924-0f03-4cf0-abc7-2923fee1b5b0`, C15 received five PASS Claims and one visible RESTRICT gap but rejected `qwen3.5:4b` structured output whose `case_id` did not exactly equal the controlled Case ID. The subsequent C15 repair removed application-owned IDs and C13-derived metadata from the model schema, then bound them deterministically after semantic parsing. A real local C15 probe then exposed omitted `related_claim_ids`; the narrow hybrid-provenance repair requires every model-generated item to select one or more IDs from the C13-governed Case-scoped allow-list. C15’s canonical FACT contract permits only formatting-equivalent reuse of one eligible PASS FACT Claim, so the prompt now explicitly requires verbatim Claim text for FACT. The selected `gemma4:12b` model passed the identical real C15 reliability probe 3/3, but the one authorized real Golden Case run `51d7f16d-7a65-4f5e-b26b-e251562c4ec2` still reached C15 after 4 VERIFIED/PASS and 2 INSUFFICIENT_EVIDENCE/RESTRICT Claims, then produced no accepted analysis. The provider call itself succeeded; C19 deliberately does not retain raw provider output, so the original failure's exact semantic content is unavailable. One authorized C15-only reproduction against the same persisted Case/context identified the first rejection as `INVALID_REFERENCE`: a model-generated `RECOMMENDATION` in `project_meaning` referenced invented Claim IDs outside C15's five-Claim governed allow-list. `_validate_claim_references` rejected it before FACT fidelity validation; no provenance or trust rule was broadened. The real context was materially more complex than the benchmark (five supplied Claims, including one RESTRICT Claim, two required gaps, and a 24,555-character prompt versus three short PASS Claims and no gaps). C15 did not synthesize, guess, or broaden provenance or factual content; C18 therefore ended `PARTIAL / INSUFFICIENT_EVIDENCE` before C16 Brief generation. This is a selected-model production semantic/reliability failure and an under-stressed benchmark, not an excuse to weaken C15's fixed trust boundary. No Ground Truth was supplied to any runtime stage.
**C15 Provenance Model-Boundary Repair:** PASS — root issue `MODEL_BOUNDARY_DESIGN_DEFECT`: opaque persisted Claim IDs were removed from the C15 model-output responsibility and replaced only at that transient boundary by deterministic bounded `CLAIM_n` aliases. The current invocation schema permits only its aliases; unknown, malformed, out-of-context, and persisted-ID references fail closed. The application maps aliases to original C13-governed persisted Claim IDs before external `StrategicAnalysis` construction and existing FACT validation. At repair closure, no benchmark or Golden Case was rerun; C11/C13 semantics and historical C20 benchmark evidence remained unchanged.
**Post-Repair Gemini Representative Benchmark:** NOT ELIGIBLE — the exact persisted real Golden Case C15 Case/context/budgets, including its governed PASS/RESTRICT Claims and required gaps, was exercised through the repaired production C15 alias prompt/schema/validation path with `gemini-3-flash-preview`; Ground Truth was not supplied. Of five independent outbound attempts, runs 1–3 were `ACCEPTED` in 9,244 ms, 14,355 ms, and 20,822 ms. Run 4 was rejected at normalized structured-output handling in 2,240 ms; no raw response was retained. Run 5 exceeded the desktop terminal collection window without yielding an application result or retained model output. The result is therefore 3 accepted of 5 attempted, below the 4/5 eligibility threshold; the Golden Case was not rerun. The pre-repair result remains 0/5 accepted with invented persisted Claim IDs. No accepted post-repair output trusted a model-produced persisted Claim ID: accepted outputs contained only application-mapped persisted provenance. The former failure mode was not observed in the completed post-repair results, but cannot be claimed eliminated across the unobserved fifth result. Credentials and raw responses were not persisted.
**Repaired-Harness Fresh Gemini Representative Benchmark:** C20-ELIGIBLE — five fresh independent calls used the same persisted real Golden Case C15 Case/context/budgets, governed PASS/RESTRICT Claims, required gaps, and semantic task through the current invocation-scoped `CLAIM_n` alias prompt/schema/validation path with `gemini-3-flash-preview`; Ground Truth was not supplied. Runs 1–5 were all `ACCEPTED` in 11,441 ms, 11,578 ms, 26,733 ms, 9,602 ms, and 23,594 ms respectively. Durable diagnostics recorded request start/completion, structured parsing acceptance, and normal production C15 validation acceptance for every run: accepted 5, model/validation rejected 0, infrastructure/unknown 0, meeting the 4/5 threshold. Aliases remained transient; every accepted external `StrategicAnalysis` contained only application-mapped persisted Claim IDs, unknown aliases remained fail-closed, exact FACT fidelity, Case scope, BLOCK exclusion, and C13-only Governance authority were preserved, and no fuzzy provenance repair or Ground Truth contamination occurred. Credentials and raw responses were not persisted. This establishes the Gemini model as a C20 Golden Case candidate; the full Golden Case itself remains unrun under this benchmark-only authorization.
**Full Gemini Golden Case Execution:** BLOCKED — the authorized measured `WorkflowApplication` → C18 run `f3adbb11-8ff7-4b80-a3cf-6a25150ab9a3` used `gemini-3-flash-preview`, the Capgemini Invent / Arash Afsarian meeting goal, existing Brave/C14 public-source composition, and no Ground Truth runtime input. It failed closed in 302 ms at `CASE_VALIDATED`: the first structured research-planning call produced the existing typed C04 `PROVIDER_UNAVAILABLE` observation (291 ms), so C18 recorded `WORKFLOW_FAILED` without a research plan, search/retrieval attempt, Source, Evidence, Claim, Verification, Governance, C15 analysis, or C16 Brief. C19 persisted 6 audit events (1 provider call, 1 error, 1 checkpoint, 0 retries) and the persisted run/audit report reloaded correctly. No raw provider response, exception detail, credential, or Ground Truth was retained. C20 Ground Truth coverage, contradiction review, meeting-value review, and Critical Path completion were therefore not reached; this execution does not alter the prior independent C15 model-eligibility result.
**Official Gemini C04 Integration Repair:** PASS — the diagnosis confirmed that checked-in production composition supported only Ollama/fake LLMs, so the blocked run depended on an external temporary adapter. `GeminiAdapter` now implements the existing C04 text and schema-driven structured-output contract behind the C14 external-request boundary; explicit `LLM_PROVIDER=gemini` routing requires `CLOUD_PROVIDERS_ENABLED=true` and reads `GEMINI_API_KEY` only from the process environment, never from `~/.codex/.env`. Missing credentials, auth, rate limit, service, network, timeout, malformed-envelope, and structured-output failures are typed and credential-safe. The normal `WorkflowApplication.from_settings` composition can now construct Gemini without a temporary adapter. Mocked C04/C06/C14/C15/C18 composition tests and the full suite (212 passed) preserve C11/C13 authority, transient aliases, exact FACT fidelity, Case scope, BLOCK exclusion, C16 provenance, and fail-closed behavior. No Golden Case rerun occurred; C20 remains BLOCKED pending separately authorized measurement.
**Fresh Golden Case Rerun with Official Gemini Provider:** BLOCKED — the authorized run `44c7e0d0-a1d1-4898-89c2-c538fd856693` verified normal `WorkflowApplication.from_environment()` factory composition of `strategic_intelligence.providers.gemini.GeminiAdapter` with `LLM_PROVIDER=gemini` and `LLM_MODEL=gemini-3-flash-preview`; no temporary provider injection occurred. It nevertheless failed closed in 297 ms at `CASE_VALIDATED`: the first structured Research Planning call recorded typed retryable `RATE_LIMITED` after 285 ms. C18 therefore recorded `FAILED / WORKFLOW_FAILED` before a research plan, search/retrieval, Sources, Evidence, Claims, C11/C13 outcomes, C15 analysis, or C16 Brief. C19 retained 6 events (1 provider call, 1 error, 1 checkpoint, 0 retries) and persisted audit reconstruction passed after reopen. Ground Truth was isolated from runtime and no raw provider response, credential, or exception detail was retained. C20 evaluation, meeting value, and Critical Path completion were not reached. This fresh measurement preserves the provider-repair validation but confirms an unresolved production runtime/provider failure that requires separate diagnosis; no retry or repair was performed.
**One Authorized Backoff Golden Case Rerun:** BLOCKED — the single fresh production-factory run `7309c698-3087-4f40-bc84-c462d5dc48cb` used the official `strategic_intelligence.providers.gemini.GeminiAdapter` with `gemini-3-flash-preview`, no temporary injection, and no Ground Truth runtime input. Planning succeeded; C18 completed bounded public search/retrieval (15 search calls, 8 retained Sources/Evidence records), created 6 Claims, C11 returned 4 `VERIFIED` and 2 `INSUFFICIENT_EVIDENCE`, C12 executed bounded follow-up for unresolved Claims, and C13 returned 4 `PASS` and 2 `RESTRICT` decisions. At `GOVERNANCE_COMPLETED`, the first C15 structured Gemini call received typed retryable `RATE_LIMITED` after 335 ms; existing stage-specific retry policy did not retry C15, so C18 correctly ended `PARTIAL / INSUFFICIENT_EVIDENCE` before C16 Brief generation. C19 recorded 75 events, 17 provider calls, 6 checkpoints, 1 error, and 0 retries over 30,705 ms; close/reopen preserved the run and audit trace. C20 evaluation, Brief/meeting-value review, and Exit Gate completion were not reached. Provenance, Case scope, C11/C13 authority, PASS/RESTRICT semantics, and fail-closed behavior remained intact; no retry, repair, or additional run was performed.
**Paid Tier 1 Golden Case Execution:** BLOCKED — the one authorized fresh run `e1d058f6-9e73-4e1f-bff4-7f1b0c0d5462` used normal production-factory `strategic_intelligence.providers.gemini.GeminiAdapter` with `gemini-3-flash-preview`, no temporary injection, and no Ground Truth runtime input. It completed planning, bounded search/retrieval (15 search calls, 29 successful retrieval observations, 8 retained Sources/Evidence records), 6 Claims, C11 (4 `VERIFIED`, 2 `INSUFFICIENT_EVIDENCE`), bounded C12 follow-up, and C13 (4 `PASS`, 2 `RESTRICT`). Both C15 structured calls succeeded (initial analysis and currentness re-establishment), and the analysis checkpoint was accepted. C16 then rejected the governed analysis; C18 recorded typed `FAILED / WORKFLOW_FAILED` at `ANALYSIS_COMPLETED` with the safe reason `Brief generation rejected the governed analysis`. C19 persisted 77 events, 18 provider calls, 7 checkpoints, 1 error, 0 retries, and 54,191 ms total duration; close/reopen preserved the run/audit record. No Brief, C20 evaluation, meeting-value review, or Exit Gate completion was reached. Trust controls remained fail closed; no repair or additional run was performed.
**C15→C16 Restriction-Metadata Handoff Repair:** PASS — read-only diagnosis of Paid Tier run `e1d058f6-9e73-4e1f-bff4-7f1b0c0d5462` recovered C16 `INVALID_PROVENANCE`: `brief removes required C15 restriction metadata`. C16 correctly rejected a model-generated C15 `knowledge_gaps` INFERENCE linked to a C13 `RESTRICT` / `UNVERIFIED_FACT` Claim while carrying no restriction state. C15 now deterministically qualifies every model-generated knowledge gap from its governed C13 context before returning accepted analysis; PASS-only references remain unqualified, multiple restricted references use the existing deterministic reason-code helper, and model-provided metadata remains non-authoritative. Focused C13→C15→C16 positive composition and C16 stripped-metadata negative proof pass; full suite: 213 passed. The Paid Tier run remains BLOCKED, no Golden Case rerun occurred, and the C20 Exit Gate remains BLOCKED pending separately authorized measurement.
**Post-Restriction-Handoff Golden Case Run:** BLOCKED — exactly one fresh production-factory run `0d7fbbe4-0959-4722-a3cb-c785ef1e5cd1` used checked-in `GeminiAdapter` / `gemini-3-flash-preview`, Brave public search, and no Ground Truth runtime input. Planning completed; 15 search calls and 29 successful retrieval observations produced 6 Sources/Evidence records and 6 Claims; C11 produced 4 `VERIFIED` and 2 `INSUFFICIENT_EVIDENCE`, C12 ran bounded follow-up, and C13 produced 4 `PASS` and 2 `RESTRICT` outcomes. The initial C15 structured call succeeded and its analysis checkpoint was accepted. The currentness re-establishment C15 provider call also succeeded but C15 returned its existing typed fail-closed `INSUFFICIENT_EVIDENCE` outcome, so C18 ended `PARTIAL / INSUFFICIENT_EVIDENCE` at `ANALYSIS_COMPLETED` with safe reason `current governed analysis could not be re-established`; C16, C20 evaluation, Briefs, coverage, and meeting-value review were not reached. C19 persisted 77 events, 18 provider calls, 7 checkpoints, 1 error, 0 retries, and 80,512 ms total duration. The content-minimized audit does not retain the rejected semantic C15 output, so its exact validation condition is unavailable. No model-generated RESTRICT-linked knowledge gap reached C16 in this run; the new deterministic handoff behavior was not contradicted. No rerun or repair was performed; C20 remains BLOCKED.
**C15 Deterministic Currentness Repair:** PASS — diagnosis confirmed that C18 had conflated rebuilding transient governed context with a second stochastic C15 synthesis before C16. C15 now owns deterministic revalidation of the checkpointed accepted `StrategicAnalysis`: it rebuilds current C11/C13-governed context at the fixed `as_of`, validates Case scope, Claim provenance, Governance fingerprint/currentness, BLOCK exclusion, RESTRICT metadata, required gaps, and exact FACT fidelity, then returns the same accepted analysis without a provider call. C18 invokes that C15 boundary before C16; C11/C13/C16, persistence, and provider behavior are unchanged. Focused C15/C16/C18 tests (59), C11/C13 tests (21), and the full suite (217) passed with no external Golden Case rerun. C20 remains BLOCKED pending separately authorized measured execution.
**Post-Currentness-Repair Golden Case Execution:** BLOCKED — exactly one fresh production-factory Tier 1 Gemini run `e6cd7563-24f5-498c-ae04-e0e8dad4e586` used checked-in `GeminiAdapter` / `gemini-3-flash-preview`, Brave public search, no temporary provider injection, and no Ground Truth runtime input. Planning completed; 15 search calls and 27 successful retrieval observations produced 6 Sources/Evidence records and 6 Claims; C11 produced 4 `VERIFIED` and 2 `INSUFFICIENT_EVIDENCE`, bounded C12 follow-up ran, and C13 produced 4 `PASS` and 2 `RESTRICT` outcomes. The single C15 semantic provider call succeeded in 12,846 ms, produced an accepted persisted `StrategicAnalysis`, and the `ANALYSIS_COMPLETED` checkpoint was accepted. The deterministic pre-C16 C15 currentness operation made no provider call but returned a typed rejected result, so C18 correctly ended `PARTIAL / INSUFFICIENT_EVIDENCE` before C16, Brief generation, or C20 evaluation. The persisted run contains 74 audit events, 17 provider calls, 0 retries, 1 error, and 7 accepted checkpoints; its final snapshot retains the accepted analysis and reload truth was not reached because the external runner was interrupted after the measured terminal result. No retry, repair, or additional Golden Case execution was performed. C20 remains BLOCKED.
**C15 Provenance-Symmetry Repair:** PASS — the target run exposed a final-output validation asymmetry, not a C11/C13 state change: C15 had injected a required gap for a current RESTRICT Claim outside the bounded model-facing Claim set, then deterministic revalidation rejected that C15-owned persisted provenance. `TrustedStrategicContext` now distinguishes bounded `model_claims` (the only Claims assigned transient aliases or exposed to the model) from authoritative final-use `claims` (which also contains C15-required current RESTRICT Claims). Initial model-output validation and qualification use `model_claims`; deterministic revalidation and unchanged C16 use authoritative `claims`. Structural regression covers the exact six-Claim/five-model-budget/two-required-RESTRICT shape, the observed over-budget multi-RESTRICT shape, below/at/above budget boundaries, multiple hidden required restrictions, model hidden-Claim rejection, BLOCK exclusion, governance-transition fail-close, currentness/reload, C15→C16 composition, and one semantic provider call with zero currentness calls. Focused C15/C16/C18/C11/C13 regression (87) and full suite (224) passed. Targeted C15 sibling-asymmetry inspection found no additional concrete instance: items, gaps, opportunities, questions, FACT/INFERENCE/RECOMMENDATION, alias mapping, and persisted provenance now use the correct owner-specific set. No Golden Case rerun occurred; C20 remains BLOCKED pending separately authorized measurement.
**Final Post-Symmetry Golden Case Execution:** BLOCKED — exactly one fresh production-factory run `a6ebfd3a-397f-4ed2-b242-c1e7ceca1212` used checked-in `WorkflowApplication.from_settings(...)`, factory-composed `strategic_intelligence.providers.gemini.GeminiAdapter`, `gemini-3-flash-preview`, Brave public search, and no temporary provider injection or Ground Truth runtime input. Planning completed; 15 search calls and 27 successful public retrieval observations produced 7 Sources/Evidence records and 5 Claims. C11 returned 3 `VERIFIED` and 2 `INSUFFICIENT_EVIDENCE`; C12 ran bounded follow-up; C13 returned 3 `PASS` and 2 `RESTRICT`. The single C15 semantic provider call succeeded in 14,074 ms and produced a persisted accepted StrategicAnalysis with three knowledge gaps; no second C15 provider call occurred. C18 then recorded safe typed `FAILED / WORKFLOW_FAILED` at `ANALYSIS_COMPLETED` with `Brief generation rejected the governed analysis`; C16 therefore did not produce a Brief. The persisted audit contains 74 events, 17 provider calls, 0 retries, 1 error, and 7 accepted checkpoints over 42,041 ms; close/reopen reconstructed the same terminal audit truth. C20 evaluation, coverage, meeting-value review, closure validation, and Exit Gate completion were not reached. No repair or additional execution was performed; C20 remains BLOCKED.
**C16 Handoff-Symmetry Repair:** PASS — diagnosis recovered the first primary-run C16 rejection: C15 had legally qualified a mixed PASS/RESTRICT Opportunity, but C16’s `_all_items()` rebuilt it as a synthetic `AnalysisItem` without `is_restricted` or authoritative C13 reason codes, then rejected its own lossy projection as unqualified RESTRICT material. C16 now uses canonical nested-item projections that preserve Claim provenance, restriction status, reason codes, and qualification for Opportunities and Smart Questions. The same audit found a sibling FACT formatting asymmetry: C15’s NFKC/case/whitespace equivalence is now exposed as the shared canonical normalizer used by C16, without semantic broadening. C15/C16 currentness composition proves mixed PASS/RESTRICT Opportunities and Smart Questions, multiple authoritative restriction reasons, persistence/reload, exact NFKC FACT parity, and valid Brief construction; stripped, wrong-reason, BLOCK, wrong-Case, unknown, and missing-provenance nested inputs still fail closed. Focused C15/C16/C18/C11/C13/persistence regression (101) and full suite (229) passed. No Golden Case rerun occurred; C20 remains BLOCKED pending separately authorized measurement.
**Post-C16-Handoff-Symmetry Golden Case Execution:** BLOCKED — exactly one authorized fresh production-factory Tier 1 Gemini run `4e2e6706-b794-412d-bfeb-fce4b965e51f` used `WorkflowApplication.from_settings(...)`, factory-composed `strategic_intelligence.providers.gemini.GeminiAdapter`, `gemini-3-flash-preview`, Brave public search, and no temporary provider injection or Ground Truth runtime input. The complete run produced a research plan, 15 search calls, 27 retrieval attempts, 7 retained Sources/Evidence records, and 5 Claims; C11 returned 3 `VERIFIED` and 2 `INSUFFICIENT_EVIDENCE`, C12 ran bounded follow-up, and C13 returned 3 `PASS` and 2 `RESTRICT` outcomes. One C15 semantic provider call (13,164 ms) produced an accepted analysis; deterministic currentness revalidation required no provider call, and C16 produced both Quick and Full Briefs with the mixed PASS/RESTRICT Opportunity and Smart Question metadata preserved. The C18 terminal state was `COMPLETED`. C19 persisted 74 events, 17 provider calls, 0 retries, 0 errors, 8 accepted checkpoints, and 41,551 ms total duration; close/reopen reconstructed the same terminal audit record. Only after that finalized Brief did the canonical isolated C20 evaluator read the independent version `1.0.0` Ground Truth. It found `0/20` verified facts (`NOT_FOUND` for every item; 0.0% coverage), while Source→Evidence→Claim, Verification, Governance, and mandatory technical trust-invariant traces passed. The evaluator’s explicit human usefulness review remained `MANUAL_REVIEW_REQUIRED`; the measured Brief does not demonstrate real meeting-preparation value because its retained factual output is page-title/snippet material and the executive material is restricted/mismatched. Therefore C20's Exit Gate remains BLOCKED. This run is preserved as measured evidence; no Ground Truth-guided retry, repair, or additional Golden Case execution occurred. Closure validation after evaluation passed: focused C20/C15/C16/C18/C19 composition 81, full suite 229, `pip check`, compile/import, and diff checks.
**C07/C08 Research Coverage Repair:** PASS — the measured 0/20 diagnosis located first loss at generic source discovery: repeated canonical URLs and successful-but-title/boilerplate retrievals occupied bounded retention capacity before Evidence. C07/C08 now apply deterministic case/run-scoped canonical URL and exact normalized-content exclusion through C18's existing sequential research path, and use a source-usability gate after C14-protected acquisition but before a retained-source slot is consumed. The gate rejects title-only, near-empty, consent/challenge boilerplate shells; it is not C10 quality/freshness scoring or C11 verification. Within the existing bounded ranked result list, weak/duplicate candidates backfill deterministically until the unchanged retained-source budget is met or the configured candidate cap is exhausted. Generic existing company-domain priority is preserved; C06 query generation, C19 event contracts, C09 Claim representation, and all C10/C11/C13/C15/C16 authority remain unchanged. Deterministic regression reproduces cross-task URL reuse, harmless URL canonicalization without collapsing query-distinct resources, title-only and cookie-shell rejection, exact duplicate content under different URLs, substantive retention, bounded candidate exhaustion, and C18 case/run isolation. Focused C06/C07/C08/C09/C10/C11/C13/C14/C18/C19 regression: 108 passed; full suite: 235 passed; `pip check`, compile/import, and diff checks passed. No Golden Case rerun occurred, Ground Truth remains absent from production selection logic, and external research-tool candidates remain deferred pending a separately authorized measurement.
**Post-C07/C08-Coverage Golden Case Execution:** BLOCKED — exactly one authorized production-factory run `0d0c2344-52bf-4209-9d6c-b9bc69c9865d` used `WorkflowApplication.from_settings(Settings.from_environment())`, factory-composed `strategic_intelligence.providers.gemini.GeminiAdapter` with `gemini-3-flash-preview`, Brave public search, and no temporary provider injection or Ground Truth runtime input. C18 completed the full pipeline and persisted/reloaded its Case/run/C19 trace: 18 search calls, 5 retained public-page Sources, 6 Evidence records, 5 Claims, 5 C11 `INSUFFICIENT_EVIDENCE` results, 5 C13 `RESTRICT` outcomes, accepted C15 analysis, deterministic provider-free currentness revalidation, and accepted C16 Quick/Full Briefs. C19 retained 99 events, 20 provider calls, 0 retries, 0 errors, 8 accepted checkpoints, and 73,934 ms total duration. Candidate URL, duplicate-skip, content-skip, and exact official-page retrieval counts remain unavailable because the current content-minimized C19 event contract records retrieval domain/outcome, not candidate URLs or source-selection reasons; no count was inferred. Post-run-only comparison found none of the four canonical official GT URLs among persisted Sources and no GT proposition in persisted Claims/Evidence; manual mapping was 20 `NOT_FOUND`, 0 `FOUND`, 0 `PARTIAL`, 0 `CONTRADICTED`, and 0.0% coverage. Traceability, Verification/Governance trace, C13-only restriction preservation, C15 alias/currentness/provenance, C16 restriction/provenance, and Ground Truth isolation passed. The C07/C08 repair did not improve measured source or proposition recall on this one execution; the narrow next bottleneck is `SOURCE_DISCOVERY_STILL_PRIMARY`, with no repair or rerun authorized or performed. Closure validation passed: focused 137, full suite 235, `pip check`, compile/import, and diff checks. C20 remains BLOCKED because the Golden Case does not demonstrate meeting-preparation value.
**Brave Discovery Benchmark Harness:** PASS — C20 now has an evaluation-only, no-live-call harness for frozen C06 task inputs. It represents Control (`count=5`), V1 result-depth (`count=10`), V2 pagination (`count=5`, offsets `0,1`), and V3 first-party-priority variants. Control/V1 execute only through the existing C04 `SearchProvider` and C07/C08/C14 acquisition/suitability path. V2 deliberately reports `NOT_EXECUTABLE_WITH_CURRENT_CONTRACT` because the current typed C04 query cannot express an offset, with no direct-HTTP bypass. V3 requires a pre-existing normal Case `company_website`, otherwise reports `INELIGIBLE_NO_RUNTIME_DOMAIN`; no Ground-Truth-derived domain is accepted. Reports retain only hashes and bounded candidate/acquisition/suitability outcomes, never page bodies or credentials. Discovery does not import the Golden Case fixture/evaluator; only an already-frozen report can receive post-freeze target hashes for scoring. Bounds, input parity, zero-denominator normalization, predeclared `NO_IMPROVEMENT`/`MARGINAL`/`MEANINGFUL`/`STRONG` classification, provider-boundary use, and no Verification/Governance authority are deterministically tested. No live Brave benchmark, Golden Case execution, production change, or production repair was authorized or performed. Benchmark tests plus relevant C04/C06/C07/C08/C14/C20 regression: 88 passed; full suite: 243 passed; `pip check`, compile/import, and diff checks passed. C20 remains BLOCKED pending separately authorized benchmark execution and measured evaluation.
**One Live Brave Discovery Benchmark:** COMPLETE — one frozen C06 plan of 13 task/query inputs (fingerprint `2228d57dcea3a1b7953763bbfc95387bfab31f140a0a3d7d81e86d1aa12ae1c8`) was generated once through the normal deterministic C06 path, then Control and V1 were measured through the checked-in C04 Brave adapter and C07/C08/C14 boundaries before any Ground Truth access. Both reports were frozen and content-minimized before post-freeze scoring; no query rewrite, tuning, live Golden Case, or downstream Evidence/Claim/Verification/Governance execution occurred. Control (`count=5`) made 13 Brave calls, requested/received 65 results, inspected 65 candidates (32 unique canonical URL hashes, 33 duplicate observations), attempted 41 acquisitions (40 success, 1 failure), classified 39 title-only, retained one unique Source, and took 45,979 ms. It discovered/persisted 0/4 exact official GT pages and had 0 proposition-source hits. V1 (`count=10`) made the same 13 calls, requested/received 130 results, inspected 130 candidates (68 unique hashes, 62 duplicates), attempted 81 acquisitions (79 success, 2 failures), classified 76 title-only, retained three unique Sources, and took 58,916 ms. V1 discovered one exact official GT page but did not retain it, persisted 0/4, and had 0 proposition-source hits. The predeclared comparison is `MARGINAL`: more authoritative discovery but no retained official page or proposition-source recall gain; API calls remained equal, while latency increased 12,937 ms. V2 remained `NOT_EXECUTABLE_WITH_CURRENT_CONTRACT` with no direct HTTP bypass. V3 was `INELIGIBLE_NO_RUNTIME_DOMAIN` because the fixed normal benchmark Case contained no independently supplied `company_website`; no domain was inferred. Frozen reports use only hashes/bounded metadata, no page bodies or credentials. This is one measured benchmark, not authorization for a Brave repair, tuning, pagination, or a Golden Case rerun. C20 remains BLOCKED pending the next separately authorized Layer-A discovery decision.
**Corrected One-Page Kitesurf Retrieval Benchmark:** COMPLETE — the prior Kitesurf measurement attempt is retained as invalid because its temporary runner passed Cloudflare Browser Run's JSON `/content` envelope to the HTML parser instead of first extracting `result`; no repository code or evidence was changed for that invalid attempt. Exactly one corrected Control and one Kitesurf request then used the already-frozen discovered Capgemini page hash `8813d3ee6c7aa981eaa0b41b2b76b10804616f0784b2bdde472b9d3a568f1963`, before Ground Truth access. Control through C14 `PublicSourceRetriever` succeeded with HTTP 200, 276,253 bytes, 63 usable characters / 11 words / 15 substantive characters, and `TITLE_ONLY` in 380 ms. Kitesurf `/content?browser=kitesurf` also succeeded with HTTP 200; strict envelope validation recovered a string `result` payload of 279,667 rendered-HTML characters from a 303,247-byte JSON envelope. Deterministic extraction produced exactly the same 63 usable characters / 11 words / 15 substantive characters and `TITLE_ONLY` (fingerprint identical to Control), in 5,767 ms. Both frozen outputs preceded post-freeze scoring; the four target-page GT propositions were 0 fully supported, 0 partially supported, 4 not found for both outputs (0.0% source-content recall). Thus the fixed threshold produced `NO_MEANINGFUL_RETRIEVAL_GAIN`: no title-only-to-substantive transition, zero text/word/recall gain, and 5,387 ms additional latency. The benchmark used one public URL only, isolated credentials, no LinkedIn, no persisted repository page body, and created no trust, C10, C11, C13, Claim, or discovery-ranking authority. Benchmark security is acceptable, but C14 production integration remains unproven. Kitesurf integration design is not justified by this one-page measurement; no production repair, Golden Case rerun, or additional request was performed.
**Narrow HTML Parser-State Repair:** PASS — diagnosis of the same frozen public Capgemini page found that the extractor's ignored-depth counter treated the HTML void `<input>` element as an ignored container, incrementing without a matching end tag and suppressing later main content. `_PublicHtmlParser` now excludes standard void elements from ignored-container depth accounting while retaining suppression of actual nested ignored containers, scripts, styles, forms, and controls. Focused regressions cover ordinary and self-closing inputs, multiple inputs before later main content, and nested ignored `header`/`nav` plus `script`/`style` suppression (10 passed); C07/C08/C14 acquisition/discovery/coverage regression passed (23 passed). Exactly one authorized repaired-path C14 retrieval of the frozen target returned 276,253 bytes / 276,146 raw characters, extracted 3,915 characters / 580 words, ended with ignored depth 0, and classified `SUBSTANTIVE`; no Kitesurf call or Golden Case rerun occurred. Full suite: 246 passed; `pip check`, compile/import, and diff checks passed. The C20 Exit Gate remains BLOCKED pending demonstrated meeting-preparation value.
**Post-Parser-Repair Golden Case Rerun:** BLOCKED — exactly one fresh production-factory run `368ad4eb-0694-4460-ba5f-a3af665e3c2d` used the checked-in C04 `GeminiAdapter` (`gemini-3-flash-preview`), Brave Search, repaired C14 `PublicSourceRetriever`, and no Ground Truth runtime input. Runtime outputs were frozen before evaluation (fingerprint `fe6a6a7751f676ca25e8a5970d316db21fdf446d62d96e1ee1447495d`). The C06 plan had 13 tasks; C18 made 17 bounded search calls and inspected 85 returned results, then made 20 acquisition attempts (19 success, 1 unsupported-content failure). C19 does not retain candidate-level URL or suitability-rejection events, so target-page discovery and title-only rejection counts are not observable; the previously diagnosed `Data and AI foundations in strategy` URL was not retained/persisted and was not manually injected. The run persisted 11 unique public-page Sources (7 official Capgemini) and 18 Evidence records, yielding 11 FACT Claims. C11 produced 7 `VERIFIED` and 4 `INSUFFICIENT_EVIDENCE`; bounded C12 made 4 follow-up attempts; C13 produced 7 `PASS`, 3 `RESTRICT`, and 1 `BLOCK`. Source→Evidence→Claim, Verification, Governance, same-Case scope, BLOCK exclusion, and provenance checks passed without unsupported-FACT leakage. One C15 provider call occurred, but no accepted current governed analysis was available; deterministic currentness and C16 Quick/Full Brief generation were therefore not reached, and C18 correctly ended `PARTIAL / INSUFFICIENT_EVIDENCE` at `GOVERNANCE_COMPLETED`. C19 persisted 78 events, 19 provider calls, 0 retries, 1 error, 6 accepted checkpoints, and 103,883 ms total duration; close/reopen reconstruction passed. Only after freeze did the evaluator map 11 `FOUND`, 1 `PARTIAL`, 8 `NOT_FOUND`, and 0 `CONTRADICTED` independently verified Ground Truth items: 12/20, 60.0% coverage, versus the prior best 0/20. Traceability, Verification/Governance integrity, and mandatory technical trust invariants passed; Brief provenance is N/A and meeting usefulness remains `MANUAL_REVIEW_REQUIRED` because no Brief exists. This is material source/evidence/coverage improvement, but C20 remains BLOCKED: the next evidenced bottleneck is C15 accepted-analysis availability for the larger governed context, not parser extraction. No repair, Kitesurf call, Ground-Truth-guided retry, or additional Golden Case execution was performed. Closure validation passed: focused C20/C14/C15/C16/C18/C19 composition 91, full suite 246, `pip check`, compile/import, and diff checks.
**C15 Post-Provider Rejection Observability Repair:** PASS — the accepted-analysis diagnosis established that a C15 provider call could pass transport, structured schema parsing, and provider observation yet be rejected by deterministic alias binding or post-parse validation before C18 exposed only its generic `PARTIAL / INSUFFICIENT_EVIDENCE` result. C15 now emits one content-minimized C19 `C15_REJECTION` observation before that existing C18 terminal mapping, containing only a stable reason code and validator stage. Codes cover alias/duplicate reference, provenance, FACT fidelity, restriction, Opportunity, question, qualification, BLOCK-boundary, and fallback post-parse validation branches; no prompt, raw provider response, Claim, Evidence, Source, secret, or exception text is retained. The repair does not change a C15 acceptance gate, C13 Governance, C18 sequencing/recovery/terminal semantics, or C19 authority. Focused C13/C15/C16/C18/C19 composition passed (101 tests): a real C13→C15 duplicate-alias rejection persists the C15 event at `GOVERNANCE_COMPLETED`, reloads through C19, and leaves C18's typed generic partial result unchanged; accepted C15 output emits no rejection event, BLOCK exclusion and existing validators remain fail closed. Full suite: 258 passed; `pip check`, compile/import, and diff checks passed. No external provider call or Golden Case rerun occurred. C20 remains BLOCKED pending separately authorized measured execution.
**POST-OBSERVABILITY C15 MEASURED REPLAY:** COMPLETE — exactly one isolated C15 Gemini generation replayed the frozen governed state from historical run `368ad4eb-0694-4460-ba5f-a3af665e3c2d`; the source SQLite database was reopened read-only and copied before replay, with no Research, Search, Retrieval, C10/C11/C12/C13 activity, Claim/Governance mutation, C16 generation, Ground Truth access, or Golden Case rerun. The reconstructed current C15 contract retained 11 Claims, C13 `PASS=7`/`RESTRICT=3`/`BLOCK=1`, 8 authoritative permitted Claims, 5 model-visible Claims/transient aliases, and 3 hidden system-required restricted gaps (input fingerprint `56c1343da571dff2ffda26af276e50d134a62c68b868a19b24fa2a5cae650548`). Factory-composed `GeminiAdapter` (`gemini-3-flash-preview`) made one `generate_structured` call, succeeded at transport/schema parsing in 34,937 ms, then C15 rejected before acceptance. The isolated persisted C19 replay trace recorded exactly one safe `C15_REJECTION` event at `GOVERNANCE_COMPLETED` with `reason_code=C15_POST_PARSE_VALIDATION_FAILED` and `validator_stage=POST_PARSE_VALIDATION`; it contains no provider output, prompt, Claim/Evidence/Source content, credential, or exception text. This establishes `GENERIC_POST_PARSE_VALIDATION` as the measured failure family; the exact pre-existing validator message was intentionally not retained, so no narrower semantic branch may be claimed. C18 was not rerun; under its unchanged mapping this rejection would remain `PARTIAL / INSUFFICIENT_EVIDENCE`. The prior run's post-provider rejection is reproduced at the same controlled-input contract but model-output equivalence is not asserted. Focused C13/C15/C18/C19 regression passed (89 tests), along with `pip check`, compile/import, and diff checks. No production/test/dependency change was made by the measurement. C20 remains BLOCKED; no repair or additional provider call was performed.
**C15 Exact Post-Parse Rule Observability Repair:** PASS — the forensic audit established that the historical/replay rule inside `C15_POST_PARSE_VALIDATION_FAILED` remains unknown, while the model-facing prompt/schema mismatch remains independently proven. C15 now records one additional enum-only `post_parse_validator_rule` field only for its five formerly generic deterministic branches: section-item limit, Opportunity limit, MeetingQuestion limit, output-text limit, and no grounded contribution. The existing top-level reason, validator order, thresholds, prompt, provider schema, C13 authority, C18 `PARTIAL / INSUFFICIENT_EVIDENCE` mapping, and C19 observer-only role are unchanged. Provider-free tests exercise all five branches individually, prove accepted output emits no rejection event, and prove the persisted/reloaded C13 → C15 → C18 → C19 path retains only safe metadata. Focused C13/C15/C18/C19 regression: 97 passed; full suite: 269 passed; `pip check`, compile/import, and diff checks passed. No provider call, replay, Golden Case execution, Ground Truth access, or dependency change occurred. The next separately authorized measured replay can identify the exact future rejection rule without retaining output content; C20 remains BLOCKED.
**POST-EXACT-RULE-OBSERVABILITY C15 MEASURED REPLAY:** COMPLETE — exactly one authorized factory-composed `GeminiAdapter` (`gemini-3-flash-preview`) call replayed the frozen governed C15 input from source run `368ad4eb-0694-4460-ba5f-a3af665e3c2d`, without Research, C11/C12/C13, C16, Ground Truth, or Golden Case execution. The reconstructed contract exactly matched the prior replay fingerprint `56c1343da571dff2ffda26af276e50d134a62c68b868a19b24fa2a5cae650548`: 11 Claims, C13 `PASS=7`/`RESTRICT=3`/`BLOCK=1`, 8 authoritative permitted Claims, 5 model-visible aliases, and 3 hidden restricted system gaps. Gemini transport and schema parsing succeeded in 30,081 ms; alias mapping and domain reconstruction completed. C15 rejected at post-parse validation with the unchanged top-level `C15_POST_PARSE_VALIDATION_FAILED` plus the new safe enum `post_parse_validator_rule=C15_OUTPUT_TEXT_LIMIT_EXCEEDED`. No provider output, prompt, Claim/Evidence/Source text, credential, rejected value, or structural count/length was persisted; only the enum identifies the rule. No repair, model-contract change, retry, C18/C16 execution, or additional provider call occurred. Focused C13/C15/C18/C19 composition regression: 97 passed; `pip check`, compile/import, and diff checks passed. This proves the next repair decision must address the existing output-text limit contract mismatch; C20 remains BLOCKED pending separate authorization.
**C15 Output-Text Contract Alignment Repair:** PASS — the measured runtime rule was `C15_OUTPUT_TEXT_LIMIT_EXCEEDED`: Gemini returned schema-valid structured output that passed alias binding and domain reconstruction but exceeded C15’s existing deterministic 2,000-character output-field limit. C15 now uses that unchanged single threshold for the model-facing prompt and semantic Pydantic schema fields that the existing validator covers: analysis-item text/rationale; Opportunity title, description, goal relevance, confidence, and assumptions; and MeetingQuestion question/reason. The dynamic JSON schema consequently exposes `maxLength: 2000` for exactly those nine model-owned text paths; a provider-free Gemini adapter test proves it passes that schema unchanged as `responseJsonSchema`. The validator, thresholds, aliases, Claim-reference limits, item/Opportunity/question bounds, grounded-contribution rule, C13, C16, C18, and C19 semantics are unchanged. Provider-free tests prove exact boundary acceptance, one-over deterministic rejection plus the existing exact C15 reason mapping, prompt/schema/validator parity, and unrelated trust composition. Focused C13/C15/C18/C19/C04 regression: 130 passed; full suite: 272 passed; `pip check`, compile/import, and diff checks passed. No provider replay, Golden Case rerun, Ground Truth access, or dependency change occurred. C20 remains BLOCKED pending separately authorized measurement.
**POST-TEXT-CONTRACT-ALIGNMENT C15 MEASURED REPLAY:** COMPLETE — exactly one current factory-composed `GeminiAdapter` (`gemini-3-flash-preview`) generation replayed the frozen governed input from source run `368ad4eb-0694-4460-ba5f-a3af665e3c2d`. The reconstructed input fingerprint exactly matched `56c1343da571dff2ffda26af276e50d134a62c68b868a19b24fa2a5cae650548`; the unchanged 2,000-character validator, prompt instruction, and nine model-owned dynamic-schema `maxLength` fields were active. Gemini transport/schema parsing succeeded in 18,336 ms, but C15 rejected at its existing deterministic FACT-fidelity gate (`reason_code=C15_FACT_FIDELITY_FAILED`) before hidden RESTRICT reconciliation or currentness; it did not emit a generic post-parse validator-rule enum. Therefore the previously measured `C15_OUTPUT_TEXT_LIMIT_EXCEEDED` did not recur on this one stochastic replay, but acceptance is not established and no broader C15 reliability claim is made. No raw output, prompt, Claim/Evidence text, credential, or structural content was persisted; no C16, Golden Case, Ground Truth, repair, retry, or additional provider call occurred. C20 remains BLOCKED pending separately authorized review.
**C15 Exact Fidelity-Subrule Observability:** PASS — forensic review confirmed that the measured `C15_FACT_FIDELITY_FAILED` category intentionally aggregated five existing deterministic predicates while retaining no exact historical predicate: knowledge-gap FACT, FACT reference cardinality, unsupported FACT Claim, normalized-text mismatch, and recommendation-to-inference escalation. C15 now carries only a stable enum-only `c15_fidelity_failure_mode` through the existing C19 rejection event for each predicate, with `validator_stage=FACT_FIDELITY`; its top-level reason, rejection strings, prompt, schema, normalizer, alias/provenance mapping, C13/C16/C18 behavior, and all trust decisions remain unchanged. Provider-free tests exercise every subrule, valid formatting-equivalent FACT acceptance, and content minimization. A composed C13 → C15 → C18 → C19 test proves the persisted/reloaded exact enum leaves C18 at its existing `PARTIAL / INSUFFICIENT_EVIDENCE` result. Focused trust/workflow regression: 117 passed; full suite: 278 passed; `pip check`, compile/import, and diff checks passed. No external provider call, C15 replay, Golden Case rerun, Ground Truth access, or dependency change occurred. C20 remains BLOCKED; the next separately authorized occurrence can identify its exact C15 predicate without retaining content.
**POST-FIDELITY-SUBRULE-OBSERVABILITY C15 MEASURED REPLAY:** COMPLETE — exactly one factory-composed `GeminiAdapter` (`gemini-3-flash-preview`) generation was authorized against frozen governed input from source run `368ad4eb-0694-4460-ba5f-a3af665e3c2d`. The source was reopened and copied before replay; the reconstructed input exactly matched fingerprint `56c1343da571dff2ffda26af276e50d134a62c68b868a19b24fa2a5cae650548` with 11 Claims, C13 `PASS=7`/`RESTRICT=3`/`BLOCK=1`, 8 authoritative permitted Claims, 5 model-visible aliases, and 3 hidden restricted system gaps. The sole `generate_structured` call ended after 37,577 ms with the existing typed provider observation `STRUCTURED_OUTPUT_INVALID`; C15 schema parsing therefore did not complete, no alias restoration/domain reconstruction/validator/Fidelity subrule/currentness path was reached, and no `C15_REJECTION` event or `c15_fidelity_failure_mode` exists for this attempt. No raw provider output, prompt, Claim/Evidence/Source text, credential, or exception detail was persisted. This is a different existing C04/Gemini structured-output gate, not a FACT-fidelity failure; no repair, retry, C16, C18, Golden Case execution, Ground Truth access, or additional provider call occurred. Focused C13/C15/C18/C19 regression: 105 passed; `pip check`, compile/import, and diff checks passed. C20 remains BLOCKED pending separately authorized review.
**Diff Review:** PASS — C20 evaluation-only fixture/module/test and a small application-owned persisted snapshot surface, plus bounded generic C04 structured-output, public-web search parsing/error transparency, the C06 approved-category composition repair, a C05-compatible Brave adapter/configuration path, the isolated Brave discovery benchmark harness, and the narrow C15 transient-alias provenance and restriction-metadata handoff repairs with focused/composition test updates; no research, verification, governance, analysis, brief, retry, or checkpoint authority changed.
**Git Status Review:** PASS — no files staged; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside C20 scope.
**Final Golden Case Closure:** PASS — final measured run `bb68d5b2-adda-4f68-a34f-da484f73931f` completed with 12 Sources, 20 Evidence records, 12 Claims, C11 `VERIFIED=8` / `INSUFFICIENT_EVIDENCE=4`, and C13 `PASS=8` / `RESTRICT=3` / `BLOCK=1`. C15 and C16 both accepted the governed output. C20's independent post-run GroundTruthMatch review recorded 12/20 (60.0%) verified-fact coverage; all mandatory traceability and trust invariants passed. The hardened C15 path retains transient aliases, deterministic persisted-Claim mapping, exact FACT fidelity, currentness revalidation, and C13-derived RESTRICT qualification; C16 preserves that metadata and now deterministically projects up to five traceable non-FACT meeting takeaways before unchanged detailed canonical FACTs in C17. Regenerating the Full Brief offline from the persisted accepted C15 analysis required no provider/research replay and produced a PASS MeetingValueReview (4/4/3/4/4/4/5). C19 metrics persisted and reloaded cleanly. The Exit Gate is met: the Golden Case passes mandatory trust invariants and demonstrates real meeting-preparation value. Historical failed runs and repair evidence above are retained unchanged.
**Diff Review:** PASS — all current changes are C20 scope: evaluation-only Golden Case contracts, public-source/provider composition, content-minimized observability, C15/C16 trust-boundary hardening, and C16/C17 meeting-ready presentation; no protected untracked item is included.
**Git Status Review:** PASS — no files staged; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside C20 scope.
**Exit Gate Evidence:** PASS — the final Golden Case has independently reviewed 60.0% verified Ground Truth coverage, PASS mandatory trust invariants, and PASS meeting-preparation value while preserving C03/C11/C13/C15/C16/C18/C19 authority boundaries.
**Git Delivery:** PASS — C20 implementation commit `15f017c464a8298392fb6dda461dacf2bcd72ef8` was pushed on `card/v1-c20-golden-case`, fast-forward integrated into canonical `main`, and verified against `github/main`.


# V1-C21 — Hardening and Regression

**Status:** COMPLETE_PENDING_GIT
**Dependencies:** V1-C20
**Exit Gate:** PASS

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Issue→root-cause fix | No production change | C21 post-C20 risk-scoped inspection | PASS / N/A | No confirmed C20 integration or Golden Case defect was reproduced; no speculative hardening was introduced. |
| Regression tests | Existing C03/C04/C11/C13/C15/C16/C18/C19/C20 surfaces | 219-test focused governance/security/provider/persistence/recovery/C15/C16/observability/Golden Case regression | PASS | All focused tests passed without provider calls. |
| Governance/security regression | Existing deterministic authorities | `test_governance.py`; `test_security_boundaries.py`; provider contract regressions | PASS | Governance, security/redaction, provider typed-error, and boundary behavior remain unchanged. |
| Baseline comparison | C20 integrated baseline | Full `pytest` | PASS | 307 passed, matching the post-C20 baseline; no regression observed. |
| No critical known defect | C21 risk-scoped review | Focused plus full regression, compile/import, dependency, and diff checks | PASS | No known critical V1 defect remains in the exercised contract surface. |

**Baseline Before:** C20 integrated baseline: 307 tests passing.
**Candidate After:** C21 risk-scoped regression: 219 passed; full suite: 307 passed; compile/import, `pip check`, and diff checks passed.
**Regression Decision:** PASS — no baseline regression and no confirmed integration, Golden Case, Governance, Security, recovery, provider, C15/C16, or persistence defect was found.
**Known Issues / Blockers:** None found. No mandatory C21 live-provider baseline exists, so no provider call was made.
**Diff Review:** PASS — only the canonical C21 Evidence record changed.
**Git Status Review:** PASS — no files staged; protected untracked `REPAIR_INSTRUCTIONS.md` and `eference/` remain outside C21 scope.
**Exit Gate Evidence:** PASS — no known critical V1 defect remains in the risk-scoped post-C20 surface and relevant quality baseline did not regress.


# V1-C22 — Documentation and Demo Readiness

**Status:** NOT_STARTED
**Dependencies:** V1-C21
**Exit Gate:** PENDING

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| README/setup/run | TBD | TBD | PENDING | TBD |
| Architecture index | TBD | TBD | PENDING | TBD |
| Verified commands | TBD | TBD | PENDING | TBD |
| Limitations/status | TBD | TBD | PENDING | TBD |
| Golden Case/demo | TBD | TBD | PENDING | TBD |
| Final reproducibility evidence | TBD | TBD | PENDING | TBD |

**Baseline Before:** PENDING / N/A with reason
**Candidate After:** PENDING / N/A with reason
**Regression Decision:** PENDING / N/A with reason
**Known Issues / Blockers:** None recorded.
**Diff Review:** PENDING
**Git Status Review:** PENDING
**Exit Gate Evidence:** TBD

# Final V1 Evidence Gate

Before V1 COMPLETE, record real evidence for: full automated suite; provider integration; persistence; recovery; Governance; security/prompt-injection; Golden Case; entity accuracy; research recall/coverage; Evidence Fidelity; important factual traceability; known unsupported factual claims=0; BLOCK leakage=0; RESTRICT preservation; Knowledge Gaps; context preservation; local-first/no-silent-cloud behavior; observability/performance baseline; final diff/status; documentation accuracy; no unresolved critical issue.

**V1 FINAL STATUS:** NOT_STARTED
