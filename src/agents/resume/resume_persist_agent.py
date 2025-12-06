# src/agents/resume/resume_persist_agent.py

from __future__ import annotations

from typing import Any, Dict

from src.graph.state import ResumeState
from src.memory.employee_store import upsert_employee


def resume_persist_agent(state: ResumeState) -> ResumeState:
    """
    Take the validated employee profile from the resume
    and persist it into data/employees.json.
    """

    profile: Dict[str, Any] = state.get("parsed_employee_json") or {}

    if not profile:
        state["success"] = False
        return state

    # Force source label
    profile.setdefault("source", "external")

    # Let the store handle ID assignment & append logic
    upsert_employee(profile)

    state["success"] = True
    return state