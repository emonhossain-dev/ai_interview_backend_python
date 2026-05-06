from app.models.message import Message

def create_message(db, chat_id, role, content):
    msg = Message(chat_id=chat_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_last_messages(db, chat_id, limit=20):
    msgs = (
        db.query(Message)
        .filter(Message.chat_id == str(chat_id))
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(msgs))

def get_all_messages(db, chat_id):
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()