def domain_matcher(state):
    employees = state["employees"]
    project = state["project"]

    dummy = {emp["name"]: 0.0 for emp in employees}

    state["scores"]["domain"] = dummy
    return state