from pathlib import Path


ROOT = Path(__file__).parents[2]
SPEC = (ROOT / "13_CARD_SPECIFICATIONS.md").read_text()


def _g01() -> str:
    section = SPEC.split("### V1.2-G01 — Graph Intelligence Contract", 1)[1].split(
        "### V1.2-G02 — Persistent Company Memory", 1
    )[0]
    return " ".join(section.split())


def test_g01_bounds_entities_relations_and_allowed_pairs() -> None:
    contract = _g01()
    for entity in ("Company", "Person", "Technology", "Project", "Event"):
        assert f"`{entity}`" in contract
    for relation in ("LEADS", "PARTNERED_WITH", "DEVELOPS", "USES", "INVOLVED_IN"):
        assert f"`{relation}`" in contract
    for pair in (
        "Person → Company",
        "Person → Project",
        "Company → Company",
        "Company → Technology",
        "Company → Project",
        "Person → Event",
        "Company → Event",
    ):
        assert pair in contract
    assert "Unsupported entity or relation types" in contract
    assert "unsupported pairs fail closed" in contract


def test_g01_requires_canonical_provenance_and_temporal_projection_metadata() -> None:
    contract = _g01()
    for field in (
        "relationship_id",
        "claim_id",
        "evidence_id",
        "source_id",
        "governance_id",
        "research_run_id",
        "created_at",
        "valid_from",
        "valid_to",
        "superseded_by",
    ):
        assert f"`{field}`" in contract
    for status in ("CURRENT", "STALE", "CONFLICTING", "SUPERSEDED"):
        assert f"`{status}`" in contract
    assert "Source, Evidence, Claim, VerificationResult, and GovernanceDecision remain canonical" in contract


def test_g01_closes_trust_memory_and_query_boundaries() -> None:
    contract = _g01()
    assert "BLOCK decision always removes" in contract
    assert "RESTRICT remains explicitly qualified" in contract
    assert "only an explicit Refresh starts a new run" in contract
    assert "Graph queries never refresh or research" in contract
    assert "Maximum traversal depth is **3 edges**" in contract
    for category in (
        "direct relationship",
        "neighborhood",
        "shared connection",
        "cross-company relationship",
        "recurring entity",
        "bounded multi-hop path",
    ):
        assert category in contract


def test_g01_defines_evaluation_and_non_goals() -> None:
    contract = _g01()
    assert "15–20 questions" in contract
    for metric in ("retrieval relevance", "answer completeness", "evidence traceability", "faithfulness", "latency"):
        assert metric in contract
    for non_goal in ("automatic company recommendation", "LinkedIn/social scraping", "replacement or bypass of the existing trust pipeline"):
        assert non_goal in contract
