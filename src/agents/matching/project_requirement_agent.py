# src/agents/project_requirement_agent.py
def project_requirement_agent(state: dict):
    """Combine outputs into final message"""
    state["final_output"] = (
        f"[Emotion] {state['emotion']}\n"
        f"[Memory] {state['memory_results']}\n"
        f"[Insight] {state['insights']}"
    )
    return state