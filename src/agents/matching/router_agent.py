# src/agents/router_agent.py
from utils.prompt_loader import load_prompt
from src.models.provider_factory import LLMProviderFactory
from utils.load_config import load_config
from src.graph.state import MatchingState

import json

config = load_config()
router_model_cfg = config["models"]["router"]
router_llm = LLMProviderFactory.load_from_config(router_model_cfg)


def router_validator(state):
    cfg = state["router_config"]

    # All mathcers False
    if not any(cfg["active_matchers"].values()):
        return {"router_valid": False}

    # Weight sum is not 1
    if abs(sum(cfg["matcher_weights"].values()) - 1.0) > 1e-6:
        return {"router_valid": False}

    return {"router_valid": True}



def router_agent(state: MatchingState):
    text = state["requirement_text"]

    prompt_template = load_prompt("router_agent.prompt")
    prompt = prompt_template.format(user_message=text)

    # Call LLM
    raw_response = router_llm.call(prompt)

    # Parse JSON
    try:
        router_config = json.loads(raw_response)
    except Exception as e:
        print("[ERROR] RouterAgent JSON Parse Failed:", e)
        router_config = {
            "activate_matchers": {
                "skill_matcher": True,
                "domain_matcher": True,
                "experience_matcher": True,
                "seniority_matcher": True,
            },
            "weights": {
                "skill_matcher": 0.3,
                "domain_matcher": 0.25,
                "experience_matcher": 0.25,
                "seniority_matcher": 0.2,
            },
            "rules": {
                "exclude": [],
                "include": [],
                "min_experience_years": None,
                "special_note": [],
            }
        }

    print("\n==== PARSED ROUTER RESULT ====")
    print(json.dumps(router_config, indent=2))

    # Extract fields directly for convenience
    activate = router_config.get("activate_matchers", {})
    weights = router_config.get("weights", {})
    rules = router_config.get("rules", {})

    # Update state so next nodes can use it
    router_config = {
        "activate_matchers": activate,
        "weights": weights,
        "rules": rules,
    }

    return {
        "router_config": router_config
    }