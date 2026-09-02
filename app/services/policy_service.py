"""HR Policy Q&A -- TF-IDF retrieval over a curated local dataset + Groq via plain HTTP."""
import json
import os
import requests
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

print("Key starts with:", api_key[:10] if api_key else "NONE LOADED")
_qa_pairs = None
_vectorizer = None
_qa_matrix = None

SIMILARITY_THRESHOLD = 0.5


def _load():
    global _qa_pairs, _vectorizer, _qa_matrix
    if _qa_pairs is None:
        local_path = Path(__file__).resolve().parents[2] / "data" / "policy_qa.jsonl"
        lines = local_path.read_text(encoding="utf-8").strip().split("\n")
        rows = [json.loads(line) for line in lines]

        _qa_pairs = [
            {"question": row["messages"][1]["content"], "answer": row["messages"][2]["content"]}
            for row in rows
        ]

        questions = [pair["question"] for pair in _qa_pairs]
        _vectorizer = TfidfVectorizer(stop_words="english")
        _qa_matrix = _vectorizer.fit_transform(questions)
    return _qa_pairs, _vectorizer, _qa_matrix


def answer_policy_question(user_question: str, top_k: int = 2) -> dict:
    qa_pairs, vectorizer, qa_matrix = _load()

    query_vec = vectorizer.transform([user_question])
    similarities = cosine_similarity(query_vec, qa_matrix).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]
    best_score = float(similarities[top_indices[0]])

    if best_score < SIMILARITY_THRESHOLD:
        return {
            "answer": "I don't have information about that in the current HR policies.",
            "matched": False,
            "confidence": round(best_score, 3),
        }

    context_blocks = [
        f"Q: {qa_pairs[i]['question']}\nA: {qa_pairs[i]['answer']}"
        for i in top_indices
    ]
    context = "\n\n".join(context_blocks)

    prompt = f"""You are an HR policy assistant. Answer the employee's question using
ONLY the policy excerpts below. If the excerpts don't fully answer it, say so.
If different excerpts give conflicting information, point out the conflict
instead of picking one or blending them.

Policy excerpts:
{context}

Employee question: {user_question}"""

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 700,
    }
    groq_response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    groq_response.raise_for_status()
    answer_text = groq_response.json()["choices"][0]["message"]["content"].strip()

    if not answer_text:
        answer_text = "I found a related policy but couldn't generate a clear answer. Please try rephrasing your question."

    return {
        "answer": answer_text,
        "matched": True,
        "confidence": round(best_score, 3),
    }
