# src/agents/matching/note_matcher.py

import json
from utils.prompt_loader import load_prompt
from utils.load_config import load_config
from src.models.provider_factory import LLMProviderFactory
from src.graph.state import MatchingState


config = load_config()
note_matcher_cfg = config["models"]["note"]
note_llm = LLMProviderFactory.load_from_config(note_matcher_cfg)


def note_matcher(state: MatchingState):

    roles = state["project"]["roles"]
    employees = state["employees"]
    rules = state["router_config"]["rules"]
    outputs = []


    prompt_template = load_prompt("note_matcher.prompt")

    # For each role run LLM
    for role in roles:
        role_name = role["role_name"]

        print(f"\n[NoteMatcher] Processing role: {role_name}")


        # --- 1. Build Prompt ---
        prompt = prompt_template.format(
            rules_json=json.dumps(rules, indent=2),
            role_json=json.dumps(role, indent=2),
            employees_json=json.dumps(employees, indent=2),
        )

        # --- 2. Call LLM ---
        raw_output = note_llm.call(prompt)

        print("[NoteMatcher] Raw Output:")
        print(raw_output)

        # --- 3. Parse JSON ---
        try:
            parsed = json.loads(raw_output)
            results = parsed.get("results", {})
        except Exception as e:
            print(f"[NoteMatcher] JSON Parse ERROR for {role_name}: {e}")

            # Fallback: everyone gets note_score=0.0
            results = {
                emp["id"]: {
                    "note_score": 0.0,
                    "reason": "LLM parsing failed; default fallback."
                }
                for emp in employees
            }

        # --- 4. Insert into state["role_scores"] ---
        for emp_id, r in results.items():
            outputs.append({
                    "type": "note",
                    "role": role_name,
                    "employee": emp_id,
                    "score": r.get("note_score", 0.0),
                    "reason": r.get("reason", "")
                })

    return { "role_scores": outputs } 