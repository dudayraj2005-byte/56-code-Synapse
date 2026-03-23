from models import Ticket
from services.nlp import classify_category, classify_severity

def create_ticket(db, message):
    category = classify_category(message)
    severity = classify_severity(message)

    ticket = Ticket(
        user_message=message,
        category=category,
        severity=severity
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket