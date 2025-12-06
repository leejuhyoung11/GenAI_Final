# src/graph/resume_workflow.py

from typing import Dict, Any
from langgraph.graph import StateGraph, END

from src.graph.state import ResumeState
from src.agents.resume.resume_extraction_agent import resume_extraction_agent
from src.agents.resume.resume_validation_agent import resume_validation_agent
from src.agents.resume.resume_persist_agent import resume_persist_agent


def build_resume_workflow():
    graph = StateGraph(ResumeState)

    # 1) Extract raw text + draft profile
    graph.add_node("resume_extraction", resume_extraction_agent)

    # 2) Validate / hallucination check / normalization
    graph.add_node("resume_validation", resume_validation_agent)

    # 3) Persist into data/employees.json (append or update)
    graph.add_node("resume_persist", resume_persist_agent)

    graph.set_entry_point("resume_extraction")
    graph.add_edge("resume_extraction", "resume_validation")
    graph.add_edge("resume_validation", "resume_persist")
    graph.add_edge("resume_persist", END)

    return graph.compile()


workflow = build_resume_workflow()


def run_resume_ingestion(file_bytes: bytes) -> Dict[str, Any]:
    """
    Run the full resume ingestion workflow for a single PDF:

      - file_content: raw PDF bytes
      - extracted_text: filled by extraction agent
      - parsed_employee_json: normalized EmployeeProfile dict
      - success: True/False flag

    resume_persist_agent is responsible for calling upsert_employee()
    so the profile is appended to data/employees.json.
    """
    initial_state: ResumeState = {
        "file_content": file_bytes,
        "extracted_text": None,
        "parsed_employee_json": None,
        "success": False,
    }
    return workflow.invoke(initial_state)