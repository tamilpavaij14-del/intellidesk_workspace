import asyncio
from unittest.mock import AsyncMock, patch

from graph.build import build_graph, initial_state


def test_graph_completes_plan_successfully():
    """The graph should complete all tasks and save accepted results."""

    state = initial_state("Complete two simple tasks")

    with (
        patch(
            "graph.build.needs_planning",
            return_value=True,
        ),
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
                {"last_result": "Task 1 completed"},
                {"last_result": "Task 2 completed"},
            ],
        ) as worker,
        patch(
            "graph.build.auditor_node",
            side_effect=[
                {"last_audit": {"verdict": "PASS", "critique": ""}},
                {"last_audit": {"verdict": "PASS", "critique": ""}},
            ],
        ) as auditor,
        patch("graph.build.synthesizer_node", return_value={}),
    ):
        app = build_graph()
        result = asyncio.run(app.ainvoke(state))

    assert worker.await_count == 2
    assert auditor.call_count == 2
    assert result["current_step"] == 2
    assert result["results"] == [
        "Task 1 completed",
        "Task 2 completed",
    ]
    assert result["retry_count"] == 0


def test_graph_retries_when_auditor_fails():
    """The graph should retry a rejected task and save the accepted result."""

    state = initial_state("Complete one task")

    with (
        patch(
            "graph.build.needs_planning",
            return_value=True,
        ),
        patch(
            "graph.build.planner_node",
            return_value={
                "plan": ["Task 1"],
                "current_step": 0,
            },
        ),
        patch(
            "graph.build.worker_node",
            new_callable=AsyncMock,
            side_effect=[
                {"last_result": "First attempt"},
                {"last_result": "Corrected result"},
            ],
        ) as worker,
        patch(
            "graph.build.auditor_node",
            side_effect=[
                {
                    "last_audit": {
                        "verdict": "FAIL",
                        "critique": "Please correct the result",
                    }
                },
                {"last_audit": {"verdict": "PASS", "critique": ""}},
            ],
        ) as auditor,
        patch("graph.build.synthesizer_node", return_value={}),
    ):
        app = build_graph()
        result = asyncio.run(app.ainvoke(state))

    assert worker.await_count == 2
    assert auditor.call_count == 2
    assert result["current_step"] == 1
    assert result["results"] == ["Corrected result"]
    assert result["retry_count"] == 0


def test_graph_stops_after_max_attempts():
    """The graph should stop retrying after three worker attempts."""

    state = initial_state("Complete one task")

    with (
        patch(
            "graph.build.needs_planning",
            return_value=True,
        ),
        patch(
            "graph.build.planner_node",
            return_value={
                "plan": ["Task 1"],
                "current_step": 0,
            },
        ),
        patch(
            "graph.build.worker_node",
            new_callable=AsyncMock,
            return_value={"last_result": "Incorrect result"},
        ) as worker,
        patch(
            "graph.build.auditor_node",
            side_effect=[
                {
                    "last_audit": {
                        "verdict": "FAIL",
                        "critique": "Try again",
                    }
                },
                {
                    "last_audit": {
                        "verdict": "FAIL",
                        "critique": "Still incorrect",
                    }
                },
                {
                    "last_audit": {
                        "verdict": "FAIL",
                        "critique": "Maximum attempts reached",
                    }
                },
            ],
        ) as auditor,
        patch("graph.build.synthesizer_node", return_value={}),
    ):
        app = build_graph()
        result = asyncio.run(app.ainvoke(state))

    assert worker.await_count == 3
    assert auditor.call_count == 3
    assert result["current_step"] == 1
    assert len(result["results"]) == 1
    assert "Could not complete task" in result["results"][0]
    assert result["retry_count"] == 0