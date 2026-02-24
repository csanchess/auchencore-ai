from fastapi import APIRouter, Depends
from auth import get_current_user

router = APIRouter(prefix="/conversation", tags=["Conversation"])


@router.get("/me")
def my_conversations(current_user = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user.email
    }
