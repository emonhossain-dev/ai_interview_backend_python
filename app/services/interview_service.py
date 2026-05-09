from app.repositories.interview_repo import (
    create_session, get_session,
    create_interview_message, get_session_messages,
    update_session_count, mark_session_complete,
)
from app.utils.interview_client import get_interview_response, MAX_QUESTIONS
from datetime import datetime, timezone


def start_interview(db, user_id, category: str, topics: list, difficulty: str):
    """
    নতুন interview session শুরু করো।
    AI প্রথম question করবে।
    """
    # 1. Session তৈরি করো
    session = create_session(db, user_id, category, topics, difficulty)

    # 2. AI কে first question করতে বলো
    starter = [{"role": "user", "content": "Start the interview. Ask the first question."}]
    question_count = 1

    ai_reply = get_interview_response(
        messages=starter,
        category=category,
        topics=topics,
        difficulty=difficulty,
        question_count=question_count,
    )

    # 3. AI message save করো
    ai_msg = create_interview_message(db, session.id, "assistant", ai_reply)

    # 4. question_count update করো
    update_session_count(db, session, question_count)

    return {
        "session_id": str(session.id),
        "reply": ai_reply,
        "question_count": question_count,
        "max_questions": MAX_QUESTIONS,
        "is_complete": False,
        "created_at": ai_msg.created_at.isoformat() if ai_msg.created_at else datetime.now(timezone.utc).isoformat(),
    }


def handle_interview(db, user_id, session_id, user_message: str):
    """
    User answer দেওয়ার পর AI feedback + next question দেবে।
    """
    # 1. Session load করো
    session = get_session(db, session_id, user_id)
    if not session:
        raise Exception("Interview session not found")

    if session.is_complete:
        raise Exception("This interview session is already complete")

    # 2. User message save করো
    create_interview_message(db, session.id, "user", user_message)

    # 3. Full history load করো
    history = get_session_messages(db, session.id)
    messages = [{"role": m.role, "content": m.content} for m in history]

    # 4. Question count বাড়াও
    current_count = session.question_count
    is_last = current_count >= MAX_QUESTIONS

    # 5. AI কে বলো কী করতে হবে
    if is_last:
        instruction = "That was the last answer. Now give the final overall summary."
    else:
        instruction = "Give feedback on my answer, then ask the next question."

    messages.append({"role": "user", "content": instruction})

    next_count = current_count + 1 if not is_last else current_count

    ai_reply = get_interview_response(
        messages=messages,
        category=session.category,
        topics=session.topics.split(","),   # string → list
        difficulty=session.difficulty,
        question_count=next_count,
    )

    # 6. AI reply save করো
    ai_msg = create_interview_message(db, session.id, "assistant", ai_reply)

    # 7. Session update করো
    if is_last:
        mark_session_complete(db, session)
    else:
        update_session_count(db, session, next_count)

    return {
        "session_id": session.id,
        "reply": ai_reply,
        "question_count": next_count,
        "max_questions": MAX_QUESTIONS,
        "is_complete": is_last,
        "created_at": ai_msg.created_at.isoformat() if ai_msg.created_at else datetime.now(timezone.utc).isoformat(),
    }
