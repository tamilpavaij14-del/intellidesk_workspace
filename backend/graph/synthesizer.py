from graph.events import log_transition
from services.llm import complete


def synthesizer_node(state: dict) -> dict:
    """Combine task results into a final response."""

    # Log synthesizer execution.
    log_transition("synthesizer", state)

    # Copy the existing conversation and results.
    messages = list(state.get("messages") or [])
    results = list(state.get("results") or [])

    # Find the original user request.
    user_goal = ""

    for message in messages:
        if message.get("role") == "user":
            user_goal = message.get("content", "")
            break

    # Format the task results.
    if results:
        results_text = "\n".join(
            f"{index}. {result}"
            for index, result in enumerate(results, start=1)
        )
    else:
        results_text = "No task results are available."

    # Prepare the final response prompt.
    prompt = f"""
You are the final response synthesizer for IntelliDesk.

Original user request:
{user_goal}

Results produced by the workflow:
{results_text}

Instructions:
- Write a clear and helpful final response.
- Use only the information contained in the task results.
- Do not invent facts or claim unfinished tasks succeeded.
- Explain honestly when a task could not be completed.
- Keep the response relevant to the original request.
"""

    # Generate the final response.
    try:
        response = complete(prompt)

        if isinstance(response, str):
            answer = response.strip()
        else:
            answer = ""

    except Exception:
        answer = ""

    # Provide a fallback if generation fails or returns no text.
    if not answer:
        answer = (
            "I couldn't generate a final summary at this time. "
            "Please try the request again."
        )

    # Add the final answer to the conversation.
    messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    # Return the updated state.
    return {
        "messages": messages,
        "final_answer": answer,
    }
