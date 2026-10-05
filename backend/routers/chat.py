from fastapi import APIRouter
from pydantic import BaseModel
from services.llm import complete

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


# TODO: add JWT auth dependency once Story 1.2 is built
@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = complete(request.message)
    return ChatResponse(reply=reply)