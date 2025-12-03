# src/agents/matching/aggregator_agent.py

from src.graph.state import MatchingState
from utils.save_state import save_project_scores

def aggregator_agent(state: MatchingState):

    role_scores = state.get("role_scores", {})
    router_cfg = state.get("router_config", {})
    weights = router_cfg.get("matcher_weights", {})
    rules = router_cfg.get("rules", {})

    final_result = {}

    # Iterate roles
    for role_name, emp_scores in role_scores.items():

        final_result[role_name] = {}

        for emp_id, scores in emp_scores.items():

            skill = scores.get("skill_score", 0)
            domain = scores.get("domain_score", 0)
            experience = scores.get("experience_score", 0)
            seniority = scores.get("seniority_score", 0)
            note = scores.get("note_score", 0)

            # weighted calculation
            weighted_sum = (
                weights.get("skill_matcher", 0) * skill +
                weights.get("domain_matcher", 0) * domain +
                weights.get("experience_matcher", 0) * experience +
                weights.get("seniority_matcher", 0) * seniority
            )

            # note overrides
            if note == 1.0:
                final_score = 10.0      # absolute include
            elif note == -1.0:
                final_score = -10.0     # absolute exclude
            else:
                final_score = weighted_sum

            final_result[role_name][emp_id] = {
                "final_score": final_score
            }

        # Sorting
        sorted_list = sorted(
            final_result[role_name].items(),
            key=lambda x: x[1]["final_score"],
            reverse=True
        )

        # Attach sorted version
        final_result[role_name]["_sorted"] = sorted_list

    # store result into global state
    state["final_result"] = final_result

    # Save compact output file
    save_project_scores(state)

    return {
        "final_result": final_result
    }