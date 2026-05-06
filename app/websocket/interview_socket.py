# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from app.services.ai_engine import get_ai_response, get_ai_response_chat
#
# router = APIRouter()
#
#
# # =========================
# # Connection Manager
# # =========================
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections = {}
#
#     async def connect(self, websocket: WebSocket, user_id: str):
#         self.active_connections[user_id] = websocket
#
#     def disconnect(self, user_id: str):
#         self.active_connections.pop(user_id, None)
#
#     async def send(self, user_id: str, message: dict):
#         ws = self.active_connections.get(user_id)
#         if ws:
#             await ws.send_json(message)
#
#
# manager = ConnectionManager()
#
#
# # =========================
# # 1. INTERVIEW WEBSOCKET (UNCHANGED)
# # =========================
# @router.websocket("/ws/interview")
# async def interview_socket(websocket: WebSocket):
#     await websocket.accept()
#
#     user_id = None
#
#     try:
#         init_data = await websocket.receive_json()
#
#         user_id = init_data.get("user_id")
#         role = init_data.get("role", "software engineer")
#
#         await manager.connect(websocket, user_id)
#
#         await manager.send(user_id, {
#             "type": "system",
#             "message": "Interview started"
#         })
#
#         while True:
#             data = await websocket.receive_json()
#             user_message = data.get("message")
#
#             ai_reply = await get_ai_response(user_message, role)
#
#             await manager.send(user_id, {
#                 "type": "ai",
#                 "message": ai_reply
#             })
#
#     except WebSocketDisconnect:
#         if user_id:
#             manager.disconnect(user_id)
#
#
# # =========================
# # 2. NORMAL CHAT WEBSOCKET (SIMPLE)
# # =========================
# @router.websocket("/ws/chat")
# async def chat_socket(websocket: WebSocket):
#     await websocket.accept()
#
#     user_id = None
#
#     try:
#         init_data = await websocket.receive_json()
#         user_id = init_data.get("user_id")
#
#         if not user_id:
#             await websocket.close(code=1008)
#             return
#
#         await manager.connect(websocket, user_id)
#
#         # ❌ NO SYSTEM MESSAGE HERE (silent connect)
#
#         while True:
#             try:
#                 data = await websocket.receive_json()
#                 user_message = data.get("message")
#
#                 if not user_message:
#                     continue
#
#                 ai_reply = await get_ai_response_chat(user_message)
#
#                 await manager.send(user_id, {
#                     "type": "ai",
#                     "message": ai_reply
#                 })
#
#             except WebSocketDisconnect:
#                 print("Client disconnected inside loop")
#                 break
#
#     except WebSocketDisconnect:
#         print("Client disconnected before init")
#
#     except Exception as e:
#         print("WebSocket crash:", e)
#
#     finally:
#         if user_id:
#             manager.disconnect(user_id)