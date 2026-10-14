import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from graph.build import initial_state, run_graph

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request using the LangGraph workflow."""

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # Identity must come from a trusted authentication system.
    # Do not accept identity values directly from the request body.
    state = initial_state(
        message=message,
        user_id="",
        project_id="",
    )

    try:
        result = await run_graph(state)

        messages = result.get("messages") or []

        reply = next(
            (
                item.get("content", "")
                for item in reversed(messages)
                if item.get("role") == "assistant"
            ),
            "",
        )

        if not isinstance(reply, str) or not reply.strip():
            raise RuntimeError(
                "The workflow returned no final answer."
            )

        return ChatResponse(reply=reply.strip())

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("IntelliDesk chat workflow failed")

        raise HTTPException(
            status_code=500,
            detail="The chat workflow failed. Please try again.",
        ) from exc
