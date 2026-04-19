from src.deep_research_agent.graph import build_graph

if __name__ == "__main__":
    graph = build_graph()
    print("Graph built")
    while True:
        query = input("Ask: ")
        result = graph.invoke({"query": query})
        print("Result:", result)
