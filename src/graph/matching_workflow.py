from langgraph.graph import StateGraph, END
from src.graph.state import MatchingState

from src.agents.matching.skill_matcher import skill_matcher
from src.agents.matching.domain_matcher import domain_matcher
from src.agents.matching.experience_matcher import experience_matcher
from src.agents.matching.seniority_matcher import seniority_matcher
from src.agents.matching.note_matcher import note_matcher

from src.agents.matching.router_agent import router_agent
from src.agents.matching.aggregator_agent import aggregator_agent

graph = StateGraph(MatchingState)

graph.add_node("router_agent", router_agent)
graph.add_node("aggregator_agent", aggregator_agent)

graph.add_node("skill_matcher", skill_matcher)
graph.add_node("domain_matcher", domain_matcher)
graph.add_node("experience_matcher", experience_matcher)
graph.add_node("seniority_matcher", seniority_matcher)
graph.add_node("note_matcher", note_matcher)



graph.add_conditional_edges(
    "router_agent",
    lambda state: [
        "skill_matcher" if state["router_config"]["activate_matchers"]["skill_matcher"] else None,
    ],
)
# graph.add_conditional_edges(
#     "router_agent",
#     lambda state: [
#         "skill_matcher" if state["router_config"]["activate_matchers"]["skill_matcher"] else None,
#         "domain_matcher" if state["router_config"]["activate_matchers"]["domain_matcher"] else None,
#         "experience_matcher" if state["router_config"]["activate_matchers"]["experience_matcher"] else None,
#         "seniority_matcher" if state["router_config"]["activate_matchers"]["seniority_matcher"] else None,
#     ],
# )
# graph.add_edge("router_matcher", "note_matcher")


graph.add_edge("skill_matcher", END)
# graph.add_edge("composer_agent", END)



graph.set_entry_point("router_agent")

workflow = graph.compile()