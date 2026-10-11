from unittest.mock import patch

from graph.auditor import auditor_node


def test_auditor_returns_pass():
    state = {
        "plan": ["Add two numbers"],
        "current_step": 0,
        "worker_result": "print(1 + 1)",
        "attempts": 0,
    }

    with patch(
        "graph.auditor.complete",
        return_value='{"status": "PASS", "feedback": ""}',
    ):
        result = auditor_node(state)

    assert result["audit_status"] == "PASS"
    assert result["attempts"] == 1


def test_auditor_returns_fail():
    state = {
        "plan": ["Add two numbers"],
        "current_step": 0,
        "worker_result": "print('Hello World')",
        "attempts": 0,
    }

    with patch(
        "graph.auditor.complete",
        return_value='{"status": "FAIL", "feedback": "Addition is missing"}',
    ):
        result = auditor_node(state)

    assert result["audit_status"] == "FAIL"
    assert result["audit_feedback"] == "Addition is missing"
    assert result["attempts"] == 1