from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import SessionLocal
from services.ticket import create_ticket
from services.ai import process_message
import json

router = APIRouter()

# DB session helper
def get_db():
    return SessionLocal()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    db: Session = get_db()

    try:
        while True:
            # 📩 Receive message from client
            data = await websocket.receive_text()
            data = json.loads(data)
            message = data.get("message")

            if not message:
                await websocket.send_text(json.dumps({
                    "error": "Message is required"
                }))
                continue

            try:
                # 🧠 Process using AI
                ai_result = process_message(message)

                # 🎫 Escalate if needed
                if ai_result["escalate"]:
                    ticket = create_ticket(db, message)

                    response = {
                        "response": ai_result["response"],
                        "ticket_id": ticket.id,
                        "category": ai_result["category"],
                        "severity": ai_result["severity"],
                        "status": "Ticket Created"
                    }
                else:
                    response = {
                        "response": ai_result["response"],
                        "category": ai_result["category"],
                        "severity": ai_result["severity"],
                        "status": "Resolved by Bot"
                    }

                # 📤 Send response back instantly
                await websocket.send_text(json.dumps(response))

            except Exception as e:
                # ⚠️ Fallback
                ticket = create_ticket(db, message)

                await websocket.send_text(json.dumps({
                    "response": "Error occurred, escalated to support.",
                    "ticket_id": ticket.id,
                    "category": "General",
                    "severity": "High",
                    "status": "Fallback Ticket Created",
                    "error": str(e)
                }))

    except WebSocketDisconnect:
        print("Client disconnected")
        db.close()