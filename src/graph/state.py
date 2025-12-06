import operator
from typing import TypedDict, List, Dict, Any, Optional, Literal
from typing_extensions import Annotated



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
    role_scores: Annotated[List[dict], operator.add]
    final_result: Dict[str, Any]


########################################################################3

class ResumeState(TypedDict):
    """
    State used in the resume ingestion workflow.

    - file_content: raw PDF bytes
    - extracted_text: plain text extracted from the PDF
    - parsed_employee_json: structured EmployeeProfile dict
    - success: whether pipeline finished OK
    """
    file_content: Optional[bytes]
    extracted_text: Optional[str]
    parsed_employee_json: Optional[Dict[str, Any]]
    success: bool