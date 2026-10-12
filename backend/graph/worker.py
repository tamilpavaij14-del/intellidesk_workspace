from services.agent import run_agent


async def worker_node(state):
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    # Check whether all plan steps are completed
    if current_step >= len(plan):
        return {
            "last_result": "All plan steps are completed."
        }

    # Get the current task
    task = plan[current_step]

    # Create the Worker prompt
    prompt = f"""
You are the Worker agent in a multi-agent workflow.

Execute the following task:
{task}
"""

    # Include Auditor feedback when retrying
    last_audit = state.get("last_audit") or {}

    if state.get("retry_count", 0) > 0 and last_audit:
        critique = last_audit.get("critique", "")

        if critique:
            prompt += f"""

The Auditor rejected the previous result.

Auditor feedback:
{critique}

Correct the previous result using this feedback.
"""

    # Execute the task
    result = await run_agent(prompt)

    return {
        "last_result": result
    }