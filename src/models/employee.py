# src/models/employee.py

from typing import TypedDict, List, Optional, Literal


class CareerItem(TypedDict, total=False):
    period: str
    company: str
    role: str
    division: Optional[str]
    project: Optional[str]
    description: List[str]
    domain_experience: List[str]


class ProjectItem(TypedDict, total=False):
    name: str
    role: str
    duration_months: int
    tech_stack: List[str]
    responsibilities: List[str]
    impact: List[str]
    domain: str


class EmployeeProfile(TypedDict, total=False):
    """
    Standard employee schema used across:
    - resume ingestion
    - matching workflow
    - employee store (data/employees.json)
    """

    id: str
    name: str
    role: str                         # backend / frontend / data / mlops ...
    skills: List[str]
    experience_years: int

    career_path: List[CareerItem]
    projects: List[ProjectItem]

    certifications: List[str]
    availability: float
    seniority: Literal["junior", "mid", "mid-senior", "senior"]

    source: str                       # "internal" or "external"