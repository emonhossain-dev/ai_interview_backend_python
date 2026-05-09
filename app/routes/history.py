from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.history_service import get_history, get_history_detail, get_history_analysis
from app.utils.current_user_token_check import get_current_user

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/")
def list_history(
    page:   int = Query(1,    ge=1),
    limit:  int = Query(20,   ge=1, le=100),
    filter: str = Query("all",description="all | this_month | last_month | older"),
    search: str = Query("",   description="Search by category or topics"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_history(
        db=db,
        user_id=str(current_user.id),
        page=page,
        limit=limit,
        filter=filter,
        search=search,
        candidate_name=current_user.name,
    )


@router.get("/{session_id}")
def history_detail(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_history_detail(
        db=db,
        user_id=str(current_user.id),
        session_id=session_id,
        candidate_name=current_user.name,
    )


@router.get("/{session_id}/analysis")
def history_analysis(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_history_analysis(
        db=db,
        user_id=str(current_user.id),
        session_id=session_id,
        candidate_name=current_user.name,
    )