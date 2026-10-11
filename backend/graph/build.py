from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from graph.planner import planner_node
from graph.worker import worker_node
from graph.auditor import auditor_node
from graph.synthesizer import synthesizer_node

MAX_ATTEMPTS = 3


def route_after_audit(state):
    status = state.get("audit_status")
    attempts = state.get("attempts", 0)

    if status == "PASS":
        return "advance"

    if attempts >= MAX_ATTEMPTS:
        return "synthesize"

    return "retry"


def advance_step(state):
    return {
        "current_step": state.get("current_step", 0) + 1,
        "attempts": 0,
        "audit_feedback": None,
        "audit_status": None,
        }


def route_after_step(state):
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    if current_step >= len(plan):
        return "synthesize"

    return "work"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("worker", worker_node)
    graph.add_node("auditor", auditor_node)
    graph.add_node("advance", advance_step)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "worker")
    graph.add_edge("worker", "auditor")

    graph.add_conditional_edges(
        "auditor",
        route_after_audit,
        {
            "retry": "worker",
            "advance": "advance",
            "synthesize": "synthesizer",
        },
    )

    graph.add_conditional_edges(
        "advance",
        route_after_step,
        {
            "work": "worker",
            "synthesize": "synthesizer",
        },
    )

    graph.add_edge("synthesizer", END)

    return graph.compile()
