from __future__ import annotations

from typing import Dict, List

SENSITIVE_KEYWORDS: List[str] = [
    "complaint",
    "loss",
    "lost money",
    "lawsuit",
    "legal",
    "fraud",
    "regulator",
    "chargeback",
    "escalate",
    "scam",
    "unauthorized",
    "stolen",
    "dispute",
    "ombudsman",
    "misleading",
]


def should_escalate(query: str) -> bool:
    normalized = query.lower()
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)



def create_case_summary(user_query: str, conversation: List[Dict[str, str]]) -> str:
    last_messages = conversation[-4:]
    history_lines = []
    for item in last_messages:
        role = item.get("role", "user").capitalize()
        content = item.get("content", "").strip()
        history_lines.append(f"- {role}: {content}")

    history_text = "\n".join(history_lines) if history_lines else "- No prior conversation history available."

    return (
        "**Escalation recommended**\n\n"
        "**Reason:** The query may involve financial loss, complaint handling, fraud risk, dispute resolution, or another sensitive matter requiring human review.\n\n"
        f"**Customer issue summary:** {user_query.strip()}\n\n"
        "**Recent conversation:**\n"
        f"{history_text}\n\n"
        "**Suggested agent action:** Review account activity, verify whether any transaction issue or policy exception occurred, and send a compliant human response."
    )
