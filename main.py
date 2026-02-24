from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select
from database import engine
from models import User, Conversation, Message
from auth import hash_password, verify_password, create_token, decode_token
from llm import stream_analysis
from prompts import AUCHENCORE_SYSTEM_PROMPT


from fastapi import FastAPI
from routers import auth_routes, conversation_routes

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(conversation_routes.router)


app = FastAPI(title="AuchenCore AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLModel.metadata.create_all(engine)

@app.post("/auth/register")
def register(payload: dict):
    with Session(engine) as session:
        user = User(
            email=payload["email"],
            hashed_password=hash_password(payload["password"])
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        conversation = Conversation(user_id=user.id)
        session.add(conversation)
        session.commit()

    return {"status": "registered"}

@app.post("/auth/login")
def login(payload: dict):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == payload["email"])
        ).first()

        if not user or not verify_password(payload["password"], user.hashed_password):
            raise HTTPException(status_code=401)

        return {"access_token": create_token(user.email)}

@app.post("/chat-stream")
def chat_stream(payload: dict):

    token = payload["token"]
    user_message = payload["message"]

    decoded = decode_token(token)
    email = decoded["sub"]

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        conversation = session.exec(
            select(Conversation).where(Conversation.user_id == user.id)
        ).first()

        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        ).all()

        formatted = [{"role": "system", "content": AUCHENCORE_SYSTEM_PROMPT}]

        for m in messages:
            formatted.append({"role": m.role, "content": m.content})

        formatted.append({"role": "user", "content": user_message})

        session.add(Message(
            conversation_id=conversation.id,
            role="user",
            content=user_message
        ))
        session.commit()

    def generate():
        full = ""
        for chunk in stream_analysis(formatted):
            full += chunk
            yield chunk

        with Session(engine) as session:
            session.add(Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full
            ))
            session.commit()


    return StreamingResponse(generate(), media_type="text/plain")

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

from fastapi import Depends
from auth import get_current_user

@app.get("/me")
def read_me(current_user = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "id": current_user.id
    }

