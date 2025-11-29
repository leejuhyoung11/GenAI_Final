# src/agents/router_agent.py
from utils.prompt_loader import load_prompt
from src.models.provider_factory import LLMProviderFactory
from utils.load_config import load_config

import json

config = load_config()
router_model_cfg = config["models"]["router"]
router_llm = LLMProviderFactory.load_from_config(router_model_cfg)




def router_agent(state):
    text = state["requirement_text"]

    prompt_template = load_prompt("router_agent.prompt")
    prompt = prompt_template.format(user_message=text)

    response = router_llm.call(prompt)

    print("==== RAW RESPONSE ====")
    print(response)

    try:
        data = json.loads(response)
        print("\n==== PARSED JSON ====")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("\n[ERROR] JSON parsing failed:", e)
    

    