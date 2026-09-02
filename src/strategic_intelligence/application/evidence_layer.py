"""Traceable C09 Source, Evidence, and candidate-Claim construction."""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.domain.models import (
    Claim, ClaimEvidenceLink, ClaimEvidenceRelationship, ClaimType, ContentOrigin, Evidence,
    RawFinding, Source, SourceQuality, SourceType,
)
from urllib.parse import urlsplit
from strategic_intelligence.security import UnsafeExternalUrlError, normalize_external_url


class EvidenceLayerStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class EvidenceLayerErrorCode(str, Enum):
    INVALID_FINDING = "INVALID_FINDING"
    INVALID_CLAIM = "INVALID_CLAIM"
    PERSISTENCE_FAILED = "PERSISTENCE_FAILED"


class EvidenceLayerModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EvidenceLayerError(EvidenceLayerModel):
    code: EvidenceLayerErrorCode
    message: str


class EvidenceLayerResult(EvidenceLayerModel):
    status: EvidenceLayerStatus
    source: Source | None = None
    evidence: Evidence | None = None
    candidate_claim: Claim | None = None
    link: ClaimEvidenceLink | None = None
    sources: list[Source] = Field(default_factory=list)
    evidence_items: list[Evidence] = Field(default_factory=list)
    links: list[ClaimEvidenceLink] = Field(default_factory=list)
    originating_finding_id: str | None = None
    errors: list[EvidenceLayerError] = Field(default_factory=list)


class EvidenceLayerService:
    """Owns C09 traceability, not fidelity or verification judgment."""

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository

    def create_candidate(
        self,
        finding: RawFinding | Sequence[RawFinding],
        *,
        claim_text: str,
        claim_type: ClaimType = ClaimType.FACT,
        relationship: ClaimEvidenceRelationship | Sequence[ClaimEvidenceRelationship] = ClaimEvidenceRelationship.SUPPORTS,
    ) -> EvidenceLayerResult:
        findings = (finding,) if isinstance(finding, RawFinding) else tuple(finding)
        if not findings or not all(self._valid_finding(item) for item in findings):
            return self._rejected(EvidenceLayerErrorCode.INVALID_FINDING, "raw finding lacks required provenance or excerpt")
        if len({item.case_id for item in findings}) != 1:
            return self._rejected(EvidenceLayerErrorCode.INVALID_FINDING, "raw findings for one candidate must belong to one case")
        if not claim_text.strip():
            return self._rejected(EvidenceLayerErrorCode.INVALID_CLAIM, "candidate claim text must not be blank")
        relationships = self._relationships_for(relationship, len(findings))
        if relationships is None:
            return self._rejected(EvidenceLayerErrorCode.INVALID_CLAIM, "each evidence item requires one relationship")
        try:
            sources = [self._repository.save_source(Source(
                case_id=item.case_id, url=item.source_url, title=item.title,
                publisher=item.publisher, publication_date=item.publication_date,
                discovery_url=item.discovery_url, content_origin=item.content_origin,
                source_type=self._source_type(item), quality_class=SourceQuality.OTHER,
            )) for item in findings]
            evidence_items = [self._repository.save_evidence(Evidence(
                case_id=item.case_id, source_id=source.source_id,
                content=item.extracted_content, topic=item.topic, relevance=item.relevance, publication_date=item.publication_date,
            )) for item, source in zip(findings, sources, strict=True)]
            claim = Claim(
                case_id=findings[0].case_id, text=claim_text.strip(), claim_type=claim_type,
                topic=findings[0].topic, evidence_ids=[item.evidence_id for item in evidence_items],
            )
            links = [ClaimEvidenceLink(
                claim_id=claim.claim_id, evidence_id=evidence.evidence_id,
                relationship_type=item_relationship,
            ) for evidence, item_relationship in zip(evidence_items, relationships, strict=True)]
            claim = self._repository.save_claim_with_links(claim, links)
        except Exception:
            return self._rejected(EvidenceLayerErrorCode.PERSISTENCE_FAILED, "traceable evidence could not be persisted")
        return EvidenceLayerResult(
            status=EvidenceLayerStatus.ACCEPTED, source=sources[0], evidence=evidence_items[0],
            candidate_claim=claim, link=links[0], sources=sources,
            evidence_items=evidence_items, links=links,
            originating_finding_id=findings[0].finding_id,
        )

    def retain_follow_up_evidence(self, finding: RawFinding, *, source_type: SourceType = SourceType.OTHER, quality_class: SourceQuality = SourceQuality.OTHER) -> EvidenceLayerResult:
        """Persist C07/C08 provenance without creating or promoting a new Claim."""
        if not self._valid_finding(finding):
            return self._rejected(EvidenceLayerErrorCode.INVALID_FINDING, "raw finding lacks required provenance or excerpt")
        try:
            source = self._repository.save_source(Source(
                case_id=finding.case_id, url=finding.source_url, title=finding.title,
                publisher=finding.publisher, publication_date=finding.publication_date,
                discovery_url=finding.discovery_url, content_origin=finding.content_origin,
                source_type=source_type, quality_class=quality_class,
            ))
            evidence = self._repository.save_evidence(Evidence(
                case_id=finding.case_id, source_id=source.source_id,
                content=finding.extracted_content, topic=finding.topic, relevance=finding.relevance, publication_date=finding.publication_date,
            ))
        except Exception:
            return self._rejected(EvidenceLayerErrorCode.PERSISTENCE_FAILED, "follow-up evidence could not be persisted")
        return EvidenceLayerResult(status=EvidenceLayerStatus.ACCEPTED, source=source, evidence=evidence, sources=[source], evidence_items=[evidence], originating_finding_id=finding.finding_id)

    @staticmethod
    def _valid_finding(finding: RawFinding) -> bool:
        try:
            normalize_external_url(finding.source_url)
        except UnsafeExternalUrlError:
            return False
        return bool(finding.case_id and finding.research_task_id and finding.title.strip() and finding.extracted_content.strip())

    def _source_type(self, finding: RawFinding) -> SourceType:
        """Only acquired first-party public pages receive a first-party type."""
        if finding.content_origin is ContentOrigin.PUBLIC_PAGE:
            host = urlsplit(finding.source_url).hostname or ""
            case = self._repository.get_case(finding.case_id)
            company_host = "" if case is None or not case.company_website else (urlsplit(case.company_website).hostname or "")
            if company_host and (host == company_host or host.endswith(f".{company_host}")):
                return SourceType.OFFICIAL_COMPANY
        return SourceType.OTHER

    @staticmethod
    def _relationships_for(
        relationship: ClaimEvidenceRelationship | Sequence[ClaimEvidenceRelationship], count: int,
    ) -> tuple[ClaimEvidenceRelationship, ...] | None:
        if isinstance(relationship, ClaimEvidenceRelationship):
            return (relationship,) * count
        relationships = tuple(relationship)
        return relationships if len(relationships) == count else None

    @staticmethod
    def _rejected(code: EvidenceLayerErrorCode, message: str) -> EvidenceLayerResult:
        return EvidenceLayerResult(status=EvidenceLayerStatus.REJECTED, errors=[EvidenceLayerError(code=code, message=message)])
