from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: int


class KnowledgeBase:
    """Lightweight local retrieval engine for classroom demos.

    This uses a TF-IDF vector index so the project runs offline.
    The interface mirrors a typical vector retrieval step used in RAG systems.
    """

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.chunks: List[Chunk] = []
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = None
        self._load_documents()

    def _load_documents(self) -> None:
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Knowledge base directory not found: {self.data_dir}")

        files = sorted(self.data_dir.glob("*.txt"))
        if not files:
            raise FileNotFoundError(f"No .txt files found in {self.data_dir}")

        self.chunks.clear()
        for file_path in files:
            text = file_path.read_text(encoding="utf-8")
            for idx, chunk_text in enumerate(self._chunk_text(text)):
                self.chunks.append(Chunk(text=chunk_text, source=file_path.name, chunk_id=idx))

        self.matrix = self.vectorizer.fit_transform([chunk.text for chunk in self.chunks])

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 700) -> List[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: List[str] = []
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= max_chars:
                current = f"{current}\n\n{para}".strip()
            else:
                if current:
                    chunks.append(current)
                current = para

        if current:
            chunks.append(current)
        return chunks

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.matrix is None or not self.chunks:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = scores.argsort()[::-1][:top_k]

        results: List[Dict[str, Any]] = []
        for idx in top_indices:
            if float(scores[idx]) <= 0:
                continue
            results.append(
                {
                    "score": float(scores[idx]),
                    "text": self.chunks[idx].text,
                    "source": self.chunks[idx].source,
                    "chunk_id": self.chunks[idx].chunk_id,
                }
            )
        return results


class AnswerGenerator:
    def __init__(self) -> None:
        self.openai_client = None
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            try:
                from openai import OpenAI

                self.openai_client = OpenAI(api_key=api_key)
            except Exception:
                self.openai_client = None

    def generate(self, query: str, retrievals: List[Dict[str, Any]]) -> str:
        if not retrievals:
            return (
                "I could not find enough grounded information in the knowledge base. "
                "Please rephrase the question or escalate it to a human support agent."
            )

        if self.openai_client:
            return self._generate_with_openai(query, retrievals)
        return self._generate_fallback(query, retrievals)

    def _generate_with_openai(self, query: str, retrievals: List[Dict[str, Any]]) -> str:
        context = "\n\n".join(
            [
                f"Source: {r['source']} (chunk {r['chunk_id']})\nContent:\n{r['text']}"
                for r in retrievals
            ]
        )
        prompt = f"""
You are a customer-support assistant for a digital investment platform.
Answer ONLY using the retrieved context below.
Do not provide financial advice, trading recommendations, or unsupported claims.
If the answer is not clearly supported by the context, say you do not have enough information.
Keep the answer concise, professional, and actionable.
Include a final line starting with 'Sources:' and list the filenames used.

User question:
{query}

Retrieved context:
{context}
""".strip()

        try:
            response = self.openai_client.responses.create(
                model=self.model_name,
                input=prompt,
                temperature=0.2,
            )
            return response.output_text.strip()
        except Exception:
            return self._generate_fallback(query, retrievals)

    def _generate_fallback(self, query: str, retrievals: List[Dict[str, Any]]) -> str:
        ranked_sentences: List[tuple[float, str, str]] = []
        keywords = {
            token.lower()
            for token in re.findall(r"[A-Za-z]{3,}", query)
            if token.lower() not in {"what", "when", "where", "which", "about", "could", "would"}
        }

        for item in retrievals:
            sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", item["text"]).strip())
            for sentence in sentences:
                match_count = sum(1 for kw in keywords if kw in sentence.lower())
                score = item["score"] + (0.03 * match_count)
                ranked_sentences.append((score, sentence.strip(), item["source"]))

        ranked_sentences.sort(key=lambda x: x[0], reverse=True)
        selected: List[str] = []
        used_sources: List[str] = []

        # Always include the strongest sentence from the top retrievals so the answer
        # surfaces practical next-step language such as re-uploading documents.
        for item in retrievals[:2]:
            sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", item["text"]).strip())
            if sentences:
                sentence = sentences[0].strip()
                if sentence and sentence not in selected:
                    selected.append(sentence)
                    used_sources.append(item["source"])

        for _, sentence, source in ranked_sentences:
            if sentence and sentence not in selected:
                selected.append(sentence)
                used_sources.append(source)
            if len(selected) == 4:
                break

        if not selected:
            selected = [retrievals[0]["text"][:500].strip()]
            used_sources = [retrievals[0]["source"]]

        answer_body = " ".join(selected)
        answer_body = answer_body[:900] + ("..." if len(answer_body) > 900 else "")
        source_names = ", ".join(sorted(set(used_sources)))

        return (
            "Based on the retrieved policy content, here is the best grounded answer:\n\n"
            f"{answer_body}\n\n"
            "If your case involves a complaint, financial loss, suspected fraud, or a regulatory dispute, it should be reviewed by a human agent.\n"
            f"Sources: {source_names}"
        )
