import asyncio
from unittest.mock import AsyncMock, patch

from graph.build import build_graph


def test_graph_completes_plan_successfully():
    initial_state = {
        "messages": [
            {"role": "user", "content": "Complete two simple tasks"}
        ],
        "plan": ["Task 1", "Task 2"],
        "current_step": 0,
        "user_id": "test-user",
        "project_id": "test-project",
        "worker_result": None,
        "audit_status": None,
        "audit_feedback": None,
        "attempts": 0,
    }

    with (
        patch(
            "graph.build.planner_node",
            return_value={
                "plan": ["Task 1", "Task 2"],
                "current_step": 0,
            },
        ),
        patch(
            "graph.build.worker_node",
            new_callable=AsyncMock,
            side_effect=[
                {"worker_result": "Task 1 completed"},
                {"worker_result": "Task 2 completed"},
            ],
        ),
        patch(
            "graph.build.auditor_node",
            side_effect=[
                {
                    "audit_status": "PASS",
                    "audit_feedback": "",
                    "attempts": 1,
                },
                {
                    "audit_status": "PASS",
                    "audit_feedback": "",
                    "attempts": 1,
                },
            ],
        ),
    ):
        app = build_graph()
        result = asyncio.run(app.ainvoke(initial_state))

    assert result["current_step"] == 2
    assert result["audit_status"] is None
    assert result["attempts"] == 0
    assert result["worker_result"] == "Task 2 completed"

def test_graph_retries_when_auditor_fails():
    initial_state = {
        "messages": [{"role": "user", "content": "Complete one task"}],
        "plan": ["Task 1"],
        "current_step": 0,
        "user_id": "test-user",
        "project_id": "test-project",
        "worker_result": None,
        "audit_status": None,
        "audit_feedback": None,
        "attempts": 0,
    }

    with (
        patch(
            "graph.build.planner_node",
            return_value={"plan": ["Task 1"], "current_step": 0},
        ),
        patch(
            "graph.build.worker_node",
            new_callable=AsyncMock,
            side_effect=[
                {"worker_result": "First attempt"},
                {"worker_result": "Corrected result"},
            ],
        ) as worker,
        patch(
            "graph.build.auditor_node",
            side_effect=[
                {
                    "audit_status": "FAIL",
                    "audit_feedback": "Please correct the result",
                    "attempts": 1,
                },
                {
                    "audit_status": "PASS",
                    "audit_feedback": "",
                    "attempts": 2,
                },
            ],
        ),
    ):
        app = build_graph()
        result = asyncio.run(app.ainvoke(initial_state))

    assert worker.await_count == 2
    assert result["current_step"] == 1
    assert result["worker_result"] == "Corrected result"