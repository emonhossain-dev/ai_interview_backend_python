from app.models.chat import Chat

def create_chat(db, user_id, title):
    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat(db, chat_id, user_id):
    return db.query(Chat).filter(
        Chat.id == str(chat_id),
        Chat.user_id == str(user_id)
    ).first()

def get_user_chats(db, user_id):
    return db.query(Chat).filter(
        Chat.user_id == str(user_id)
    ).order_by(Chat.created_at.desc()).all()