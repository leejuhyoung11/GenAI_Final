from langgraph.graph import StateGraph, END
from src.graph.state import MatchingState

from src.agents.matching.skill_matcher import skill_matcher
from src.agents.matching.domain_matcher import domain_matcher
from src.agents.matching.experience_matcher import experience_matcher
from src.agents.matching.seniority_matcher import seniority_matcher
from src.agents.matching.note_matcher import note_matcher

from src.agents.matching.router_agent import router_agent, router_validator
from src.agents.matching.aggregator_agent import aggregator_agent

graph = StateGraph(MatchingState)

graph.add_node("router_agent", router_agent)
graph.add_node("aggregator_agent", aggregator_agent)

graph.add_node("skill_matcher", skill_matcher)
graph.add_node("domain_matcher", domain_matcher)
graph.add_node("experience_matcher", experience_matcher)
graph.add_node("seniority_matcher", seniority_matcher)
graph.add_node("note_matcher", note_matcher)


graph.set_entry_point("router_agent")

# graph.add_edge("router_agent", "router_validator")


# -------------------------
# Conditional matcher edges
# -------------------------
def matcher_conditions(state):

    active = state["router_config"]["active_matchers"]
    branches = []

    if active.get("skill_matcher", False):
        branches.append("skill_matcher")
    if active.get("domain_matcher", False):
        branches.append("domain_matcher")
    if active.get("experience_matcher", False):
        branches.append("experience_matcher")
    if active.get("seniority_matcher", False):
        branches.append("seniority_matcher")

    # fallback -> skip matchers completely
    if not branches:
        return ["note_matcher"]

    return branches


# =========================
# Router -> Conditional Edges
# =========================
graph.add_conditional_edges("router_agent", matcher_conditions)


# -------------------------
# All matchers -> note
# -------------------------
graph.add_edge("skill_matcher", "note_matcher")
graph.add_edge("domain_matcher", "note_matcher")
graph.add_edge("experience_matcher", "note_matcher")
graph.add_edge("seniority_matcher", "note_matcher")


# -------------------------
# note -> aggregator -> END
# -------------------------
graph.add_edge("note_matcher", "aggregator_agent")
graph.add_edge("aggregator_agent", END)




workflow = graph.compile()