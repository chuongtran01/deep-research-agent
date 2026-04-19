from langgraph.graph import StateGraph, START, END
from src.deep_research_agent.state import AgentState
from src.deep_research_agent.nodes.planner import planner_node
from src.deep_research_agent.nodes.question_analyzer import question_analyzer_node
from src.deep_research_agent.nodes.web_search import web_search_node


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("question_analyzer", question_analyzer_node)
    graph.add_node("web_search", web_search_node)

    graph.add_edge(START, "question_analyzer")
    graph.add_edge("question_analyzer", "planner")

    return graph.compile()
