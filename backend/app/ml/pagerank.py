"""
Expert PageRank — Graph-based Expert Influence Scoring
Computes expert influence scores by building a skill-expert-project graph
and applying a PageRank-inspired iterative algorithm.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _load_jsonl(filename: str) -> List[Dict[str, Any]]:
    path = DATA_DIR / filename
    records = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records


class ExpertPageRank:
    """
    Builds a bipartite expert-skill graph plus project edges,
    then uses iterative PageRank to score expert influence.

    Score factors:
    - Skill diversity (breadth)
    - Expertise levels (depth)
    - Project participation (impact)
    - Document contributions (knowledge sharing)
    """

    def __init__(self):
        self._experts: List[Dict[str, Any]] = []
        self._scores: Dict[str, float] = {}
        self._is_trained = False

    def train(self) -> Dict[str, Any]:
        """Build the graph and compute PageRank scores."""
        employees = _load_jsonl("employees.jsonl")
        projects = _load_jsonl("projects.jsonl")
        documents = _load_jsonl("documents.jsonl")

        if not employees:
            return {"status": "failed", "reason": "No employee data"}

        self._experts = employees

        # ── Build adjacency graph ──────────────────────────────────
        # Nodes: experts (emp_*), skills (skill_name), projects (proj_*)
        graph: Dict[str, set] = defaultdict(set)

        # Expert → skill edges (weighted by level)
        expert_skill_levels: Dict[str, Dict[str, int]] = defaultdict(dict)
        for emp in employees:
            eid = emp["id"]
            for s in emp.get("skills", []):
                sname = s["name"] if isinstance(s, dict) else s
                level = s.get("level", 3) if isinstance(s, dict) else 3
                skill_node = f"_sk_{sname}"
                graph[eid].add(skill_node)
                graph[skill_node].add(eid)
                expert_skill_levels[eid][sname] = level

        # Expert → project edges
        for proj in projects:
            pid = proj["id"]
            for member_id in proj.get("team_members", []):
                graph[member_id].add(pid)
                graph[pid].add(member_id)

        # Expert → document edges (author)
        doc_count: Dict[str, int] = defaultdict(int)
        for doc in documents:
            author = doc.get("author", "")
            if author:
                doc_count[author] += 1

        # ── Compute base scores ────────────────────────────────────
        # Initial score = combination of skill depth, breadth, docs, projects
        raw_scores: Dict[str, float] = {}
        for emp in employees:
            eid = emp["id"]
            skills = expert_skill_levels.get(eid, {})
            skill_breadth = len(skills)
            skill_depth = sum(skills.values()) / max(1, skill_breadth)
            project_count = sum(1 for p in projects
                                if eid in p.get("team_members", []))
            docs = doc_count.get(eid, 0)
            experience = emp.get("experience_years", 1)

            raw_scores[eid] = (
                skill_breadth * 1.5 +
                skill_depth * 2.0 +
                project_count * 3.0 +
                docs * 2.5 +
                math.log1p(experience) * 1.0
            )

        # ── Iterative PageRank ─────────────────────────────────────
        damping = 0.85
        iterations = 20
        emp_ids = [e["id"] for e in employees]
        N = len(emp_ids)

        if N == 0:
            return {"status": "failed", "reason": "No experts to rank"}

        # Initialize with normalized base scores
        max_raw = max(raw_scores.values()) if raw_scores else 1.0
        scores = {eid: raw_scores.get(eid, 0) / max_raw for eid in emp_ids}

        for _ in range(iterations):
            new_scores = {}
            for eid in emp_ids:
                # Sum contributions from connected experts (via shared skills/projects)
                neighbors_expert = [
                    n2 for n1 in graph.get(eid, set())
                    for n2 in graph.get(n1, set())
                    if n2 != eid and n2 in scores
                ]
                incoming = sum(
                    scores.get(ne, 0) / max(1, len(graph.get(ne, set())))
                    for ne in neighbors_expert
                )
                new_scores[eid] = (1 - damping) / N + damping * incoming
            # Normalize
            total = sum(new_scores.values()) or 1
            scores = {k: v / total * 100 for k, v in new_scores.items()}

        # Blend: 60% PageRank + 40% base score
        for eid in emp_ids:
            base_norm = raw_scores.get(eid, 0) / max_raw * 100
            scores[eid] = scores.get(eid, 0) * 0.6 + base_norm * 0.4

        self._scores = scores
        self._is_trained = True

        return {
            "status": "trained",
            "experts_scored": len(scores),
            "top_score": round(max(scores.values()), 2) if scores else 0,
        }

    def rank_experts(
        self,
        query: Optional[str] = None,
        department: Optional[str] = None,
        top_k: int = 20,
    ) -> Dict[str, Any]:
        """
        Return ranked experts by influence score.
        Optionally filter/boost by query (skill match) or department.
        """
        if not self._is_trained:
            self.train()

        emp_map = {e["id"]: e for e in self._experts}
        results = []

        for eid, score in self._scores.items():
            emp = emp_map.get(eid)
            if not emp:
                continue

            # Department filter
            if department and emp.get("department", "").lower() != department.lower():
                continue

            # Query boost: if query matches a skill, boost score
            final_score = score
            skill_names = [
                (s["name"] if isinstance(s, dict) else s)
                for s in emp.get("skills", [])
            ]
            matched_skills = []
            if query:
                q_lower = query.lower()
                for sn in skill_names:
                    if q_lower in sn.lower():
                        matched_skills.append(sn)
                if matched_skills:
                    final_score *= 1.5  # 50% boost for query match
                elif q_lower not in emp.get("role", "").lower() and \
                     q_lower not in emp.get("department", "").lower():
                    final_score *= 0.3  # penalize non-matches

            results.append({
                "id": emp["id"],
                "name": emp["name"],
                "role": emp.get("role", ""),
                "department": emp.get("department", ""),
                "location": emp.get("location", ""),
                "experience_years": emp.get("experience_years", 0),
                "influence_score": round(final_score, 2),
                "skills": skill_names[:10],
                "matched_skills": matched_skills,
            })

        results.sort(key=lambda x: x["influence_score"], reverse=True)
        return {
            "query": query,
            "department_filter": department,
            "total_ranked": len(results),
            "results": results[:top_k],
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model": "ExpertPageRank",
            "algorithm": "Iterative PageRank (damping=0.85, 20 iterations) + base feature scoring",
            "is_trained": self._is_trained,
            "experts_scored": len(self._scores),
        }


# Singleton
expert_pagerank = ExpertPageRank()
