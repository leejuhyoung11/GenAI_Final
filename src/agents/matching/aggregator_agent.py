# src/agents/aggregator_agent.py

from utils.prompt_loader import load_prompt
from src.models.provider_factory import LLMProviderFactory
from utils.load_config import load_config

config = load_config()
composer_cfg = config["models"]["composer"]
composer_llm = LLMProviderFactory.load_from_config(composer_cfg)

def aggregator_agent(state):
    scores = state["scores"]
    weights = state["router_result"]["weights"]

    # STUB: 합친 값 0.0으로 초기화
    final = {}

    for emp in state["employees"]:
        name = emp["name"]
        final[name] = 0.0

    state["final_scores"] = final
    return state