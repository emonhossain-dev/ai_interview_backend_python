from app.repositories.chat_repo import create_chat, get_chat
from app.repositories.message_repo import create_message, get_last_messages
from app.utils.groq_client import get_ai_response
from datetime import datetime, timezone

def handle_chat(db, user_id, chat_id, user_message):

    # 1. নতুন chat অথবা আগেরটা
    if not chat_id:
        chat = create_chat(db, user_id, title=user_message[:50])
        chat_id = chat.id
    else:
        chat = get_chat(db, chat_id, user_id)
        if not chat:
            raise Exception("Chat not found")
        chat_id = chat.id

    # 2. User message save
    create_message(db, chat_id, "user", user_message)

    # 3. History load করো
    history = get_last_messages(db, chat_id, limit=20)

    # 4. Groq format
    messages = [{"role": m.role, "content": m.content} for m in history]

    # 5. Groq call
    ai_reply = get_ai_response(messages)

    # 6. AI reply save ── created_at নাও
    ai_message = create_message(db, chat_id, "assistant", ai_reply)

    return {
        "chat_id": chat_id,
        "reply": ai_reply,
        "created_at": ai_message.created_at.isoformat() if ai_message.created_at else datetime.now(timezone.utc).isoformat(),  # ← এইটা add
    }