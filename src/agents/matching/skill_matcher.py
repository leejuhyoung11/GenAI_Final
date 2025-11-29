from utils.prompt_loader import load_prompt
from src.models.llm import llm
from src.graph.state import MatchingState

def skill_matcher(state: MatchingState):

    prompt = load_prompt("skill_matcher.prompt").format(
        project_roles=state["project"]["roles"],
        employees=state["employees"]
    )

    response = llm.invoke(prompt)
    scores = response.to_json()   

    state["partial_scores"]["skill"] = scores
    return state