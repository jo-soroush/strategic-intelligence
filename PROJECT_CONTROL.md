# PROJECT_CONTROL.md

## Strategic Intelligence Project — Live Project Control

This file is the live operational state. Repository reality and approved project authorities override chat memory.

## Current Project State

**Project:** Strategic Intelligence Project
**Version:** V1
**Architecture Status:** FROZEN FOR IMPLEMENTATION
**Implementation Status:** V1-C06 COMPLETE — RESEARCH PLANNER
**Current Phase:** CARD COMPLETE — AWAITING SEPARATE V1-C07 AUTHORIZATION
**Active Card:** NONE
**Last Completed Card:** V1-C06 — Research Planner
**Next Card Candidate:** V1-C07 — Company Research
**V1-C01 Status:** COMPLETE
**V1-C02 Status:** COMPLETE
**V1-C03 Status:** COMPLETE
**V1-C04 Status:** COMPLETE
**V1-C05 Status:** COMPLETE
**V1-C06 Status:** COMPLETE
**V1-C07 Status:** NOT_STARTED
**Next Card Start Approval:** V1-C07 REQUIRED
**Current Blocker:** NONE
**Roadmap Cards:** 22 — canonical complete file restored
**Card Specifications:** 22 — canonical complete file restored
**Evidence Map:** 22 — canonical complete ledger restored
**Golden Case Contract:** DEFINED
**Modernization / Pre-Mortem Controls:** CONSOLIDATED INTO CANONICAL CARD CONTRACTS

## Repository Reality From Pre-C01 Audit

- No `.git` repository was present at audit time.
- No application implementation/tests/configuration were present at audit time.
- The directory was documentation-only.
- Architecture filename mismatch existed: `02_SYSTEM_ARCHITECTURE (1).md` instead of canonical `02_SYSTEM_ARCHITECTURE.md`.
- No V1 Card had started at the pre-C01 audit; V1-C01 is now complete.

These facts must be re-inspected by Codex before changing project state.

## Current Git State

**Git Repository:** INITIALIZED; C01–C05 Card commits are committed and pushed
**Canonical Branch:** `main`
**GitHub Default Branch:** `main`
**Integrated-State Authority:** dynamically verify that local `main` HEAD equals `github/main`; do not store a self-referential current `main` SHA here
**Live Operational Git State:** dynamically verify current branch, upstream, local/remote `main` equality, and tracked-worktree cleanliness from Git before every state-changing action; `REPAIR_INSTRUCTIONS.md` is a recognized untracked artifact outside Card scope
**Last Completed / Integrated Card:** V1-C05 — Case Input and Validation; approved commit `46e857a4e6d3ca0e04a0f6a3c645bc455f706b37` is integrated into canonical `main`
**C05 Card Branch:** `card/v1-c05-case-input-validation` is preserved at approved commit `46e857a4e6d3ca0e04a0f6a3c645bc455f706b37`
**C04 Card Branch:** `card/v1-c04-provider-foundation` is preserved at approved commit `8da3f527c1f095bdd2e9a9ec237018bf745bca22`
**C04 Repair Integration State:** approved repair commit `cb882e2` is integrated into canonical `main`; `card/v1-c04-provider-foundation-repair` is preserved; live branch/commit state remains dynamically verified
**C01 Card Branch:** `card/v1-c01-repository-baseline` → `61de4a96178ad227d7ede26ea75252d8ec7db7c0`
**C02 Card Branch:** `card/v1-c02-domain-models` → `17bb25c5b22d27087fa649ed57abf20d36e2e3c9`
**GitHub Remote:** `github` → `https://github.com/jo-soroush/strategic-intelligence.git`
**Main Upstream:** `github/main` — verify local/remote HEAD equality dynamically before Card work
**C01–C05 Card/Main Pushes:** SUCCESSFUL — verify current references dynamically

Follow the canonical workflow and Post-Integration Reconciliation Gate in `AGENTS.md` §21: every new Card branch starts only after that gate passes against dynamically verified current `main`; integration, commit, push, PR, merge, and force-push remain explicitly user-approved. Exact SHAs remain historical evidence in Git history, Card Evidence, and commit reports, not a self-synchronizing Project Control field.

## Mandatory Authority Read Order

1. AGENTS.md
2. PROJECT_CONTROL.md
3. approved architecture docs
4. 12_V1_ROADMAP.md
5. 13_CARD_SPECIFICATIONS.md
6. 14_CARD_EVIDENCE_MAP.md
7. 15_CODEX_EXECUTION_PROTOCOL.md
8. 16_GOLDEN_CASE_EVALUATION_CONTRACT.md when relevant
9. README.md when present
10. repository/Git reality
11. relevant code/tests

Any conflict: STOP, report, no implementation.

## Final Pre-C01 Audit

**Audit completed:** 2026-08-25
**Audit verdict:** READY_WITH_MINOR_DOCUMENTATION_FIXES
**Control-document repair:** COMPLETE
**Canonical 22-Card Roadmap:** VERIFIED
**Canonical 22-Card Specifications:** VERIFIED
**Canonical 22-Card Evidence Map:** VERIFIED
**Architecture filename:** STANDARDIZED as `02_SYSTEM_ARCHITECTURE.md`
**Harness design-chain audit:** PASS
**Scope-leak check:** PASS
**Remaining design/control gap after this update:** NONE
**Runtime behavior:** appropriately UNPROVEN until implementation

The only issue reported by the final audit was stale resume text in this file. This update resolves that issue.

## Current Resume Instruction

V1-C06 is complete. Do not start V1-C07 without separate explicit user approval and the required dynamically verified Git/control gate on canonical `main`.

Safe next sequence after approval:

1. obtain separate authorization for C06 delivery/integration as applicable;
2. complete required post-delivery/integration reconciliation on canonical `main` when authorized;
3. obtain separate authorization to start `V1-C07 — Company Research` only after the dynamic gate passes;
4. STOP; do not begin C07 in this session.

## Last Execution Checkpoint

**Card:** V1-C06 — Research Planner
**Step:** Bounded ResearchPlan, coverage-aware completion check, and C06 closure reconciliation completed
**Status:** COMPLETE
**Implementation Files Changed:** typed ResearchCoverage/requirements and plan budgets; application-owned ResearchPlanner; C06 planner tests; C06 Evidence and Project Control
**Project-State Change:** C06 Card branch begins from dynamically verified canonical `main`; at this closure checkpoint, no commit, push, merge, or C07 action had been authorized
**Tests Run:** `tests/unit/test_research_planning.py` — 6 passed; full suite — 39 passed; `pip check`; `compileall -q src`; package import; diff/ignore/scope review
**Result:** C06 exact Exit Gate PASS; Critical-Path Validation PASS; Final Card Closure Gate PASS; research receives a typed bounded plan and completion requires coverage status, not result count
**Evidence Updated:** C06 closure evidence reconciled; V1-C07–V1-C22 remain NOT_STARTED
**Blocker:** NONE
**Safe Resume Point:** POST-V1-C06 — delivery/integration decision pending
**Next Action:** STOP and await explicit user approval for C06 delivery/integration or for a separately gated V1-C07 start

## Guiding Rule

If project state is uncertain, STOP coding and reconstruct reality from Repository + Git + Roadmap + Card Spec + Evidence Map + Project Control.
