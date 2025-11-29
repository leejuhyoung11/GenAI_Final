import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(provider: str):
    provider = provider.lower()
    if provider == "openai":
        return os.getenv("OPENAI_API_KEY")
    if provider == "anthropic":
        return os.getenv("ANTHROPIC_API_KEY")
    if provider == "gemini" or provider == "google":
        return os.getenv("GOOGLE_API_KEY")
    raise ValueError(f"Unknown provider for API key: {provider}")