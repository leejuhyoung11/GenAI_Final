# main.py
import os, json

from src.graph.matching_workflow import workflow

from src.agents.matching.router_agent import router_agent
from src.agents.matching.skill_matcher import skill_matcher
from src.agents.matching.domain_matcher import domain_matcher
from src.agents.matching.seniority_matcher import seniority_matcher
from src.agents.matching.note_matcher import note_matcher
from src.agents.matching.experience_matcher import experience_matcher

if __name__ == "__main__":

    PROJ_PATH = os.path.join("data", "projects.json")     
    with open(PROJ_PATH, "r", encoding="utf-8") as f:
        projects = json.load(f)
    EMP_PATH = os.path.join("data", "employees.json")
    with open(EMP_PATH, "r", encoding="utf-8") as f:
        employees = json.load(f)

    
            
    # Initialize State
    state = {
        "requirement_text":"""
        We need 2 backend engineers with strong Python, AWS, and FastAPI.
        Please exclude Alice and Bob.
        """,
        "project": projects[0],
        "employees": employees,
        "router_config":{},
        "role_scores":[],
        "final_result": {}
    }

    # workflow.get_graph().draw_png("graph.png")
    
    result = workflow.invoke(state, dubug=True)

    # experience_matcher(state)


    # print(result)

