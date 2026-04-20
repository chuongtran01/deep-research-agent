from typing import Any

from src.deep_research_agent.state import AgentState
from src.deep_research_agent.adapters.fetcher import Fetcher


def content_fetcher_node(state: AgentState) -> AgentState:
    """
    Fetch the content of the search results.
    """

    print("Content fetcher node called")

    search_batches = state.get("search_results", [])
    existing_docs = state.get("fetched_documents", [])

    if not search_batches:
        return {
            "summary": ["No search results to fetch content from."],
        }

    latest_batch = search_batches[-1]

    query = latest_batch.get("query")
    subtopic = latest_batch.get("subtopic")
    goal = latest_batch.get("goal")
    evidence_to_collect = latest_batch.get("evidence_to_collect")
    results = latest_batch.get("results", [])

    fetcher = Fetcher()

    documents = []

    for result in results[:5]:
        row: dict[str, Any] = (
            result if isinstance(result, dict) else result.model_dump()
        )
        url = row.get("url")
        title = row.get("title")
        snippet = row.get("content")
        score = row.get("score")

        if not url:
            continue

        fetched = fetcher.fetch(url)

        documents.append({
            "url": url,
            "title": title,
            "snippet": snippet,
            "score": score,
            "text": fetched.text,
            "error": fetched.error,
        })

    fetched_batch = {
        "query": query,
        "subtopic": subtopic,
        "goal": goal,
        "evidence_to_collect": evidence_to_collect,
        "documents": documents,
    }

    return {
        "fetched_documents": existing_docs + [fetched_batch],
        "summary": [
            f"Fetched {len(documents)} documents from {latest_batch.get('query')}.",
        ],
    }
