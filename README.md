# Strategic Intelligence Project

Strategic Intelligence is a local-first V1 system for preparing an important
professional meeting with a company executive. It turns bounded public research
into a traceable, governed Quick Brief and Full Brief without allowing an LLM,
search provider, or UI to override Verification, Governance, or provenance.

## What V1 does

```text
Validated Case
  → bounded research plan and public-source discovery/retrieval
  → Source → Evidence → Claim
  → C11 Verification → C12 bounded follow-up → C13 Governance
  → C15 Strategic Analysis → C16 Quick/Full Brief
  → C18 checkpointed workflow and recovery → C19 redacted audit
```

The local UI is a thin loopback-only presentation layer:

```text
Browser UI → WorkflowApplication → WorkflowExecutor → governed system
```

The durable architecture, provider rules, Golden Case contract, and execution
evidence are documented in [02_SYSTEM_ARCHITECTURE.md](02_SYSTEM_ARCHITECTURE.md),
[08_PROVIDER_ARCHITECTURE.md](08_PROVIDER_ARCHITECTURE.md),
[16_GOLDEN_CASE_EVALUATION_CONTRACT.md](16_GOLDEN_CASE_EVALUATION_CONTRACT.md),
and [14_CARD_EVIDENCE_MAP.md](14_CARD_EVIDENCE_MAP.md). Git is the source of
truth for live branch and delivery state.

## Clean setup

Requirements: Python 3.11, Git, and (for the default local model) a running
local Ollama service with the configured model available.

```bash
git clone <repository-url>
cd STRATEGIC_INTELLIGENCE_PROJECT
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Create an environment file only for your shell; it is never loaded by the
application automatically and must not be committed:

```bash
cp .env.example .env
set -a
source .env
set +a
```

Alternatively, export the documented variables directly in the shell that
starts the application. Secrets remain process environment values—not source
files, domain models, logs, audit events, or Git artifacts.

## Local configuration

The configuration boundary is `strategic_intelligence.config.Settings`; the
provider factory is the only normal provider-construction path.

| Setting | Default | Meaning |
|---|---|---|
| `APP_ENV` | `development` | Non-secret environment label. |
| `DATA_DIR` / `LOG_DIR` | `data` / `logs` | Relative local runtime directories. |
| `LLM_PROVIDER` | `ollama` | `ollama`, `gemini`, or test-only `fake`. |
| `LLM_MODEL` | provider default | Local default: `llama3.2`; Gemini default: `gemini-3.7-flash`. |
| `LLM_TIMEOUT_SECONDS` | `30` | Positive bounded LLM request timeout. |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint unless cloud enablement is explicit. |
| `SEARCH_PROVIDER` | `fake` | `fake`, `duckduckgo`, or `brave`. |
| `CLOUD_PROVIDERS_ENABLED` | `false` | Must be `true` to select Gemini. |
| `GEMINI_API_KEY` | unset | Required only for `LLM_PROVIDER=gemini`. |
| `BRAVE_SEARCH_API_KEY` | unset | Required only for `SEARCH_PROVIDER=brave`. |

Examples:

```bash
# Local-first model with deterministic fake search.
export LLM_PROVIDER=ollama
export LLM_MODEL=llama3.2
export SEARCH_PROVIDER=fake

# Explicit cloud LLM and public-web search. Never commit either credential.
export CLOUD_PROVIDERS_ENABLED=true
export LLM_PROVIDER=gemini
export LLM_MODEL=gemini-3.7-flash
export GEMINI_API_KEY='set-in-your-shell'
export SEARCH_PROVIDER=brave
export BRAVE_SEARCH_API_KEY='set-in-your-shell'
```

There is no silent local-to-cloud fallback. Missing credentials, unavailable
models, unsafe network destinations, malformed responses, and provider limits
remain typed failures handled by the existing workflow policy.

## Run locally

Start the browser UI with the configured process environment:

```bash
.venv/bin/python -m strategic_intelligence.ui
```

Open <http://127.0.0.1:8765>. The server binds to loopback only. The form asks
for company name, executive name, and meeting goal. It also requires C05
identity support: a company website, company LinkedIn URL, or country plus
business unit; and an executive LinkedIn URL or current title. The UI does not
collect provider credentials, expose resume controls, or create a second
workflow/trust authority.

Press `Ctrl-C` to stop it. Local data is stored beneath `DATA_DIR` and is
ignored by Git.

## Test and verification commands

```bash
# Full deterministic regression suite
.venv/bin/python -m pytest

