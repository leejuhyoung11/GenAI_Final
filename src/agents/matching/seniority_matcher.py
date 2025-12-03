# src/agents/matching/seniority_matcher.py
from src.graph.state import MatchingState

def seniority_matcher(state: MatchingState):

    roles = state["project"]["roles"]
    employees = state["employees"]

    # Initialize role_scores if not exists
    if "role_scores" not in state or state["role_scores"] is None:
        state["role_scores"] = {}

    def compute_seniority_score(years: int):
        if years is None:
            return 0.0
        if years < 2:
            return 0.2
        if years < 4:
            return 0.4
        if years < 7:
            return 0.7
        if years < 10:
            return 0.85
        return 1.0

    for role in roles:
        role_name = role["role_name"]

        print(f"\n[SeniorityMatcher] Processing role: {role_name}")

        if role_name not in state["role_scores"]:
            state["role_scores"][role_name] = {}

        for emp in employees:
            emp_id = emp["id"]
            years = emp.get("experience_years", None)

            score = compute_seniority_score(years)
            reason = years if years is not None else 0

            if emp_id not in state["role_scores"][role_name]:
                state["role_scores"][role_name][emp_id] = {}

            state["role_scores"][role_name][emp_id]["seniority_score"] = score
            state["role_scores"][role_name][emp_id]["seniority_reason"] = reason

    return {
        "role_scores": state["role_scores"]
    }