from sqlalchemy import and_, or_, func
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from app.models.interview import InterviewSession, InterviewMessage


def get_completed_sessions(
    db,
    user_id: str,
    page: int = 1,
    limit: int = 20,
    filter: str = "all",
    search: str = "",
):
    """
    User এর completed interview sessions query করবে।
    filter এবং search apply করবে।
    """
    now = datetime.now(timezone.utc)
    query = db.query(InterviewSession).filter(
        InterviewSession.user_id == str(user_id),
        InterviewSession.is_complete == True,
    )

    # ── Date filter ──────────────────────────────────────────────────────────
    if filter == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(InterviewSession.created_at >= start)

    elif filter == "last_month":
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = this_month_start - relativedelta(months=1)
        query = query.filter(
            InterviewSession.created_at >= last_month_start,
            InterviewSession.created_at < this_month_start,
        )

    elif filter == "older":
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = this_month_start - relativedelta(months=1)
        query = query.filter(InterviewSession.created_at < last_month_start)

    # ── Search ───────────────────────────────────────────────────────────────
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                InterviewSession.category.ilike(term),
                InterviewSession.topics.ilike(term),
            )
        )

    # ── Total count ──────────────────────────────────────────────────────────
    total = query.count()

    # ── Pagination ───────────────────────────────────────────────────────────
    offset = (page - 1) * limit
    sessions = (
        query.order_by(InterviewSession.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return sessions, total


def get_session_with_messages(db, session_id: str, user_id: str):
    """
    একটি session এবং তার সব messages একসাথে load করবে।
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == str(session_id),
        InterviewSession.user_id == str(user_id),
        InterviewSession.is_complete == True,
    ).first()

    if not session:
        return None, []

    messages = (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == str(session_id))
        .order_by(InterviewMessage.created_at.asc())
        .all()
    )

    return session, messages