# Focused trust, provider, persistence, workflow, and Golden Case surfaces
.venv/bin/python -m pytest \
  tests/unit/test_governance.py \
  tests/unit/test_security_boundaries.py \
  tests/unit/test_providers.py \
  tests/unit/test_persistence.py \
  tests/unit/test_workflow_executor.py \
  tests/unit/test_strategic_analysis.py \
  tests/unit/test_brief_generator.py \
  tests/unit/test_golden_case.py

.venv/bin/python -m compileall -q src
.venv/bin/python -m pip check
git diff --check
```

The test suite uses deterministic fakes and does not require a provider call.
Live provider or Golden Case execution is an explicit, separately authorized
operation.

## Trust, security, and recovery

- Public external URLs pass deterministic safety and redirect checks before a
  request; automated LinkedIn scraping, access-control bypass, and private
  personal profiling are out of scope.
- A factual Claim requires Source → Evidence → Claim provenance. C11 evaluates
  fidelity, quality, freshness, and conflicts; C13 alone decides `PASS`,
  `RESTRICT`, or `BLOCK`.
- `BLOCK` material cannot enter a Brief. `RESTRICT` material retains visible
  reason codes and qualification. FACTs preserve exact governed Claim text;
  INFERENCE and RECOMMENDATION remain distinct.
- C18 resumes only accepted persisted checkpoints. C19 records a redacted,
  ordered audit trace and bounded performance metrics; raw prompts, provider
  responses, credentials, and tracebacks are not audit content.
- C16 produces Quick/Full Briefs from accepted C15 analysis only. Full Briefs
  put bounded, traceable non-FACT meeting takeaways before detailed canonical
  FACT evidence; the underlying FACTs are unchanged.

See [06_GOVERNANCE_AND_TRUST.md](06_GOVERNANCE_AND_TRUST.md),
[11_SECURITY_AND_PRIVACY.md](11_SECURITY_AND_PRIVACY.md),
[07_WORKFLOW_AND_ORCHESTRATION.md](07_WORKFLOW_AND_ORCHESTRATION.md), and
[09_STORAGE_AND_PERSISTENCE.md](09_STORAGE_AND_PERSISTENCE.md) for the
architecture records.

## Golden Case / demo guide

The versioned V1 Golden Case fixture is
`evaluations/fixtures/c20_capgemini_invent_arash_afsarian_v1.json`. It is an
evaluation answer key only: runtime research, Verification, Governance,
analysis, and Brief generation must not import or receive it.

To demonstrate V1 with public/professional research, use a separately approved
environment with explicit providers, then submit the selected company,
executive, meeting goal, and identity support through the local UI or the
`WorkflowApplication` boundary. After the workflow finishes, evaluate the
persisted run through the C20 evaluation surface. A valid review checks
GroundTruthMatch coverage, Source → Evidence → Claim traceability, current
Verification/Governance decisions, restrictions, audit metrics, and the
human-scored `MeetingValueReview` rubric.

The historical C20 Golden Case used Capgemini Invent / Arash Afsarian for an
enterprise-AI strategy meeting. It reached 12/20 reviewed Ground Truth items,
passed mandatory trust invariants, and passed the MeetingValueReview. Do not
use the fixture to seed or improve a runtime run.

## V1 boundaries and deferred work

V1 is intentionally local-first, single-user, and bounded. It does not provide
a deployment service, multi-user access control, a dashboard, distributed
telemetry, automatic LinkedIn scraping, a vector database/embedding stack,
unbounded autonomous research, provider/model routing, or a silent cloud
fallback. Those are potential V2 considerations, not implied commitments.

The system can return `PARTIAL`, visible knowledge gaps, `RESTRICT`, or
`BLOCK` rather than fabricate completeness. A successful workflow run is not a
license to treat unverified material as FACT.

## Repository navigation

| Path | Use it for |
|---|---|
| `README.md` | Setup, local run, configuration, tests, and demo orientation. |
| `02_SYSTEM_ARCHITECTURE.md` | Implemented V1 topology and ownership map. |
| `08_PROVIDER_ARCHITECTURE.md` | Provider contracts, configuration, errors, and safety boundary. |
| `16_GOLDEN_CASE_EVALUATION_CONTRACT.md` | Golden Case rubric and mandatory trust gate. |
| `12_V1_ROADMAP.md` | Planned card sequence. |
| `13_CARD_SPECIFICATIONS.md` | Planned Card contracts. |
| `14_CARD_EVIDENCE_MAP.md` | Actual Card evidence and learning history. |
| `15_CODEX_EXECUTION_PROTOCOL.md` | Git delivery procedure. |
| `AGENTS.md` | Repository execution and safety rules. |
