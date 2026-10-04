import json
from pydantic import BaseModel
from typing import List
from services.llm import complete


class Plan(BaseModel):
    steps: List[str]


def planner_node(state):
    user_goal = state["messages"][-1]["content"]

    prompt = f"""Break the following user goal into 1 to 6 short, concrete steps.
Respond with ONLY valid JSON in exactly this form, nothing else:
{{"steps": ["step one", "step two"]}}

Goal: {user_goal}"""

    raw = complete(prompt)
    data = json.loads(raw)
    plan = Plan(**data)

    return {"plan": plan.steps, "current_step": 0}




def needs_planning(state) -> bool:
    text = state["messages"][-1]["content"].lower()

    simple_signals = [
        "calculate",
        "what is",
        "what's",
        "search for",
        "look up"
    ]

    word_count = len(text.split())

    if word_count <= 12 and any(signal in text for signal in simple_signals):
        return False

    return True