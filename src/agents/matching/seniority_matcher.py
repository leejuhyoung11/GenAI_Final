# src/agents/matching/seniority_matcher.py
from src.graph.state import MatchingState

def seniority_matcher(state: MatchingState):

    roles = state["project"]["roles"]
    employees = state["employees"]
    list_output = []


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


        for emp in employees:
            emp_id = emp["id"]
            years = emp.get("experience_years", None)

            score = compute_seniority_score(years)
            reason = years if years is not None else 0

            list_output.append({
                "type": "seniority",
                "role": role_name,
                "employee": emp_id,
                "score": score,
                "reason": reason
            })


    return {
        "role_scores": list_output
    }