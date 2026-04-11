import streamlit as st
from rag_engine import KnowledgeBase
from tools import handle_structured_query
from escalation import detect_escalation, build_escalation_response


st.set_page_config(
    page_title="AI-Powered Fintech Support Assistant",
    page_icon="💬",
    layout="wide"
)


@st.cache_resource
def load_kb():
    return KnowledgeBase()


def render_response(response: dict):
    route = response.get("route", "Unknown")

    if route == "Escalated to Human Support":
        st.error(f"Route: {route}")
    elif route == "Tool Response":
        st.info(f"Route: {route}")
    else:
        st.success(f"Route: {route}")

    st.markdown(f"### Answer")
    st.write(response.get("answer", "No answer available."))

    st.markdown(f"**Why this route was chosen:**")
    st.write(response.get("reason", "No reason provided."))

    st.markdown(f"**Recommended next step:**")
    st.write(response.get("next_step", "No next step available."))

    st.markdown(f"**Source:** `{response.get('source', 'Unknown')}`")

    if response.get("summary"):
        st.markdown("**Escalation summary:**")
        st.write(response["summary"])

    if response.get("context"):
        with st.expander("Retrieved policy context"):
            st.write(response["context"])


def main():
    kb = load_kb()

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
        st.markdown(
            """
1. Detect sensitive issues that require human escalation.  
2. Route structured IDs to mock backend tools.  
3. Otherwise retrieve policy text and answer from the knowledge base.
            """
        )

        st.divider()
        st.caption("This is a simplified prototype using mock data and local support documents.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                render_response(msg["content"])

    user_input = st.chat_input("Ask a policy, account, or trade-support question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            if detect_escalation(user_input):
                response = build_escalation_response(user_input)
            else:
                tool_response = handle_structured_query(user_input)
                if tool_response is not None:
                    response = tool_response
                else:
                    response = kb.answer_question(user_input)

            render_response(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
                    }

    st.session_state.messages.append(assistant_message)
