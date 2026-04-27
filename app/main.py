from fastapi import FastAPI
from app.routes import auth, interview, ai
from app.websocket.interview_socket import router as interview_socket_router
from app.database import Base, engine
from dotenv import load_dotenv
load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(interview.router, prefix="/interview")
app.include_router(ai.router, prefix="/ai")
app.include_router(interview_socket_router)


@app.get("/")
def root():
    return {"message": "AI Interview WebSocket Server Running"}