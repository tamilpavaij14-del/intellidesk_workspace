
from graph import synthesizer


def test_synthesizer_generates_final_answer(monkeypatch):
    monkeypatch.setattr(
        synthesizer,
        "complete",
        lambda prompt: "The task is complete.",
    )

    state = {
        "messages": [
            {"role": "user", "content": "Summarize the results."}
        ],
        "results": [
            "Task one completed.",
            "Task two completed.",
        ],
    }

    result = synthesizer.synthesizer_node(state)

    assert result["final_answer"] == "The task is complete."
    assert result["messages"][-1] == {
        "role": "assistant",
        "content": "The task is complete.",
    }


def test_synthesizer_preserves_existing_messages(monkeypatch):
    monkeypatch.setattr(
        synthesizer,
        "complete",
        lambda prompt: "Summary generated.",
    )

    original_messages = [
        {"role": "user", "content": "Explain the results."},
        {"role": "assistant", "content": "Previous response."},
    ]

    state = {
        "messages": original_messages.copy(),
        "results": ["Result one."],
    }

    result = synthesizer.synthesizer_node(state)

    assert result["messages"][:-1] == original_messages
    assert len(result["messages"]) == len(original_messages) + 1
    assert result["final_answer"] == "Summary generated."


def test_synthesizer_handles_missing_results(monkeypatch):
    def fake_complete(prompt):
        assert "No task results are available." in prompt
        return "No results were available."

    monkeypatch.setattr(synthesizer, "complete", fake_complete)

    result = synthesizer.synthesizer_node({"messages": []})

    assert result["final_answer"] == "No results were available."


def test_synthesizer_handles_llm_failure(monkeypatch):
    def fake_complete(prompt):
        raise RuntimeError("Simulated LLM failure")

    monkeypatch.setattr(synthesizer, "complete", fake_complete)

    result = synthesizer.synthesizer_node(
        {
            "messages": [
                {"role": "user", "content": "Summarize this."}
            ],
            "results": ["A task result."],
        }
    )

    assert result["final_answer"] == (
        "I couldn't generate a final summary at this time. "
        "Please try the request again."
    )

