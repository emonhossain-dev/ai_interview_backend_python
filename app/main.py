from fastapi import FastAPI, Request
from dotenv import load_dotenv
from app.routes.interview import router as interview_router
from app.routes.ai import router as ai_router
from app.routes.registration import router as registration_router
from app.websocket.interview_socket import router as interview_socket_router
from app.database import Base, engine
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(interview_router, prefix="/interview")
app.include_router(ai_router, prefix="/ai")

app.include_router(registration_router, prefix="/register")
app.include_router(interview_socket_router)


@app.get("/")
def root():
    return {"message": "AI Interview WebSocket Server Running"}