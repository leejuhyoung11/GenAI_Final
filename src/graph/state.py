from typing import TypedDict, List, Dict, Any, Optional, Literal

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
    partial_scores: Dict[str, Any]
    final_result: Dict[str, Any]




# class MatchingState(TypedDict):
#     last_user_message: str
#     project_requirement: Dict[str, Any] | None
#     employee_list: List[Dict[str, Any]]

#     role_scores: Dict[str, float] | None
#     skill_scores: Dict[str, float] | None
#     domain_scores: Dict[str, float] | None
#     experience_scores: Dict[str, float] | None
#     availability_scores: Dict[str, float] | None

#     final_scores: List[Dict[str, Any]] | None

class ResumeState(TypedDict):
    file_content: bytes | None
    extracted_text: str | None
    parsed_employee_json: dict | None
    success: bool