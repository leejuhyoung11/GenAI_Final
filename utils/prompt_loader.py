# src/utils/prompt_loader.py
import os

def load_prompt(filename):
    prompt_path = os.path.join("src", "prompts", filename)

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()