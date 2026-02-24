from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from database import engine
from models import User
from auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class AuthRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: AuthRequest):
    with Session(engine) as session:

        existing_user = session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password)
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return {"message": "User created"}


@router.post("/login")
def login(data: AuthRequest):
    with Session(engine) as session:

        user = session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token(user.email)

        return {
            "access_token": token,
            "token_type": "bearer"
        }
