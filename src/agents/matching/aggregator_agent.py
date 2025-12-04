# src/agents/matching/aggregator_agent.py

from typing import Dict, Any, List
from src.graph.state import MatchingState
from utils.save_state import save_project_scores


def aggregator_agent(state: MatchingState):

    router_cfg = state.get("router_config", {}) or {}
    role_score_items: List[dict] = state.get("role_scores", []) or []
    employees_list: List[dict] = state.get("employees", []) or []
    project = state.get("project", {}) or {}

    active = router_cfg.get("activate_matchers", {}) or {}
    weights = router_cfg.get("weights", {}) or {}
    rules = router_cfg.get("rules", {}) or {}

    exclude_names = set(rules.get("exclude", []) or [])
    include_names = set(rules.get("include", []) or [])
    min_exp_years = rules.get("min_experience_years", None)

    # ----------------------------
    # employee lookup by ID
    # ----------------------------
    employee_by_id: Dict[str, dict] = {
        e.get("id"): e for e in employees_list if "id" in e
    }

    # ----------------------------
    # role_scores: flatten ListAppend into nested dict
    # scores_by_role[role][emp][matcher] = {...}
    # ----------------------------
    scores_by_role: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}

    for item in role_score_items:
        role_name = item.get("role")
        emp_id = item.get("employee")
        score_type = item.get("type")   # skill / domain / experience / seniority / note
        score = item.get("score", 0.0)
        reason = item.get("reason", "")

        if not role_name or not emp_id or not score_type:
            continue

        scores_by_role \
            .setdefault(role_name, {}) \
            .setdefault(emp_id, {})[score_type] = {
                "score": score,
                "reason": reason
            }

    # ----------------------------
    # matcher → type mapping
    # ----------------------------
    matcher_to_type = {
        "skill_matcher": "skill",
        "domain_matcher": "domain",
        "experience_matcher": "experience",
        "seniority_matcher": "seniority",
    }

    roles_output = []
    project_roles = project.get("roles", []) or []

    # ============================
    # PROCESS EACH ROLE
    # ============================
    for role_req in project_roles:
        role_name = role_req.get("role_name")
        headcount = role_req.get("headcount")
        if not role_name:
            continue

        emp_scores_for_role = scores_by_role.get(role_name, {})

        candidates_for_role = []

        # =====================================
        # Process each employee for this role
        # =====================================
        for emp_id, per_matcher_scores in emp_scores_for_role.items():

            emp = employee_by_id.get(emp_id)
            if not emp:
                continue

            emp_name = emp.get("name", emp_id)
            experience_years = emp.get("experience_years") or emp.get("years_experience")

            # ----------------------------
            # 1) RULE FLAGS
            # ----------------------------
            forced_excluded = False
            forced_included = False

            # exclude by name
            if emp_name in exclude_names:
                forced_excluded = True

            # minimal experience filter
            if min_exp_years is not None and experience_years is not None:
                if experience_years < min_exp_years:
                    forced_excluded = True

            # include list
            if emp_name in include_names:
                forced_included = True
                forced_excluded = False

            # ----------------------------
            # 2) BASE SCORE (matchers weighted sum)
            # ----------------------------
            total = 0.0
            w_sum = 0.0

            for matcher_name, score_type in matcher_to_type.items():

                if not active.get(matcher_name, False):
                    continue

                w = float(weights.get(matcher_name, 0.0))
                if w <= 0:
                    continue

                score_info = per_matcher_scores.get(score_type)
                if not score_info:
                    continue

                s_val = float(score_info.get("score", 0.0))
                total += w * s_val
                w_sum += w

            base_score = total / w_sum if w_sum > 0 else 0.0  # 0~1

            # ----------------------------
            # 3) NOTE SCORE HANDLING
            # ----------------------------
            note_info = per_matcher_scores.get("note")
            note_score = float(note_info.get("score", 0.0)) if note_info else 0.0

            # hard rules
            if note_score >= 0.99:        # force include
                forced_included = True
                forced_excluded = False

            if note_score <= -0.99:       # force exclude
                forced_excluded = True
                forced_included = False

            # soft rules only (do NOT mix hard 1.0 / -1.0)
            final_score = base_score
            if -0.99 < note_score < 0.99:
                final_score = base_score + 0.2 * note_score
                final_score = max(0.0, min(1.0, final_score))

            # exclude unless forced_included
            if forced_excluded:
                final_score = 0.0
            elif forced_included:
                final_score = 1.0

            # convert to 0–100 scale
            final_score_100 = round(final_score * 100.0, 2)

            # ----------------------------
            # Add candidate
            # ----------------------------
            candidates_for_role.append({
                "employee_id": emp_id,
                "name": emp_name,
                "experience_years": experience_years,
                "base_score": round(base_score * 100, 2),
                "final_score": final_score_100,
                "forced_included": forced_included,
                "note_score": note_score,
                "per_matcher": {
                    stype: {
                        "score": sinfo["score"],
                        "reason": sinfo["reason"]
                    }
                    for stype, sinfo in per_matcher_scores.items()
                },
            })

        # sort by final_score desc
        candidates_for_role.sort(key=lambda x: x["final_score"], reverse=True)

        roles_output.append({
            "role_name": role_name,
            "headcount": headcount,
            "candidates": candidates_for_role
        })

    final_result = {
        "project_id": project.get("project_id"),
        "project_name": project.get("project_name") or project.get("name"),
        "roles": roles_output,
        "weights": weights,
        "rules": rules
    }

    # save compact file
    if final_result["project_id"]:
        save_project_scores(final_result["project_id"], final_result)

    return {"final_result": final_result}