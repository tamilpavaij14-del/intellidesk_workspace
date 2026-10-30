<<<<<<< HEAD
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import get_current_user
from services.llm import complete
=======
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from graph.build import initial_state

logger = logging.getLogger(__name__)
>>>>>>> 0a2ced1229742708dd9d8ef4fb170099e22dc9f9

router = APIRouter()


class ChatRequest(BaseModel):
<<<<<<< HEAD
    message: str
=======
    message: str = Field(..., min_length=1)
>>>>>>> 0a2ced1229742708dd9d8ef4fb170099e22dc9f9


class ChatResponse(BaseModel):
    reply: str


<<<<<<< HEAD
@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    reply = complete(request.message)
    return ChatResponse(reply=reply)
=======
async def run_graph_async(state: dict) -> dict:
    """Run the compiled LangGraph asynchronously."""

    from graph.build import app, RECURSION_LIMIT

    return await app.ainvoke(
        state,
        config={"recursion_limit": RECURSION_LIMIT},
    )


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # Validate the incoming message.
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # Create the initial graph state.
    state = initial_state(message)

    try:
        # Execute the LangGraph workflow.
        result = await run_graph_async(state)

        # Find the final assistant response.
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
>>>>>>> 0a2ced1229742708dd9d8ef4fb170099e22dc9f9
