# main.py
import os, json

from src.graph.matching_workflow import workflow

from src.agents.matching.router_agent import router_agent
from src.agents.matching.skill_matcher import skill_matcher

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
        ML model serving experience is very important.
        Please exclude Alice and Bob.
        Only check skill not the other one.
        """,
        "project": projects[0],
        "employees": employees,
        "router_config": {},
        "role_scores":{},
        "final_result": {}
    }

    print(skill_matcher(state))

    # result = workflow.invoke(state)

    # print(result)