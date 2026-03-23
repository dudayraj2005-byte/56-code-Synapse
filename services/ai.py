from transformers import pipeline

# Load models
classifier = pipeline("zero-shot-classification")
sentiment = pipeline("sentiment-analysis")

CATEGORIES = ["Billing", "Technical", "Account", "General"]

HIGH_PRIORITY_WORDS = [
    "urgent", "immediately", "asap",
    "not working at all", "payment failed",
    "refund not received", "error again and again"
]

MEDIUM_PRIORITY_WORDS = [
    "not working", "issue", "problem", "unable", "failed"
]


def process_message(message: str):
    message_lower = message.lower()

    # 1. Category detection
    category_result = classifier(message, CATEGORIES)
    category = category_result["labels"][0]

    # 2. Sentiment
    sentiment_result = sentiment(message)[0]

    # 3. Improved severity logic
    if any(word in message_lower for word in HIGH_PRIORITY_WORDS):
        severity = "High"
    elif any(word in message_lower for word in MEDIUM_PRIORITY_WORDS):
        severity = "Medium"
    elif sentiment_result["label"] == "NEGATIVE":
        severity = "Medium"
    else:
        severity = "Low"

    # 4. Escalation logic
    escalate = severity == "High"

    # 5. Response generation
    if severity == "Low":
        response = "I can help you with that. Let me guide you."
    elif severity == "Medium":
        response = "I understand the issue. I'll try to assist you, and escalate if needed."
    else:
        response = "This seems important. I'm escalating this to our support team right away."

    return {
        "response": response,
        "category": category,
        "severity": severity,
        "escalate": escalate
    }