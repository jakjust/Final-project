from __future__ import annotations

from typing import Dict, Optional

ORDERS: Dict[str, Dict[str, str]] = {
    "ORD001": {
        "status": "Rejected",
        "reason": "Insufficient buying power in the cash account.",
        "next_step": "Deposit additional funds or reduce order size before resubmitting.",
    },
    "ORD002": {
        "status": "Pending",
        "reason": "Order queued outside market hours.",
        "next_step": "The order will be sent when the market opens unless the client cancels it first.",
    },
    "ORD003": {
        "status": "Executed",
        "reason": "Trade completed successfully at market price.",
        "next_step": "Review the contract note and portfolio position for execution details.",
    },
}

ACCOUNTS: Dict[str, Dict[str, str]] = {
    "CUST1001": {
        "verification": "Pending Review",
        "details": "Proof-of-address document is blurred and needs to be re-uploaded.",
        "next_step": "Upload a clear document showing your full name, address, and issue date.",
    },
    "CUST1002": {
        "verification": "Verified",
        "details": "All onboarding checks were completed successfully.",
        "next_step": "No further action is required.",
    },
    "CUST1003": {
        "verification": "Rejected",
        "details": "Name mismatch between identity document and account registration.",
        "next_step": "Update the profile details or submit a corrected identity document.",
    },
}


def lookup_order_status(order_id: str) -> Optional[str]:
    record = ORDERS.get(order_id.upper())
    if not record:
        return "I could not find that order ID in the demo system. Please verify the ID or escalate to human support."

    return (
        f"Order {order_id.upper()} status: {record['status']}. "
        f"Reason: {record['reason']} "
        f"Recommended next step: {record['next_step']}"
    )



def lookup_account_verification(customer_id: str) -> Optional[str]:
    record = ACCOUNTS.get(customer_id.upper())
    if not record:
        return "I could not find that customer ID in the demo system. Please verify the ID or ask a human agent to investigate."

    return (
        f"Customer {customer_id.upper()} verification status: {record['verification']}. "
        f"Details: {record['details']} "
        f"Recommended next step: {record['next_step']}"
    )
