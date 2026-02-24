from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from database import engine
from models import Conversation, Message
from auth import get_current_user
from llm import stream_analysis
from prompts import AUCHENCORE_SYSTEM_PROMPT

from pydantic import BaseModel

router = APIRouter(prefix="/conversation", tags=["Conversation"])


# ----------------------------
# Request Model
# ----------------------------

class ChatRequest(BaseModel):
    message: str


# ----------------------------
# Protected Test Route
# ----------------------------

@router.get("/me")
def my_conversations(current_user = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user.email
    }


# ----------------------------
# Protected Chat Stream
# ----------------------------

@router.post("/chat-stream")
def chat_stream(
    data: ChatRequest,
    current_user = Depends(get_current_user)
):

    user_message = data.message

    with Session(engine) as session:

        # Get user's conversation (or create one)
        conversation = session.exec(
            select(Conversation).where(
                Conversation.user_id == current_user.id
            )
        ).first()

        if not conversation:
            conversation = Conversation(user_id=current_user.id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Get previous messages
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        ).all()

        formatted = [{"role": "system", "content": AUCHENCORE_SYSTEM_PROMPT}]

        for m in messages:
            formatted.append({
                "role": m.role,
                "content": m.content
            })

        formatted.append({
            "role": "user",
            "content": user_message
        })

        # Save user message
        session.add(Message(
            conversation_id=conversation.id,
            role="user",
            content=user_message
        ))
        session.commit()

    # Streaming generator
    def generate():
        full_response = ""

        for chunk in stream_analysis(formatted):
            full_response += chunk
            yield chunk

        # Save assistant response
        with Session(engine) as session:
            session.add(Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response
            ))
            session.commit()

    return StreamingResponse(generate(), media_type="text/plain")
