
import logging
from typing import Literal

from pydantic import BaseModel, ValidationError

from graph.events import log_transition
from services.llm import complete, extract_json


logger = logging.getLogger(__name__)


class AuditResult(BaseModel):
    """Validate the Auditor's decision."""

    verdict: Literal["PASS", "FAIL"]
    critique: str


def auditor_node(state: dict) -> dict:
    """Check whether the Worker's result completes the current task."""

    # Log Auditor execution.
    log_transition("auditor", state)

    # Get the current plan and step.
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    # Fail safely if there is no task to audit.
    if current_step >= len(plan):
        audit = AuditResult(
            verdict="FAIL",
            critique="No task is available to audit.",
        )
        return {"last_audit": audit.model_dump()}

    # Get the task and Worker's result.
    task = plan[current_step]
    result = state.get("last_result") or ""

    # Prepare the audit prompt.
    prompt = f"""
You are the Auditor agent in a multi-agent workflow.

Evaluate whether the Worker's result adequately completes the task.
Be strict, objective, and specific.

Task:
{task}

Worker result:
{result}

Return only a valid JSON object in this format:
{{"verdict": "PASS", "critique": ""}}

Rules:
- Use "PASS" if the result adequately completes the task.
- Use "FAIL" if the result is incomplete, incorrect, or irrelevant.
- When using "FAIL", explain the required correction in critique.
- Do not include Markdown or text outside the JSON.
"""

    # Call the LLM and validate its response.
    try:
        response = complete(prompt)
        parsed = extract_json(response)
        audit = AuditResult.model_validate(parsed)

    except (ValueError, TypeError, ValidationError):
        # Fail closed: an invalid response must not be accepted.
        logger.exception("Auditor could not validate the LLM response")

        audit = AuditResult(
            verdict="FAIL",
            critique=(
                "The audit response could not be validated. "
                "The task needs another attempt."
            ),
        )

    except Exception:
        # Handle unexpected LLM or processing errors safely.
        logger.exception("Unexpected error during auditing")

        audit = AuditResult(
            verdict="FAIL",
            critique=(
                "The audit could not be completed because of an error. "
                "The task needs another attempt."
            ),
        )

    # Log the decision without printing prompts or API keys.
    logger.info(
        "Audit completed | verdict=%s | retry_count=%s",
        audit.verdict,
        state.get("retry_count", 0),
    )

    # Return the validated audit result.
    return {"last_audit": audit.model_dump()}
