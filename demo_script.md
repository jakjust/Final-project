# 3–5 Minute Demo Script

## Setup
- Open terminal in the project folder
- Run `streamlit run app.py`
- Keep the browser window ready at the chat interface
- Mention that this is a classroom prototype for a digital investment platform

## Suggested narration
### 1. Problem and objective (20–30 seconds)
"Our project solves the problem of slow and inconsistent customer support in digital investment platforms. Users ask policy-heavy questions about KYC, fees, trade issues, and withdrawals. We built an AI-powered support assistant that can retrieve answers from internal documents, call mock tools for structured account checks, and escalate sensitive issues to human agents."

### 2. Show RAG policy QA (45–60 seconds)
Type:
`What are the fees for US stock trades?`

Say:
"The system routes this to the RAG policy QA flow. It retrieves the most relevant policy chunks from the internal knowledge base and answers using grounded content rather than guessing. On the right, or in the evidence section, we can show the retrieved source text used for the answer."

### 3. Show KYC support question (30–45 seconds)
Type:
`How do I update my KYC documents?`

Say:
"This is another document-grounded support question. The app retrieves the KYC policy, explains which documents are acceptable, and tells the user how to re-upload corrected documents."

### 4. Show mock tool routing (45–60 seconds)
Type:
`Why was my order rejected? Order ID ORD001`

Say:
"When the query includes a structured identifier like an order ID, the assistant routes the request to a mock backend tool instead of relying on free-text generation. This is safer for structured operational data such as order status."

### 5. Show account verification tool (30–45 seconds)
Type:
`Check account verification for customer CUST1001`

Say:
"The assistant can also look up a mock account status and return a next step for the customer. In a real company, this would connect to internal systems through secure APIs."

### 6. Show escalation workflow (45–60 seconds)
Type:
`I lost money because your system failed and I want to make a complaint.`

Say:
"For sensitive topics such as losses, fraud, legal issues, or complaints, the system does not respond freely. Instead, it generates a summary for a human agent and recommends escalation. This is important for compliance and risk control in finance."

### 7. Close with business value (20–30 seconds)
"Overall, the prototype shows how LLMs, retrieval, simple agent routing, and escalation logic can reduce response time, improve consistency, and keep risky cases under human supervision."
