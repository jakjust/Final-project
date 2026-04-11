import re
from typing import Optional


MOCK_ORDERS = {
    "ORD001": "Rejected due to insufficient buying power.",
    "ORD002": "Pending until market open.",
    "ORD003": "Executed successfully.",
    "ORD004": "Rejected due to invalid order quantity."
}

MOCK_CUSTOMERS = {
    "CUST1001": "Verification pending additional identity documents.",
    "CUST1002": "Fully verified.",
    "CUST1003": "Verification rejected due to mismatched address information."
}


def extract_order_id(text: str) -> Optional[str]:
    match = re.search(r"\bORD\d+\b", text.upper())
    return match.group(0) if match else None


def extract_customer_id(text: str) -> Optional[str]:
    match = re.search(r"\bCUST\d+\b", text.upper())
    return match.group(0) if match else None


def format_order_response(order_id: str, status: str) -> dict:
    return {
        "route": "Tool Response",
        "answer": f"Your order {order_id} status is: {status}",
        "reason": "The system detected an order ID and used the mock order-status lookup tool.",
        "next_step": (
            "If the issue is unresolved, review your account balance, trading permissions, "
            "or contact support with the same order ID."
        ),
        "source": "Mock order lookup tool"
    }


def format_customer_response(customer_id: str, status: str) -> dict:
    return {
        "route": "Tool Response",
        "answer": f"Customer {customer_id} verification status: {status}",
        "reason": "The system detected a customer ID and used the mock account-verification lookup tool.",
        "next_step": (
            "If additional documents are required, resubmit them through the verification portal "
            "and wait for the next compliance review."
        ),
        "source": "Mock account verification tool"
    }


def handle_structured_query(user_text: str) -> Optional[dict]:
    order_id = extract_order_id(user_text)
    if order_id:
        status = MOCK_ORDERS.get(order_id, "No matching order record was found.")
        return format_order_response(order_id, status)

    customer_id = extract_customer_id(user_text)
    if customer_id:
        status = MOCK_CUSTOMERS.get(customer_id, "No matching customer record was found.")
        return format_customer_response(customer_id, status)

    return None
