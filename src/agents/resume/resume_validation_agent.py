# src/agents/resume/resume_validation_agent.py

import json
from typing import Dict, Any

from utils.load_config import load_config
from src.models.provider_factory import LLMProviderFactory
from src.models.employee import EmployeeProfile

config = load_config()
resume_validator_cfg = config["models"]["resume_validator"]
resume_validator_llm = LLMProviderFactory.load_from_config(resume_validator_cfg)


def _build_validation_prompt(resume_text: str, candidate_json: str) -> str:
    return f"""
You are a strict JSON VALIDATOR.

You are given:
1) RAW RESUME TEXT
2) A CANDIDATE JSON profile that was extracted from that resume.

Your job:
- Remove or fix any field that is NOT clearly supported by the resume text.
- Do NOT invent new information.
- Ensure numeric values such as experience_years and duration_months
  are consistent with the dates in the resume, when possible.
- Keep the JSON structure the same, but you may delete unsupported items.
- If something is unknown, set it to null, 0, or [].

Return ONLY corrected JSON. No comments, no markdown.

RAW RESUME TEXT:
\"\"\"{resume_text}\"\"\"

CANDIDATE JSON:
{candidate_json}
"""


def resume_validation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
        state["extracted_text"]
        state["parsed_employee_json"]
    Output:
        state["parsed_employee_json"] (validated)
        state["success"] = True
    """
    resume_text = state.get("extracted_text")
    candidate = state.get("parsed_employee_json")

    if not resume_text or not candidate:
        raise ValueError("[resume_validation_agent] Missing resume_text or candidate JSON")

    candidate_json = json.dumps(candidate, ensure_ascii=False, indent=2)

    max_loops = 2
    last_good = candidate_json

    for _ in range(max_loops):
        prompt = _build_validation_prompt(resume_text, candidate_json)
        raw = resume_validator_llm.call(prompt).strip()

        # Strip ```json fences if present
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

        try:
            parsed: EmployeeProfile = json.loads(raw)
            last_good = json.dumps(parsed, ensure_ascii=False)
            candidate_json = last_good
            break
        except json.JSONDecodeError:
            # Retry with last good JSON if malformed
            candidate_json = last_good
            continue

    final_profile: EmployeeProfile = json.loads(candidate_json)
    state["parsed_employee_json"] = final_profile
    state["success"] = True
    return state