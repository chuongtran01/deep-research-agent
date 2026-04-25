import json
from datetime import datetime
from pathlib import Path

from src.deep_research_agent.graph import build_graph

if __name__ == "__main__":
    graph = build_graph()
    output_dir = Path(__file__).resolve().parents[1] / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    query = input("Enter your research question: ")

    result = graph.invoke(
        {
            "query": query,
            "plan": [],
            "pending_tasks": [],
            "completed_tasks": [],
            "current_task": None,
            "normalized_question": "",
            "research_scope": "",
            "subtopics": [],
            "ambiguities": [],
            "time_sensitivity": "medium",
            "preferred_source_types": [],
            "search_results": [],
            "evidence_items": [],
            "fetched_documents": [],
            "summary": [],
            "final_answer": ""
        },
        config={
            "recursion_limit": 100,
        }
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"result_{timestamp}.json"
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"Result written to {output_path}")
