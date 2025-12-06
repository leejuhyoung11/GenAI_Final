# src/agents/matching/external_candidate_agent.py

from typing import List
from src.graph.state import MatchingState
from src.models.employee import EmployeeProfile
from src.memory.employee_rag import find_similar_employees


def external_candidate_agent(state: MatchingState) -> MatchingState:
    """
    RAG agent that augments state['employees'] with semantically similar
    candidates (internal + external) based on the project requirements.

    It:
      - Builds a rich text query from project + roles
      - Uses embeddings search to find top-K similar employees
      - Adds them to state['employees'] (if not already present)
    """
    project = state.get("project")
    employees: List[dict] = state.get("employees") or []

    if not project:
        # nothing to do if project isn't set yet
        return state

    # Build query text from project fields
    pieces = [
        project.get("project_name", ""),
        project.get("description", ""),
        project.get("domain", ""),
    ]

    for role in project.get("roles", []):
        pieces.append(role.get("role_name", ""))
        pieces.extend(role.get("required_skills", []))
        pieces.extend(role.get("nice_to_have_skills", []))
        # required_domain is optional string
        if role.get("required_domain"):
            pieces.append(role["required_domain"])

    query_text = "\n".join(str(p) for p in pieces if p)

    # Use RAG to find similar employees
    top_k = 5
    similar = find_similar_employees(query_text, k=top_k)

    existing_ids = {e.get("id") for e in employees if e.get("id")}
    for emp, score in similar:
        if emp.get("id") in existing_ids:
            continue
        emp_copy: EmployeeProfile = dict(emp)
        emp_copy["notes"] = f"RAG_similarity_score={score:.3f}"
        employees.append(emp_copy)

    state["employees"] = employees
    return state