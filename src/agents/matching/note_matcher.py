def note_matcher(state):
    employees = state["employees"]

    dummy = {emp["name"]: 0.0 for emp in employees}

    state["scores"]["availability"] = dummy
    return state