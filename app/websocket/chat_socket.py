from fastapi import WebSocket, WebSocketDisconnect
from app.database import SessionLocal
from app.services.chat_service import handle_chat
import json
import traceback

async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket Connected")

    # # ── প্রথম message শুধু handshake, process করবো না ──
    # handshake = await websocket.receive_text()
    # print("🤝 Handshake:", handshake)

    while True:
        try:
            raw = await websocket.receive_text()
            print("📩 Received:", raw)

            try:
                data = json.loads(raw)
            except:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue

            user_id = data.get("user_id")
            chat_id = data.get("chat_id")
            message = data.get("message")

            if not user_id or not message:
                await websocket.send_text(json.dumps({
                    "error": "user_id and message required"
                }))
                continue

            db = SessionLocal()
            try:
                result = handle_chat(db, user_id, chat_id, message)
                await websocket.send_text(json.dumps(result))
                print("✅ Done:", result)
            except Exception as e:
                traceback.print_exc()
                db.rollback()
                await websocket.send_text(json.dumps({"error": str(e)}))
            finally:
                db.close()

        except WebSocketDisconnect:
            print("🔌 Disconnected")
            break
        except Exception as e:
            traceback.print_exc()
            break