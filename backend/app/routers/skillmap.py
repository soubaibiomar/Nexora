"""
Skill Map & Team Builder API
Provides endpoints for interactive skill visualization and AI-powered team assembly.
Uses skills.jsonl catalog + employees.jsonl to create meaningful skill assignments.
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
from ..auth_guards import require_auth, require_manager

router = APIRouter(prefix="/api/skills", tags=["skills"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _load_jsonl(filename: str) -> list:
    filepath = DATA_DIR / filename
    records = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except FileNotFoundError:
        pass
    return records


# ── Deterministic skill assignment based on role/department ────────
ROLE_SKILL_MAP = {
    "Full Stack Developer": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "Docker", "Git"],
    "Backend Developer": ["Python", "Java", "FastAPI", "PostgreSQL", "Docker", "Redis", "Git"],
    "Frontend Developer": ["JavaScript", "TypeScript", "React", "Vue.js", "Next.js", "Git"],
    "Data Scientist": ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PostgreSQL"],
    "ML Engineer": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Docker", "AWS", "Spark"],
    "Platform Engineer": ["Python", "Kubernetes", "Docker", "Terraform", "AWS", "Prometheus", "Git"],
    "Cloud Architect": ["AWS", "Azure", "Google Cloud", "Kubernetes", "Terraform", "Docker", "Jenkins"],
    "DevOps Engineer": ["Docker", "Kubernetes", "Jenkins", "GitLab CI", "Terraform", "Ansible", "Helm"],
    "Security Engineer": ["OWASP", "Penetration Testing", "Encryption", "IAM", "Network Security", "Python"],
    "Solutions Architect": ["AWS", "Azure", "Kubernetes", "Docker", "Python", "PostgreSQL", "Kafka"],
    "Research Scientist": ["Python", "PyTorch", "TensorFlow", "NumPy", "Pandas", "Spark"],
    "Principal Engineer": ["Python", "Java", "Go", "Kubernetes", "AWS", "PostgreSQL", "Kafka"],
    "Senior Developer": ["Python", "JavaScript", "React", "Docker", "PostgreSQL", "Git", "Redis"],
    "Lead Developer": ["Python", "TypeScript", "React", "Node.js", "Docker", "AWS", "Git"],
    "Staff Engineer": ["Go", "Python", "Kubernetes", "AWS", "Terraform", "Kafka", "Prometheus"],
    "Tech Lead": ["Python", "TypeScript", "React", "Docker", "AWS", "PostgreSQL", "GitHub Actions"],
    "Engineering Manager": ["Python", "AWS", "Docker", "Kubernetes", "Git", "Grafana"],
    "Junior Developer": ["Python", "JavaScript", "Git", "React", "PostgreSQL"],
    "Software Architect": ["Java", "Python", "Go", "AWS", "Kubernetes", "Docker", "Kafka", "Redis"],
    "SRE": ["Kubernetes", "Docker", "Terraform", "Prometheus", "Grafana", "AWS", "Python", "Ansible"],
}

DEPT_BONUS_SKILLS = {
    "AI Research": ["TensorFlow", "PyTorch", "NumPy"],
    "Machine Learning": ["Scikit-learn", "Pandas", "Spark"],
    "DevOps": ["ArgoCD", "Helm", "Jenkins"],
    "Cloud Infrastructure": ["Azure", "Google Cloud", "AWS Lambda"],
    "Security": ["Security Auditing", "IAM", "Encryption"],
    "Web Development": ["React", "Next.js", "TypeScript"],
    "Mobile Development": ["Swift", "Kotlin", "React"],
    "Data Science": ["Pandas", "NumPy", "Elasticsearch"],
    "Quality Assurance": ["Git", "Jenkins", "Docker"],
    "Platform Engineering": ["Kubernetes", "Terraform", "ArgoCD"],
    "Architecture": ["AWS", "GraphQL", "Kafka"],
    "Product Development": ["React", "TypeScript", "Node.js"],
    "Engineering": ["Python", "Docker", "Git"],
}


def _assign_skills_to_employee(emp: dict) -> list:
    """Deterministically assign skills to an employee based on role & department."""
    role = emp.get("role", "")
    dept = emp.get("department", "")
    expertise = emp.get("expertise_level", 3)
    exp_years = emp.get("experience_years", 0)

    # Get base skills from role
    base_skills = list(ROLE_SKILL_MAP.get(role, ["Python", "Git"]))

    # Add department bonus skills
    bonus = DEPT_BONUS_SKILLS.get(dept, [])
    for b in bonus:
        if b not in base_skills:
            base_skills.append(b)

    # Deterministic "randomization" based on employee id
    seed = int(hashlib.md5(emp.get("id", "").encode()).hexdigest()[:8], 16)

    # Assign levels based on expertise and experience
    skills = []
    for i, skill_name in enumerate(base_skills[:8]):  # Max 8 skills per person
        # Level varies by expertise_level and position in list
        base_level = min(expertise, 5)
        variation = ((seed + i * 7) % 3) - 1  # -1, 0, or 1
        level = max(1, min(5, base_level + variation))

        # More experienced = higher levels on primary skills
        if i < 3 and exp_years > 10:
            level = min(5, level + 1)

        skills.append({"name": skill_name, "level": level})

    return skills


def _get_enriched_employees() -> list:
    """Load employees and enrich with assigned skills."""
    employees = _load_jsonl("employees.jsonl")
    for emp in employees:
        emp["skills"] = _assign_skills_to_employee(emp)
    return employees


# ── Skill Map Endpoints ────────────────────────────────────────────

@router.get("/map")
async def get_skill_map(_user: dict = Depends(require_auth)):
    """
    Returns org-wide skill map data: frequency, departments, levels, and trends.
    """
    employees = _get_enriched_employees()
    skills_catalog = _load_jsonl("skills.jsonl")
    catalog_categories = {s["name"]: s.get("category", "Other") for s in skills_catalog}
    catalog_demand = {s["name"]: s.get("demand", 50) for s in skills_catalog}

    # Skill frequency and level distribution
    skill_data: Dict[str, Dict[str, Any]] = {}
    dept_skills: Dict[str, Counter] = defaultdict(Counter)
    dept_list = set()

    for emp in employees:
        dept = emp.get("department", "Unknown")
        dept_list.add(dept)
        for s in emp.get("skills", []):
            name = s.get("name", "")
            level = s.get("level", 0)
            if name not in skill_data:
                skill_data[name] = {
                    "name": name,
                    "count": 0,
                    "levels": [],
                    "departments": Counter(),
                    "experts": [],
                }
            skill_data[name]["count"] += 1
            skill_data[name]["levels"].append(level)
            skill_data[name]["departments"][dept] += 1
            if level >= 4:
                skill_data[name]["experts"].append({
                    "name": emp.get("name"),
                    "department": dept,
                    "level": level,
                })
            dept_skills[dept][name] += 1

    # Build skill nodes
    skills = []
    for name, data in skill_data.items():
        avg_level = sum(data["levels"]) / len(data["levels"]) if data["levels"] else 0
        top_dept = data["departments"].most_common(1)[0][0] if data["departments"] else "Unknown"
        category = catalog_categories.get(name, "Other")
        demand = catalog_demand.get(name, 50)
        skills.append({
            "name": name,
            "count": data["count"],
            "avgLevel": round(avg_level, 2),
            "maxLevel": max(data["levels"]) if data["levels"] else 0,
            "topDepartment": top_dept,
            "departments": dict(data["departments"]),
            "expertCount": len(data["experts"]),
            "topExperts": data["experts"][:5],
            "category": category,
            "demand": demand,
        })

    skills.sort(key=lambda x: -x["count"])

    # Department heatmap
    departments = sorted(dept_list)
    all_skill_names = [s["name"] for s in skills[:20]]
    heatmap = []
    for dept in departments:
        row = {"department": dept}
        for skill_name in all_skill_names:
            row[skill_name] = dept_skills[dept].get(skill_name, 0)
        heatmap.append(row)

    # Skill categories
    categories = Counter(s["category"] for s in skills)

    return {
        "skills": skills,
        "heatmap": heatmap,
        "heatmapSkills": all_skill_names,
        "departments": departments,
        "categories": [{"name": k, "count": v} for k, v in categories.most_common()],
        "totalExperts": len(employees),
        "totalSkills": len(skills),
    }


# ── Team Builder Endpoints ─────────────────────────────────────────

@router.post("/team-builder")
async def build_team(request: dict, _user: dict = Depends(require_auth)):
    """
    AI-powered team builder: given required skills and team size,
    suggests the optimal team composition from available experts.
    """
    required_skills = request.get("skills", [])
    team_size = request.get("teamSize", 5)
    project_name = request.get("projectName", "New Project")
    priority = request.get("priority", "balanced")

    employees = _get_enriched_employees()

    # Score each employee based on skill match
    candidates = []
    for emp in employees:
        emp_skills = {s.get("name", "").lower(): s.get("level", 0) for s in emp.get("skills", [])}
        matched = []
        total_match_score = 0

        for req_skill in required_skills:
            req_lower = req_skill.lower()
            if req_lower in emp_skills:
                matched.append({"skill": req_skill, "level": emp_skills[req_lower], "match": "exact"})
                total_match_score += emp_skills[req_lower]
            else:
                for emp_skill, level in emp_skills.items():
                    if req_lower in emp_skill or emp_skill in req_lower:
                        matched.append({"skill": req_skill, "level": level, "match": "partial"})
                        total_match_score += level * 0.5
                        break

        if not matched:
            continue

        coverage = len(matched) / len(required_skills) if required_skills else 0
        exp_years = emp.get("experience_years", 0) or 0
        expertise = emp.get("expertise_level", 0) or 0

        if priority == "skill_coverage":
            score = coverage * 60 + total_match_score * 3 + expertise * 2
        elif priority == "experience":
            score = exp_years * 5 + total_match_score * 2 + coverage * 20
        else:
            score = coverage * 30 + total_match_score * 3 + exp_years * 2 + expertise * 3

        candidates.append({
            "id": emp.get("id"),
            "name": emp.get("name"),
            "role": emp.get("role"),
            "department": emp.get("department"),
            "experienceYears": exp_years,
            "expertiseLevel": expertise,
            "matchedSkills": matched,
            "coveragePercent": round(coverage * 100),
            "score": round(score, 2),
            "allSkills": [s.get("name") for s in emp.get("skills", [])],
        })

    candidates.sort(key=lambda x: -x["score"])

    # Greedy team selection: maximize skill coverage
    team = []
    covered_skills = set()
    remaining = candidates.copy()

    while len(team) < team_size and remaining:
        best = None
        best_new = -1
        for c in remaining:
            new_skills = sum(1 for m in c["matchedSkills"] if m["skill"].lower() not in covered_skills)
            if new_skills > best_new or (new_skills == best_new and (best is None or c["score"] > best["score"])):
                best = c
                best_new = new_skills
        if best:
            team.append(best)
            for m in best["matchedSkills"]:
                covered_skills.add(m["skill"].lower())
            remaining.remove(best)
        else:
            break

    total_coverage = len(covered_skills) / len(required_skills) * 100 if required_skills else 0
    skill_gaps = [s for s in required_skills if s.lower() not in covered_skills]

    return {
        "projectName": project_name,
        "team": team,
        "alternates": candidates[len(team):len(team) + 5],
        "stats": {
            "teamSize": len(team),
            "skillCoverage": round(total_coverage),
            "avgExperience": round(sum(m.get("experienceYears", 0) for m in team) / len(team), 1) if team else 0,
            "skillGaps": skill_gaps,
            "coveredSkills": list(covered_skills),
        },
    }


@router.get("/available")
async def get_available_skills(_user: dict = Depends(require_auth)):
    """Returns all unique skills in the organization for autocomplete."""
    skills_catalog = _load_jsonl("skills.jsonl")
    return {"skills": sorted(s.get("name", "") for s in skills_catalog)}
