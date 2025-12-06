# src/memory/employee_rag.py
from typing import List, Tuple
import numpy as np
from openai import OpenAI

from src.models.employee import EmployeeProfile
from src.memory.employee_store import load_employees
from utils.load_env import get_api_key


_EMBED_MODEL = "text-embedding-3-small"


def _get_client() -> OpenAI:
    api_key = get_api_key("openai")
    return OpenAI(api_key=api_key)


def embed_text(text: str) -> np.ndarray:
    client = _get_client()
    resp = client.embeddings.create(
        model=_EMBED_MODEL,
        input=text,
    )
    vec = np.array(resp.data[0].embedding, dtype=np.float32)
    return vec


def _employee_to_doc(emp: EmployeeProfile) -> str:
    """
    Convert employee profile into a text document for embedding.
    """
    lines = [
        f"Name: {emp.get('name')}",
        f"Role: {emp.get('role')}",
        "Skills: " + ", ".join(emp.get("skills", [])),
        f"Seniority: {emp.get('seniority')}",
        f"Experience years: {emp.get('experience_years')}",
    ]

    for step in emp.get("career_path", []):
        lines.append(
            f"Career: {step.get('period')} at {step.get('company')} "
            f"as {step.get('role')} on {step.get('project')}"
        )
        lines.extend(step.get("description", []))

    for proj in emp.get("projects", []):
        lines.append(
            f"Project: {proj.get('name')} ({proj.get('role')}) "
            f"Domain: {proj.get('domain')}"
        )
        lines.extend(proj.get("responsibilities", []))
        lines.extend(proj.get("impact", []))

    return "\n".join(lines)


def find_similar_employees(query_text: str, k: int = 5) -> List[Tuple[EmployeeProfile, float]]:
    """
    Basic RAG: embed query_text and all employees, return top-k by cosine similarity.
    """
    employees = load_employees()
    if not employees:
        return []

    query_vec = embed_text(query_text)
    query_norm = np.linalg.norm(query_vec) + 1e-8

    scored: List[Tuple[EmployeeProfile, float]] = []
    for emp in employees:
        doc = _employee_to_doc(emp)
        emp_vec = embed_text(doc)
        sim = float(emp_vec @ query_vec / ((np.linalg.norm(emp_vec) + 1e-8) * query_norm))
        scored.append((emp, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]