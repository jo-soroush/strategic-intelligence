"""Deterministic C11 Evidence Fidelity and Claim Verification boundary."""

from __future__ import annotations

import re
import hashlib
import json
from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.application.source_quality import (
    SourceMetadataResult,
    SourceMetadataStatus,
    SourceQualityService,
)
from strategic_intelligence.domain.models import (
    Claim, ClaimEvidenceLink, ClaimEvidenceRelationship, ClaimType, Evidence, FidelityStatus,
    FreshnessStatus, Source, SourceQuality, VerificationResult, VerificationStatus,
)


class VerificationAssessmentStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class VerificationErrorCode(str, Enum):
    MISSING_CLAIM = "MISSING_CLAIM"
    INVALID_PROVENANCE = "INVALID_PROVENANCE"


class VerificationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class VerificationError(VerificationModel):
    code: VerificationErrorCode
    message: str


class VerificationAssessment(VerificationModel):
    status: VerificationAssessmentStatus
    claim: Claim | None = None
    fidelity_status: FidelityStatus | None = None
    verification: VerificationResult | None = None
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradictory_evidence_ids: list[str] = Field(default_factory=list)
    context_evidence_ids: list[str] = Field(default_factory=list)
    errors: list[VerificationError] = Field(default_factory=list)


class VerificationService:
    """Judges C09 provenance with C10 metadata; it never governs or mutates Claims."""

    def __init__(self, repository: PersistenceRepository, source_quality: SourceQualityService | None = None) -> None:
        self._repository = repository
        self._source_quality = source_quality or SourceQualityService()

    def verify(self, claim_id: str, *, as_of: date) -> VerificationAssessment:
        claim = self._repository.get_claim(claim_id)
        if claim is None:
            return self._rejected(VerificationErrorCode.MISSING_CLAIM, "candidate claim is not persisted")
        if claim.claim_type is not ClaimType.FACT:
            return self._rejected(VerificationErrorCode.INVALID_PROVENANCE, "only FACT claims may enter factual verification")
        links = self._repository.get_claim_evidence_links(claim_id)
        if {link.evidence_id for link in links} != set(claim.evidence_ids) or not links:
            return self._rejected(VerificationErrorCode.INVALID_PROVENANCE, "claim links do not exactly match persisted evidence")

        resolved = self._resolve(claim, links)
        if resolved is None:
            return self._rejected(VerificationErrorCode.INVALID_PROVENANCE, "linked evidence or source is unavailable")
        evidence_by_id, source_by_evidence = resolved
        metadata = {evidence_id: self._source_quality.assess(source, as_of=as_of) for evidence_id, source in source_by_evidence.items()}
        if any(item.status is SourceMetadataStatus.REJECTED for item in metadata.values()):
            return self._rejected(VerificationErrorCode.INVALID_PROVENANCE, "source metadata is invalid")

        supporting = [link.evidence_id for link in links if link.relationship_type is ClaimEvidenceRelationship.SUPPORTS]
        contradictory = [link.evidence_id for link in links if link.relationship_type is ClaimEvidenceRelationship.CONTRADICTS]
        context = [link.evidence_id for link in links if link.relationship_type is ClaimEvidenceRelationship.CONTEXT]
        fidelity = self._fidelity_for(claim, [evidence_by_id[item] for item in supporting], bool(context))
        if fidelity is None:
            return self._rejected(VerificationErrorCode.INVALID_PROVENANCE, "claim text is unusable for fidelity comparison")
        verification = self._verification_for(
            claim, fidelity, supporting, contradictory, metadata,
        )
        return VerificationAssessment(
            status=VerificationAssessmentStatus.ACCEPTED,
            claim=claim,
            fidelity_status=fidelity,
            verification=verification,
            supporting_evidence_ids=supporting,
            contradictory_evidence_ids=contradictory,
            context_evidence_ids=context,
        )

    def _resolve(self, claim: Claim, links: list[ClaimEvidenceLink]) -> tuple[dict[str, Evidence], dict[str, Source]] | None:
        evidence_by_id: dict[str, Evidence] = {}
        source_by_evidence: dict[str, Source] = {}
        for link in links:
            evidence = self._repository.get_evidence(link.evidence_id)
            if evidence is None or evidence.case_id != claim.case_id:
                return None
            source = self._repository.get_source(evidence.source_id)
            if source is None or source.case_id != evidence.case_id:
                return None
            evidence_by_id[evidence.evidence_id] = evidence
            source_by_evidence[evidence.evidence_id] = source
        return evidence_by_id, source_by_evidence

    @staticmethod
    def _fidelity_for(claim: Claim, supporting: list[Evidence], has_context: bool) -> FidelityStatus | None:
        normalized_claim = " ".join(re.findall(r"[a-z0-9]+", claim.text.casefold()))
        if not normalized_claim:
            return None
        if not supporting:
            return FidelityStatus.AMBIGUOUS if has_context else FidelityStatus.NOT_SUPPORTED
        claim_words = set(normalized_claim.split())
        exact = False
        partial = False
        for evidence in supporting:
            content = evidence.content.casefold()
            if normalized_claim in " ".join(re.findall(r"[a-z0-9]+", content)):
                exact = True
            evidence_words = set(re.findall(r"[a-z0-9]+", content))
            if claim_words and len(claim_words & evidence_words) / len(claim_words) >= 0.6:
                partial = True
        if exact:
            return FidelityStatus.SUPPORTED_BY_EVIDENCE
        if partial:
            return FidelityStatus.PARTIALLY_SUPPORTED
        return FidelityStatus.NOT_SUPPORTED

    @staticmethod
    def _verification_for(
        claim: Claim,
        fidelity: FidelityStatus,
        supporting: list[str],
        contradictory: list[str],
        metadata: dict[str, SourceMetadataResult],
    ) -> VerificationResult:
        accepted = [metadata[item] for item in supporting]
        qualities = [item.quality_class for item in accepted]
        freshnesses = [item.freshness_status for item in accepted]
        quality = max(qualities, key=lambda value: {SourceQuality.OTHER: 0, SourceQuality.STRONG_SECONDARY: 1, SourceQuality.PRIMARY: 2}[value]) if qualities else SourceQuality.OTHER
        freshness = FreshnessStatus.STALE if FreshnessStatus.STALE in freshnesses else (FreshnessStatus.UNKNOWN if FreshnessStatus.UNKNOWN in freshnesses else (FreshnessStatus.AGING if FreshnessStatus.AGING in freshnesses else FreshnessStatus.CURRENT))
        origins = {item.source.origin_source_id or item.source.source_id for item in accepted if item.source is not None}
        duplicate_risk = len(origins) != len(accepted)
        if contradictory:
            status = VerificationStatus.CONFLICTING
        elif fidelity is not FidelityStatus.SUPPORTED_BY_EVIDENCE:
            status = VerificationStatus.INSUFFICIENT_EVIDENCE
        elif freshness is FreshnessStatus.STALE:
            status = VerificationStatus.STALE
        elif freshness is FreshnessStatus.UNKNOWN or quality is SourceQuality.OTHER:
            status = VerificationStatus.INSUFFICIENT_EVIDENCE
        elif quality is SourceQuality.PRIMARY and not duplicate_risk:
            status = VerificationStatus.VERIFIED
        else:
            status = VerificationStatus.SUPPORTED
        return VerificationResult(
            claim_id=claim.claim_id,
            fidelity_status=fidelity,
            status=status,
            source_quality=quality,
            freshness_status=freshness,
            independent_source_count=len(origins),
            conflict_detected=bool(contradictory),
            duplicate_risk=duplicate_risk,
            notes="C11 deterministic Fidelity/Verification outcome; Governance remains deferred.",
        )

    @staticmethod
    def _rejected(code: VerificationErrorCode, message: str) -> VerificationAssessment:
        return VerificationAssessment(
            status=VerificationAssessmentStatus.REJECTED,
            errors=[VerificationError(code=code, message=message)],
        )


def verification_fingerprint(assessment: VerificationAssessment | None) -> str | None:
    """Stable C11 trust-state identity for a C13 final-use decision."""

    if assessment is None or assessment.status is not VerificationAssessmentStatus.ACCEPTED or assessment.claim is None:
        return None
    payload = {
        "claim_id": assessment.claim.claim_id,
        "evidence_ids": assessment.claim.evidence_ids,
        "fidelity_status": assessment.fidelity_status.value if assessment.fidelity_status else None,
        "verification": {
            "fidelity_status": assessment.verification.fidelity_status.value,
            "status": assessment.verification.status.value,
            "source_quality": assessment.verification.source_quality.value,
            "freshness_status": assessment.verification.freshness_status.value,
            "independent_source_count": assessment.verification.independent_source_count,
            "conflict_detected": assessment.verification.conflict_detected,
            "duplicate_risk": assessment.verification.duplicate_risk,
        } if assessment.verification else None,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
