from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeBase:
    def __init__(self, data_dir: str = "data"):
        self.base_path = Path(__file__).resolve().parent
        self.data_dir = self.base_path / data_dir

        # Render-safe fallback:
        # If /data does not exist, also allow .txt files in repo root.
        if self.data_dir.exists() and self.data_dir.is_dir():
            txt_files = sorted(self.data_dir.glob("*.txt"))
        else:
            txt_files = sorted(self.base_path.glob("*.txt"))

        if not txt_files:
            raise FileNotFoundError(
                f"No knowledge-base text files found. Checked: {self.data_dir} and repo root."
            )

        self.documents: List[str] = []
        self.sources: List[str] = []

        for file_path in txt_files:
            text = file_path.read_text(encoding="utf-8").strip()
            if text:
                self.documents.append(text)
                self.sources.append(file_path.name)

        if not self.documents:
            raise ValueError("Knowledge base files were found, but all were empty.")

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(self.documents)

    def retrieve(self, question: str, top_k: int = 1) -> List[Tuple[str, str, float]]:
        query_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(query_vec, self.doc_matrix).flatten()

        ranked_indices = scores.argsort()[::-1][:top_k]
        results = []

        for idx in ranked_indices:
            results.append((self.sources[idx], self.documents[idx], float(scores[idx])))

        return results

    def answer_question(self, question: str) -> dict:
        retrieved = self.retrieve(question, top_k=1)
        source_name, retrieved_text, score = retrieved[0]

        if score < 0.05:
            return {
                "route": "Knowledge Base Answer",
                "answer": (
                    "I could not find enough reliable policy information in the knowledge base to answer this confidently."
                ),
                "reason": (
                    "The retrieval score was too low, which means no document matched the question strongly enough."
                ),
                "next_step": (
                    "Please rephrase the question, provide more details, or contact a human support agent for help."
                ),
                "source": source_name,
                "context": retrieved_text[:500]
            }

        short_answer = self._summarize_context(retrieved_text)

        return {
            "route": "Knowledge Base Answer",
            "answer": short_answer,
            "reason": (
                f"The system matched your question to the most relevant internal policy document: {source_name} "
                f"(relevance score: {score:.2f})."
            ),
            "next_step": (
                "Review the policy guidance above. If your issue depends on a specific order or customer record, "
                "include an order ID or customer ID."
            ),
            "source": source_name,
            "context": retrieved_text
        }

    def _summarize_context(self, text: str, max_chars: int = 450) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[:max_chars].rsplit(" ", 1)[0] + "..."
