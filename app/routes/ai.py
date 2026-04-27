from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import generate_answer

router = APIRouter()

class AIRequest(BaseModel):
    question: str
    role: str

@router.post("/answer")
def get_ai_answer(data: AIRequest):

    answer = generate_answer(data.question, data.role)

    return {
        "question": data.question,
        "answer": answer
    }