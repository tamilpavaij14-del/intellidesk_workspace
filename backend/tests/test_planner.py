from graph.planner import needs_planning, planner_node


def test_simple_calculation_skips_planning():
    state = {
        "messages": [
            {
                "role": "user",
                "content": "What is 15% of 840?"
            }
        ]
    }

    assert needs_planning(state) is False


def test_complex_request_needs_planning():
    state = {
        "messages": [
            {
                "role": "user",
                "content": "Summarise my notes and create tasks for the hard topics"
            }
        ]
    }

    assert needs_planning(state) is True


def test_planner_produces_valid_ordered_plan():
    state = {
        "messages": [
            {
                "role": "user",
                "content": "Summarise my notes and create a task for each difficult topic"
            }
        ]
    }

    result = planner_node(state)

    assert "plan" in result
    assert isinstance(result["plan"], list)
    assert 1 <= len(result["plan"]) <= 6
    assert all(isinstance(step, str) and len(step) > 0 for step in result["plan"])
    assert result["current_step"] == 0