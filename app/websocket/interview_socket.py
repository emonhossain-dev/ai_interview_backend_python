from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.ai_engine import get_ai_response

router = APIRouter()

# =========================
# Connection Manager
# =========================
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        # ❌ NO accept here
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send(self, user_id: str, message: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)


manager = ConnectionManager()


# =========================
# WebSocket Route
# =========================
@router.websocket("/ws/interview")
async def interview_socket(websocket: WebSocket):
    await websocket.accept()

    # প্রথম message receive করো safely
    init_data = await websocket.receive_json()

    user_id = init_data.get("user_id")
    role = init_data.get("role", "software engineer")

    await manager.connect(websocket, user_id)

    await manager.send(user_id, {
        "type": "system",
        "message": "Interview started"
    })

    try:
        while True:
            data = await websocket.receive_json()

            user_message = data.get("message")

            ai_reply = await get_ai_response(user_message, role)

            await manager.send(user_id, {
                "type": "ai",
                "message": ai_reply
            })

    except WebSocketDisconnect:
        manager.disconnect(user_id)