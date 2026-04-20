from src.deep_research_agent.graph import build_graph

if __name__ == "__main__":
    graph = build_graph()
    while True:
        query = input("Ask: ")
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
        print("Result:", result)
