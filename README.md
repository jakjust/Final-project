# AI-Powered Fintech Support Assistant

This repository is a **coding-based classroom prototype** for the AI / LLM / RAG group assignment. It demonstrates how a digital investment platform can use retrieval-augmented generation, simple AI-agent routing, and human escalation logic to support customers more consistently.

## Business problem
Digital investment platforms receive complex support questions about:
- account verification and KYC documents
- fees and charges
- order rejections and trade issues
- withdrawals and fraud-related concerns

Human agents often have to search multiple policy documents manually. This prototype shows how an AI support assistant can retrieve relevant knowledge, use simple backend tools, and escalate high-risk cases instead of answering them freely.

## What the prototype demonstrates
1. **RAG-style policy QA** over internal support documents
2. **Tool routing** for structured order/account lookups
3. **Safety escalation** for complaints, fraud, legal, and loss-related queries
4. **Transparent evidence display** in the Streamlit interface

## Project structure
```bash
ai_finance_submission/
├── app.py
├── rag_engine.py
├── tools.py
├── escalation.py
├── evaluate.py
├── evaluation_results.csv
├── requirements.txt
├── README.md
├── demo_script.md
├── submission_checklist.md
└── data/
    ├── fees_faq.txt
    ├── kyc_policy.txt
    ├── order_issues.txt
    ├── withdrawals.txt
    ├── product_suitability.txt
    └── complaints_policy.txt
```

## How to run
### 1. Create a virtual environment
```bash
python -m venv .venv
```

### 2. Activate it
**Windows**
```bash
.venv\Scripts\activate
```

**Mac / Linux**
```bash
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the app
```bash
streamlit run app.py
```

## Optional OpenAI integration
The prototype works offline using deterministic fallback generation. If you want live LLM answers, set an API key:

**Windows PowerShell**
```bash
$env:OPENAI_API_KEY="your_api_key_here"
```

**Mac / Linux**
```bash
export OPENAI_API_KEY="your_api_key_here"
```

Optional model override:
```bash
export OPENAI_MODEL="gpt-4.1-mini"
```

## Demo prompts
- What are the fees for US stock trades?
- How do I update my KYC documents?
- Why was my order rejected? Order ID ORD001
- Check account verification for customer CUST1001
- I lost money because your system failed and I want to make a complaint.
- Why can a withdrawal be delayed?

## Evaluation
Run the included mini test set:
```bash
python evaluate.py
```
This generates `evaluation_results.csv` so your group can show a simple validation table in the report or demo.

## Suggested division of work
- **Member 1:** business problem, report writing, presenter
- **Member 2:** knowledge-base documents and test questions
- **Member 3:** retrieval and answer generation
- **Member 4:** Streamlit UI and tool routing
- **Member 5:** evaluation, slides, and demo video

## Submission reminder
For the coding brief, you still need a **3–5 minute screen-recorded walkthrough**. This folder includes the code, mini evaluation, and demo script, but the video itself must be recorded by your group.


## Deploy on Render
This project can be deployed on **Render** as a simple Python web service without changing the app architecture.

### Option 1: Blueprint deployment (recommended)
1. Push this folder to GitHub.
2. In Render, click **New +** → **Blueprint**.
3. Select your repository.
4. Render will detect `render.yaml` and create the web service automatically.
5. After deployment completes, open the public URL.

### Option 2: Manual web service deployment
1. Push this folder to GitHub.
2. In Render, click **New +** → **Web Service**.
3. Connect the repository.
4. Set:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
5. Deploy and open the generated URL.

### Optional environment variables
- `OPENAI_API_KEY` for live LLM responses
- `OPENAI_MODEL` if you want to override the default model name

### Why Render is acceptable for this assignment
The brief only requires a **working prototype or demo using Python or other tools**. It does not require any specific framework or hosting platform, so deploying this Streamlit prototype on Render still complies with the coding-based submission requirements.
