import logging
from datetime import datetime, timezone

logger = logging.getLogger("intellidesk.graph")


def log_transition(node: str, state: dict) -> None:
    """Log graph-node execution without exposing prompts or secrets."""

    logger.info(
        "Graph node executed | node=%s | timestamp=%s | current_step=%s",
        node,
        datetime.now(timezone.utc).isoformat(),
        state.get("current_step", 0),
    )