from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import ChatRequest
import os
import requests

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔁 FALLBACK RULE-BASED CLASSIFICATION (VERY IMPORTANT)
def fallback_classify(message: str):
    msg = message.lower()

    # Category
    if any(x in msg for x in ["payment", "refund", "billing", "charge"]):
        category = "Billing"
    elif any(x in msg for x in ["error", "bug", "crash", "not working"]):
        category = "Technical"
    else:
        category = "General"

    # Severity
    if any(x in msg for x in ["urgent", "asap", "immediately", "not working"]):
        severity = "High"
    elif any(x in msg for x in ["slow", "delay", "issue"]):
        severity = "Medium"
    else:
        severity = "Low"

    return category, severity


# 🤖 AI Classification (FIXED + SAFE)
def ai_classify(message: str):
    HF_API_KEY = os.getenv("HF_API_KEY")

    if not HF_API_KEY:
        return fallback_classify(message)

    prompt = f"""
    Classify this complaint.

    Complaint: {message}

    Output format:
    Category: Billing/Technical/General
    Severity: High/Medium/Low
    """

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-base",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt},
            timeout=10
        )

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            text = result[0]["generated_text"].lower()

            category = "General"
            severity = "Low"

            if "billing" in text:
                category = "Billing"
            elif "technical" in text:
                category = "Technical"

            if "high" in text:
                severity = "High"
            elif "medium" in text:
                severity = "Medium"

            return category, severity

    except Exception as e:
        print("AI classify error:", e)

    # fallback if AI fails
    return fallback_classify(message)


# 🤖 AI Reply (FIXED)
def ai_reply(message: str):
    HF_API_KEY = os.getenv("HF_API_KEY")

    if not HF_API_KEY:
        return None

    prompt = f"""
    You are a friendly human support agent.

    Respond naturally in 2-3 lines.
    Be helpful and polite.

    User: {message}
    """

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-base",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt},
            timeout=10
        )

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

    except Exception as e:
        print("AI reply error:", e)

    return None


# 💬 CHAT ENDPOINT (FINAL LOGIC)
@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    message = req.message

    # 1️⃣ Always classify
    category, severity = ai_classify(message)

    # 2️⃣ Get AI reply
    reply = ai_reply(message)

    # 3️⃣ Ticket logic
    if severity in ["High", "Medium"]:
        ticket = models.Ticket(
            user_message=message,
            category=category,
            severity=severity
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return {
            "response": reply or "I understand your issue. I've created a support ticket for you.",
            "ticket_id": ticket.id,
            "category": category,
            "severity": severity
        }

    # 4️⃣ Normal chat
    return {
        "response": reply or "I'm here to help! 😊",
        "category": category,
        "severity": severity
    }