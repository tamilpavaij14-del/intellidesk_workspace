from services.llm import complete


def synthesizer_node(state):
    # Get messages and completed task results.
    messages = list(state.get("messages") or [])
    results = list(state.get("results") or [])

    # Get the original user goal.
    user_goal = ""

    for message in messages:
        if message.get("role") == "user":
            user_goal = message.get("content", "")
            break

    # Include only the results actually produced.
    if results:
        results_text = "\n".join(
            f"{index}. {result}"
            for index, result in enumerate(results, start=1)
        )
    else:
        results_text = "No tasks were completed successfully."

    # Prepare the final response prompt.
    prompt = f"""
You are the final response synthesizer.

Original user goal:
{user_goal}

Results produced by the workflow:
{results_text}

Write a clear, helpful response to the user based only on the results above.
Do not claim that an incomplete task was completed.
If there are no successful results, explain that honestly.
Do not invent facts or results.
"""

    # Generate the final response.
    answer = complete(prompt).strip()

    # Handle an empty response.
    if not answer:
        answer = (
            "I couldn't generate a final summary. "
            "Please try the request again."
        )

    # Append the final answer to the conversation.
    messages.append({
        "role": "assistant",
        "content": answer,
    })

    # Return the updated state.
    return {
        "messages": messages,
        "results": results,
    }
