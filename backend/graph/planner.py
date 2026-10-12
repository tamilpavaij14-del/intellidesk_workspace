from typing import List

from pydantic import BaseModel, Field

from services.llm import complete, extract_json


class Plan(BaseModel):
    steps: List[str] = Field(min_length=1, max_length=6)


def planner_node(state):
    # Get messages from the current state.
    messages = state.get("messages") or []

    if not messages:
        raise ValueError("Cannot create a plan without a user message.")

    # Get the user's goal.
    user_goal = messages[-1]["content"]

    # Prepare the planning prompt.
    prompt = f"""
Break the following user goal into 1 to 6 short, concrete steps.

Respond with ONLY valid JSON in exactly this format:
{{"steps": ["step one", "step two"]}}

Goal: {user_goal}
"""

    # Generate and validate the plan.
    raw = complete(prompt)
    data = extract_json(raw)
    plan = Plan.model_validate(data)

    # Return the plan and initialize the current step.
    return {
        "plan": plan.steps,
        "current_step": 0,
    }


def needs_planning(state) -> bool:
    # Get messages from the current state.
    messages = state.get("messages") or []

    if not messages:
        return False

    # Read the user's latest message.
    text = messages[-1]["content"].lower()

    # Signals that may indicate a simple request.
    simple_signals = [
        "calculate",
        "what is",
        "what's",
        "search for",
        "look up",
    ]

    word_count = len(text.split())

    # Skip planning for short, simple requests.
    if word_count <= 12 and any(
        signal in text for signal in simple_signals
    ):
        return False

    # Use planning for other requests.
    return True
