from fastapi import WebSocket, WebSocketDisconnect
from app.database import SessionLocal
from app.services.interview_service import start_interview, handle_interview
from app.services.subscription_service import can_start_interview, increment_interview_usage   # ← NEW
import json
import traceback
import uuid


async def interview_websocket(websocket: WebSocket):
    await websocket.accept()
    print("✅ Interview WebSocket Connected")

    while True:
        try:
            raw = await websocket.receive_text()
            print("📩 Received:", raw)

            try:
                data = json.loads(raw)
            except Exception:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue

            user_id    = data.get("user_id")
            action     = data.get("action")
            session_id = data.get("session_id")
            message    = data.get("message")

            if not user_id:
                await websocket.send_text(json.dumps({"error": "user_id required"}))
                continue

            if action not in ("start", "answer"):
                await websocket.send_text(json.dumps({"error": "action must be 'start' or 'answer'"}))
                continue

            if action == "answer" and not session_id:
                await websocket.send_text(json.dumps({"error": "session_id required for action=answer"}))
                continue

            if action == "answer" and not message:
                await websocket.send_text(json.dumps({"error": "message required for action=answer"}))
                continue

            db = SessionLocal()
            try:
                if action == "start":
                    category   = data.get("category", "General")
                    topics     = data.get("topics", [])
                    difficulty = data.get("difficulty", "Medium")

                    if not topics:
                        await websocket.send_text(json.dumps({"error": "topics required"}))
                        db.close()
                        continue

                    # ── NEW: Daily limit check ──────────────────────────────
                    if not can_start_interview(db, int(user_id)):
                        await websocket.send_text(json.dumps({
                            "error":   "daily_limit_reached",
                            "message": "আজকের interview limit শেষ। Pro plan নিলে unlimited interview করতে পারবে।"
                        }))
                        db.close()
                        continue
                    # ───────────────────────────────────────────────────────

                    result = start_interview(db, user_id, category, topics, difficulty)

                    # ── NEW: Usage count বাড়াও ──────────────────────────────
                    increment_interview_usage(db, int(user_id))
                    # ───────────────────────────────────────────────────────

                elif action == "answer":
                    result = handle_interview(db, user_id, session_id, message)

                await websocket.send_text(json.dumps(serialize_result(result)))
                print("✅ Done:", result)

            except Exception as e:
                traceback.print_exc()
                db.rollback()
                await websocket.send_text(json.dumps({"error": str(e)}))
            finally:
                db.close()

        except WebSocketDisconnect:
            print("🔌 Interview WebSocket Disconnected")
            break
        except Exception as e:
            traceback.print_exc()
            break


def serialize_result(result: dict) -> dict:
    return {
        k: str(v) if isinstance(v, uuid.UUID) else v
        for k, v in result.items()
    }