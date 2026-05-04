import os

from fastapi import FastAPI, Request, Depends
from dotenv import load_dotenv
from app.routes.auth import router as registration_router
from app.websocket.interview_socket import router as interview_socket_router
from app.database import Base, engine
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter
from app.database import get_db, SessionLocal
from fastapi.staticfiles import StaticFiles


load_dotenv()
print("GROQ:", os.getenv("GROQ_API_KEY"))

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(registration_router, prefix="/auth")
app.include_router(interview_socket_router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def root():
    return {"message": "AI Interview WebSocket Server Running"}


@app.get("/test-db")
def test_db(db: SessionLocal = Depends(get_db)):
    return {"message": "Supabase connected successfully 🚀"}