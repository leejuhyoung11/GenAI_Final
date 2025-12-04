import os
import json

OUTPUT_DIR = "output"


def save_project_scores(project_id, final_result):

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"{project_id}.json")



    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)

    print(f"[Aggregator] Saved final score file: {filepath}")

    return filepath