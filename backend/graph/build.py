from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from graph.planner import planner_node, needs_planning
from graph.worker import worker_node
from graph.auditor import auditor_node
from graph.synthesizer import synthesizer_node
from graph.events import log_transition


MAX_ATTEMPTS = 3
RECURSION_LIMIT = 100


def initial_state(
    message: str,
    user_id: str = "",
    project_id: str = "",
) -> AgentState:
    """Create the initial state for a new user request."""

    return {
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
        "plan": None,
        "current_step": 0,
        "user_id": user_id,
        "project_id": project_id,
        "last_result": None,
        "last_audit": None,
        "retry_count": 0,
        "results": [],
    }


def route_entry(state: AgentState) -> str:
    """Choose whether the request needs planning."""

    if needs_planning(state):
        return "planner"

    return "simple_plan"


def simple_plan_node(state: AgentState) -> dict:
    """Use the user's request as a single task for simple requests."""

    log_transition("simple_plan", state)

    messages = state.get("messages") or []
    user_goal = ""

    for message in reversed(messages):
        if message.get("role") == "user":
            user_goal = message.get("content", "")
            break

    return {
        "plan": [user_goal] if user_goal else [],
        "current_step": 0,
        "retry_count": 0,
        "last_result": None,
        "last_audit": None,
        "results": [],
    }


def accept_node(state: AgentState) -> dict:
    """Save an audited result and move to the next task."""

    log_transition("accept", state)

    results = list(state.get("results") or [])
    last_result = state.get("last_result")

    if last_result is not None:
        results.append(last_result)

    return {
        "results": results,
        "current_step": state.get("current_step", 0) + 1,
        "retry_count": 0,
        "last_result": None,
        "last_audit": None,
    }


def retry_node(state: AgentState) -> dict:
    """Increase the retry counter before repeating a failed task."""

    log_transition("retry", state)

    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "last_result": None,
        "last_audit": None,
    }


def give_up_node(state: AgentState) -> dict:
    """Record a failure note when retries are exhausted."""

    log_transition("give_up", state)

    results = list(state.get("results") or [])
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)
    last_audit = state.get("last_audit") or {}

    if current_step < len(plan):
        task = plan[current_step]
    else:
        task = "Unknown task"

    critique = last_audit.get(
        "critique",
        "The task could not be completed successfully.",
    )

    results.append(
        f"Could not complete task '{task}' after "
        f"{MAX_ATTEMPTS} attempts. Reason: {critique}"
    )

    return {
        "results": results,
        "current_step": current_step + 1,
        "last_result": None,
        "last_audit": None,
        "retry_count": 0,
    }


def route_after_audit(state: AgentState) -> str:
    """Choose whether to accept, retry, or give up."""

    last_audit = state.get("last_audit") or {}
    verdict = str(last_audit.get("verdict", "")).upper()
    retry_count = state.get("retry_count", 0)

    if verdict == "PASS":
        return "accept"

    if retry_count < MAX_ATTEMPTS - 1:
        return "retry"

    return "give_up"


def route_after_accept(state: AgentState) -> str:
    """Check whether more tasks remain."""

    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    if current_step >= len(plan):
        return "synthesizer"

    return "worker"


def route_after_give_up(state: AgentState) -> str:
    """Continue with remaining tasks or finish the workflow."""

    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)

    if current_step >= len(plan):
        return "synthesizer"

    return "worker"


def build_graph():
    """Build and compile the Planner-Worker-Auditor workflow."""

    graph = StateGraph(AgentState)

    # Register workflow nodes.
    graph.add_node("planner", planner_node)
    graph.add_node("simple_plan", simple_plan_node)
    graph.add_node("worker", worker_node)
    graph.add_node("auditor", auditor_node)
    graph.add_node("accept", accept_node)
    graph.add_node("retry", retry_node)
    graph.add_node("give_up", give_up_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Choose the planning path.
    graph.add_conditional_edges(
        START,
        route_entry,
        {
            "planner": "planner",
            "simple_plan": "simple_plan",
        },
    )

    # Send planned tasks to the worker.
    graph.add_edge("planner", "worker")
    graph.add_edge("simple_plan", "worker")

    # Audit every worker result.
    graph.add_edge("worker", "auditor")

    graph.add_conditional_edges(
        "auditor",
        route_after_audit,
        {
            "accept": "accept",
            "retry": "retry",
            "give_up": "give_up",
        },
    )

    # Retry failed tasks.
    graph.add_edge("retry", "worker")

    # Continue after a task exhausts its attempts.
    graph.add_conditional_edges(
        "give_up",
        route_after_give_up,
        {
            "worker": "worker",
            "synthesizer": "synthesizer",
        },
    )

    # Continue after a successful task.
    graph.add_conditional_edges(
        "accept",
        route_after_accept,
        {
            "worker": "worker",
            "synthesizer": "synthesizer",
        },
    )

    # Generate the final response.
    graph.add_edge("synthesizer", END)

    return graph.compile()


# Compile the graph once.
app = build_graph()


async def run_graph(state: AgentState) -> dict:
    """Run the workflow asynchronously with a recursion limit."""

    return await app.ainvoke(
        state,
        config={"recursion_limit": RECURSION_LIMIT},
    )
