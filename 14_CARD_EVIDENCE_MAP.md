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

**Status:** NOT_STARTED
**Dependencies:** V1-C05, V1-C16
**Exit Gate:** PENDING

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Case input | TBD | TBD | PENDING | TBD |
| Workflow execution | TBD | TBD | PENDING | TBD |
| Quick/Full display | TBD | TBD | PENDING | TBD |
| Partial/failure display | TBD | TBD | PENDING | TBD |

**Baseline Before:** PENDING / N/A with reason
**Candidate After:** PENDING / N/A with reason
**Regression Decision:** PENDING / N/A with reason
**Known Issues / Blockers:** None recorded.
**Diff Review:** PENDING
**Git Status Review:** PENDING
**Exit Gate Evidence:** TBD


# V1-C18 — Workflow Recovery

**Status:** NOT_STARTED
**Dependencies:** V1-C03, V1-C16
**Exit Gate:** PENDING

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Accepted-checkpoint protocol | TBD | TBD | PENDING | TBD |
| Persistence/invariant rejection | TBD | TBD | PENDING | TBD |
| Fallback to prior accepted checkpoint | TBD | TBD | PENDING | TBD |
| Trust-stage preservation | TBD | TBD | PENDING | TBD |
| Bounded counters | TBD | TBD | PENDING | TBD |
| Idempotent/duplicate-safe resume | TBD | TBD | PENDING | TBD |

**Baseline Before:** PENDING / N/A with reason
**Candidate After:** PENDING / N/A with reason
**Regression Decision:** PENDING / N/A with reason
**Known Issues / Blockers:** None recorded.
**Diff Review:** PENDING
**Git Status Review:** PENDING
**Exit Gate Evidence:** TBD


# V1-C19 — Observability and Audit

**Status:** NOT_STARTED
**Dependencies:** V1-C03, V1-C04, V1-C13
**Exit Gate:** PENDING

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Structured harness trace | TBD | TBD | PENDING | TBD |
| Verification/Governance events | TBD | TBD | PENDING | TBD |
| Checkpoint decisions | TBD | TBD | PENDING | TBD |
| Retry/error events | TBD | TBD | PENDING | TBD |
| Secret redaction | TBD | TBD | PENDING | TBD |
| Performance baseline telemetry | TBD | TBD | PENDING | TBD |

**Baseline Before:** PENDING / N/A with reason
**Candidate After:** PENDING / N/A with reason
**Regression Decision:** PENDING / N/A with reason
**Known Issues / Blockers:** None recorded.
**Diff Review:** PENDING
**Git Status Review:** PENDING
**Exit Gate Evidence:** TBD


# V1-C20 — Golden Case

**Status:** NOT_STARTED
**Dependencies:** V1-C07 through V1-C19
**Exit Gate:** PENDING

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Real Case/Ground Truth | TBD | TBD | PENDING | TBD |
| Entity accuracy | TBD | TBD | PENDING | TBD |
| Research recall/coverage | TBD | TBD | PENDING | TBD |
| Evidence Fidelity | TBD | TBD | PENDING | TBD |
| Governance/traceability | TBD | TBD | PENDING | TBD |
| Context preservation | TBD | TBD | PENDING | TBD |
| Strategic insight/usefulness | TBD | TBD | PENDING | TBD |
| Performance/baseline comparison | TBD | TBD | PENDING | TBD |

**Baseline Before:** PENDING / N/A with reason
**Candidate After:** PENDING / N/A with reason
**Regression Decision:** PENDING / N/A with reason
**Known Issues / Blockers:** None recorded.
**Diff Review:** PENDING
**Git Status Review:** PENDING
**Exit Gate Evidence:** TBD


# V1-C21 — Hardening and Regression

**Status:** NOT_STARTED
**Dependencies:** V1-C20
**Exit Gate:** PENDING

### Evidence

| Requirement | Implementation Location | Test / Evaluation | Result | Evidence |
|---|---|---|---|---|
| Issue→root-cause fix | TBD | TBD | PENDING | TBD |
| Regression tests | TBD | TBD | PENDING | TBD |
| Governance/security regression | TBD | TBD | PENDING | TBD |
| Baseline comparison | TBD | TBD | PENDING | TBD |
| No critical known defect | TBD | TBD | PENDING | TBD |

**Baseline Before:** PENDING / N/A with reason
**Candidate After:** PENDING / N/A with reason
**Regression Decision:** PENDING / N/A with reason
**Known Issues / Blockers:** None recorded.
**Diff Review:** PENDING
**Git Status Review:** PENDING
**Exit Gate Evidence:** TBD


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
