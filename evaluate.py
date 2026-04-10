from __future__ import annotations

import csv
from pathlib import Path

from escalation import should_escalate
from rag_engine import AnswerGenerator, KnowledgeBase
from tools import lookup_account_verification, lookup_order_status

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_CSV = Path(__file__).parent / "evaluation_results.csv"

TEST_CASES = [
    {
        "query": "What are the fees for US stock trades?",
        "expected_route": "rag_policy_qa",
        "expected_keyword": "USD 2.50",
    },
    {
        "query": "How do I update my KYC documents?",
        "expected_route": "rag_policy_qa",
        "expected_keyword": "re-upload",
    },
    {
        "query": "Why was my order rejected? Order ID ORD001",
        "expected_route": "order_status_tool",
        "expected_keyword": "Insufficient buying power",
    },
    {
        "query": "Check account verification for customer CUST1001",
        "expected_route": "account_verification_tool",
        "expected_keyword": "blurred",
    },
    {
        "query": "I lost money because your system failed and I want to make a complaint.",
        "expected_route": "human_escalation",
        "expected_keyword": "Escalation recommended",
    },
    {
        "query": "Why can a withdrawal be delayed?",
        "expected_route": "rag_policy_qa",
        "expected_keyword": "delayed",
    },
]


def route_query(query: str, kb: KnowledgeBase, generator: AnswerGenerator) -> tuple[str, str]:
    if should_escalate(query):
        return "human_escalation", "Escalation recommended"

    upper = query.upper()
    import re
    order_match = re.search(r"\bORD\d{3,}\b", upper)
    if order_match:
        return "order_status_tool", lookup_order_status(order_match.group())
    customer_match = re.search(r"\bCUST\d{3,}\b", upper)
    if customer_match:
        return "account_verification_tool", lookup_account_verification(customer_match.group())

    retrievals = kb.search(query, top_k=3)
    return "rag_policy_qa", generator.generate(query, retrievals)


if __name__ == "__main__":
    kb = KnowledgeBase(data_dir=str(DATA_DIR))
    generator = AnswerGenerator()
    rows = []

    for case in TEST_CASES:
        route, answer = route_query(case["query"], kb, generator)
        passed = route == case["expected_route"] and case["expected_keyword"].lower() in answer.lower()
        rows.append(
            {
                "query": case["query"],
                "expected_route": case["expected_route"],
                "actual_route": route,
                "expected_keyword": case["expected_keyword"],
                "pass": passed,
            }
        )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    passed = sum(1 for row in rows if row["pass"])
    print(f"Saved {OUTPUT_CSV.name}. Passed {passed}/{len(rows)} test cases.")
