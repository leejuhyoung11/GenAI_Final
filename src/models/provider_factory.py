from src.models.base_wrapper import BaseLLMWrapper
from src.models.anthropic_wrapper import AnthropicWrapper
from src.models.openai_wrapper import OpenAIWrapper
from src.models.gemini_wrapper import GoogleGeminiWrapper

from utils.load_env import get_api_key


class LLMProviderFactory:
    @staticmethod
    def load_from_config(model_cfg: dict):
        provider = model_cfg["provider"].lower()
        model_name = model_cfg["model"]
        temperature = model_cfg.get("temperature", 0)
        max_tokens = model_cfg.get("max_tokens", 400)

        api_key = get_api_key(provider)

        if provider == "openai":
            return OpenAIWrapper(
                model=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )

        elif provider == "anthropic":
            return AnthropicWrapper(
                model=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )

        elif provider in ["gemini", "google"]:
            return GoogleGeminiWrapper(
                model=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )

        else:
            raise ValueError(f"[ERROR] Unknown provider: {provider}")