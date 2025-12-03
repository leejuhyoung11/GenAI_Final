from langgraph.graph import StateGraph, END
from src.graph.state import MatchingState

from src.agents.matching.skill_matcher import skill_matcher
from src.agents.matching.domain_matcher import domain_matcher
from src.agents.matching.experience_matcher import experience_matcher
from src.agents.matching.seniority_matcher import seniority_matcher
from src.agents.matching.note_matcher import note_matcher

from src.agents.matching.router_agent import router_agent, router_branch, router_validator
from src.agents.matching.aggregator_agent import aggregator_agent

graph = StateGraph(MatchingState)

graph.add_node("router_agent", router_agent)
graph.add_node("router_validator", router_validator)
graph.add_node("aggregator_agent", aggregator_agent)

graph.add_node("skill_matcher", skill_matcher)
graph.add_node("domain_matcher", domain_matcher)
graph.add_node("experience_matcher", experience_matcher)
graph.add_node("seniority_matcher", seniority_matcher)
graph.add_node("note_matcher", note_matcher)


graph.set_entry_point("router_agent")

graph.add_edge("router_agent", "router_validator")

# =========================
# Router -> Conditional Edges
# =========================
graph.add_conditional_edges(
    "router_validator",
    router_branch,
    {
        "skill_matcher": "skill_matcher",
        "domain_matcher": "domain_matcher",
        "experience_matcher": "experience_matcher",
        "seniority_matcher": "seniority_matcher",
        "note_matcher": "note_matcher",
        "router_agent": "router_agent"  # fallback loop
    }
)


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
graph.add_edge("note_matcher", END)
# graph.add_edge("aggregator_agent", END)




workflow = graph.compile()