def seniority_matcher(state):
    employees = state["employees"]
    router_rules = state["router_result"]["rules"]

    dummy = {emp["name"]: 0.0 for emp in employees}

    state["scores"]["seniority"] = dummy
    return state