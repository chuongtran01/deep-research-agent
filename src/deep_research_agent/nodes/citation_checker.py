from __future__ import annotations

import re
from typing import Any

from src.deep_research_agent.state import AgentState
from src.deep_research_agent.schemas.citation_check import CitationCheckResult, CitationIssue
from src.deep_research_agent.schemas.writer import ReportWriterOutput
from src.deep_research_agent.schemas.evidence import EvidenceItem


CITATION_PATTERN = re.compile(r"\[([Ee]\d+(?:\s*,\s*[Ee]\d+)*)\]")


def _get_evidence_id(item: EvidenceItem, index: int) -> str:
    return getattr(item, "evidence_id", None) or f"E{index}"


def _extract_citation_ids(text: str) -> list[str]:
    ids: list[str] = []

    for match in CITATION_PATTERN.finditer(text or ""):
        raw_ids = match.group(1).split(",")
        for raw_id in raw_ids:
            ids.append(raw_id.strip().upper())

    return ids


def _report_to_sections(draft_report: ReportWriterOutput) -> list[dict[str, str]]:
    """
    Converts your structured draft report into sections to inspect.
    Supports Pydantic model or dict.
    """
    if draft_report is None:
        return []

    if hasattr(draft_report, "model_dump"):
        data = draft_report.model_dump()
    else:
        data = draft_report

    sections: list[dict[str, str]] = []

    answer_summary = data.get("answer_summary", "")
    if answer_summary:
        sections.append({
            "location": "answer_summary",
            "text": answer_summary,
        })

    for section in data.get("sections", []):
        heading = section.get("heading", "Untitled section")
        content = section.get("content", "")
        sections.append({
            "location": heading,
            "text": content,
        })

    limitations = data.get("limitations", [])
    if limitations:
        sections.append({
            "location": "limitations",
            "text": "\n".join(limitations),
        })

    return sections


def _looks_like_factual_sentence(sentence: str) -> bool:
    """
    Very rough MVP heuristic.

    This intentionally catches many sentences, because citation review should be strict.
    Later your LLM reviewer can handle deeper faithfulness checks.
    """
    sentence = sentence.strip()

    if not sentence:
        return False

    if len(sentence.split()) < 6:
        return False

    # Skip obvious hedging/transition-only lines
    lower = sentence.lower()
    non_factual_starters = (
        "this report",
        "in summary",
        "overall",
        "the evidence is limited",
        "limitations include",
    )

    if lower.startswith(non_factual_starters):
        return False

    return True


def _split_sentences(text: str) -> list[str]:
    """
    Simple sentence splitter for MVP.
    """
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text or "")
        if s.strip()
    ]


def citation_checker_node(state: AgentState) -> AgentState:
    """
    Deterministic citation validator.

    Checks:
    - all citation IDs exist in ranked_evidence_items
    - factual-looking sentences have at least one citation
    - citations are formatted like [E1] or [E1, E2]

    Writes:
    - citation_check
    - citation_check_passed
    - summary
    """
    print("Citation checker node called")

    draft_report = state.get("draft_report")
    ranked_evidence = state.get("ranked_evidence_items", [])

    if draft_report is None:
        result = CitationCheckResult(
            passed=False,
            issues=[
                CitationIssue(
                    issue_type="missing_citation",
                    location="draft_report",
                    text="",
                    message="No draft report was available to check.",
                )
            ],
            cited_evidence_ids=[],
            uncited_evidence_ids=[],
        )

        return {
            "citation_check": result,
            "citation_check_passed": False,
            "summary": ["Citation check failed because no draft report was available."],
        }

    evidence_ids = {
        _get_evidence_id(item, idx).upper()
        for idx, item in enumerate(ranked_evidence, start=1)
    }

    sections = _report_to_sections(draft_report)

    issues: list[CitationIssue] = []
    cited_ids: set[str] = set()

    for section in sections:
        location = section["location"]
        text = section["text"]

        section_citations = _extract_citation_ids(text)
        cited_ids.update(section_citations)

        for citation_id in section_citations:
            if citation_id not in evidence_ids:
                issues.append(
                    CitationIssue(
                        issue_type="unknown_evidence_id",
                        location=location,
                        text=citation_id,
                        message=f"Citation {citation_id} does not exist in ranked evidence.",
                    )
                )

        for sentence in _split_sentences(text):
            if _looks_like_factual_sentence(sentence):
                if not _extract_citation_ids(sentence):
                    issues.append(
                        CitationIssue(
                            issue_type="missing_citation",
                            location=location,
                            text=sentence,
                            message="This factual-looking sentence has no citation.",
                        )
                    )

    uncited_ids = sorted(evidence_ids - cited_ids)

    # MVP: unused evidence is not a failure, but useful to report.
    for evidence_id in uncited_ids:
        issues.append(
            CitationIssue(
                issue_type="unused_evidence",
                location="ranked_evidence_items",
                text=evidence_id,
                message="This evidence item was not cited in the draft report.",
            )
        )

    blocking_issues = [
        issue for issue in issues
        if issue.issue_type in {"missing_citation", "unknown_evidence_id", "malformed_citation"}
    ]

    passed = len(blocking_issues) == 0

    result = CitationCheckResult(
        passed=passed,
        issues=issues,
        cited_evidence_ids=sorted(cited_ids),
        uncited_evidence_ids=uncited_ids,
    )

    return {
        "citation_check": result,
        "citation_check_passed": passed,
        "summary": [
            f"Citation check {'passed' if passed else 'failed'} with {len(blocking_issues)} blocking issues and {len(issues)} total issues."
        ],
    }
