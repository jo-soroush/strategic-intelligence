"""C13 deterministic final-use Governance over persisted Claims and C11 results."""

from __future__ import annotations

import re
from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.application.verification import VerificationAssessment, VerificationAssessmentStatus, VerificationService, verification_fingerprint
from strategic_intelligence.domain.models import (
    Claim, ClaimType, FidelityStatus, GovernanceDecision, GovernanceDecisionStatus,
    GovernanceReasonCode, VerificationStatus,
)


class GovernanceAssessmentStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class GovernanceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    status: GovernanceAssessmentStatus
    claim: Claim | None = None
    verification: VerificationAssessment | None = None
    decision: GovernanceDecision | None = None
    reason: str


class GovernanceService:
    """Applies non-overridable deterministic final-use policy; it never researches or verifies."""

    _PRIVATE_PERSONAL_PATTERNS = (
        re.compile(r"\b(?:personal\s+)?(?:phone|mobile|home\s+address|medical|health\s+condition)\b", re.IGNORECASE),
        re.compile(r"\b(?:\+?\d[\d .()\-]{7,}\d)\b"),
    )

    def __init__(self, repository: PersistenceRepository, verification: VerificationService) -> None:
        self._repository = repository
        self._verification = verification

    def evaluate(self, claim_id: str, *, as_of: date) -> GovernanceAssessment:
        try:
            claim = self._repository.get_claim(claim_id)
        except ValueError:
            return GovernanceAssessment(
                status=GovernanceAssessmentStatus.REJECTED,
                reason="governance rejects invalid persisted Claim data before final use",
            )
        if claim is None:
            return GovernanceAssessment(
                status=GovernanceAssessmentStatus.REJECTED,
                reason="governance requires a persisted Claim",
            )
        if self._contains_private_personal_data(claim.text):
            return self._persist(claim, GovernanceDecisionStatus.BLOCK, [GovernanceReasonCode.PRIVACY_BOUNDARY], "private or sensitive personal content is not eligible for final use")
        if claim.claim_type is ClaimType.FACT:
            return self._evaluate_fact(claim, as_of=as_of)
        if claim.claim_type is ClaimType.INFERENCE:
            if not self._has_traceable_provenance(claim):
                return self._persist(claim, GovernanceDecisionStatus.BLOCK, [GovernanceReasonCode.UNTRACEABLE_CLAIM], "inference lacks traceable same-Case evidence")
            return self._persist(claim, GovernanceDecisionStatus.RESTRICT, [GovernanceReasonCode.INFERENCE_REQUIRES_QUALIFICATION], "inference may be used only as explicitly qualified inference, never as a verified fact")
        return self._persist(claim, GovernanceDecisionStatus.RESTRICT, [GovernanceReasonCode.RECOMMENDATION_REQUIRES_QUALIFICATION], "recommendation is not factual intelligence and must remain visibly qualified")

    def _evaluate_fact(self, claim: Claim, *, as_of: date) -> GovernanceAssessment:
        assessment = self._verification.verify(claim.claim_id, as_of=as_of)
        if assessment.status is not VerificationAssessmentStatus.ACCEPTED or assessment.verification is None:
            reason = GovernanceReasonCode.MISSING_EVIDENCE if not claim.evidence_ids else GovernanceReasonCode.UNTRACEABLE_CLAIM
            return self._persist(claim, GovernanceDecisionStatus.BLOCK, [reason], "FACT provenance is incomplete or invalid", assessment)
        verification = assessment.verification
        if assessment.fidelity_status is FidelityStatus.NOT_SUPPORTED:
            return self._persist(claim, GovernanceDecisionStatus.BLOCK, [GovernanceReasonCode.UNVERIFIED_FACT], "FACT is not supported by its linked Evidence", assessment)
        if verification.status is VerificationStatus.CONFLICTING:
            return self._persist(claim, GovernanceDecisionStatus.RESTRICT, [GovernanceReasonCode.CONFLICTING_EVIDENCE], "conflicting Evidence remains visible and cannot be silently selected", assessment)
        if verification.status is VerificationStatus.STALE:
            return self._persist(claim, GovernanceDecisionStatus.RESTRICT, [GovernanceReasonCode.STALE_INFORMATION], "stale factual information requires visible qualification", assessment)
        if verification.status is VerificationStatus.INSUFFICIENT_EVIDENCE:
            return self._persist(claim, GovernanceDecisionStatus.RESTRICT, [GovernanceReasonCode.UNVERIFIED_FACT], "FACT remains unresolved and cannot be promoted", assessment)
        return self._persist(claim, GovernanceDecisionStatus.PASS, [], "FACT has accepted C11 verification and traceable provenance", assessment)

    def _persist(
        self, claim: Claim, decision: GovernanceDecisionStatus, reasons: list[GovernanceReasonCode], notes: str,
        verification: VerificationAssessment | None = None,
    ) -> GovernanceAssessment:
        stored = self._repository.save_governance_decision(GovernanceDecision(
            case_id=claim.case_id,
            target_type="claim",
            target_id=claim.claim_id,
            decision=decision,
            reason_codes=reasons,
            notes=notes,
            verification_fingerprint=verification_fingerprint(verification) if verification is not None else None,
        ))
        return GovernanceAssessment(
            status=GovernanceAssessmentStatus.ACCEPTED,
            claim=claim,
            verification=verification,
            decision=stored,
            reason=notes,
        )

    def _has_traceable_provenance(self, claim: Claim) -> bool:
        links = self._repository.get_claim_evidence_links(claim.claim_id)
        if not claim.evidence_ids or {link.evidence_id for link in links} != set(claim.evidence_ids):
            return False
        for evidence_id in claim.evidence_ids:
            evidence = self._repository.get_evidence(evidence_id)
            if evidence is None or evidence.case_id != claim.case_id:
                return False
            source = self._repository.get_source(evidence.source_id)
            if source is None or source.case_id != claim.case_id:
                return False
        return True

    @classmethod
    def _contains_private_personal_data(cls, text: str) -> bool:
        return any(pattern.search(text) for pattern in cls._PRIVATE_PERSONAL_PATTERNS)
