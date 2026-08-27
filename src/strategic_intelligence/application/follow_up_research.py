"""C12 bounded follow-up research over existing discovery, evidence, and verification boundaries."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from enum import Enum
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.application.evidence_layer import EvidenceLayerService, EvidenceLayerStatus
from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.application.verification import VerificationAssessment, VerificationAssessmentStatus, VerificationService
from strategic_intelligence.domain.models import (
    Case, ClaimEvidenceLink, ClaimEvidenceRelationship, FollowUpResearchAttempt,
    FollowUpResearchStatus, RawFinding, ResearchTask, SourceQuality, SourceType, VerificationStatus,
)


class FollowUpResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    status: FollowUpResearchStatus
    attempts: list[FollowUpResearchAttempt] = Field(default_factory=list)
    verification: VerificationAssessment | None = None
    reason: str


class FollowUpResearchService:
    """Runs at most the task budget; it never governs or upgrades evidence itself."""

    def __init__(self, repository: PersistenceRepository, evidence: EvidenceLayerService, verification: VerificationService) -> None:
        self._repository = repository
        self._evidence = evidence
        self._verification = verification

    def run(
        self, case: Case, claim_id: str, task: ResearchTask,
        discover: Callable[[Case, ResearchTask], list[RawFinding]], *, as_of: date,
    ) -> FollowUpResult:
        claim = self._repository.get_claim(claim_id)
        initial = self._verification.verify(claim_id, as_of=as_of)
        if claim is None or claim.case_id != case.case_id or task.case_id != case.case_id or initial.status is not VerificationAssessmentStatus.ACCEPTED or initial.verification is None:
            return FollowUpResult(status=FollowUpResearchStatus.REJECTED, reason="follow-up requires a persisted same-Case verifiable claim")
        if initial.verification.status in {VerificationStatus.VERIFIED, VerificationStatus.SUPPORTED}:
            return FollowUpResult(status=FollowUpResearchStatus.REJECTED, verification=initial, reason="follow-up is only authorized for unresolved verification gaps")

        attempts: list[FollowUpResearchAttempt] = []
        for number in range(1, task.max_attempts + 1):
            findings = discover(case, task)
            retained = [self._evidence.retain_follow_up_evidence(item, **self._source_classification(case, item)) for item in findings]
            evidence_items = [item.evidence for item in retained if item.status is EvidenceLayerStatus.ACCEPTED and item.evidence is not None]
            if evidence_items:
                self._repository.append_claim_evidence(claim_id, evidence_items, [ClaimEvidenceLink(claim_id=claim_id, evidence_id=item.evidence_id, relationship_type=ClaimEvidenceRelationship.SUPPORTS) for item in evidence_items])
            assessment = self._verification.verify(claim_id, as_of=as_of)
            verification_status = assessment.verification.status if assessment.verification else VerificationStatus.INSUFFICIENT_EVIDENCE
            resolved = assessment.status is VerificationAssessmentStatus.ACCEPTED and verification_status in {VerificationStatus.VERIFIED, VerificationStatus.SUPPORTED}
            terminal = resolved or not evidence_items or number == task.max_attempts
            reason = "verification resolved" if resolved else ("no retainable follow-up evidence" if not evidence_items else "attempt budget exhausted")
            attempt = self._repository.save_follow_up_attempt(FollowUpResearchAttempt(
                case_id=case.case_id, claim_id=claim_id, research_task_id=task.research_task_id,
                attempt_number=number, finding_ids=[item.finding_id for item in findings], evidence_ids=[item.evidence_id for item in evidence_items],
                verification_status=verification_status, terminal=terminal, reason=reason,
            ))
            attempts.append(attempt)
            if terminal:
                return FollowUpResult(status=FollowUpResearchStatus.RESOLVED if resolved else (FollowUpResearchStatus.NO_PROGRESS if not evidence_items else FollowUpResearchStatus.EXHAUSTED), attempts=attempts, verification=assessment, reason=reason)
        raise AssertionError("bounded follow-up loop must terminate")

    @staticmethod
    def _source_classification(case: Case, finding: RawFinding) -> dict[str, object]:
        website = urlsplit(case.company_website or "").hostname
        source = urlsplit(finding.source_url).hostname
        if website and source and source.casefold() == website.casefold():
            return {"source_type": SourceType.OFFICIAL_COMPANY, "quality_class": SourceQuality.PRIMARY}
        return {"source_type": SourceType.OTHER, "quality_class": SourceQuality.OTHER}
