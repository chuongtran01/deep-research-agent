from __future__ import annotations

import json
from typing import Any
from pydantic import ValidationError

from src.deep_research_agent.state import AgentState
from src.deep_research_agent.adapters.llm import LLM
from src.deep_research_agent.utils.load_prompt import load_prompt
from src.deep_research_agent.schemas.report_review import ReportReviewOutput
from src.deep_research_agent.schemas.writer import ReportWriterOutput
from src.deep_research_agent.schemas.evidence import EvidenceItem


SYSTEM_PROMPT_TEMPLATE = load_prompt("report_reviewer_system").strip()
USER_PROMPT_TEMPLATE = load_prompt("report_reviewer_user").strip()

MAX_EVIDENCE_ITEMS = 25


def _evidence_to_prompt_payload(evidence_items: list[EvidenceItem]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []

    for idx, item in enumerate(evidence_items[:MAX_EVIDENCE_ITEMS], start=1):
        evidence_id = getattr(item, "evidence_id", None) or f"E{idx}"

        payload.append(
            {
                "evidence_id": evidence_id,
                "subtopic": getattr(item, "subtopic", ""),
                "source_title": getattr(item, "source_title", ""),
                "source_url": getattr(item, "source_url", ""),
                "source_summary": getattr(item, "source_summary", ""),
                "extracted_claim": getattr(item, "extracted_claim", ""),
                "snippet": getattr(item, "snippet", ""),
                "relevance_score": getattr(item, "relevance_score", None),
                "stance": getattr(item, "stance", ""),
                "evidence_type": getattr(item, "evidence_type", ""),
                "notes": getattr(item, "notes", ""),
            }
        )

    return payload


def _render_final_answer(draft_report: ReportWriterOutput) -> str:
    """
    Convert structured draft report into user-facing markdown.
    """

    data = draft_report

    if not data:
        return "No draft report was available."

    lines: list[str] = []

    title = data.get("title")
    if title:
        lines.append(f"# {title}")
        lines.append("")

    answer_summary = data.get("answer_summary")
    if answer_summary:
        lines.append("## Summary")
        lines.append(answer_summary)
        lines.append("")

    for section in data.get("sections", []):
        heading = section.get("heading", "Untitled Section")
        content = section.get("content", "")

        lines.append(f"## {heading}")
        lines.append(content)
        lines.append("")

    limitations = data.get("limitations", [])
    if limitations:
        lines.append("## Limitations")
        for item in limitations:
            lines.append(f"- {item}")
        lines.append("")

    confidence = data.get("confidence")
    if confidence:
        lines.append(f"**Confidence:** {confidence}")

    return "\n".join(lines).strip()


def report_reviewer_node(state: AgentState) -> AgentState:
    print("Review report node called")

    draft_report = state.get("draft_report")
    ranked_evidence = state.get("ranked_evidence_items", [])
    citation_check = state.get("citation_check")
    citation_check_passed = state.get("citation_check_passed", False)

    if draft_report is None:
        return {
            "review_passed": False,
            "review_result": None,
            "summary": ["Review report found no draft report."],
            "final_answer": "I could not review the report because no draft report was available.",
        }

    if not ranked_evidence:
        return {
            "review_passed": False,
            "review_result": None,
            "summary": ["Review report found no ranked evidence."],
            "final_answer": "I could not review the report because no ranked evidence was available.",
        }

    query = state.get("query", "")
    normalized_question = state.get("normalized_question", query)
    research_scope = state.get("research_scope", "Not specified")

    draft_payload = draft_report.model_dump()
    evidence_payload = _evidence_to_prompt_payload(ranked_evidence)
    citation_payload = citation_check.model_dump()

    llm = LLM(
        structured_output=ReportReviewOutput,
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
    )

    prompt = USER_PROMPT_TEMPLATE.format(
        query=query,
        normalized_question=normalized_question,
        research_scope=research_scope,
        draft_report=json.dumps(draft_payload, ensure_ascii=False, indent=2),
        ranked_evidence=json.dumps(
            evidence_payload, ensure_ascii=False, indent=2),
        citation_check=json.dumps(
            citation_payload, ensure_ascii=False, indent=2),
    )

    try:
        result: ReportReviewOutput = llm.structured_chat(prompt)
    except ValidationError as e:
        return {
            "review_passed": False,
            "review_result": None,
            "summary": [f"Report review validation failed: {e}"],
            "final_answer": "I failed to produce a valid report review.",
        }
    except Exception as e:
        return {
            "review_passed": False,
            "review_result": None,
            "summary": [f"Report review failed: {e}"],
            "final_answer": "I failed to review the report due to an internal error.",
        }

    review_passed = result.verdict == "pass" and citation_check_passed

    if review_passed:
        final_answer = _render_final_answer(draft_report)
        summary = (
            f"Review passed. Verdict: {result.verdict}. "
            f"Issues found: {len(result.issues)}."
        )
    else:
        final_answer = (
            "The draft report did not pass review yet.\n\n"
            f"Review verdict: {result.verdict}\n"
            f"Citation check passed: {citation_check_passed}\n"
            f"Issues found: {len(result.issues)}\n\n"
            "Top issues:\n"
        )

        for issue in result.issues[:5]:
            final_answer += (
                f"- [{issue.severity}] {issue.issue_type}: "
                f"{issue.explanation}\n"
            )

        summary = (
            f"Review did not pass. Verdict: {result.verdict}. "
            f"Citation check passed: {citation_check_passed}. "
            f"Issues found: {len(result.issues)}."
        )

    return {
        "review_result": result,
        "review_passed": review_passed,
        "summary": [summary],
        "final_answer": final_answer,
    }
