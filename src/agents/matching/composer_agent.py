# src/agents/composer_agent.py

from utils.prompt_loader import load_prompt
from src.models.provider_factory import LLMProviderFactory
from utils.load_config import load_config

config = load_config()
composer_cfg = config["models"]["composer"]
composer_llm = LLMProviderFactory.load_from_config(composer_cfg)


def composer_agent(state: dict):
    user_message = state.get("last_user_message", "")
    preferences = state.get("preferences", {})
    follow_up = state.get("follow_up", "")

    template = load_prompt("composer_agent.prompt")

    prompt = template.format(
        user_message=user_message,
        preferences=preferences,
        follow_up=follow_up,
    )

    response = composer_llm.call(prompt)

   
    state["final"] = response
    return state