# src/memory/employee_store.py

import json
from pathlib import Path
from typing import List, Dict, Any

EmployeeProfile = Dict[str, Any]

# Always save in <project_root>/data/employees.json
ROOT_DIR = Path(__file__).resolve().parents[2]
EMPLOYEE_FILE = ROOT_DIR / "data" / "employees.json"


def load_employees() -> List[EmployeeProfile]:
    """
    Load employees from data/employees.json.
    Returns empty list if file doesn't exist.
    """
    if not EMPLOYEE_FILE.exists():
        return []
    with EMPLOYEE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_employees(employees: List[EmployeeProfile]) -> None:
    """
    Save employees to data/employees.json.
    """
    EMPLOYEE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EMPLOYEE_FILE.open("w", encoding="utf-8") as f:
        json.dump(employees, f, indent=2, ensure_ascii=False)


def _generate_external_id(existing_ids: List[str]) -> str:
    """
    Generate a new unique external id like EXT-001, EXT-002, ...
    based on already existing ids.
    """
    max_n = 0
    for eid in existing_ids:
        if isinstance(eid, str) and eid.startswith("EXT-"):
            try:
                n = int(eid.split("-")[1])
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
    return f"EXT-{max_n + 1:03d}"


def upsert_employee(profile: EmployeeProfile) -> None:
    """
    Insert or update an employee.

    - If profile has a new id → append.
    - If profile id already exists → update that record.
    - If profile has no id OR uses an existing id (e.g. LLM always returns EXT-001),
      we auto-generate a fresh EXT-### id so each resume becomes a distinct employee.
    """
    employees = load_employees()
    existing_ids = [e.get("id") for e in employees]

    profile_id = profile.get("id")

    # Ensure unique ID for each uploaded resume
    if not profile_id or profile_id in existing_ids:
        profile_id = _generate_external_id(
            [eid for eid in existing_ids if isinstance(eid, str)]
        )
        profile["id"] = profile_id

    # Mark source if not set
    profile.setdefault("source", "external")

    # Normal upsert: replace if id exists, else append
    replaced = False
    for idx, emp in enumerate(employees):
        if emp.get("id") == profile_id:
            employees[idx] = profile
            replaced = True
            break

    if not replaced:
        employees.append(profile)

    save_employees(employees)