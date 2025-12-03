# src/agents/router_agent.py
from utils.prompt_loader import load_prompt
from src.models.provider_factory import LLMProviderFactory
from utils.load_config import load_config
from src.graph.state import MatchingState

import json, logging

config = load_config()
router_model_cfg = config["models"]["router"]
router_llm = LLMProviderFactory.load_from_config(router_model_cfg)


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

    print("\n==== PARSED ROUTER CONFIG ====")
    print(json.dumps(router_config, indent=2))

    return {
        "router_config": router_config
    }


def router_validator(state: MatchingState):
    cfg = state.get("router_config")
    if not cfg:
        return {"router_valid": False}

    # weight check
    w = cfg.get("weights", {})
    if abs(sum(w.values()) - 1.0) > 1e-6:
        return {"router_valid": False}

    return {"router_valid": True}



def router_branch(state: MatchingState):
    if "router_config" not in state or state["router_config"] is None:
        print("[RouterBranch] ERROR: router_config missing")
        return ["router_agent"] 

    activate = state["router_config"].get("activate_matchers", {})
    branches = []

    if activate.get("skill_matcher", False):
        branches.append("skill_matcher")
    if activate.get("domain_matcher", False):
        branches.append("domain_matcher")
    if activate.get("experience_matcher", False):
        branches.append("experience_matcher")
    if activate.get("seniority_matcher", False):
        branches.append("seniority_matcher")

    # If no matchers selected → go straight to note_matcher
    if not branches:
        return ["note_matcher"]

    logging.warning(f"[RouterBranch] branches = {branches}")

    return branches