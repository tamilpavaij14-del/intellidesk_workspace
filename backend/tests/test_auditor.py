from unittest.mock import patch

from graph.auditor import auditor_node


def test_auditor_returns_pass():
    state = {
        "plan": ["Add two numbers"],
        "current_step": 0,
        "last_result": "2",
        "retry_count": 0,
    }

    with patch(
        "graph.auditor.complete",
        return_value='{"verdict": "PASS", "critique": ""}',
    ):
        result = auditor_node(state)

    assert result["last_audit"]["verdict"] == "PASS"
    assert result["last_audit"]["critique"] == ""


def test_auditor_returns_fail():
    state = {
        "plan": ["Add two numbers"],
        "current_step": 0,
        "last_result": "Hello World",
        "retry_count": 0,
    }

    with patch(
        "graph.auditor.complete",
        return_value=(
            '{"verdict": "FAIL", '
            '"critique": "Addition is missing"}'
        ),
    ):
        result = auditor_node(state)

    assert result["last_audit"]["verdict"] == "FAIL"
    assert result["last_audit"]["critique"] == "Addition is missing"
