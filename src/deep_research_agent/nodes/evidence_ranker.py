from src.deep_research_agent.state import AgentState
from src.deep_research_agent.schemas.evidence import EvidenceItem


MIN_RELEVANCE_SCORE = 0.6
MIN_TOTAL_EVIDENCE_ITEMS = 5
MIN_SUBTOPIC_COVERAGE_RATIO = 0.6


def _dedupe_evidence(evidence_items: list[EvidenceItem]) -> list[EvidenceItem]:
    """
    Simple dedupe for MVP.

    Keeps the highest-relevance version of near-duplicate evidence
    based on (source_url, extracted_claim).
    """
    best_by_key: dict[tuple[str, str], EvidenceItem] = {}

    for item in evidence_items:
        key = (item.source_url.strip(), item.extracted_claim.strip().lower())

        existing = best_by_key.get(key)
        if existing is None or item.relevance_score > existing.relevance_score:
            best_by_key[key] = item

    return list(best_by_key.values())


def _filter_relevant_evidence(evidence_items: list[EvidenceItem]) -> list[EvidenceItem]:
    """
    Keep only reasonably relevant evidence for MVP.
    """
    return [
        item
        for item in evidence_items
        if item.relevance_score >= MIN_RELEVANCE_SCORE
    ]


def _sort_evidence(evidence_items: list[EvidenceItem]) -> list[EvidenceItem]:
    """
    Sort descending by relevance score.
    """
    return sorted(
        evidence_items,
        key=lambda item: item.relevance_score,
        reverse=True,
    )


def _compute_subtopic_coverage(
    evidence_items: list[EvidenceItem],
    expected_subtopics: list[str],
) -> tuple[list[str], list[str], float]:
    """
    Returns:
    - covered_subtopics
    - missing_subtopics
    - coverage_ratio
    """

    if not expected_subtopics:
        return [], [], 1.0

    covered = {
        item.subtopic.strip().lower()
        for item in evidence_items
        if item.subtopic.strip()
    }

    normalized_expected = [subtopic.strip() for subtopic in expected_subtopics]

    covered_subtopics = [
        subtopic for subtopic in normalized_expected
        if subtopic.lower() in covered
    ]
    missing_subtopics = [
        subtopic for subtopic in normalized_expected
        if subtopic.lower() not in covered
    ]

    coverage_ratio = len(covered_subtopics) / \
        len(normalized_expected) if normalized_expected else 1.0

    return covered_subtopics, missing_subtopics, coverage_ratio


def evidence_ranker_node(state: AgentState) -> AgentState:
    """
    Rank and evaluate evidence quality for MVP.

    Reads:
    - evidence_items
    - subtopics

    Writes:
    - ranked_evidence_items
    - research_complete
    - missing_subtopics
    - summary
    """

    print("Evidence ranker node called")

    evidence_items = state.get("evidence_items", [])
    expected_subtopics = state.get("subtopics", [])

    if not evidence_items:
        return {
            "ranked_evidence_items": [],
            "research_complete": False,
            "missing_subtopics": expected_subtopics,
            "summary": ["Rank evidence found no evidence items. Research is not complete."],
        }

    deduped_evidences = _dedupe_evidence(evidence_items)
    filtered_evidences = _filter_relevant_evidence(deduped_evidences)
    ranked_evidences = _sort_evidence(filtered_evidences)

    covered_subtopics, missing_subtopics, coverage_ratio = _compute_subtopic_coverage(
        ranked_evidences, expected_subtopics)

    enough_total_evidence = len(ranked_evidences) >= MIN_TOTAL_EVIDENCE_ITEMS
    enough_subtopic_coverage = coverage_ratio >= MIN_SUBTOPIC_COVERAGE_RATIO

    research_complete = enough_total_evidence and enough_subtopic_coverage

    summary = (
        f"Ranked {len(evidence_items)} raw evidence items into {len(ranked_evidences)} retained items. "
        f"Covered {len(covered_subtopics)}/{len(expected_subtopics) if expected_subtopics else 0} subtopics. "
        f"Research complete: {research_complete}."
    )

    if missing_subtopics:
        summary += f" Missing subtopics: {', '.join(missing_subtopics)}."

    return {
        "ranked_evidence_items": ranked_evidences,
        "research_complete": research_complete,
        "missing_subtopics": missing_subtopics,
        "summary": [summary],
    }
