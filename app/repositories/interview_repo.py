from app.models.interview import InterviewSession, InterviewMessage

# ── Session ──────────────────────────────────────────────────────────────────

def create_session(db, user_id, category, topics, difficulty):
    session = InterviewSession(
        user_id=user_id,
        category=category,
        topics=",".join(topics),   # list → comma separated string
        difficulty=difficulty,
        question_count=0,
        is_complete=False,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session(db, session_id, user_id):
    return db.query(InterviewSession).filter(
        InterviewSession.id == str(session_id),
        InterviewSession.user_id == str(user_id),
    ).first()

def update_session_count(db, session, count):
    session.question_count = count
    db.commit()
    db.refresh(session)
    return session

def mark_session_complete(db, session):
    session.is_complete = True
    db.commit()
    db.refresh(session)
    return session

def get_user_sessions(db, user_id, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    total = db.query(InterviewSession).filter(
        InterviewSession.user_id == str(user_id)
    ).count()
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == str(user_id)
    ).order_by(InterviewSession.created_at.desc()).offset(offset).limit(limit).all()
    return sessions, total

# ── Messages ─────────────────────────────────────────────────────────────────

def create_interview_message(db, session_id, role, content):
    msg = InterviewMessage(
        session_id=session_id,
        role=role,
        content=content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_session_messages(db, session_id, limit=50):
    msgs = (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == str(session_id))
        .order_by(InterviewMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return msgs
