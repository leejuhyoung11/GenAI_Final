import json
from utils.prompt_loader import load_prompt
from utils.load_config import load_config
from src.models.provider_factory import LLMProviderFactory
from src.graph.state import MatchingState


config = load_config()
exp_cfg = config["models"]["experience"]
exp_llm = LLMProviderFactory.load_from_config(exp_cfg)


def experience_matcher(state: MatchingState):

    roles = state["project"]["roles"]
    employees = state["employees"]


    # Load prompt template
    prompt_template = load_prompt("experience_matcher.prompt")

    # Accumulate Annotated[ListAppend] items
    list_output = []

    # -----------------------
    # Process each role
    # -----------------------
    for role in roles:
        role_name = role["role_name"]

        print(f"\n[ExperienceMatcher] Processing role: {role_name}")

        # Build prompt from template
        prompt = prompt_template.format(
            role_json=json.dumps(role, indent=2),
            employees_json=json.dumps(employees, indent=2),
        )

        # LLM call
        raw_output = exp_llm.call(prompt)

        # Try JSON parse
        try:
            parsed = json.loads(raw_output)
        except Exception as e:
            print(f"[ExperienceMatcher] JSON Parse ERROR for role '{role_name}': {e}")
            # Fallback JSON (LLM broke formatting)
            parsed = {
                "role_name": role_name,
                "results": {
                    emp["id"]: {
                        "score": 0.0,
                        "reason": "LLM parsing failed; fallback applied."
                    }
                    for emp in employees
                }
            }

        results = parsed.get("results", {})


        # -----------------------
        # Write results to state
        # -----------------------
        for emp_id, score_data in results.items():

            score = score_data.get("score", 0.0)
            reason = score_data.get("reason", "")

            # Also push to ListAppend channel
            list_output.append({
                "type": "experience",
                "role": role_name,
                "employee": emp_id,
                "score": score,
                "reason": reason
            })


    # Return only ListAppend output
    return {
        "role_scores": list_output
    }