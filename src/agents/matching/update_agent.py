# from utils.prompt_loader import load_prompt
# from src.models.provider_factory import LLMProviderFactory
# from utils.load_config import load_config


# config = load_config()
# preference_model_cfg = config["models"]["preference"]
# preference_llm = LLMProviderFactory.load_from_config(preference_model_cfg)


# def update_agent(state):
#     user_text = state["last_user_message"]

#     template = load_prompt("trip_preference_agent.prompt")
#     prompt = template.format(user_message=user_text)

#     output = preference_llm.call(prompt)

#     state["preferences"] = output
#     return state