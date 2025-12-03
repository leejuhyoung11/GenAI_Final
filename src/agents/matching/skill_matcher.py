from utils.prompt_loader import load_prompt
from src.models.provider_factory import LLMProviderFactory
from utils.load_config import load_config
from src.graph.state import MatchingState

import json

config = load_config()
skill_matcher_cfg = config["models"]["skill"]
skill_llm = LLMProviderFactory.load_from_config(skill_matcher_cfg)


def skill_matcher(state: MatchingState):

    roles = state["project"]["roles"]
    employees = state["employees"]

    outputs = []


    # Load prompt template
    prompt_template = load_prompt("skill_matcher.prompt")

    # For each role = run LLM 1 time
    for role in roles:
        role_name = role["role_name"]

        print(f"\n[SkillMatcher] Processing role: {role_name}")

        # Prepare prompt
        prompt = prompt_template.format(
            role_json=json.dumps(role, indent=2),
            employees_json=json.dumps(employees, indent=2)
        )

        # Call LLM
        raw_output = skill_llm.call(prompt)

        # Parse JSON
        try:
            parsed = json.loads(raw_output)
        except:
            print(f"[SkillMatcher] JSON Parse ERROR for {role_name}")
            parsed = {
                "role_name": role_name,
                "results": {
                    emp["id"]: {
                        "score": 0.0,
                        "reason": "LLM parsing failed; default fallback."
                    }
                    for emp in employees
                }
            }

        # parsed = { "role_name": "...", "results": {...} }
        results = parsed.get("results", {})


        # Insert skill_score for each employee
        for emp_id, r in results.items():
            outputs.append({
                "type": "skill",
                "role": role_name,
                "employee": emp_id,
                "score": r.get("score", 0.0),
                "reason": r.get("reason", "")
            })


    return { "role_scores": outputs }


