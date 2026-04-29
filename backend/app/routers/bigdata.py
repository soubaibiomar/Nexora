"""
Big Data Analytics Router
Serves pre-computed Spark analytics and provides endpoints
for skill trends, document stats, and expert rankings.
Falls back to in-memory computation if Spark output is unavailable.
"""

from fastapi import APIRouter, Depends, Query
from pathlib import Path
from typing import Dict, Any, List
import json
from collections import Counter, defaultdict

from .. import fallback_data
from ..auth_guards import require_auth, require_manager

router = APIRouter(prefix="/api/bigdata", tags=["bigdata"])

SPARK_OUTPUT_DIR = Path(__file__).parent.parent.parent / "spark" / "output"


def _load_spark_results(filename: str) -> Dict[str, Any] | None:
    """Load pre-computed Spark results if available."""
    filepath = SPARK_OUTPUT_DIR / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# ── Skill Analytics ────────────────────────────────────────────────

@router.get("/skill-analytics")
async def get_skill_analytics(_user: dict = Depends(require_auth)):
    """
    Spark-computed skill analytics: frequency, co-occurrence, department breakdown.
    Falls back to in-memory computation if Spark output is unavailable.
    """
    # Try Spark output first
    spark_results = _load_spark_results("skill_analytics_results.json")
    if spark_results:
        return {
            "source": "spark_batch",
            "data": spark_results,
        }

    # Fallback: in-memory computation
    employees = fallback_data.get_employees()
    skills_data = fallback_data.get_skills()

    skill_counts = Counter()
    skill_levels = defaultdict(list)
    dept_skills = defaultdict(lambda: Counter())

    for emp in employees:
        dept = emp.get("department", "Unknown")
        for s in emp.get("skills", []):
            name = s.get("name", s) if isinstance(s, dict) else s
            level = s.get("level", 1) if isinstance(s, dict) else 1
            skill_counts[name] += 1
            skill_levels[name].append(level)
            dept_skills[dept][name] += 1

    # Skill frequency
    import numpy as np
    skill_frequency = []
    for name, cnt in skill_counts.most_common(30):
        levels = skill_levels[name]
        skill_frequency.append({
            "skill_name": name,
            "expert_count": cnt,
            "avg_level": round(float(np.mean(levels)), 2) if levels else 0,
        })

    # Co-occurrence
    co_occurrence = []
    emp_skill_sets = []
    for emp in employees:
        skills = [s.get("name", s) if isinstance(s, dict) else s for s in emp.get("skills", [])]
        emp_skill_sets.append(set(skills))

    pair_counts = Counter()
    for skills_set in emp_skill_sets:
        skills_list = sorted(skills_set)
        for i in range(len(skills_list)):
            for j in range(i + 1, len(skills_list)):
                pair_counts[(skills_list[i], skills_list[j])] += 1

    for (s1, s2), cnt in pair_counts.most_common(20):
        co_occurrence.append({"skill_1": s1, "skill_2": s2, "co_occurrence": cnt})

    # Department breakdown
    dept_breakdown = {}
    for dept, skills in dept_skills.items():
        dept_breakdown[dept] = [{"skill": s, "count": c} for s, c in skills.most_common(5)]

    return {
        "source": "in_memory_fallback",
        "data": {
            "skill_frequency": skill_frequency,
            "skill_co_occurrence": co_occurrence,
            "department_skills": dept_breakdown,
            "total_records_processed": len(employees),
        },
    }


# ── Document Stats ─────────────────────────────────────────────────

@router.get("/document-stats")
async def get_document_stats(_user: dict = Depends(require_auth)):
    """
    Spark-computed document statistics: topic distribution, word frequency,
    rating analysis. Falls back to in-memory computation.
    """
    spark_results = _load_spark_results("document_processing_results.json")
    if spark_results:
        return {"source": "spark_batch", "data": spark_results}

    # Fallback
    documents = fallback_data.get_documents()

    topic_counts = Counter()
    type_counts = Counter()
    rating_sum = defaultdict(lambda: {"total": 0, "count": 0, "views": 0})

    for doc in documents:
        topic = doc.get("topic", "Unknown")
        doc_type = doc.get("type", "Unknown")
        rating = doc.get("rating", 0)
        views = doc.get("views", 0)

        topic_counts[topic] += 1
        type_counts[doc_type] += 1
        rating_sum[topic]["total"] += rating
        rating_sum[topic]["count"] += 1
        rating_sum[topic]["views"] += views

    topic_stats = []
    for topic, cnt in topic_counts.most_common():
        r = rating_sum[topic]
        topic_stats.append({
            "topic": topic,
            "count": cnt,
            "avg_rating": round(r["total"] / max(r["count"], 1), 2),
            "total_views": r["views"],
        })

    return {
        "source": "in_memory_fallback",
        "data": {
            "total_documents": len(documents),
            "documents_by_topic": topic_stats,
            "documents_by_type": [{"type": t, "count": c} for t, c in type_counts.most_common()],
        },
    }


# ── Expert Rankings ────────────────────────────────────────────────

