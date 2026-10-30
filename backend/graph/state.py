from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    # Conversation
    messages: List[dict]

    # Planning
    plan: Optional[List[str]]
    current_step: int

    # Identity and project context
    user_id: str
    project_id: str

    # Worker and auditor
    last_result: Optional[str]
    last_audit: Optional[dict]
    retry_count: int

    # Execution results
    results: List[str]