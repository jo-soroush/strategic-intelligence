"""G03 stable, conservative entity identity and alias resolution."""

from __future__ import annotations

import unicodedata
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.domain.models import ClaimEvidenceRelationship, EntityAlias, EntityRecord, EntityType, GovernanceDecisionStatus


def canonicalize_entity_label(value: str) -> str:
    """Apply only Unicode compatibility, whitespace, and case normalization."""
    return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()


def canonicalize_context(value: str | None) -> str | None:
    return None if value is None else canonicalize_entity_label(value)


class ResolutionStatus(str, Enum):
    CREATED = "CREATED"
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"


class EntityResolutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    status: ResolutionStatus
    entity: EntityRecord | None = None
    candidates: list[EntityRecord] = Field(default_factory=list)
    reason: str | None = None


class EntityResolutionService:
    """Resolves only stable canonical labels or evidence-backed aliases."""

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository

    def resolve(
        self,
        entity_type: EntityType,
        label: str,
        *,
        context_key: str | None = None,
        supporting_claim_ids: list[str] | None = None,
        supporting_evidence_ids: list[str] | None = None,
        governance_id: str | None = None,
        governance_status: GovernanceDecisionStatus | None = None,
    ) -> EntityResolutionResult:
        normalized = canonicalize_entity_label(label)
        context = canonicalize_context(context_key)
        if not normalized:
            return EntityResolutionResult(status=ResolutionStatus.AMBIGUOUS, reason="entity label is blank")

        exact = [item for item in self._repository.list_entities() if item.entity_type is entity_type and item.normalized_name == normalized and item.context_key == context]
        if len(exact) == 1:
            return EntityResolutionResult(status=ResolutionStatus.RESOLVED, entity=exact[0])
        if len(exact) > 1:
            return EntityResolutionResult(status=ResolutionStatus.AMBIGUOUS, candidates=exact, reason="duplicate canonical entities exist")

        same_name = [item for item in self._repository.list_entities() if item.entity_type is entity_type and any(alias.normalized_alias == normalized and alias.context_key == context for alias in item.aliases)]
        if same_name:
            if len(same_name) > 1:
                return EntityResolutionResult(status=ResolutionStatus.AMBIGUOUS, candidates=same_name, reason="alias matches multiple entities")
            if not self._alias_support_is_sufficient(supporting_claim_ids, supporting_evidence_ids, governance_id, governance_status):
                return EntityResolutionResult(status=ResolutionStatus.AMBIGUOUS, candidates=same_name, reason="alias reuse requires governed Claim and Evidence support")
            return EntityResolutionResult(status=ResolutionStatus.RESOLVED, entity=same_name[0])

        # A same-name Person is never resolved without a contextual discriminator.
        if entity_type is EntityType.PERSON:
            prior = [item for item in self._repository.list_entities() if item.entity_type is entity_type and item.normalized_name == normalized]
            if prior and context is None:
                return EntityResolutionResult(status=ResolutionStatus.AMBIGUOUS, candidates=prior, reason="same-name people require context")

        entity = EntityRecord(
            entity_type=entity_type,
            canonical_name=" ".join(unicodedata.normalize("NFKC", label).split()),
            normalized_name=normalized,
            context_key=context,
        )
        self._repository.save_entity(entity)
        return EntityResolutionResult(status=ResolutionStatus.CREATED, entity=entity)

    def add_alias(
        self,
        entity_id: str,
        alias: str,
        *,
        context_key: str | None,
        supporting_claim_ids: list[str],
        supporting_evidence_ids: list[str],
        governance_id: str,
        governance_status: GovernanceDecisionStatus,
    ) -> EntityRecord:
        entity = self._repository.get_entity(entity_id)
        if entity is None:
            raise KeyError("entity not found")
        if not self._alias_support_is_sufficient(supporting_claim_ids, supporting_evidence_ids, governance_id, governance_status):
            raise ValueError("entity alias requires governed Claim and Evidence support")
        normalized = canonicalize_entity_label(alias)
        if not normalized:
            raise ValueError("entity alias is blank")
        if any(item.normalized_alias == normalized and item.context_key == canonicalize_context(context_key) for item in entity.aliases):
            return entity
        updated = entity.model_copy(update={
            "aliases": [*entity.aliases, EntityAlias(
                alias=" ".join(unicodedata.normalize("NFKC", alias).split()),
                normalized_alias=normalized,
                context_key=canonicalize_context(context_key),
                supporting_claim_ids=supporting_claim_ids,
                supporting_evidence_ids=supporting_evidence_ids,
                governance_id=governance_id,
                governance_status=governance_status,
            )],
            "updated_at": datetime.now(timezone.utc),
        })
        return self._repository.save_entity(updated)

    def _alias_support_is_sufficient(
        self,
        claim_ids: list[str] | None,
        evidence_ids: list[str] | None,
        governance_id: str | None,
        governance_status: GovernanceDecisionStatus | None,
    ) -> bool:
        if not claim_ids or not evidence_ids or not governance_id or governance_status is not GovernanceDecisionStatus.PASS:
            return False
        evidence_set = set(evidence_ids)
        for claim_id in claim_ids:
            claim = self._repository.get_claim(claim_id)
            if claim is None or claim.case_id == "":
                return False
            links = self._repository.get_claim_evidence_links(claim_id)
            linked_support = {
                link.evidence_id for link in links
                if link.relationship_type is ClaimEvidenceRelationship.SUPPORTS
            }
            if not evidence_set.intersection(linked_support):
                return False
            for evidence_id in evidence_set.intersection(linked_support):
                evidence = self._repository.get_evidence(evidence_id)
                if evidence is None or evidence.case_id != claim.case_id:
                    return False
                if self._repository.get_source(evidence.source_id) is None:
                    return False
            decisions = self._repository.list_governance_decisions(claim_id)
            if not decisions or decisions[-1].governance_id != governance_id or decisions[-1].decision is not GovernanceDecisionStatus.PASS:
                return False
        return True
