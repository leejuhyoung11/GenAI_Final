from utils.prompt_loader import load_prompt
from src.models.provider_factory import LLMProviderFactory
from utils.load_config import load_config
from src.graph.state import MatchingState

import json

config = load_config()
domain_cfg = config["models"]["domain"]
domain_llm = LLMProviderFactory.load_from_config(domain_cfg)


def domain_matcher(state: MatchingState):

    roles = state["project"]["roles"]
    employees = state["employees"]

    # Create bucket if does not exist
    if "role_scores" not in state or state["role_scores"] is None:
        state["role_scores"] = {}

    prompt_template = load_prompt("domain_matcher.prompt")

    for role in roles:
        role_name = role["role_name"]

        print(f"\n[DomainMatcher] Processing role: {role_name}")

        prompt = prompt_template.format(
            role_json=json.dumps(role, indent=2),
            employees_json=json.dumps(employees, indent=2)
        )

        raw_output = domain_llm.call(prompt)

        # -------------------------------
        #  SAFE PARSING
        # -------------------------------
        try:
            parsed = json.loads(raw_output)
        except Exception as e:
            print(f"[DomainMatcher] JSON Parse ERROR for {role_name}: {e}")
            print("[DomainMatcher] Raw Output:", raw_output)

            # fallback: every employee gets default low score
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

        results = parsed.get("results", {})

        # role bucket
        if role_name not in state["role_scores"]:
            state["role_scores"][role_name] = {}

        # update each employee record
        for emp_id, item in results.items():

            score = item.get("score", 0.0)
            reason = item.get("reason", "")

            if emp_id not in state["role_scores"][role_name]:
                state["role_scores"][role_name][emp_id] = {}

            state["role_scores"][role_name][emp_id]["domain_score"] = score
            state["role_scores"][role_name][emp_id]["domain_reason"] = reason

    return {
        "role_scores": state["role_scores"]
    }