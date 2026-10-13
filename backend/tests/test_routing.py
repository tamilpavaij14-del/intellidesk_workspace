from graph.build import MAX_ATTEMPTS, route_after_accept, route_after_audit


def _state(verdict="PASS", retry=0, step=0, plan=("a", "b")):
    return {
        "last_audit": {"verdict": verdict, "critique": "x"},
        "retry_count": retry,
        "current_step": step,
        "plan": list(plan),
    }


def test_pass_goes_to_accept():
    assert route_after_audit(_state("PASS")) == "accept"


def test_fail_retries_under_the_cap():
    assert route_after_audit(_state("FAIL", retry=0)) == "retry"


def test_fail_gives_up_at_the_cap():
    assert route_after_audit(
        _state("FAIL", retry=MAX_ATTEMPTS)
    ) == "give_up"


def test_more_steps_go_back_to_worker():
    assert route_after_accept(_state(step=1)) == "worker"


def test_last_step_goes_to_synthesizer():
    assert route_after_accept(_state(step=2)) == "synthesizer"