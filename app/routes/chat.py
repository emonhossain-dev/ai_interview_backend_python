from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.chat_repo import get_user_chats, get_chat
from app.repositories.message_repo import get_all_messages

router = APIRouter(prefix="/api/chats", tags=["Chats"])

# ── সব chat list ──────────────────────────────
@router.get("/{user_id}")
def list_chats(user_id: str, db: Session = Depends(get_db)):
    chats = get_user_chats(db, user_id)
    return [
        {
            "chat_id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat() if chat.created_at else None,
        }
        for chat in chats
    ]

# ── নির্দিষ্ট chat এর messages ────────────────
@router.get("/{user_id}/{chat_id}/messages")
def get_messages(user_id: str, chat_id: str, db: Session = Depends(get_db)):
    chat = get_chat(db, chat_id, user_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = get_all_messages(db, chat_id)
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
        for msg in messages
    ]