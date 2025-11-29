from langgraph.graph import StateGraph, END
from src.graph.state import MatchingState

from src.agents.matching.skill_matcher import skill_matcher

from src.agents.matching.router_agent import router_agent
from src.agents.matching.project_requirement_agent import project_requirement_agent
from src.agents.matching.composer_agent import composer_agent

graph = StateGraph(MatchingState)

graph.add_node("router_agent", router_agent)
graph.add_node("skill_matcher", skill_matcher)

# graph.add_node("project_requirement_agent", project_requirement_agent)
# graph.add_node("composer_agent", composer_agent)

graph.set_entry_point("router_agent")


graph.add_edge("router_agent", "skill_matcher")
graph.add_edge("skill_matcher", END)
# graph.add_edge("composer_agent", END)

workflow = graph.compile()