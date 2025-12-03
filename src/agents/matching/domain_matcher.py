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
    outputs = []


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


        # update each employee record
        for emp_id, r in results.items():
            outputs.append({
                "type": "domain",
                "role": role_name,
                "employee": emp_id,
                "score": r.get("score", 0.0),
                "reason": r.get("reason", "")
            })

    return { "role_scores": outputs }
          