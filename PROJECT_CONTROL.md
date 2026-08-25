# PROJECT_CONTROL.md

## Strategic Intelligence Project — Live Project Control

This file is the live operational state. Repository reality and approved project authorities override chat memory.

## Current Project State

**Project:** Strategic Intelligence Project
**Version:** V1
**Architecture Status:** FROZEN FOR IMPLEMENTATION
**Implementation Status:** V1-C03 COMPLETE
**Current Phase:** CARD COMPLETE — WAITING FOR USER AUTHORIZATION FOR V1-C04
**Active Card:** NONE
**Last Completed Card:** V1-C03 — Persistence Foundation
**Next Card Candidate:** V1-C04 — Provider Foundation
**V1-C01 Status:** COMPLETE
**V1-C02 Status:** COMPLETE
**V1-C03 Status:** COMPLETE
**V1-C04 Status:** NOT_STARTED
**Next Card Start Approval:** REQUIRED
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

**Git Repository:** INITIALIZED; C01 and C02 COMMITTED AND PUSHED
**Canonical Branch:** `main`
**GitHub Default Branch:** `main`
**Integrated-State Authority:** dynamically verify that local `main` HEAD equals `github/main`; do not store a self-referential current `main` SHA here
**Current Branch:** `card/v1-c03-persistence-foundation`
**C03 Base:** dynamically verified `main` at `fd9658d2dd8d1d04a5761d4289bc5b0d17e8a29e`
**Working Tree:** uncommitted C03 persistence changes; untracked `REPAIR_INSTRUCTIONS.md` remains outside Card scope
**C01 Card Branch:** `card/v1-c01-repository-baseline` → `61de4a96178ad227d7ede26ea75252d8ec7db7c0`
**C02 Card Branch:** `card/v1-c02-domain-models` → `17bb25c5b22d27087fa649ed57abf20d36e2e3c9`
**GitHub Remote:** `github` → `https://github.com/jo-soroush/strategic-intelligence.git`
**Main Upstream:** `github/main` — verify local/remote HEAD equality dynamically before Card work
**C01/C02/Main Push:** SUCCESSFUL — remote branches match their local references

Follow the canonical workflow in `AGENTS.md` §21: every new Card branch starts from dynamically verified current `main`; integration, commit, push, PR, merge, and force-push remain explicitly user-approved. Exact SHAs remain historical evidence in Git history, Card Evidence, and commit reports, not a self-synchronizing Project Control field.

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

V1-C03 is complete. Do not start V1-C04 without explicit user approval.

Safe next sequence after approval:

1. re-read all project authorities and inspect repository/Git state;
2. activate `V1-C04 — Provider Foundation` only after explicit user approval;
3. perform its inspect-only Contract / Risk Map and Roadmap Alignment Gate;
4. execute only bounded C04 scope if the gate passes;
5. STOP after C04; do not begin C05.

## Last Execution Checkpoint

**Card:** V1-C03 — Persistence Foundation
**Step:** Exit Gate and closure validation completed
**Status:** COMPLETE
**Implementation Files Changed:** application persistence interfaces; SQLite repository/schema; local artifact adapter; configuration storage paths; C03 tests; Evidence Map; Project Control
**Project-State Change:** C03 completed locally on `card/v1-c03-persistence-foundation`; no commit or push created
**Tests Run:** C03 persistence tests (7 passed); full suite (18 passed); `pip check`; compile/import; Git diff/status checks
**Result:** C03 Exit Gate PASS
**Evidence Updated:** V1-C03 evidence recorded; V1-C04–V1-C22 remain NOT_STARTED
**Blocker:** NONE
**Safe Resume Point:** PRE-V1-C04
**Next Action:** Explicit user approval to start V1-C04

## Guiding Rule

If project state is uncertain, STOP coding and reconstruct reality from Repository + Git + Roadmap + Card Spec + Evidence Map + Project Control.
