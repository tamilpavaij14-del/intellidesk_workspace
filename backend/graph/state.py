from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    messages: List[dict]
    plan: Optional[List[str]]
    current_step: int
    user_id: str
    project_id: str