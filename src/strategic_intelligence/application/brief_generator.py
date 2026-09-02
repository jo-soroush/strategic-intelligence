"""C16 deterministic Brief presentation over accepted C15 governed analysis."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.application.strategic_analysis import (
    StrategicAnalysisResult,
    StrategicAnalysisStatus,
    TrustedClaimContext,
    normalize_formatting_equivalent_text,
)
from strategic_intelligence.domain.models import (
    AnalysisItem, Case, Claim, ClaimType, GovernanceDecisionStatus, MeetingBrief, MeetingQuestion, MeetingTakeaway, Opportunity,
    QuickBrief, StrategicAnalysis,
)


class BriefGenerationStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class BriefGenerationErrorCode(str, Enum):
    MISSING_CASE = "MISSING_CASE"
    INVALID_ANALYSIS = "INVALID_ANALYSIS"
    INVALID_PROVENANCE = "INVALID_PROVENANCE"
    NO_MEANINGFUL_CONTENT = "NO_MEANINGFUL_CONTENT"


class BriefGenerationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class BriefGenerationError(BriefGenerationModel):
    code: BriefGenerationErrorCode
    message: str


class BriefGenerationResult(BriefGenerationModel):
    status: BriefGenerationStatus
    quick_brief: QuickBrief | None = None
    full_brief: MeetingBrief | None = None
    errors: list[BriefGenerationError] = Field(default_factory=list)


class BriefGeneratorService:
    """Formats only a validated C15 result; it never re-researches or re-governs."""

    _QUICK_ITEM_LIMIT = 5
    _QUICK_GAP_LIMIT = 5
    _MEETING_TAKEAWAY_LIMIT = 5
    _MAX_ANALYSIS_ITEMS_PER_SECTION = 20
    _MAX_KNOWLEDGE_GAPS = 20
    _MAX_TEXT_LENGTH = 2_000
    _MAX_CLAIM_REFERENCES = 5
    _MAX_SOURCE_REFERENCES = 100

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository

    def generate(self, case_id: str, analysis_result: StrategicAnalysisResult) -> BriefGenerationResult:
        case = self._repository.get_case(case_id)
        if case is None:
            return self._rejected(BriefGenerationErrorCode.MISSING_CASE, "brief generation requires a persisted Case")
        if analysis_result.status is not StrategicAnalysisStatus.ACCEPTED or analysis_result.analysis is None or analysis_result.context is None:
            return self._rejected(BriefGenerationErrorCode.INVALID_ANALYSIS, "brief generation requires an accepted governed strategic analysis")
        analysis = analysis_result.analysis
        if analysis.case_id != case_id or analysis_result.context.case_id != case_id:
            return self._rejected(BriefGenerationErrorCode.INVALID_ANALYSIS, "analysis does not belong to the requested Case")
        if error := self._validate_bounds(analysis):
            return self._rejected(BriefGenerationErrorCode.INVALID_ANALYSIS, error)
        if error := self._validate_analysis(case, analysis, analysis_result.context.claims):
            return self._rejected(BriefGenerationErrorCode.INVALID_PROVENANCE, error)
        if not self._meaningful(analysis):
            return self._rejected(BriefGenerationErrorCode.NO_MEANINGFUL_CONTENT, "brief requires meaningful governed material")

        sources = self._source_references(case, analysis)
        if sources is None:
            return self._rejected(BriefGenerationErrorCode.INVALID_PROVENANCE, "brief source references are not traceable to the requested Case")
        gaps = analysis.knowledge_gaps[: self._QUICK_GAP_LIMIT]
        quick = QuickBrief(
            case_id=case_id,
            key_facts=self._limited(self._facts(analysis)),
            key_signals=self._limited(analysis.strategic_signals),
            top_opportunities=analysis.opportunity_areas[: self._QUICK_ITEM_LIMIT],
            top_questions=analysis.smart_questions[: self._QUICK_ITEM_LIMIT],
            major_risks=self._limited(analysis.risks),
            knowledge_gaps=gaps,
            omitted_restriction_count=analysis.omitted_restriction_count,
            omitted_knowledge_gap_count=len(analysis.knowledge_gaps) - len(gaps),
        )
        full = MeetingBrief(
            case_id=case_id,
            version=1,
            executive_summary=f"Prepare {case.executive_name} meeting: {case.meeting_goal}",
            meeting_takeaways=self._meeting_takeaways(analysis),
            company_situation=analysis.company_direction,
            strategy_direction=analysis.project_meaning,
            projects_client_cases=analysis.project_meaning,
            ai_activity=[],
            executive_intelligence=analysis.executive_priorities,
            strategic_signals=analysis.strategic_signals,
            opportunity_map=analysis.opportunity_areas,
            user_relevance=analysis.user_relevance,
            meeting_strategy=analysis.meeting_topics,
            questions=analysis.smart_questions,
            do_not_assume=self._do_not_assume(analysis),
            knowledge_gaps=[item.text for item in analysis.knowledge_gaps],
            knowledge_gap_details=analysis.knowledge_gaps,
            source_references=sources,
        )
        return BriefGenerationResult(status=BriefGenerationStatus.ACCEPTED, quick_brief=quick, full_brief=full)

    def _validate_analysis(self, case: Case, analysis: StrategicAnalysis, context_claims: list[TrustedClaimContext]) -> str | None:
        permitted = {item.claim_id: item for item in context_claims}
        for item in self._all_items(analysis):
            if not item.related_claim_ids:
                if item in analysis.user_relevance and item.type is ClaimType.RECOMMENDATION:
                    continue
                if item in analysis.knowledge_gaps and item.is_restricted and item.rationale:
                    continue
                return "brief item lacks Claim provenance"
            for claim_id in item.related_claim_ids:
                if claim_id not in permitted:
                    return "brief references a Claim outside accepted C15 context"
                if error := self._validate_claim(case, self._repository.get_claim(claim_id)):
                    return error
            if len(item.related_claim_ids) != len(set(item.related_claim_ids)):
                return "brief item contains duplicate Claim references"
            if item.type is ClaimType.FACT:
                claim = self._repository.get_claim(item.related_claim_ids[0]) if len(item.related_claim_ids) == 1 else None
                if (
                    len(item.related_claim_ids) != 1
                    or permitted[item.related_claim_ids[0]].claim_type is not ClaimType.FACT
                    or permitted[item.related_claim_ids[0]].governance_decision is not GovernanceDecisionStatus.PASS
                    or claim is None
                    or self._normalized(item.text) != self._normalized(claim.text)
                ):
                    return "FACT brief item lacks factual C15 provenance"
            if error := self._validate_restriction(item.is_restricted, item.restriction_reason_codes, item.related_claim_ids, permitted):
                return error
        for item in [*analysis.opportunity_areas, *analysis.smart_questions]:
            if item.case_id != case.case_id:
                return "brief nested item does not belong to the requested Case"
            if not item.related_claim_ids:
                return "brief nested item lacks Claim provenance"
            for claim_id in item.related_claim_ids:
                if claim_id not in permitted:
                    return "brief references a Claim outside accepted C15 context"
                if error := self._validate_claim(case, self._repository.get_claim(claim_id)):
                    return error
            if len(item.related_claim_ids) != len(set(item.related_claim_ids)):
                return "brief nested item contains duplicate Claim references"
            if error := self._validate_restriction(item.is_restricted, item.restriction_reason_codes, item.related_claim_ids, permitted):
                return error
        return None

    def _validate_bounds(self, analysis: StrategicAnalysis) -> str | None:
        sections = (
            analysis.company_direction, analysis.executive_priorities, analysis.project_meaning,
            analysis.strategic_signals, analysis.user_relevance, analysis.meeting_topics,
            analysis.risks,
        )
        if any(len(section) > self._MAX_ANALYSIS_ITEMS_PER_SECTION for section in sections):
            return "brief input exceeds the per-section item limit"
        if len(analysis.opportunity_areas) > self._MAX_ANALYSIS_ITEMS_PER_SECTION or len(analysis.smart_questions) > self._MAX_ANALYSIS_ITEMS_PER_SECTION:
            return "brief input exceeds the nested-item limit"
        if len(analysis.knowledge_gaps) > self._MAX_KNOWLEDGE_GAPS:
            return "brief input exceeds the knowledge-gap limit"
        values = [
            # Canonical FACT text is validated immediately afterwards against
            # its persisted PASS FACT Claim.  It is not model-authored output
            # and therefore is not subject to the LLM-output text bound.
            item.text for item in self._all_items(analysis)
            if item.type is not ClaimType.FACT
        ]
        values.extend(item.rationale for item in self._all_items(analysis) if item.rationale is not None)
        values.extend(
            value for item in analysis.opportunity_areas
            for value in (item.title, item.description, item.relevance_to_goal, item.confidence, item.qualification, *item.assumptions)
            if value is not None
        )
        values.extend(
            value for item in analysis.smart_questions
            for value in (item.question, item.reason, item.qualification)
            if value is not None
        )
        if any(len(value) > self._MAX_TEXT_LENGTH for value in values):
            return "brief input exceeds the text-length limit"
        if any(len(item.related_claim_ids) > self._MAX_CLAIM_REFERENCES for item in self._all_items(analysis)):
            return "brief input exceeds the Claim-reference limit"
        return None

    @staticmethod
    def _validate_restriction(is_restricted: bool, reasons: list, claim_ids: list[str], permitted: dict[str, TrustedClaimContext]) -> str | None:
        expected = {
            reason for claim_id in claim_ids for reason in permitted[claim_id].governance_reasons
            if permitted[claim_id].governance_decision is GovernanceDecisionStatus.RESTRICT
        }
        if expected and (not is_restricted or not expected.issubset(set(reasons))):
            return "brief removes required C15 restriction metadata"
        return None

    def _validate_claim(self, case: Case, claim: Claim | None) -> str | None:
        if claim is None or claim.case_id != case.case_id:
            return "brief Claim does not belong to the requested Case"
        for evidence_id in claim.evidence_ids:
            evidence = self._repository.get_evidence(evidence_id)
            if evidence is None or evidence.case_id != case.case_id:
                return "brief Evidence does not belong to the requested Case"
            source = self._repository.get_source(evidence.source_id)
            if source is None or source.case_id != case.case_id:
                return "brief Source does not belong to the requested Case"
        return None

    def _source_references(self, case: Case, analysis: StrategicAnalysis) -> list[str] | None:
        references: list[str] = []
        seen: set[str] = set()
        for item in self._all_items(analysis):
            for claim_id in item.related_claim_ids:
                claim = self._repository.get_claim(claim_id)
                if claim is None:
                    return None
                for evidence_id in claim.evidence_ids:
                    evidence = self._repository.get_evidence(evidence_id)
                    source = None if evidence is None else self._repository.get_source(evidence.source_id)
                    if evidence is None or source is None or evidence.case_id != case.case_id or source.case_id != case.case_id:
                        return None
                    reference = f"{source.title}: {source.url}"
                    if reference not in seen:
                        seen.add(reference)
                        references.append(reference)
                        if len(references) > self._MAX_SOURCE_REFERENCES:
                            return None
        return references

    @staticmethod
    def _all_items(analysis: StrategicAnalysis) -> list[AnalysisItem]:
        return [
            *analysis.company_direction, *analysis.executive_priorities, *analysis.project_meaning,
            *analysis.strategic_signals, *analysis.user_relevance, *analysis.meeting_topics,
            *analysis.risks, *analysis.knowledge_gaps,
            *[BriefGeneratorService._opportunity_as_item(item) for item in analysis.opportunity_areas],
            *[BriefGeneratorService._question_as_item(item) for item in analysis.smart_questions],
        ]

    @staticmethod
    def _opportunity_as_item(item: Opportunity) -> AnalysisItem:
        """Preserve C15-governed metadata when validating nested Brief input."""

        return AnalysisItem(
            text=item.title,
            type=ClaimType.INFERENCE,
            related_claim_ids=item.related_claim_ids,
            rationale=item.qualification,
            is_restricted=item.is_restricted,
            restriction_reason_codes=item.restriction_reason_codes,
        )

    @staticmethod
    def _question_as_item(item: MeetingQuestion) -> AnalysisItem:
        """Preserve C15-governed metadata when validating nested Brief input."""

        return AnalysisItem(
            text=item.question,
            type=ClaimType.RECOMMENDATION,
            related_claim_ids=item.related_claim_ids,
            rationale=item.qualification,
            is_restricted=item.is_restricted,
            restriction_reason_codes=item.restriction_reason_codes,
        )

    @staticmethod
    def _facts(analysis: StrategicAnalysis) -> list[AnalysisItem]:
        return [item for item in [*analysis.company_direction, *analysis.executive_priorities] if item.type is ClaimType.FACT]

    @classmethod
    def _meeting_takeaways(cls, analysis: StrategicAnalysis) -> list[MeetingTakeaway]:
        """Select concise, already-validated C15 non-FACT material for meeting use.

        This is presentation-only: it copies exact text and authoritative
        qualification/provenance metadata without interpreting it.
        """

        candidates = [
            *(item for item in analysis.executive_priorities if item.type is not ClaimType.FACT),
            *(item for item in analysis.strategic_signals if item.type is not ClaimType.FACT),
            *(cls._opportunity_as_item(item) for item in analysis.opportunity_areas),
            *(cls._question_as_item(item) for item in analysis.smart_questions),
            *(item for item in analysis.risks if item.type is not ClaimType.FACT),
        ]
        return [
            MeetingTakeaway(
                text=item.text,
                type=item.type,
                supporting_claim_ids=list(item.related_claim_ids),
                rationale=item.rationale,
                is_restricted=item.is_restricted,
                restriction_reason_codes=list(item.restriction_reason_codes),
            )
            for item in candidates[: cls._MEETING_TAKEAWAY_LIMIT]
        ]

    @staticmethod
    def _limited(items: list[AnalysisItem]) -> list[AnalysisItem]:
        return items[: BriefGeneratorService._QUICK_ITEM_LIMIT]

    @staticmethod
    def _meaningful(analysis: StrategicAnalysis) -> bool:
        return any((analysis.company_direction, analysis.executive_priorities, analysis.project_meaning, analysis.strategic_signals, analysis.opportunity_areas, analysis.meeting_topics, analysis.smart_questions, analysis.risks))

    @staticmethod
    def _do_not_assume(analysis: StrategicAnalysis) -> list[str]:
        values = [item.rationale or item.text for item in analysis.knowledge_gaps if item.is_restricted]
        if analysis.omitted_restriction_count:
            values.append(f"{analysis.omitted_restriction_count} additional governed restriction(s) were omitted from bounded analysis context.")
        return values

    @staticmethod
    def _normalized(value: str) -> str:
        return normalize_formatting_equivalent_text(value)

    @staticmethod
    def _rejected(code: BriefGenerationErrorCode, message: str) -> BriefGenerationResult:
        return BriefGenerationResult(status=BriefGenerationStatus.REJECTED, errors=[BriefGenerationError(code=code, message=message)])