@router.get("/expert-rankings")
async def get_expert_rankings(
    limit: int = Query(20, ge=1, le=100),
):
    """
    Spark-computed expert influence rankings based on skill diversity,
    expertise level, and document contributions.
    """
    spark_results = _load_spark_results("expert_scoring_results.json")
    if spark_results:
        rankings = spark_results.get("expert_rankings", [])[:limit]
        return {
            "source": "spark_batch",
            "data": {
                "rankings": rankings,
                "tier_distribution": spark_results.get("tier_distribution", []),
                "department_rankings": spark_results.get("department_rankings", []),
            },
        }

    # Fallback: simple scoring
    employees = fallback_data.get_employees()

    scored = []
    for emp in employees:
        skills = emp.get("skills", [])
        num_skills = len(skills)
        avg_level = 0
        if skills:
            levels = [s.get("level", 1) if isinstance(s, dict) else 1 for s in skills]
            avg_level = sum(levels) / len(levels)

        exp = emp.get("experience_years", 0) or 0
        expertise = emp.get("expertise_level", 1) or 1

        score = round((num_skills * 0.3) + (avg_level * 0.3) + (exp / 10 * 0.2) + (expertise * 0.2), 4)

        tier = (
            "🏆 Expert Leader" if score >= 3.0
            else "⭐ Senior Expert" if score >= 2.0
            else "📈 Rising Expert" if score >= 1.0
            else "🌱 Developing Expert"
        )

        scored.append({
            "employee_id": emp.get("id"),
            "employee_name": emp.get("name"),
            "department": emp.get("department"),
            "role": emp.get("role"),
            "num_skills": num_skills,
            "avg_skill_level": round(avg_level, 2),
            "influence_score": score,
            "tier": tier,
        })

    scored.sort(key=lambda x: x["influence_score"], reverse=True)

    # Tier distribution
    tier_counts = Counter(s["tier"] for s in scored)

    return {
        "source": "in_memory_fallback",
        "data": {
            "rankings": scored[:limit],
            "tier_distribution": [{"tier": t, "count": c} for t, c in tier_counts.most_common()],
            "total_experts_scored": len(scored),
        },
    }


# ── Company Data ───────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def _load_companies_jsonl():
    """Load companies directly from JSONL as fallback."""
    path = DATA_DIR / "companies.jsonl"
    companies = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    companies.append(json.loads(line))
    return companies


@router.get("/companies")
async def get_companies(
    industry: str = None,
    size: str = None,
    limit: int = Query(50, ge=1, le=200),
):
    """
    All companies with optional filtering by industry and size.
    Uses Spark catalog if available, otherwise reads JSONL directly.
    """
    # Try Spark pre-computed catalog
    spark_catalog = _load_spark_results("companies_catalog.json")
    companies = spark_catalog if spark_catalog else _load_companies_jsonl()

    if industry:
        companies = [c for c in companies if c.get("industry", "").lower() == industry.lower()]
    if size:
        companies = [c for c in companies if c.get("size", "").lower() == size.lower()]

    return {
        "companies": companies[:limit],
        "total": len(companies),
        "source": "spark_batch" if spark_catalog else "jsonl_direct",
    }


@router.get("/companies/{company_id}")
async def get_company(company_id: str, _user: dict = Depends(require_auth)):
    """Single company details by ID."""
    spark_catalog = _load_spark_results("companies_catalog.json")
    companies = spark_catalog if spark_catalog else _load_companies_jsonl()

    for c in companies:
        if c.get("id") == company_id:
            return c
    return {"error": "Company not found"}


@router.get("/company-analytics")
async def get_company_analytics(_user: dict = Depends(require_auth)):
    """
    Spark-computed company analytics: industry distribution, tech stack trends,
    geographic analysis, and company rankings.
    Falls back to in-memory computation from JSONL.
    """
    spark_results = _load_spark_results("company_analytics_results.json")
    if spark_results:
        return {"source": "spark_batch", "data": spark_results}

    # Fallback: compute from JSONL
    companies = _load_companies_jsonl()

    industry_counts = Counter()
    industry_ratings = defaultdict(list)
    industry_roles = Counter()
    tech_counts = Counter()
    size_counts = Counter()
    geo_counts = Counter()

    for c in companies:
        ind = c.get("industry", "Unknown")
        industry_counts[ind] += 1
        industry_ratings[ind].append(c.get("rating", 0))
        industry_roles[ind] += c.get("open_roles", 0)
        size_counts[c.get("size", "Unknown")] += 1
        geo_counts[c.get("location", "Unknown")] += 1
        for t in c.get("tech_stack", []):
            tech_counts[t] += 1

    industry_stats = []
    for ind, cnt in industry_counts.most_common():
        ratings = industry_ratings[ind]
        industry_stats.append({
            "industry": ind,
            "company_count": cnt,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "total_open_roles": industry_roles[ind],
        })

    return {
        "source": "in_memory_fallback",
        "data": {
            "total_companies": len(companies),
            "industry_stats": industry_stats,
            "size_distribution": [{"size": s, "count": c} for s, c in size_counts.most_common()],
            "tech_stack_frequency": [{"technology": t, "company_count": c} for t, c in tech_counts.most_common(30)],
            "geographic_distribution": [{"location": l, "company_count": c} for l, c in geo_counts.most_common()],
        },
    }


# ── Pipeline Status ────────────────────────────────────────────────

@router.get("/pipeline-status")
async def get_pipeline_status(_user: dict = Depends(require_auth)):
    """Check the status of Spark batch processing pipeline."""
    jobs = {
        "skill_analytics": SPARK_OUTPUT_DIR / "skill_analytics_results.json",
        "document_processing": SPARK_OUTPUT_DIR / "document_processing_results.json",
        "expert_scoring": SPARK_OUTPUT_DIR / "expert_scoring_results.json",
        "company_analytics": SPARK_OUTPUT_DIR / "company_analytics_results.json",
    }

    status = {}
    for name, path in jobs.items():
        if path.exists():
            import os
            stat = os.stat(path)
            from datetime import datetime
            status[name] = {
                "status": "completed",
                "output_file": str(path),
                "size_bytes": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        else:
            status[name] = {
                "status": "not_run",
                "output_file": str(path),
                "message": "Run the Spark job to generate results",
            }

    return {
        "pipeline": "Apache Spark (PySpark)",
        "jobs": status,
        "spark_output_dir": str(SPARK_OUTPUT_DIR),
    }
