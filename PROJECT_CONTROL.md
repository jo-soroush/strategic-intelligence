# PROJECT_CONTROL.md

## Strategic Intelligence Project — Live Project Control

This file is the live operational state. Repository reality and approved project authorities override chat memory.

## Current Project State

**Project:** Strategic Intelligence Project
**Version:** V1
**Architecture Status:** FROZEN FOR IMPLEMENTATION
**Implementation Status:** V1-C11 COMPLETE — VERIFICATION ENGINE
**Current Phase:** CARD CLOSED — V1-C12 NOT AUTHORIZED
**Active Card:** NONE
**Last Completed Card:** V1-C11 — Verification Engine
**Next Card Candidate:** V1-C12 — Bounded Follow-Up Research (NOT AUTHORIZED)
**V1-C01 Status:** COMPLETE
**V1-C02 Status:** COMPLETE
**V1-C03 Status:** COMPLETE
**V1-C04 Status:** COMPLETE
**V1-C05 Status:** COMPLETE
**V1-C06 Status:** COMPLETE
**V1-C07 Status:** COMPLETE
**V1-C08 Status:** COMPLETE
**V1-C09 Status:** COMPLETE
**V1-C10 Status:** COMPLETE
**V1-C11 Status:** COMPLETE
**Next Card Start Approval:** V1-C12 REQUIRED
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

**Git Repository:** INITIALIZED; C01–C10 Card commits are committed and pushed; dynamically verify C11 branch/delivery state from Git when separately authorized
**Canonical Branch:** `main`
**GitHub Default Branch:** `main`
**Integrated-State Authority:** dynamically verify that local `main` HEAD equals `github/main`; do not store a self-referential current `main` SHA here
**Live Operational Git State:** dynamically verify current branch, upstream, local/remote `main` equality, and tracked-worktree cleanliness from Git before every state-changing action; `REPAIR_INSTRUCTIONS.md` is a recognized untracked artifact outside Card scope
**Last Completed / Integrated Card:** V1-C10 — Source Quality and Freshness; approved commit `2c2868910c5bd433f76d38e7e2641dc237626220` is integrated into canonical `main`
**C10 Card Branch:** `card/v1-c10-source-quality-freshness` is preserved at approved commit `2c2868910c5bd433f76d38e7e2641dc237626220`
**C09 Card Branch:** `card/v1-c09-evidence-layer` is preserved at approved commit `92a3e074bca8ada18d3f6ee02868b5b1f9fdad66`
**C08 Card Branch:** `card/v1-c08-executive-research` is preserved at approved commit `89712a7f7ff0d388580f6a7c7b84bbbd17b2e347`
**C07 Card Branch:** `card/v1-c07-company-research` is preserved at approved commit `4c6dcd4d80273269d3790fb5b67522d3d012e3c8`
**C06 Card Branch:** `card/v1-c06-research-planner` is preserved at approved commit `d784694ec1665dd8660a0d882db672d70c88d45e`
**C05 Card Branch:** `card/v1-c05-case-input-validation` is preserved at approved commit `46e857a4e6d3ca0e04a0f6a3c645bc455f706b37`
**C04 Card Branch:** `card/v1-c04-provider-foundation` is preserved at approved commit `8da3f527c1f095bdd2e9a9ec237018bf745bca22`
**C04 Repair Integration State:** approved repair commit `cb882e2` is integrated into canonical `main`; `card/v1-c04-provider-foundation-repair` is preserved; live branch/commit state remains dynamically verified
**C01 Card Branch:** `card/v1-c01-repository-baseline` → `61de4a96178ad227d7ede26ea75252d8ec7db7c0`
**C02 Card Branch:** `card/v1-c02-domain-models` → `17bb25c5b22d27087fa649ed57abf20d36e2e3c9`
**GitHub Remote:** `github` → `https://github.com/jo-soroush/strategic-intelligence.git`
**Main Upstream:** `github/main` — verify local/remote HEAD equality dynamically before Card work
**C01–C10 Card/Main Pushes:** SUCCESSFUL — verify current references dynamically

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

V1-C11 is COMPLETE and Active Card is NONE. Keep C12 and later Cards
NOT_STARTED; dynamically verify Git state before any separately authorized
delivery or next-Card action. Do not commit, push, or merge without separate
authorization.

## Last Execution Checkpoint

**Card:** V1-C11 — Verification Engine
**Step:** pre-finalization audit F001–F004 repaired; Final Card Closure Gate and C11 Critical Path revalidated
**Status:** COMPLETE
**Implementation Files Changed:** `domain/models.py`; application persistence
protocol and deterministic verification service; SQLite repository read path;
C11 baseline fixture/tests; C11 Evidence; `PROJECT_CONTROL.md`; README.
**Project-State Change:** C11 was implemented and validated on
`card/v1-c11-verification-engine`, created from verified integrated `main` at
`2ee6e1e`; no commit, push, merge, rebase, or force-push has occurred.
**Tests Run:** `.venv/bin/python -m pytest tests/unit/test_verification.py -q`
(13 passed); `.venv/bin/python -m pytest` (71 passed); `pip check`; compile,
import, and diff checks.
**Result:** repaired deterministic C11 Fidelity/Verification permits FACT only,
enforces same-Case provenance, rejects unusable normalized Claims, consumes C10
metadata, preserves candidate Claims without promotion/mutation, and leaves
Governance/follow-up research deferred.
**Evidence Updated:** single C11 closure record includes F001–F004 diagnosis,
repairs, expanded static expected-vs-actual baseline, and fresh Exit Gate proof;
C12–V1-C22 remain NOT_STARTED.
**Blocker:** NONE
**Safe Resume Point:** PRE-V1-C12 — REQUIRE DYNAMIC GIT REVIEW AFTER EXPLICIT
AUTHORIZATION
**Next Action:** STOP and await explicit authorization; do not start C12

## Guiding Rule

If project state is uncertain, STOP coding and reconstruct reality from Repository + Git + Roadmap + Card Spec + Evidence Map + Project Control.
