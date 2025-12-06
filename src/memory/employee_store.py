# src/memory/employee_store.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

EmployeeProfile = Dict[str, Any]

EMPLOYEE_FILE = Path(__file__).resolve().parents[2] / "data" / "employees.json"


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


def _next_external_id(employees: List[EmployeeProfile]) -> str:
    """
    Find the next EXT-XXX id based on existing employees.
    """
    max_idx = 0
    for emp in employees:
        eid = str(emp.get("id", ""))
        if eid.startswith("EXT-"):
            try:
                num = int(eid.split("-")[1])
                if num > max_idx:
                    max_idx = num
            except ValueError:
                continue
    return f"EXT-{max_idx + 1:03d}"


def upsert_employee(profile: EmployeeProfile) -> None:
    """
    Insert or update an employee.

    - Internal employees (fixed id like E001, E002) → updated by id.
    - External resumes (id missing or starts with EXT-) → 
      get a NEW EXT-XXX id and are APPENDED (no overwrite).
    """
    employees = load_employees()

    emp_id = str(profile.get("id", "") or "")
    if not emp_id or emp_id.startswith("EXT-"):
        for emp in employees:
            if (
                emp.get("name") == profile.get("name")
                and emp.get("role") == profile.get("role")
            ):
                emp.update(profile)
                save_employees(employees)
                return

        profile["id"] = _next_external_id(employees)
        profile.setdefault("source", "external")
        employees.append(profile)
        save_employees(employees)
        return

    for idx, emp in enumerate(employees):
        if emp.get("id") == emp_id:
            employees[idx] = profile
            break
    else:
        employees.append(profile)

    save_employees(employees)