# Strategic Intelligence Project

Local-first, evidence-backed preparation for an important meeting with a company executive.

## Implemented foundations

The repository currently contains the implemented V1 foundations for typed
domain models; local persistence and repository infrastructure; vendor-neutral
provider boundaries; validated Case intake; bounded research planning; company
and public-professional executive research; Source → Evidence → candidate Claim
provenance; deterministic source-quality/freshness metadata; and deterministic
Evidence Fidelity/Verification judgment; deterministic Governance; governed
strategic analysis; and trustworthy, traceable Quick/Full Brief generation.

End-to-end workflow orchestration, local UI, recovery, and later V1
capabilities remain governed by their owning future Cards.
The canonical Evidence Map owns actual Card delivery evidence, while Git proves
live delivery state; this README describes durable repository capabilities
rather than live Card state.

### Requirements

- Python 3.11 (the project supports `>=3.11,<3.13`)
- Git

### Local setup

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```

The project reads non-secret settings from the process environment. `.env.example` documents safe development defaults; `.env` is intentionally ignored and no secret belongs in the repository.

## Package ownership

| Location | Ownership | Current role |
|---|---|---|
| `src/strategic_intelligence/application/` | application/use-case composition | Case intake, research planning, company/executive research, evidence provenance, source metadata, and deterministic Verification services. |
| `src/strategic_intelligence/domain/` | domain contracts | Typed V1 models, enums, invariants, and serialization. |
| `src/strategic_intelligence/harness/` | workflow orchestration | Reserved for the controlled orchestration/routing capability owned by future Cards. |
| `src/strategic_intelligence/providers/` | provider adapters | Application-owned LLM/search contracts, explicit adapters, factory, and deterministic fakes. |
| `src/strategic_intelligence/infrastructure/` | persistence / external infrastructure | Local SQLite repository and safe local artifact storage. |
| `src/strategic_intelligence/security/` | security controls | Reserved for deterministic security boundaries. |
| `src/strategic_intelligence/governance/` | deterministic governance | Reserved for C13 trust-policy enforcement. |
| `src/strategic_intelligence/observability/` | logs / audit traces | Hosts the C01 logging foundation. |
| `src/strategic_intelligence/ui/` | local interface | Reserved for C17's thin local UI. |

Business behavior belongs in its owning component; provider SDKs, database details, and external source content do not enter domain contracts. The Harness coordinates later runtime work but does not replace component business logic.

## Tests and evaluation conventions

- `tests/unit/`: deterministic component tests.
- `tests/integration/`: bounded adapter or system-boundary tests.
- `tests/fixtures/`: reusable deterministic test fixtures.
- `evaluations/fixtures/`: versioned, deterministic evaluation inputs and labels.
- `evaluations/artifacts/`: generated evaluation outputs; ignored except for its `.gitkeep` marker.

V1 establishes its measurable evaluation baseline incrementally. The canonical
Evidence Map records Card-specific validation and evaluation evidence; this
README does not duplicate volatile results.
