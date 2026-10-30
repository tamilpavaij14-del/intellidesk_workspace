from graph.events import log_transition
from services.agent import run_agent


async def worker_node(state: dict) -> dict:
    """Execute the current task and return the Worker's result."""

    # Log Worker execution.
    log_transition("worker", state)

    # Get the current plan and step.
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    # Check whether a task is available.
    if current_step >= len(plan):
        return {
            "last_result": "No task is available to execute."
        }

    # Get the current task.
    task = plan[current_step]

    if not isinstance(task, str) or not task.strip():
        return {
            "last_result": "The current task is empty or invalid."
        }

    # Prepare the Worker prompt.
    prompt = f"""
You are the Worker agent in a multi-agent workflow.

Complete the task below carefully and return the result clearly.

Task:
{task.strip()}
"""

    # Include Auditor feedback when retrying.
    last_audit = state.get("last_audit") or {}
    retry_count = state.get("retry_count", 0)

    if retry_count > 0:
        critique = last_audit.get("critique", "")

        if critique:
            prompt += f"""

The Auditor rejected the previous result.

Auditor feedback:
{critique}

Try again and correct the issues identified by the Auditor.
"""

    # Execute the task asynchronously.
    result = await run_agent(prompt)

    # Normalize the result.
    if not isinstance(result, str) or not result.strip():
        result = "The Worker did not produce a valid result."

    # Return the result for the Auditor to evaluate.
    return {
        "last_result": result.strip()
    }
