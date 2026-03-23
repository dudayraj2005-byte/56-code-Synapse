def classify_category(message: str):
    message = message.lower()

    if "refund" in message or "payment" in message:
        return "Billing"
    elif "error" in message or "bug" in message:
        return "Technical"
    elif "login" in message:
        return "Account"
    return "General"


def classify_severity(message: str):
    message = message.lower()

    if "urgent" in message or "immediately" in message:
        return "High"
    elif "not working" in message:
        return "Medium"
    return "Low"