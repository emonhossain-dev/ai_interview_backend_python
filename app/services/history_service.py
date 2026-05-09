from fastapi import HTTPException
from datetime import timezone
import json
from groq import Groq

from app.repositories.history_repo import (
    get_completed_sessions,
    get_session_with_messages,
)

client = Groq()  # GROQ_API_KEY env থেকে নেবে


def _calc_duration(session) -> str:
    if session.ended_at and session.created_at:
        diff = session.ended_at - session.created_at.astimezone(timezone.utc)
        total_seconds = int(diff.total_seconds())
        if total_seconds < 60:
            return f"{total_seconds}s"
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        if minutes < 60:
            return f"{minutes}m {seconds}s"
        hours = minutes // 60
        mins  = minutes % 60
        return f"{hours}h {mins}m"
    return "N/A"


def _format_session(session, candidate_name: str) -> dict:
    return {
        "session_id":     str(session.id),
        "title":          session.category,
        "candidate_name": candidate_name,
        "category":       session.category,
        "topics":         session.topics.split(","),
        "difficulty":     session.difficulty,
        "question_count": session.question_count,
        "is_complete":    session.is_complete,
        "mode":           session.mode,
        "score":          int(session.score) if session.score is not None else None,
        "duration":       _calc_duration(session),
        "created_at": (
            session.created_at.astimezone(timezone.utc).isoformat()
            if session.created_at else None
        ),
    }


def _format_message(msg) -> dict:
    return {
        "id":      str(msg.id),
        "role":    msg.role,
        "content": msg.content,
        "created_at": (
            msg.created_at.astimezone(timezone.utc).isoformat()
            if msg.created_at else None
        ),
    }


def get_history(db, user_id, page, limit, filter, search, candidate_name):
    sessions, total = get_completed_sessions(
        db=db, user_id=user_id, page=page,
        limit=limit, filter=filter, search=search,
    )
    total_pages = (total + limit - 1) // limit
    return {
        "sessions": [_format_session(s, candidate_name) for s in sessions],
        "pagination": {
            "page":        page,
            "limit":       limit,
            "total":       total,
            "total_pages": total_pages,
            "has_next":    page < total_pages,
            "has_prev":    page > 1,
        },
    }


def get_history_detail(db, user_id, session_id, candidate_name):
    session, messages = get_session_with_messages(
        db=db, session_id=session_id, user_id=user_id,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session":       _format_session(session, candidate_name),
        "messages":      [_format_message(m) for m in messages],
        "message_count": len(messages),
    }


def get_history_analysis(db, user_id, session_id, candidate_name):
    session, messages = get_session_with_messages(
        db=db, session_id=session_id, user_id=user_id,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Transcript বানাও
    transcript = ""
    for msg in messages:
        role = "Interviewer" if msg.role == "assistant" else candidate_name
        transcript += f"{role}: {msg.content}\n\n"

    prompt = f"""You are an expert interview coach. Analyze this interview transcript and provide structured feedback.

    Interview Details:
    - Category: {session.category}
    - Topics: {session.topics}
    - Difficulty: {session.difficulty}
    - Score: {session.score if session.score else 'Not scored'}

    Transcript:
    {transcript}

    Respond ONLY in this exact JSON format with no extra text:
    {{
      "headline": "Great Job! | Good Effort! | Keep Practicing! | Needs Improvement!",
      "overall_summary": "2-3 sentence overall performance summary",
      "score_justification": "Why this score was given (1-2 sentences)",
      "performance": {{
        "communication":      85,
        "technical_accuracy": 78,
        "confidence":         90,
        "structure":          72
      }},
      "strengths": [
        {{"title": "Strength title", "detail": "Explanation", "tag": "STRENGTH"}},
        {{"title": "Strength title", "detail": "Explanation", "tag": "STRENGTH"}},
        {{"title": "Strength title", "detail": "Explanation", "tag": "STRENGTH"}}
      ],
      "weaknesses": [
        {{"title": "Weakness title", "detail": "Explanation", "tag": "IMPROVEMENT"}},
        {{"title": "Weakness title", "detail": "Explanation", "tag": "IMPROVEMENT"}}
      ],
      "suggestions": [
        {{"title": "Suggestion title", "detail": "What to do", "tag": "TIP"}},
        {{"title": "Suggestion title", "detail": "What to do", "tag": "TIP"}},
        {{"title": "Suggestion title", "detail": "What to do", "tag": "TIP"}}
      ],
      "verdict": "Strong Hire | Hire | Maybe | No Hire"
    }}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        analysis = json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return {
        "session":  _format_session(session, candidate_name),
        "analysis": analysis,
        "messages": [_format_message(m) for m in messages],
    }