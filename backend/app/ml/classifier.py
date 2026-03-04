"""
Document Auto-Classification Engine
Uses TF-IDF + Logistic Regression pipeline to classify documents
by topic/category based on title and content.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
import numpy as np

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


class DocumentClassifier:
    """TF-IDF + Logistic Regression document classification pipeline."""

    def __init__(self):
        self._pipeline: Optional[Pipeline] = None
        self._label_encoder: Optional[LabelEncoder] = None
        self._is_trained = False
        self._accuracy: float = 0.0
        self._class_names: List[str] = []
        self._num_documents: int = 0

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_documents(self) -> List[Dict[str, Any]]:
        filepath = DATA_DIR / "documents.jsonl"
        records: List[Dict[str, Any]] = []
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        return records

    def _build_text(self, doc: Dict[str, Any]) -> str:
        """Combine title and content into a single text for classification."""
        parts = []
        if doc.get("title"):
            parts.append(doc["title"])
        if doc.get("content"):
            parts.append(doc["content"])
        if doc.get("type"):
            parts.append(doc["type"])
        return " ".join(parts).lower()

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self) -> Dict[str, Any]:
        """Train the classification model on existing document data."""
        documents = self._load_documents()

        # Filter documents with valid topics
        valid_docs = [d for d in documents if d.get("topic")]

        if len(valid_docs) < 10:
            self._is_trained = False
            return {"status": "failed", "reason": "Not enough labeled documents (need >= 10)"}

        texts = [self._build_text(d) for d in valid_docs]
        labels = [d["topic"] for d in valid_docs]

        # Encode labels
        self._label_encoder = LabelEncoder()
        encoded_labels = self._label_encoder.fit_transform(labels)
        self._class_names = list(self._label_encoder.classes_)

        # Build sklearn pipeline
        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=5000,
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True,
            )),
            ("classifier", LogisticRegression(
                max_iter=1000,
                C=1.0,
                class_weight="balanced",
                random_state=42,
            )),
        ])

        # Train
        self._pipeline.fit(texts, encoded_labels)
        self._num_documents = len(valid_docs)

        # Cross-validate for accuracy estimate
        try:
            n_splits = min(5, len(set(encoded_labels)))
            if n_splits >= 2:
                scores = cross_val_score(
                    self._pipeline, texts, encoded_labels,
                    cv=n_splits, scoring="accuracy"
                )
                self._accuracy = float(np.mean(scores))
            else:
                self._accuracy = 0.0
        except Exception:
            self._accuracy = 0.0

        self._is_trained = True

        return {
            "status": "trained",
            "num_documents": self._num_documents,
            "num_classes": len(self._class_names),
            "classes": self._class_names,
            "cross_val_accuracy": round(self._accuracy, 4),
        }

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def classify_document(
        self, title: str, content: str = ""
    ) -> Dict[str, Any]:
        """Classify a document and return predicted topic with confidence."""
        if not self._is_trained:
            self.train()

        if not self._is_trained or self._pipeline is None:
            return {
                "predicted_topic": "Unknown",
                "confidence": 0.0,
                "all_predictions": [],
            }

        text = f"{title} {content}".lower()
        probabilities = self._pipeline.predict_proba([text])[0]
        predicted_idx = np.argmax(probabilities)
        predicted_label = self._label_encoder.inverse_transform([predicted_idx])[0]

        # Build all predictions sorted by confidence
        all_predictions = []
        for idx, prob in enumerate(probabilities):
            all_predictions.append({
                "topic": self._label_encoder.inverse_transform([idx])[0],
                "confidence": round(float(prob), 4),
            })
        all_predictions.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "predicted_topic": predicted_label,
            "confidence": round(float(probabilities[predicted_idx]), 4),
            "all_predictions": all_predictions[:5],
        }

    def get_classification_report(self) -> Dict[str, Any]:
        """Return model performance metrics."""
        return {
            "is_trained": self._is_trained,
            "model": "TF-IDF + Logistic Regression",
            "num_documents": self._num_documents,
            "num_classes": len(self._class_names),
            "classes": self._class_names,
            "cross_val_accuracy": round(self._accuracy, 4),
            "pipeline_steps": ["TfidfVectorizer(ngram_range=(1,2))", "LogisticRegression(balanced)"],
        }


# Singleton instance
classifier = DocumentClassifier()
