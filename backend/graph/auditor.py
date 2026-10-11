from services.llm import complete

MAX_ATTEMPTS = 3


def auditor_node(state):
    task = (state.get("plan") or [])[state.get("current_step", 0)]
    result = state.get("worker_result", "")

    prompt = f"""
You are the Auditor agent.

Evaluate whether the worker's result adequately completes the task.

Task:
{task}

Worker result:
{result}

Return ONLY valid JSON in this exact format:
{{"status": "PASS", "feedback": ""}}

Use "PASS" if the result adequately completes the task.
Use "FAIL" if it does not, and explain what needs to be corrected
in the feedback field.
"""

    try:
        import json

        response = complete(prompt)
        audit = json.loads(response)

        status = audit.get("status", "").upper()
        feedback = audit.get("feedback", "")

        if status not in {"PASS", "FAIL"}:
            raise ValueError("Invalid audit status")

    except (ValueError, TypeError, AttributeError):
        status = "FAIL"
        feedback = "The audit response was invalid. Please try again."

    attempts = state.get("attempts", 0) + 1

    if status == "FAIL" and attempts >= MAX_ATTEMPTS:
        feedback = (
            f"Maximum attempts ({MAX_ATTEMPTS}) reached. "
            f"Last audit feedback: {feedback}"
        )

    return {
        "audit_status": status,
        "audit_feedback": feedback,
        "attempts": attempts,
    }