import os

from fastapi import FastAPI, Request, Depends, WebSocket
from dotenv import load_dotenv
from app.routes.auth import router as registration_router
#from app.websocket.interview_socket import router as interview_socket_router
from app.database import Base, engine
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes.resume import router as resume_router

from app.websocket.chat_socket import chat_websocket
from app.models import chat, message
from app.routes.chat import router as chat_router






load_dotenv()
#print("GROQ:", os.getenv("GEMINI_API_KEY"))

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(registration_router, prefix="/auth")
#app.include_router(interview_socket_router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(resume_router)
app.include_router(chat_router)


# existing code এর নিচে add করো
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await chat_websocket(websocket)

@app.get("/")
def root():
    return {"message": "AI Interview WebSocket Server Running"}




