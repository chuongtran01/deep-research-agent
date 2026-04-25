from src.deep_research_agent.state import AgentState
from src.deep_research_agent.utils.load_prompt import load_prompt
from src.deep_research_agent.adapters.llm import LLM
from src.deep_research_agent.schemas.report import ReportOutlineOutput
from pydantic import ValidationError
import json

SYSTEM_PROMPT_TEMPLATE = load_prompt("outline_report_system").strip()
USER_PROMPT_TEMPLATE = load_prompt("outline_report_user").strip()

MAX_EVIDENCE_ITEMS = 20


def _evidence_to_prompt_payload(evidence_items: list) -> list[dict]:
    payload = []

    for idx, item in enumerate(evidence_items[:MAX_EVIDENCE_ITEMS], start=1):
        evidence_id = getattr(item, "evidence_id", None) or f"E{idx}"

        payload.append(
            {
                "evidence_id": evidence_id,
                "subtopic": getattr(item, "subtopic", ""),
                "source_title": getattr(item, "source_title", ""),
                "source_url": getattr(item, "source_url", ""),
                "extracted_claim": getattr(item, "extracted_claim", ""),
                "snippet": getattr(item, "snippet", ""),
                "relevance_score": getattr(item, "relevance_score", None),
                "stance": getattr(item, "stance", ""),
                "evidence_type": getattr(item, "evidence_type", ""),
                "notes": getattr(item, "notes", ""),
            }
        )

    return payload


def outline_report_node(state: AgentState) -> AgentState:
    print("Outline report node called")

    ranked_evidence = state.get("ranked_evidence_items", [])

    if not ranked_evidence:
        return {
            "report_outline": None,
            "summary": ["Outline report found no ranked evidence."],
            "final_answer": "I could not create a report outline because no ranked evidence was available.",
        }

    query = state.get("query", "")
    normalized_question = state.get("normalized_question", query)
    research_scope = state.get("research_scope", "Not specified")
    subtopics = state.get("subtopics", [])

    evidence_payload = _evidence_to_prompt_payload(ranked_evidence)

    llm = LLM(
        structured_output=ReportOutlineOutput,
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
    )

    prompt = USER_PROMPT_TEMPLATE.format(
        query=query,
        normalized_question=normalized_question,
        research_scope=research_scope,
        subtopics=", ".join(subtopics) if subtopics else "None",
        ranked_evidence=json.dumps(
            evidence_payload, ensure_ascii=False, indent=2),
    )

    try:
        result: ReportOutlineOutput = llm.structured_chat(prompt)
    except ValidationError as e:
        return {
            "report_outline": None,
            "summary": [f"Outline report validation failed: {e}"],
            "final_answer": "I failed to create a valid report outline.",
        }
    except Exception as e:
        return {
            "report_outline": None,
            "summary": [f"Outline report failed: {e}"],
            "final_answer": "I failed to create a report outline due to an internal error.",
        }

    return {
        "report_outline": result,
        "summary": [
            f"Created report outline with {len(result.sections)} sections and {sum(len(s.claims) for s in result.sections)} planned claims."
        ],
    }
