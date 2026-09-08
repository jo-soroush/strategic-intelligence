"""G04: bounded, governed relationship extraction without graph persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from strategic_intelligence.domain.models import (
    ClaimEvidenceRelationship,
    FreshnessStatus,
    GovernanceDecisionStatus,
    RelationshipRecord,
    RelationshipTemporalStatus,
    RelationshipType,
    VerificationStatus,
)
from strategic_intelligence.application.persistence import PersistenceRepository


class RelationshipExtractionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class RelationshipExtractionResult:
    status: RelationshipExtractionStatus
    relationship: RelationshipRecord | None = None
    reason: str | None = None


class GovernedRelationshipExtractor:
    """Builds a transient G04 relationship projection from persisted proof.

    G05 owns durable graph projection. This service therefore never writes a
    relationship record and treats all caller-provided identifiers as claims
    to verify against canonical repository records.
    """

    _ALLOWED_PAIRS = {
        RelationshipType.LEADS: {("Person", "Company"), ("Person", "Project")},
        RelationshipType.PARTNERED_WITH: {("Company", "Company")},
        RelationshipType.DEVELOPS: {("Company", "Technology"), ("Company", "Project")},
        RelationshipType.USES: {("Company", "Technology")},
        RelationshipType.INVOLVED_IN: {
            ("Person", "Project"),
            ("Person", "Event"),
            ("Company", "Project"),
            ("Company", "Event"),
        },
    }

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository

    def extract(
        self,
        relation_type: RelationshipType | str,
        source_entity_id: str,
        target_entity_id: str,
        claim_ids: list[str],
        evidence_ids: list[str],
        research_run_id: str,
        *,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        superseded_by: str | None = None,
    ) -> RelationshipExtractionResult:
        try:
            relation = RelationshipType(relation_type)
        except (TypeError, ValueError):
            return self._reject("unsupported relation type")
        if not source_entity_id or not target_entity_id or source_entity_id == target_entity_id:
            return self._reject("relationship endpoints are invalid")
        if not claim_ids or len(claim_ids) != len(set(claim_ids)):
            return self._reject("relationship requires unique claims")
        if not evidence_ids or len(evidence_ids) != len(set(evidence_ids)):
            return self._reject("relationship requires unique evidence")

        source = self._repository.get_entity(source_entity_id)
        target = self._repository.get_entity(target_entity_id)
        if source is None or target is None:
            return self._reject("relationship endpoint entity is not persisted")
        pair = (source.entity_type.value, target.entity_type.value)
        if pair not in self._ALLOWED_PAIRS[relation]:
            return self._reject("entity pair is not allowed for relation")
        if len(self._repository.find_entities(source.entity_type.value, source.normalized_name, source.context_key)) != 1:
            return self._reject("source entity identity is ambiguous")
        if len(self._repository.find_entities(target.entity_type.value, target.normalized_name, target.context_key)) != 1:
            return self._reject("target entity identity is ambiguous")

        run = self._repository.get_workflow_run(research_run_id)
        if run is None or run.case_id == "":
            return self._reject("research run is not persisted")
        states = [state for state in [run.snapshot, *run.accepted_snapshots.values()] if state is not None]
        if not states:
            return self._reject("research run has no persisted snapshot")
        run_claim_ids = {claim.claim_id for state in states for claim in state.claims}
        run_evidence_ids = {item.evidence_id for state in states for item in state.evidence}
        if not set(claim_ids).issubset(run_claim_ids) or not set(evidence_ids).issubset(run_evidence_ids):
            return self._reject("claim or evidence does not belong to research run")

        claims = []
        support_links = set()
        for claim_id in claim_ids:
            claim = self._repository.get_claim(claim_id)
            if claim is None or claim.case_id != run.case_id:
                return self._reject("claim is missing or crosses case boundary")
            claims.append(claim)
            links = self._repository.get_claim_evidence_links(claim_id)
            support_links.update(
                link.evidence_id
                for link in links
                if link.relationship_type is ClaimEvidenceRelationship.SUPPORTS
            )
        if not set(evidence_ids).issubset(support_links):
            return self._reject("every relationship evidence item needs a SUPPORTS link")

        source_ids: set[str] = set()
        for evidence_id in evidence_ids:
            evidence = self._repository.get_evidence(evidence_id)
            if evidence is None or evidence.case_id != run.case_id:
                return self._reject("evidence is missing or crosses case boundary")
            source_record = self._repository.get_source(evidence.source_id)
            if source_record is None or source_record.case_id != run.case_id:
                return self._reject("evidence source is missing or crosses case boundary")
            source_ids.add(evidence.source_id)

        decisions = []
        for claim in claims:
            candidates = [decision for decision in self._repository.list_governance_decisions(claim.claim_id) if decision.case_id == run.case_id]
            if not candidates:
                return self._reject("claim has no persisted governance decision")
            decisions.append(max(candidates, key=lambda item: item.decided_at))
        if any(decision.decision is GovernanceDecisionStatus.BLOCK for decision in decisions):
            return self._reject("BLOCK governance cannot become graph knowledge")
        governance_status = (
            GovernanceDecisionStatus.RESTRICT
            if any(decision.decision is GovernanceDecisionStatus.RESTRICT for decision in decisions)
            else GovernanceDecisionStatus.PASS
        )

        verifications = []
        for claim in claims:
            candidates = [
                result
                for state in states
                if state is not None
                for result in state.verification_results
                if result.claim_id == claim.claim_id
            ]
            if not candidates:
                return self._reject("claim has no persisted verification result")
            verifications.append(max(candidates, key=lambda item: item.verified_at))

        temporal_status = RelationshipTemporalStatus.CURRENT
        if superseded_by:
            temporal_status = RelationshipTemporalStatus.SUPERSEDED
        elif any(result.status is VerificationStatus.CONFLICTING or result.conflict_detected for result in verifications):
            temporal_status = RelationshipTemporalStatus.CONFLICTING
        elif any(result.status is VerificationStatus.STALE or result.freshness_status is FreshnessStatus.STALE for result in verifications):
            temporal_status = RelationshipTemporalStatus.STALE
        elif any(result.status is VerificationStatus.INSUFFICIENT_EVIDENCE for result in verifications):
            return self._reject("insufficient verification evidence")

        if relation is RelationshipType.PARTNERED_WITH and source_entity_id > target_entity_id:
            source_entity_id, target_entity_id = target_entity_id, source_entity_id
        usable = governance_status is GovernanceDecisionStatus.PASS and temporal_status is RelationshipTemporalStatus.CURRENT
        try:
            record = RelationshipRecord(
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                relation_type=relation,
                claim_ids=claim_ids,
                evidence_ids=evidence_ids,
                source_ids=sorted(source_ids),
                governance_ids=[decision.governance_id for decision in decisions],
                governance_status=governance_status,
                research_run_id=research_run_id,
                valid_from=valid_from,
                valid_to=valid_to,
                superseded_by=superseded_by,
                temporal_status=temporal_status,
                usable=usable,
            )
        except ValueError as error:
            return self._reject(str(error))
        return RelationshipExtractionResult(RelationshipExtractionStatus.ACCEPTED, record)

    @staticmethod
    def _reject(reason: str) -> RelationshipExtractionResult:
        return RelationshipExtractionResult(RelationshipExtractionStatus.REJECTED, reason=reason)
