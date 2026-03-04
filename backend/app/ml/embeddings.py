"""
Text Embedding Engine
Generates TF-IDF based embeddings for texts and computes
similarity scores between documents and entities.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


class EmbeddingEngine:
    """TF-IDF-based text embedding engine."""

    def __init__(self):
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._is_trained = False

    def train(self) -> Dict[str, Any]:
        """Train the vectorizer on all available text data."""
        corpus: List[str] = []

        # Load all text data
        for fname in ["employees.jsonl", "documents.jsonl", "skills.jsonl", "projects.jsonl"]:
            filepath = DATA_DIR / fname
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)
                            text_parts = []
                            for key in ["name", "title", "content", "role", "department", "topic", "description"]:
                                if record.get(key):
                                    text_parts.append(str(record[key]))
                            if text_parts:
                                corpus.append(" ".join(text_parts).lower())

        if not corpus:
            return {"status": "failed", "reason": "No text data found"}

        self._vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self._vectorizer.fit(corpus)
        self._is_trained = True

        return {
            "status": "trained",
            "corpus_size": len(corpus),
            "vocabulary_size": len(self._vectorizer.vocabulary_),
        }

    def get_embedding(self, text: str) -> Dict[str, Any]:
        """Generate a TF-IDF embedding vector for the given text."""
        if not self._is_trained:
            self.train()

        if not self._is_trained or self._vectorizer is None:
            return {"error": "Model not trained", "embedding": []}

        vec = self._vectorizer.transform([text.lower()])
        dense = vec.toarray()[0]

        # Return only non-zero elements for compactness
        non_zero = [(int(i), round(float(v), 4)) for i, v in enumerate(dense) if v > 0]

        return {
            "text": text[:100],
            "embedding_dim": len(dense),
            "non_zero_elements": len(non_zero),
            "top_features": non_zero[:20],
            "embedding_norm": round(float(np.linalg.norm(dense)), 4),
        }

    def compute_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compute cosine similarity between two texts."""
        if not self._is_trained:
            self.train()

        if not self._is_trained or self._vectorizer is None:
            return {"error": "Model not trained", "similarity": 0.0}

        vecs = self._vectorizer.transform([text1.lower(), text2.lower()])
        sim = cosine_similarity(vecs[0], vecs[1])[0][0]

        return {
            "text1": text1[:100],
            "text2": text2[:100],
            "similarity": round(float(sim), 4),
            "interpretation": (
                "Very similar" if sim > 0.7
                else "Somewhat similar" if sim > 0.4
                else "Slightly related" if sim > 0.1
                else "Not related"
            ),
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "is_trained": self._is_trained,
            "model": "TF-IDF Vectorizer",
            "vocabulary_size": len(self._vectorizer.vocabulary_) if self._vectorizer else 0,
        }


# Singleton
embedding_engine = EmbeddingEngine()
