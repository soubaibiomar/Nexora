"""
Skill Gap Predictor
Uses collaborative filtering on the user-skill matrix to predict
which skills an expert should learn next, and computes skill trends.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


class SkillPredictor:
    """Collaborative filtering-based skill gap analysis engine."""

    def __init__(self):
        self._employees: List[Dict[str, Any]] = []
        self._skills: List[Dict[str, Any]] = []
        self._skill_names: List[str] = []
        self._user_skill_matrix: Optional[np.ndarray] = None
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

            relevant_cats = []
            for keyword, cats in dept_to_categories.items():
                if keyword in dept or keyword in role:
                    relevant_cats.extend(cats)

            if not relevant_cats:
                relevant_cats = all_categories[:3]

            seed = int(hashlib.md5(str(emp.get("id", "")).encode()).hexdigest()[:8], 16)
            rng = np.random.RandomState(seed)

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
    # Training
    # ------------------------------------------------------------------

    def train(self) -> Dict[str, Any]:
        """Build the user-skill co-occurrence matrix."""
        self._employees = self._load_jsonl("employees.jsonl")
        self._skills = self._load_jsonl("skills.jsonl")

        if not self._employees or not self._skills:
            self._is_trained = False
            return {"status": "failed", "reason": "No data available"}

        # Assign skills to employees
        self._employees = self._assign_skills_to_employees(self._employees, self._skills)

        # Collect all skill names
        all_skill_names: set = set()
        for skill in self._skills:
            all_skill_names.add(skill.get("name", ""))

        for emp in self._employees:
            for s in emp.get("skills", []):
                if isinstance(s, dict):
                    all_skill_names.add(s.get("name", ""))
                elif isinstance(s, str):
                    all_skill_names.add(s)

        all_skill_names.discard("")
        self._skill_names = sorted(all_skill_names)
        skill_idx = {name: i for i, name in enumerate(self._skill_names)}

        # Build user-skill matrix
        n_users = len(self._employees)
        n_skills = len(self._skill_names)
        matrix = np.zeros((n_users, n_skills), dtype=np.float32)

        for u, emp in enumerate(self._employees):
            for s in emp.get("skills", []):
                name = s.get("name", s) if isinstance(s, dict) else s
                level = s.get("level", 1) if isinstance(s, dict) else 1
                if name in skill_idx:
                    matrix[u, skill_idx[name]] = float(level)

        self._user_skill_matrix = matrix
        self._is_trained = True

        return {
            "status": "trained",
            "num_employees": n_users,
            "num_skills": n_skills,
            "matrix_shape": [n_users, n_skills],
            "matrix_density": round(float(np.count_nonzero(matrix)) / max(matrix.size, 1), 4),
        }

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_skill_gaps(
        self, expert_id: str, top_k: int = 8
    ) -> Dict[str, Any]:
        """Predict skills an expert should learn based on similar experts."""
        if not self._is_trained:
            self.train()

        if not self._is_trained:
            return {"expert_id": expert_id, "recommended_skills": []}

        # Find the expert
        expert_idx = None
        expert_data = None
        for i, emp in enumerate(self._employees):
            if emp.get("id") == expert_id:
                expert_idx = i
                expert_data = emp
                break

        if expert_idx is None:
            return {"expert_id": expert_id, "recommended_skills": [], "error": "Expert not found"}

        # Compute similarity with all other experts
        expert_vec = self._user_skill_matrix[expert_idx].reshape(1, -1)
        similarities = cosine_similarity(expert_vec, self._user_skill_matrix).flatten()
        similarities[expert_idx] = -1  # exclude self

        # Get top similar experts
        top_similar = np.argsort(similarities)[::-1][:10]

        # Skills the expert does NOT have
        current_skills = set()
        for j, name in enumerate(self._skill_names):
            if self._user_skill_matrix[expert_idx, j] > 0:
                current_skills.add(name)

        # Score candidate skills by weighted frequency among similar experts
        skill_scores: Dict[str, float] = defaultdict(float)
        for sim_idx in top_similar:
            if similarities[sim_idx] <= 0:
                continue
            for j, name in enumerate(self._skill_names):
                if name not in current_skills and self._user_skill_matrix[sim_idx, j] > 0:
                    skill_scores[name] += similarities[sim_idx] * self._user_skill_matrix[sim_idx, j]

        # Sort and return top-k
        ranked = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        recommended = []
        for name, score in ranked:
            # Find category from skill data
            category = "General"
            for s in self._skills:
                if s.get("name") == name:
                    category = s.get("category", "General")
                    break
            recommended.append({
                "skill": name,
                "category": category,
                "relevance_score": round(float(score), 4),
                "reason": f"Commonly held by experts similar to {expert_data.get('name', 'this expert')}",
            })

        return {
            "expert_id": expert_id,
            "expert_name": expert_data.get("name", "Unknown"),
            "current_skills": sorted(current_skills),
            "recommended_skills": recommended,
            "num_similar_experts_analyzed": int(np.sum(similarities > 0)),
        }

    def get_skill_trends(self) -> Dict[str, Any]:
        """Analyze skill trends across the organization."""
        if not self._is_trained:
            self.train()

        if not self._is_trained:
            return {"trends": []}

        # Frequency analysis
        skill_counts = Counter()
        skill_levels = defaultdict(list)
        dept_skills = defaultdict(lambda: Counter())

        for emp in self._employees:
            dept = emp.get("department", "Unknown")
            for s in emp.get("skills", []):
                name = s.get("name", s) if isinstance(s, dict) else s
                level = s.get("level", 1) if isinstance(s, dict) else 1
                skill_counts[name] += 1
                skill_levels[name].append(level)
                dept_skills[dept][name] += 1

        # Top trending skills (by frequency)
        total_experts = len(self._employees)
        trends = []
        for name, count in skill_counts.most_common(20):
            avg_level = np.mean(skill_levels[name]) if skill_levels[name] else 0
            trends.append({
                "skill": name,
                "expert_count": count,
                "adoption_rate": round(count / max(total_experts, 1), 4),
                "average_level": round(float(avg_level), 2),
            })

        # Department breakdown
        dept_breakdown = {}
        for dept, skills in dept_skills.items():
            dept_breakdown[dept] = [
                {"skill": s, "count": c}
                for s, c in skills.most_common(5)
            ]

        return {
            "total_experts": total_experts,
            "total_unique_skills": len(skill_counts),
            "top_skills": trends,
            "department_breakdown": dept_breakdown,
        }

    # ------------------------------------------------------------------
    # Emerging & Future Skills
    # ------------------------------------------------------------------

    def get_emerging_skills(self) -> Dict[str, Any]:
        """Identify skills with the highest adoption growth rate.

        Uses hire-date cohorts: compares skill adoption in employees hired
        in the last 2 years vs those hired 2-5 years ago to detect trends.
        """
        if not self._is_trained:
            self.train()
        if not self._is_trained:
            return {"emerging_skills": []}

        from datetime import datetime, timedelta
        import random as _rng

        now = datetime.now()
        cutoff_recent = (now - timedelta(days=730)).strftime("%Y-%m-%d")   # 2 yrs
        cutoff_older  = (now - timedelta(days=1825)).strftime("%Y-%m-%d")  # 5 yrs

        recent_skills: Counter = Counter()
        older_skills: Counter = Counter()
        recent_count = 0
        older_count = 0

        for emp in self._employees:
            hire = emp.get("hire_date", "2020-01-01")
            for s in emp.get("skills", []):
                name = s.get("name", s) if isinstance(s, dict) else s
                if hire >= cutoff_recent:
                    recent_skills[name] += 1
                elif hire >= cutoff_older:
                    older_skills[name] += 1

            if hire >= cutoff_recent:
                recent_count += 1
            elif hire >= cutoff_older:
                older_count += 1

        emerging = []
        all_names = set(recent_skills.keys()) | set(older_skills.keys())
        for name in all_names:
            r = recent_skills.get(name, 0) / max(recent_count, 1)
            o = older_skills.get(name, 0) / max(older_count, 1)
            growth = (r - o) / max(o, 0.01)
            emerging.append({
                "skill": name,
                "recent_adoption_rate": round(r, 4),
                "older_adoption_rate": round(o, 4),
                "growth_rate": round(growth, 4),
                "status": "rising" if growth > 0.2 else "stable" if growth > -0.1 else "declining",
            })

        emerging.sort(key=lambda x: x["growth_rate"], reverse=True)
        return {
            "recent_cohort_size": recent_count,
            "older_cohort_size": older_count,
            "emerging_skills": emerging[:15],
            "declining_skills": [s for s in emerging if s["status"] == "declining"][:10],
        }

    def predict_future_skills(self, months: int = 12) -> Dict[str, Any]:
        """Predict which skills will be most in-demand in N months.

        Combines project-skill demand with emerging-skill growth rates
        to forecast future skill needs.
        """
        if not self._is_trained:
            self.train()
        if not self._is_trained:
            return {"predictions": []}

        import random as _rng

        projects = self._load_jsonl("projects.jsonl")
        emerging = self.get_emerging_skills()
        growth_map = {s["skill"]: s["growth_rate"]
                      for s in emerging.get("emerging_skills", [])}

        # Count current project demand
        project_demand: Counter = Counter()
        for proj in projects:
            for sk in proj.get("required_skills", proj.get("technologies", [])):
                name = sk if isinstance(sk, str) else sk.get("name", "")
                if name:
                    project_demand[name] += 1

        # Current supply
        supply: Counter = Counter()
        for emp in self._employees:
            for s in emp.get("skills", []):
                name = s.get("name", s) if isinstance(s, dict) else s
                supply[name] += 1

        # Forecast
        predictions = []
        for name in set(list(project_demand.keys()) + list(supply.keys())):
            demand_now = project_demand.get(name, 0)
            supply_now = supply.get(name, 0)
            growth = growth_map.get(name, 0)

            # Project demand grows based on growth rate
            factor = 1 + max(growth, 0) * (months / 12)
            demand_future = int(demand_now * factor) + max(0, int(growth * 3))
            gap = max(0, demand_future - supply_now)

            predictions.append({
                "skill": name,
                "current_supply": supply_now,
                "current_project_demand": demand_now,
                "predicted_demand": demand_future,
                "predicted_gap": gap,
                "growth_rate": round(growth, 4),
                "urgency": "critical" if gap > 10 else "high" if gap > 5 else "medium" if gap > 0 else "low",
            })

        predictions.sort(key=lambda x: x["predicted_gap"], reverse=True)
        return {
            "forecast_horizon_months": months,
            "total_skills_analyzed": len(predictions),
            "critical_gaps": len([p for p in predictions if p["urgency"] == "critical"]),
            "predictions": predictions[:20],
        }

    def get_cross_department_suggestions(self) -> Dict[str, Any]:
        """Find departments with complementary skill profiles for collaboration."""
        if not self._is_trained:
            self.train()
        if not self._is_trained:
            return {"suggestions": []}

        dept_skills: Dict[str, Counter] = defaultdict(Counter)
        for emp in self._employees:
            dept = emp.get("department", "Unknown")
            for s in emp.get("skills", []):
                name = s.get("name", s) if isinstance(s, dict) else s
                dept_skills[dept][name] += 1

        departments = list(dept_skills.keys())
        suggestions = []

        for i, d1 in enumerate(departments):
            for d2 in departments[i + 1:]:
                s1 = set(dept_skills[d1].keys())
                s2 = set(dept_skills[d2].keys())
                shared = s1 & s2
                unique_d1 = s1 - s2
                unique_d2 = s2 - s1
                complementarity = len(unique_d1) + len(unique_d2)
                overlap = len(shared)

                if complementarity > 3 and overlap > 0:
                    suggestions.append({
                        "department_1": d1,
                        "department_2": d2,
                        "shared_skills": sorted(shared)[:5],
                        "unique_to_dept_1": sorted(unique_d1)[:5],
                        "unique_to_dept_2": sorted(unique_d2)[:5],
                        "complementarity_score": complementarity,
                        "overlap_score": overlap,
                        "collaboration_potential": round(
                            complementarity / max(len(s1 | s2), 1) * 100, 1
                        ),
                        "rationale": f"{d1} can contribute {', '.join(sorted(unique_d1)[:3])} while {d2} brings {', '.join(sorted(unique_d2)[:3])}",
                    })

        suggestions.sort(key=lambda x: x["collaboration_potential"], reverse=True)
        return {
            "total_departments": len(departments),
            "suggestions": suggestions[:15],
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "is_trained": self._is_trained,
            "model": "Collaborative Filtering (User-Skill Matrix + Cosine Similarity)",
            "num_employees": len(self._employees),
            "num_skills": len(self._skill_names),
            "capabilities": [
                "skill_gap_prediction",
                "skill_trends",
                "emerging_skills",
                "future_skill_prediction",
                "cross_department_collaboration",
            ],
        }


# Singleton
skill_predictor = SkillPredictor()
