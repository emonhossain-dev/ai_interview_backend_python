from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resumes import Resume
import os
import uuid

router = APIRouter(prefix="/resume", tags=["Resume"])


UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/uploadResume")
async def upload_resume(
    user_id: int = Form(...),
    title: str = Form(None),
    summary: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ❌ prevent multiple resume
    existing = db.query(Resume).filter(Resume.user_id == user_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Resume already exists. Please delete first."
        )

    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    new_resume = Resume(
        user_id=user_id,
        title=title,
        summary=summary,
        file_url=file_path
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "message": "Resume uploaded successfully",
        "resume_id": new_resume.id,
        "file_url": new_resume.file_url
    }


@router.delete("/deleteResume/{user_id}")
async def delete_resume(
    user_id: int,
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.user_id == user_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # delete file from storage
    if resume.file_url and os.path.exists(resume.file_url):
        os.remove(resume.file_url)

    db.delete(resume)
    db.commit()

    return {
        "message": "Resume deleted successfully"
    }