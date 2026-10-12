
from typing import Literal

from pydantic import BaseModel, ValidationError

from services.llm import complete, extract_json


MAX_ATTEMPTS = 3


class AuditResult(BaseModel):
    verdict: Literal["PASS", "FAIL"]
    critique: str


def auditor_node(state):
    # Get the current plan and step
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    # Check whether a task is available
    if current_step >= len(plan):
        audit = AuditResult(
            verdict="FAIL",
            critique="No task is available to audit.",
        )
        return {"last_audit": audit.model_dump()}

    # Get the current task and Worker result
    task = plan[current_step]
    result = state.get("last_result") or ""

    # Prepare the audit prompt
    prompt = f"""
You are the Auditor agent.

Evaluate whether the worker's result adequately completes the task.
Be strict, objective, and specific.

Task:
{task}

Worker result:
{result}

Return only a JSON object in this exact format:
{{"verdict": "PASS", "critique": ""}}

Use "PASS" if the result adequately completes the task.
Use "FAIL" if it does not.
Explain what needs correction in critique when the verdict is FAIL.
"""

    # Call the LLM and validate its response
    try:
        response = complete(prompt)
        parsed = extract_json(response)
        audit = AuditResult.model_validate(parsed)

    except (ValueError, TypeError, ValidationError) as exc:
        audit = AuditResult(
            verdict="FAIL",
            critique=f"Invalid audit response: {exc}",
        )

    # Get the retry count
    retry_count = state.get("retry_count", 0)

    # Log the audit result
    print(
        f"AUDIT: verdict={audit.verdict}, "
        f"retry_count={retry_count}, "
        f"critique={audit.critique}"
    )

    # Return the audit result
    return {"last_audit": audit.model_dump()}
