import os
import json

OUTPUT_DIR = "output"


def save_project_scores(state):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    project_id = state["project"]["project_id"]
    filepath = os.path.join(OUTPUT_DIR, f"{project_id}.json")

    role_scores = state.get("role_scores", {})
    final_result = state.get("final_result", {})

    # Create compact storage dict
    compact = {
        "project_id": project_id,
        "role_scores": {},
        "final_rank": {},
    }

    # Copy partial scores per employee
    for role_name, emp_scores in role_scores.items():

        compact["role_scores"][role_name] = {}

        for emp_id, score_dict in emp_scores.items():

            filtered = {}
            for k, v in score_dict.items():
                if k.endswith("_score") or k.endswith("_reason"):
                    filtered[k] = v

            # include final score if exists
            if role_name in final_result:
                if emp_id in final_result[role_name]:
                    filtered["final_score"] = final_result[role_name][emp_id]["final_score"]

            compact["role_scores"][role_name][emp_id] = filtered

    # Add rank list
    for role_name, result in final_result.items():
        if "_sorted" in result:
            compact["final_rank"][role_name] = [
                [emp_id, data["final_score"]]
                for emp_id, data in result["_sorted"]
            ]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(compact, f, indent=2, ensure_ascii=False)

    print(f"[Aggregator] Saved compact score file: {filepath}")

    return filepath