from src.deep_research_agent.state import AgentState
from src.deep_research_agent.utils.load_prompt import load_prompt
from src.deep_research_agent.adapters.llm import LLM
from src.deep_research_agent.schemas.evidence import EvidenceExtractorOutput, EvidenceItem
from pydantic import ValidationError

SYSTEM_PROMPT_TEMPLATE = load_prompt("evidence_extractor_system").strip()
USER_PROMPT_TEMPLATE = load_prompt("evidence_extractor_user").strip()

MAX_SOURCE_TEXT_CHARS = 12000


def evidence_extractor_node(state: AgentState) -> AgentState:
    """
    Extract evidence from the most recently fetched document batch.

    Expected state:
    - fetched_documents: list[dict]
      latest batch shape:
      {
          "query": str,
          "subtopic": str,
          "goal": str,
          "evidence_to_collect": list[str] | None,
          "documents": [
              {
                  "title": str,
                  "url": str,
                  "text": str,
                  "search_snippet": str,
                  "score": float | None,
                  "fetch_status": "success" | "failed",
                  "error": str | None,
              }
          ]
      }

    Writes:
    - evidence_items: appends extracted EvidenceItem entries
    - summary: one log entry
    """

    print("Evidence extractor node called")

    fetched_batches = state.get("fetched_documents", [])
    existing_evidence = state.get("evidence_items", [])
    normalized_question = state.get("normalized_question", "")

    if not fetched_batches:
        return {
            "summary": ["No fetched documents to extract evidence from."],
            "evidence_items": existing_evidence,
        }

    latest_batch = fetched_batches[-1]
    query = latest_batch.get("query")
    subtopic = latest_batch.get("subtopic")
    goal = latest_batch.get("goal")
    evidence_to_collect = latest_batch.get("evidence_to_collect")
    documents = latest_batch.get("documents")

    if not documents:
        return {
            "summary": [
                f"Evidence extraction failed: no documents to extract for query '{query}'.",
            ],
            "evidence_items": existing_evidence,
        }

    llm = LLM(
        structured_output=EvidenceExtractorOutput,
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
    )

    new_evidence_items: list[EvidenceItem] = []
    processed_count = 0
    success_count = 0

    for doc in documents:
        processed_count += 1

        if doc.get("error") is not None:
            continue

        title = doc.get("title")
        url = doc.get("url")
        text = doc.get("text")

        if not text:
            continue

        user_prompt = USER_PROMPT_TEMPLATE.format(
            normalized_question=normalized_question,
            subtopic=subtopic,
            goal=goal,
            evidence_to_collect=", ".join(
                evidence_to_collect) if evidence_to_collect else "General evidence",
            title=title,
            url=url,
            text=text[:MAX_SOURCE_TEXT_CHARS],
        )

        try:
            result: EvidenceExtractorOutput = llm.structured_chat(user_prompt)
        except ValidationError as e:
            continue
        except Exception as e:
            continue

        if not result.evidence_items:
            continue

        success_count += 1

        for item in result.evidence_items:
            new_evidence_items.append(EvidenceItem(
                query=query,
                subtopic=subtopic or "General",
                goal=goal or "",
                source_title=title or "Untitled source",
                source_url=url or "",
                source_summary=result.source_summary,
                extracted_claim=item.extracted_claim,
                snippet=item.snippet,
                relevance_score=item.relevance_score,
                stance=item.stance,
                evidence_type=item.evidence_type,
                notes=item.notes,
            ))

    return {
        "evidence_items": existing_evidence + new_evidence_items,
        "summary": [
            f"Extracted {success_count} evidence items from {processed_count} documents for query '{query}'.",
        ],
    }
