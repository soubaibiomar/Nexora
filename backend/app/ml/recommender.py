"""
Expert Recommendation Engine
Uses TF-IDF vectorization + cosine similarity to recommend experts
based on skill profiles, roles, and departments.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


class ExpertRecommender:
    """TF-IDF + Cosine Similarity based Expert Recommendation Engine."""

    def __init__(self):
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_matrix = None
        self._experts: List[Dict[str, Any]] = []
        self._skills: List[Dict[str, Any]] = []
        self._is_trained = False

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        filepath = DATA_DIR / filename
        records: List[Dict[str, Any]] = []
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        return records

    def _assign_skills_to_employees(
        self, employees: List[Dict[str, Any]], skills: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Deterministically assign skills to employees based on department/role.

        Since employees.jsonl doesn't embed skills and the relationship only
        exists in Neo4j, we create a deterministic pseudo-assignment so that
        ML models can function without a live graph database.
        """
        if not skills:
            return employees

        # Map skills by category
        skills_by_cat: Dict[str, List[Dict[str, Any]]] = {}
        for s in skills:
            cat = s.get("category", "General")
            skills_by_cat.setdefault(cat, []).append(s)

        # Heuristic mapping from department keywords to likely skill categories
        dept_to_categories = {
            "engineering": ["Programming", "DevOps", "Cloud", "Database"],
            "data": ["Data Science", "Programming", "Database", "Cloud"],
            "design": ["Design", "Frontend", "UX"],
            "marketing": ["Marketing", "Design", "Analytics"],
            "product": ["Product", "Design", "Analytics", "Programming"],
            "hr": ["Management", "Communication", "Analytics"],
            "sales": ["Sales", "Communication", "Analytics"],
            "research": ["Data Science", "Programming", "Research"],
            "security": ["Security", "DevOps", "Cloud", "Programming"],
            "devops": ["DevOps", "Cloud", "Programming", "Security"],
        }

        all_categories = list(skills_by_cat.keys())

        for emp in employees:
            dept = emp.get("department", "").lower()
            role = emp.get("role", "").lower()
            exp_years = emp.get("experience_years", 3)

            # Find relevant categories
            relevant_cats = []
            for keyword, cats in dept_to_categories.items():
                if keyword in dept or keyword in role:
                    relevant_cats.extend(cats)

            if not relevant_cats:
                relevant_cats = all_categories[:3]

            # Deterministic seed based on employee ID
            seed = int(hashlib.md5(str(emp.get("id", "")).encode()).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed)

            # Assign 3-6 skills based on experience
            n_skills = min(3 + exp_years // 3, 6)
            assigned: List[Dict[str, Any]] = []

            for cat in relevant_cats:
                if len(assigned) >= n_skills:
                    break
                cat_skills = skills_by_cat.get(cat, [])
                if cat_skills:
                    idx = rng.randint(0, len(cat_skills))
                    skill = cat_skills[idx]
                    if skill.get("name") not in {a.get("name") for a in assigned}:
                        level = min(1 + exp_years // 2, 5)
                        assigned.append({
                            "name": skill.get("name", ""),
                            "level": level,
                            "category": cat,
                        })

            # Fill remaining from random categories
            all_skills_flat = [s for sl in skills_by_cat.values() for s in sl]
            while len(assigned) < n_skills and all_skills_flat:
                idx = rng.randint(0, len(all_skills_flat))
                skill = all_skills_flat[idx]
                if skill.get("name") not in {a.get("name") for a in assigned}:
                    assigned.append({
                        "name": skill.get("name", ""),
                        "level": rng.randint(1, 4),
                        "category": skill.get("category", "General"),
                    })

            emp["skills"] = assigned

        return employees

    # ------------------------------------------------------------------
    # Profile building
    # ------------------------------------------------------------------

    def _build_profile_text(self, expert: Dict[str, Any]) -> str:
        """Build a text representation of an expert's profile for TF-IDF."""
        parts: List[str] = []

        if expert.get("name"):
            parts.append(expert["name"])
        if expert.get("role"):
            parts.append(expert["role"])
        if expert.get("department"):
            parts.append(expert["department"])
        if expert.get("location"):
            parts.append(expert["location"])

        # Add skills (repeated by level for weighting)
        skills = expert.get("skills", [])
        if isinstance(skills, list):
            for skill in skills:
                if isinstance(skill, dict):
                    name = skill.get("name", "")
                    level = skill.get("level", 1)
                    parts.extend([name] * max(1, int(level)))
                elif isinstance(skill, str):
                    parts.append(skill)

        return " ".join(parts).lower()

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self) -> Dict[str, Any]:
        """Train the recommendation model on employee data."""
        employees = self._load_jsonl("employees.jsonl")
        skills = self._load_jsonl("skills.jsonl")

        self._skills = skills

        # Assign skills to employees (deterministic pseudo-assignment)
        employees = self._assign_skills_to_employees(employees, skills)
        self._experts = employees

        # Build text corpus
        corpus = [self._build_profile_text(e) for e in employees]

        if not corpus or all(not c.strip() for c in corpus):
            self._is_trained = False
            return {"status": "failed", "reason": "No data to train on"}

        self._vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
        self._is_trained = True

        return {
            "status": "trained",
            "num_experts": len(employees),
            "vocabulary_size": len(self._vectorizer.vocabulary_),
            "matrix_shape": list(self._tfidf_matrix.shape),
        }

    # ------------------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------------------

    def recommend_experts(
        self, query: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Recommend experts matching a free-text query."""
        if not self._is_trained:
            self.train()

        if not self._is_trained or self._vectorizer is None:
            return []

        query_vec = self._vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vec, self._tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results: List[Dict[str, Any]] = []
        for idx in top_indices:
            if similarities[idx] > 0:
                expert = self._experts[idx]
                results.append({
                    "id": expert.get("id"),
                    "name": expert.get("name"),
                    "role": expert.get("role"),
                    "department": expert.get("department"),
                    "location": expert.get("location"),
                    "experience_years": expert.get("experience_years", 0),
                    "expertise_level": expert.get("expertise_level", 1),
                    "similarity_score": round(float(similarities[idx]), 4),
                    "skills": [
                        s.get("name", s) if isinstance(s, dict) else s
                        for s in expert.get("skills", [])[:5]
                    ],
                })

        return results

    def find_similar_experts(
        self, expert_id: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find experts similar to a given expert."""
        if not self._is_trained:
            self.train()

        if not self._is_trained:
            return []

        # Find the expert index
        expert_idx = None
        for i, e in enumerate(self._experts):
            if e.get("id") == expert_id:
                expert_idx = i
                break

        if expert_idx is None:
            return []

        expert_vec = self._tfidf_matrix[expert_idx]
        similarities = cosine_similarity(expert_vec, self._tfidf_matrix).flatten()

        # Exclude the expert itself
        similarities[expert_idx] = -1
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results: List[Dict[str, Any]] = []
        for idx in top_indices:
            if similarities[idx] > 0:
                expert = self._experts[idx]
                results.append({
                    "id": expert.get("id"),
                    "name": expert.get("name"),
                    "role": expert.get("role"),
                    "department": expert.get("department"),
                    "similarity_score": round(float(similarities[idx]), 4),
                })

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Return model training status and statistics."""
        if not self._is_trained:
            return {"is_trained": False, "model": "TF-IDF + Cosine Similarity"}

        return {
            "is_trained": True,
            "model": "TF-IDF + Cosine Similarity",
            "num_experts": len(self._experts),
            "vocabulary_size": len(self._vectorizer.vocabulary_) if self._vectorizer else 0,
            "matrix_shape": list(self._tfidf_matrix.shape) if self._tfidf_matrix is not None else [],
            "ngram_range": "(1, 2)",
            "max_features": 5000,
        }


# Singleton instance
recommender = ExpertRecommender()
