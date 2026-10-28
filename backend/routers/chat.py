from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import get_current_user
from services.llm import complete

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    reply = complete(request.message)
    return ChatResponse(reply=reply)