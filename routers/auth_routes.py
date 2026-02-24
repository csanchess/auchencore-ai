from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email,
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created"}

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.email)
    return {
        "access_token": token,
        "token_type": "bearer"
    }