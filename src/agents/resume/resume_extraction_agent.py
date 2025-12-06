# src/agents/resume/resume_extraction_agent.py

import json
from typing import Dict, Any, List

from utils.pdf_utils import extract_text_from_pdf  # your existing helper
from utils.load_config import load_config
from src.models.provider_factory import LLMProviderFactory
from src.models.employee import EmployeeProfile

config = load_config()
extractor_cfg = config["models"]["resume_extractor"]
extractor_llm = LLMProviderFactory.load_from_config(extractor_cfg)


def _build_extraction_prompt(resume_text: str) -> str:
    """
    Ask the LLM to map raw resume text into our EmployeeProfile JSON format.
    IMPORTANT: career_path MUST include ALL work experiences from the resume.
    """
    return f"""
You are a highly accurate information extraction assistant.

Your task:
- Read the RAW RESUME TEXT.
- Extract a single candidate profile in the following JSON schema:

EmployeeProfile schema:

{{
  "id": "E???",               // if not given, create an ID like "EXT-001"
  "name": "Full Name",
  "role": "backend | frontend | data | mlops | ...",
  "skills": ["python", "fastapi", ...],
  "experience_years": 6,      // TOTAL professional experience across ALL jobs

  "career_path": [
    {{
      "period": "2018-2020",
      "company": "Company Name",
      "role": "Job Title",
      "division": "Team / Department",
      "project": "Project Name",
      "description": [
        "Bullet about work",
        "Another bullet"
      ],
      "domain_experience": ["e-commerce", "mlops", ...]
    }}
  ],

  "projects": [
    {{
      "name": "Project Name",
      "role": "Role on that project",
      "duration_months": 12,
      "tech_stack": ["python", "kafka", ...],
      "responsibilities": [
        "What they did"
      ],
      "impact": [
        "Measurable impact, with numbers if possible"
      ],
      "domain": "short domain string"
    }}
  ],

  "certifications": ["AWS Solutions Architect Associate"],
  "availability": 1.0,             // if unknown, use 1.0
  "seniority": "junior | mid | mid-senior | senior"
}}

CRITICAL RULES:

- "career_path" MUST contain **ALL work experiences** listed in the resume:
  - Every full-time job, internship, or contract role should be a separate object.
  - Do NOT drop older jobs just because they are earlier in the career.
- "experience_years" MUST be the **total experience** across all jobs
  (sum of all periods, rounded to the nearest whole year when needed).
- Use ONLY facts that clearly appear in the resume.
- If a field is unknown, set it to null, 0, [] or a safe default
  (e.g. availability = 1.0 if not mentioned).
- Do NOT hallucinate company names, dates, or projects.
- For "role", map to a high-level bucket like backend / frontend / data / mlops.

Return ONLY valid JSON, no explanations, no markdown.

RAW RESUME TEXT:
\"\"\"{resume_text}\"\"\" 
"""


def _normalize_career_path(candidate: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Ensure career_path is always a list of dicts and keep ALL entries.
    """
    career = candidate.get("career_path") or []

    # If model returned a single object instead of list
    if isinstance(career, dict):
        career = [career]

    # If it's anything else (string, None, etc.), reset to empty list
    if not isinstance(career, list):
        career = []

    candidate["career_path"] = career
    return career


def _recompute_experience_years(candidate: Dict[str, Any]) -> None:
    """
    If experience_years is missing or not numeric, approximate it
    by summing all career_path periods like '2018-2020' / '2017 – 2021'.
    """
    current = candidate.get("experience_years")
    if isinstance(current, (int, float)) and current > 0:
        return  # looks fine

    total_years = 0
    for item in candidate.get("career_path", []):
        period = str(item.get("period", "")).replace("–", "-")
        parts = [p.strip() for p in period.split("-")]
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            try:
                years = int(parts[1]) - int(parts[0])
                if years >= 0:
                    total_years += years
            except Exception:
                continue

    if total_years > 0:
        candidate["experience_years"] = total_years


def resume_extraction_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
        state["file_content"]: bytes of the PDF
    Output (adds to state):
        state["extracted_text"]: str
        state["parsed_employee_json"]: EmployeeProfile (first draft)
    """
    file_bytes: bytes | None = state.get("file_content")
    if not file_bytes:
        raise ValueError("[resume_extraction_agent] file_content missing")

    # 1) PDF → text
    resume_text = extract_text_from_pdf(file_bytes)
    state["extracted_text"] = resume_text

    # 2) LLM → JSON draft
    prompt = _build_extraction_prompt(resume_text)
    raw = extractor_llm.call(prompt).strip()

    # strip ```json fences if present
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    candidate: EmployeeProfile = json.loads(raw)

    # 3) Make sure ALL work experiences are preserved
    _normalize_career_path(candidate)

    # 4) Recompute total experience if needed
    _recompute_experience_years(candidate)

    # 5) Mark source as external for uploaded resumes
    candidate.setdefault("source", "external")

    state["parsed_employee_json"] = candidate
    return state