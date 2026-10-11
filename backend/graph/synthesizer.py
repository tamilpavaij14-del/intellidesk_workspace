def synthesizer_node(state):
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)
    results = list(state.get("results") or [])

    if state.get("audit_status") == "PASS" and state.get("worker_result"):
        results.append(state["worker_result"])

    completed = min(current_step, len(plan))
    remaining = plan[completed:]

    answer_parts = []

    if results:
        answer_parts.append("Completed results:")
        for index, result in enumerate(results, start=1):
            answer_parts.append(f"{index}. {result}")

    if remaining:
        answer_parts.append("\nIncomplete steps:")
        for step in remaining:
            answer_parts.append(f"- {step}")
        answer_parts.append("Some steps could not be completed successfully.")

    if not answer_parts:
        answer_parts.append("No results were produced.")

    return {
        "results": results,
        "final_answer": "\n".join(answer_parts),
    }
