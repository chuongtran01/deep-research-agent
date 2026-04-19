from langgraph.graph import StateGraph, START, END
from src.deep_research_agent.state import AgentState
from src.deep_research_agent.nodes.planner import planner_node
from src.deep_research_agent.nodes.question_analyzer import question_analyzer_node
from src.deep_research_agent.nodes.web_search import web_search_node
from src.deep_research_agent.nodes.search_router import search_router_node
from src.deep_research_agent.nodes.outline_report import outline_report_node
from src.deep_research_agent.nodes.content_fetcher import content_fetcher_node


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("question_analyzer", question_analyzer_node)
    graph.add_node("search_router", search_router_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("content_fetcher", content_fetcher_node)
    graph.add_node("outline_report", outline_report_node)

    graph.add_edge(START, "question_analyzer")
    graph.add_edge("question_analyzer", "planner")
    graph.add_edge("planner", "search_router")

    graph.add_edge("web_search", "content_fetcher")

    return graph.compile()
