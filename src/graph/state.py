from typing import TypedDict, List, Dict, Any, Optional, Literal
from typing_extensions import Annotated
from langgraph.channels import ListAppend

class RoleRequirement(TypedDict, total=False):
    role_name: str                    
    required_skills: List[str]       
    nice_to_have_skills: List[str]     
    required_domain: List[str]
    preferred_experience: Optional[str]
    priority: Optional[str]
    headcount: Optional[int]         
    notes: Optional[str] 

class ProjectRequirement(TypedDict, total=False):
    project_id: int
    project_name: str
    description: str
    domain: Optional[str]           
    duration_months: Optional[int]   
    roles: List[RoleRequirement]    
    raw_input: str  

class MatchingState(TypedDict):
    requirement_text: str
    project: ProjectRequirement
    employees: List[Dict]
    router_config: Dict[str, Any]
    role_scores: Annotated[List[dict], ListAppend]
    final_result: Dict[str, Any]

# role_scores_structure
# {
    #   "backend": {
    #       "E001": {
    #           "skill_score": 0.85,
    #           "domain_score": 0.40,
    #           "experience_score": 0.70
    #       },
    #       "E002": { ... }
    #   },
    #   "mlops": { ... }
    # }

########################################################################3

class ResumeState(TypedDict):
    file_content: bytes | None
    extracted_text: str | None
    parsed_employee_json: dict | None
    success: bool