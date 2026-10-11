from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    # Existing fields
    messages: List[dict]
    plan: Optional[List[str]]
    current_step: int
    user_id: str
    project_id: str

    # Story 4.2: Worker and Auditor fields
    worker_result: Optional[str]
    audit_status: Optional[str]
    audit_feedback: Optional[str]
    attempts: int