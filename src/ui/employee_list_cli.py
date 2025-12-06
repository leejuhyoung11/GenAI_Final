# src/ui/employee_list_cli.py
from src.memory.employee_store import load_employees


def print_employee_list() -> None:
    employees = load_employees()
    if not employees:
        print("No employees found in data/employees.json")
        return

    print(f"Total employees: {len(employees)}\n")
    for emp in employees:
        eid = emp.get("id")
        name = emp.get("name")
        role = emp.get("role")
        seniority = emp.get("seniority")
        source = emp.get("source", "internal")
        skills = ", ".join(emp.get("skills", [])[:8])

        print(f"[{eid}] {name} ({role} | {seniority} | source={source})")
        print(f"  Skills: {skills}")
        print(f"  Availability: {emp.get('availability')}")
        print("-" * 70)