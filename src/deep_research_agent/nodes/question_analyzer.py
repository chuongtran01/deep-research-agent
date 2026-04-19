from src.deep_research_agent.state import AgentState
from src.deep_research_agent.schemas.question_analyzer import AnalyzerOutput
from src.deep_research_agent.utils.load_prompt import load_prompt
from src.deep_research_agent.adapters.llm import LLM
from datetime import datetime
from pydantic import ValidationError

SYSTEM_PROMPT_TEMPLATE = load_prompt("question_analyzer_system").strip()
USER_PROMPT_TEMPLATE = load_prompt("question_analyzer_user").strip()


def question_analyzer_node(state: AgentState) -> AgentState:
    print("Question analyzer node called")

    query = state["query"]

    if not query:
        return {
            "summary": ["Question analyzer received an empty query."],
            "final_answer": "I could not analyze the question because no query was provided.",
        }

    llm = LLM(
        structured_output=AnalyzerOutput,
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
    )

    prompt = USER_PROMPT_TEMPLATE.format(
        query=query,
        current_date=datetime.now().strftime("%Y-%m-%d"))

    try:
        result: AnalyzerOutput = llm.structured_chat(prompt)
    except ValidationError as e:
        return {
            "summary": [f"Question analyzer output validation failed: {e}"],
            "final_answer": "I failed to analyze the question due to a validation error.",
        }
    except Exception as e:
        return {
            "summary": [f"Question analyzer failed: {e}"],
            "final_answer": "I failed to analyze the question due to an error.",
        }

    analyzer_summary = (
        f"Normalized question: {result.normalized_question}\n"
        f"Research scope: {result.research_scope}\n"
        f"Ambiguities: {', '.join(result.ambiguities) if result.ambiguities else 'None'}\n"
        f"Time sensitivity: {result.time_sensitivity}\n"
        f"Preferred source types: {', '.join(result.preferred_source_types)}\n"
        f"Analysis notes: {', '.join(result.analysis_notes)}\n"
    )

    return {
        "normalized_question": result.normalized_question,
        "research_scope": result.research_scope,
        "ambiguities": result.ambiguities,
        "time_sensitivity": result.time_sensitivity,
        "preferred_source_types": result.preferred_source_types,
        "summary": [analyzer_summary],
    }
