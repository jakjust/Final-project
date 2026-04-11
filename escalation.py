ESCALATION_KEYWORDS = [
    "complaint",
    "lost money",
    "financial loss",
    "fraud",
    "legal",
    "lawsuit",
    "sue",
    "dispute",
    "regulator",
    "compensation",
    "serious issue"
]


def detect_escalation(user_text: str) -> bool:
    text = user_text.lower()
    return any(keyword in text for keyword in ESCALATION_KEYWORDS)


def build_escalation_response(user_text: str) -> dict:
    return {
        "route": "Escalated to Human Support",
        "answer": (
            "This issue has been identified as sensitive and should be reviewed by a human support agent."
        ),
        "reason": (
            "The system detected language related to financial loss, complaint handling, legal risk, or dispute escalation."
        ),
        "next_step": (
            "A human agent should review the case, confirm the account context, and respond using the official "
            "complaint-handling and compliance process."
        ),
        "source": "Escalation policy",
        "summary": (
            f"Customer message flagged for escalation: {user_text}"
        )
    }
