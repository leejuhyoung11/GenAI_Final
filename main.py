# main.py

from src.agents.matching.router_agent import router_agent


if __name__ == "__main__":
    state = {
        "requirement_text": """
        We need 2 backend engineers with strong Python, AWS, and FastAPI.
        ML model serving experience is very important.
        Please exclude Alice and Bob.
        Senior engineers only.
        Domain knowledge is not important.
        """,
        "project": None,
        "employees": None,
        "partial_scores": None,
        "final_result":None
    }

    router_agent(state)