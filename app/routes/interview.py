# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.models.interview import Interview
#
# router = APIRouter()
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# @router.post("/start")
# def start_interview(user_id: int, db: Session = Depends(get_db)):
#     interview = Interview(
#         user_id=user_id,
#         type="mock",
#         status="started"
#     )
#     db.add(interview)
#     db.commit()
#     db.refresh(interview)
#
#     return {"interview_id": interview.id}