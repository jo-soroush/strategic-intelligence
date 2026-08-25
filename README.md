# Strategic Intelligence Project

Local-first, evidence-backed preparation for an important meeting with a company executive.

## C01 foundation

This repository currently provides only the V1-C01 foundation: package ownership boundaries, centralized non-secret settings, logging setup, test conventions, and deterministic evaluation locations. It does not yet implement domain models, research, providers, persistence, workflow orchestration, governance behavior, or a UI.

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
| `src/strategic_intelligence/application/` | application/use-case composition | Reserved for application services and composition. |
| `src/strategic_intelligence/domain/` | domain contracts | Reserved for C02 typed models and invariants. |
| `src/strategic_intelligence/harness/` | workflow orchestration | Reserved for controlled orchestration and routing. |
| `src/strategic_intelligence/providers/` | provider adapters | Reserved for C04 capability contracts and adapters. |
| `src/strategic_intelligence/infrastructure/` | persistence / external infrastructure | Reserved for repositories and artifact storage. |
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

V1 establishes its measurable evaluation baseline incrementally; C01 does not add an evaluation framework or fabricate baseline results.
