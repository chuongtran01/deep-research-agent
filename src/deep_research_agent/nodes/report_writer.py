from __future__ import annotations

import json
from typing import Any
from pydantic import ValidationError

from src.deep_research_agent.state import AgentState
from src.deep_research_agent.adapters.llm import LLM
from src.deep_research_agent.utils.load_prompt import load_prompt
from src.deep_research_agent.schemas.writer import ReportWriterOutput

SYSTEM_PROMPT_TEMPLATE = load_prompt("report_writer_system").strip()
USER_PROMPT_TEMPLATE = load_prompt("report_writer_user").strip()

MAX_EVIDENCE_ITEMS = 25


def _evidence_to_prompt_payload(evidence_items: list[Any]) -> list[dict[str, Any]]:
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


def report_writer_node(state: AgentState) -> AgentState:
    """
    Write a structured cited draft report.

    Reads:
    - report_outline
    - ranked_evidence_items
    - query
    - normalized_question
    - research_scope

    Writes:
    - draft_report
    - summary
    """
    print("Report writer node called")

    report_outline = state.get("report_outline")
    ranked_evidence = state.get("ranked_evidence_items", [])

    if report_outline is None:
        return {
            "draft_report": None,
            "summary": ["Report writer found no report outline."],
            "final_answer": "I could not write the report because no outline was available.",
        }

    if not ranked_evidence:
        return {
            "draft_report": None,
            "summary": ["Report writer found no ranked evidence."],
            "final_answer": "I could not write the report because no ranked evidence was available.",
        }

    query = state.get("query", "")
    normalized_question = state.get("normalized_question", query)
    research_scope = state.get("research_scope", "Not specified")

    outline_payload = report_outline.model_dump()
    evidence_payload = _evidence_to_prompt_payload(ranked_evidence)

    llm = LLM(
        structured_output=ReportWriterOutput,
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
    )

    prompt = USER_PROMPT_TEMPLATE.format(
        query=query,
        normalized_question=normalized_question,
        research_scope=research_scope,
        report_outline=json.dumps(
            outline_payload, ensure_ascii=False, indent=2),
        ranked_evidence=json.dumps(
            evidence_payload, ensure_ascii=False, indent=2),
    )

    try:
        result: ReportWriterOutput = llm.structured_chat(prompt)
    except ValidationError as e:
        return {
            "draft_report": None,
            "summary": [f"Report writer validation failed: {e}"],
            "final_answer": "I failed to create a valid draft report.",
        }
    except Exception as e:
        return {
            "draft_report": None,
            "summary": [f"Report writer failed: {e}"],
            "final_answer": "I failed to write the report due to an internal error.",
        }

    section_count = len(result.sections)

    return {
        "draft_report": result,
        "summary": [
            f"Report writer created draft with {section_count} sections and confidence '{result.confidence}'."
        ],
    }
