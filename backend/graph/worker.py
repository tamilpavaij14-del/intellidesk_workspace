from services.agent import run_agent


async def worker_node(state):
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    if current_step >= len(plan):
        return {
            "worker_result": "All plan steps are completed."
        }

    task = plan[current_step]
    feedback = state.get("audit_feedback")

    prompt = f"""
You are the Worker agent in a multi-agent workflow.

Execute the following task:
{task}
"""

    if feedback:
        prompt += f"""
The Auditor rejected the previous result.
Auditor feedback:
{feedback}

Correct the previous result using this feedback.
"""

    result = await run_agent(prompt)

    return {
        "worker_result": result
    }