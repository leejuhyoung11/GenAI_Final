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

    # Initialize role_scores if not exists
    if "role_scores" not in state or state["role_scores"] is None:
        state["role_scores"] = {}

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

        # Create role bucket if not exists
        if role_name not in state["role_scores"]:
            state["role_scores"][role_name] = {}

        # Insert skill_score for each employee
        for emp_id, score_data in results.items():

            score = score_data.get("score", 0.0)
            reason = score_data.get("reason", "")

            # Create employee entry if needed
            if emp_id not in state["role_scores"][role_name]:
                state["role_scores"][role_name][emp_id] = {}

            state["role_scores"][role_name][emp_id]["skill_score"] = score
            state["role_scores"][role_name][emp_id]["skill_reason"] = reason

    return {
        "role_scores": state["role_scores"]
    }




    return
    
    prompt = load_prompt("skill_matcher.prompt").format(
        project_roles=state["project"]["roles"],
        employees_json=state["employees"]
    )

    raw_response = skill_llm.call(prompt)

    print(raw_response)
    print("#####################")
    
    try:
        skill_results = json.loads(raw_response)
    except Exception as e:
        print("[ERROR] RouterAgent JSON Parse Failed:", e)


    
    return skill_results