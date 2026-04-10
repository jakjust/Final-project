from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from escalation import create_case_summary, should_escalate
from rag_engine import AnswerGenerator, KnowledgeBase
from tools import lookup_account_verification, lookup_order_status

st.set_page_config(page_title="Fintech Support AI", page_icon="💬", layout="wide")

DATA_DIR = Path(__file__).parent / "data"


@st.cache_resource
def load_kb() -> KnowledgeBase:
    return KnowledgeBase(data_dir=str(DATA_DIR))


@st.cache_resource
def load_generator() -> AnswerGenerator:
    return AnswerGenerator()


kb = load_kb()
generator = load_generator()

if "messages" not in st.session_state:
    st.session_state.messages = []


def run_tool_if_needed(query: str) -> tuple[str | None, str | None]:
    order_match = re.search(r"\bORD\d{3,}\b", query.upper())
    if order_match:
        return lookup_order_status(order_match.group()), "order_status_tool"

    customer_match = re.search(r"\bCUST\d{3,}\b", query.upper())
    if customer_match:
        return lookup_account_verification(customer_match.group()), "account_verification_tool"

    normalized = query.lower()
    if "account verification" in normalized or "kyc status" in normalized:
        return (
            "Please provide a customer ID such as CUST1001 so I can check the mock account verification tool.",
            "missing_customer_id",
        )

    return None, None


st.title("💬 AI-Powered Fintech Support Assistant")
st.caption(
    "Classroom prototype for a digital investment platform using retrieval-augmented generation, mock tools, and safe human escalation."
)

with st.sidebar:
    st.subheader("Demo prompts")
    st.markdown(
        """
- What are the fees for US stock trades?
- How do I update my KYC documents?
- Why was my order rejected? Order ID ORD001
- Check account verification for customer CUST1001
- I lost money because your system failed and I want to make a complaint.
        """
    )
    st.divider()
    st.subheader("Prototype routing logic")
    st.write("1. Detect sensitive issues that require human escalation.")
    st.write("2. Route structured IDs to mock backend tools.")
    st.write("3. Otherwise retrieve policy text and generate a grounded answer.")
    st.divider()
    if generator.openai_client:
        st.success("OpenAI API key detected: live LLM answer generation is enabled.")
    else:
        st.info("No API key detected: the app runs in deterministic fallback mode.")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        route = message.get("route")
        if route:
            st.caption(f"Route used: {route}")
        if message.get("sources"):
            with st.expander("Retrieved evidence"):
                for source in message["sources"]:
                    st.markdown(
                        f"**{source['source']}** · chunk {source['chunk_id']} · score {source['score']:.3f}\n\n{source['text']}"
                    )


prompt = st.chat_input("Ask a policy, account, or trade-support question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing your request..."):
            if should_escalate(prompt):
                answer = create_case_summary(prompt, st.session_state.messages)
                st.warning("Sensitive case detected. Human escalation is recommended.")
                st.markdown(answer)
                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "route": "human_escalation",
                    "sources": [],
                }
            else:
                tool_result, route = run_tool_if_needed(prompt)
                if tool_result:
                    st.markdown(tool_result)
                    assistant_message = {
                        "role": "assistant",
                        "content": tool_result,
                        "route": route,
                        "sources": [],
                    }
                else:
                    retrievals = kb.search(prompt, top_k=3)
                    answer = generator.generate(prompt, retrievals)
                    st.markdown(answer)
                    with st.expander("Retrieved evidence"):
                        for source in retrievals:
                            st.markdown(
                                f"**{source['source']}** · chunk {source['chunk_id']} · score {source['score']:.3f}\n\n{source['text']}"
                            )
                    assistant_message = {
                        "role": "assistant",
                        "content": answer,
                        "route": "rag_policy_qa",
                        "sources": retrievals,
                    }

    st.session_state.messages.append(assistant_message)
