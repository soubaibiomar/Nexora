"""
PySpark Batch Analytics Job
Reads JSONL data files and computes organizational analytics:
- Skill distribution and co-occurrence matrices
- Department analytics and cross-department overlap
- Expert influence scores
- Document topic analysis

Output is written to spark/output/ as JSON for consumption by the bigdata router.

Usage:
    python spark/spark_batch.py
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# Resolve paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"


def load_jsonl(filename: str) -> list:
    path = DATA_DIR / filename
    records = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records


def save_json(data: dict, filename: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {filename}")


def run_with_spark():
    """Run analytics using PySpark if available."""
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, explode, count, avg, collect_list

        spark = SparkSession.builder \
            .appName("Nexora-BatchAnalytics") \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()

        print("  🔥 PySpark session initialized")

        # Load data as Spark DataFrames
        employees = load_jsonl("employees.jsonl")
        if employees:
            emp_df = spark.createDataFrame(employees)
            # Department distribution
            dept_dist = emp_df.groupBy("department").count() \
                .orderBy(col("count").desc()).collect()
            dept_data = [{"department": r["department"], "count": r["count"]} for r in dept_dist]

            # Location distribution
            loc_dist = emp_df.groupBy("location").count() \
                .orderBy(col("count").desc()).collect()
            loc_data = [{"location": r["location"], "count": r["count"]} for r in loc_dist]

            # Experience stats
            exp_stats = emp_df.agg(
                avg("experience_years").alias("avg_experience"),
                count("*").alias("total_employees"),
            ).collect()[0]

            save_json({
                "computed_at": datetime.utcnow().isoformat(),
                "engine": "PySpark",
                "department_distribution": dept_data,
                "location_distribution": loc_data,
                "avg_experience_years": round(exp_stats["avg_experience"], 2),
                "total_employees": exp_stats["total_employees"],
            }, "employee_analytics.json")

        spark.stop()
        return True

    except Exception as e:
        print(f"  ⚠ PySpark failed: {e}")
        print("  📊 Falling back to pure Python analytics...")
        return False


def run_python_analytics():
    """Run all analytics using pure Python (no Spark dependency)."""
    employees = load_jsonl("employees.jsonl")
    documents = load_jsonl("documents.jsonl")
    projects = load_jsonl("projects.jsonl")
    skills = load_jsonl("skills.jsonl")

    print(f"  📦 Loaded: {len(employees)} employees, {len(documents)} docs, "
          f"{len(projects)} projects, {len(skills)} skills")

    # ── 1. Skill Analytics ─────────────────────────────────────────
    skill_freq: Counter = Counter()
    skill_by_dept: dict = defaultdict(Counter)
    skill_cooccurrence: dict = defaultdict(Counter)

    for emp in employees:
        dept = emp.get("department", "Unknown")
        emp_skills = []
        for s in emp.get("skills", []):
            name = s["name"] if isinstance(s, dict) else s
            emp_skills.append(name)
            skill_freq[name] += 1
            skill_by_dept[dept][name] += 1

        # Co-occurrence: pairs of skills that appear together
        for i, s1 in enumerate(emp_skills):
            for s2 in emp_skills[i + 1:]:
                skill_cooccurrence[s1][s2] += 1
                skill_cooccurrence[s2][s1] += 1

    # Top co-occurrences
    cooccurrence_pairs = []
    seen = set()
    for s1, peers in skill_cooccurrence.items():
        for s2, count in peers.most_common(3):
            pair = tuple(sorted([s1, s2]))
            if pair not in seen:
                seen.add(pair)
                cooccurrence_pairs.append({
                    "skill_1": pair[0], "skill_2": pair[1], "count": count
                })
    cooccurrence_pairs.sort(key=lambda x: x["count"], reverse=True)

    save_json({
        "computed_at": datetime.utcnow().isoformat(),
        "engine": "Python",
        "total_unique_skills": len(skill_freq),
        "skill_frequency": [
            {"skill": s, "count": c} for s, c in skill_freq.most_common(50)
        ],
        "skill_by_department": {
            dept: [{"skill": s, "count": c} for s, c in skills.most_common(10)]
            for dept, skills in skill_by_dept.items()
        },
        "top_cooccurrences": cooccurrence_pairs[:30],
    }, "skill_analytics.json")

    # ── 2. Document Analytics ──────────────────────────────────────
    topic_dist = Counter(d.get("topic", "Unknown") for d in documents)
    type_dist = Counter(d.get("type", "Unknown") for d in documents)
    ratings = [d.get("rating", 0) for d in documents]
    views = [d.get("views", 0) for d in documents]

    save_json({
        "computed_at": datetime.utcnow().isoformat(),
        "engine": "Python",
        "total_documents": len(documents),
        "topic_distribution": [
            {"topic": t, "count": c} for t, c in topic_dist.most_common()
        ],
        "type_distribution": [
            {"type": t, "count": c} for t, c in type_dist.most_common()
        ],
        "avg_rating": round(sum(ratings) / max(len(ratings), 1), 2),
        "avg_views": round(sum(views) / max(len(views), 1), 1),
        "top_rated": sorted(
            [{"title": d["title"], "rating": d.get("rating", 0), "topic": d.get("topic")}
             for d in documents],
            key=lambda x: x["rating"], reverse=True
        )[:10],
    }, "document_analytics.json")

    # ── 3. Expert Influence Scores ─────────────────────────────────
    expert_scores = []
    doc_author_count = Counter(d.get("author", "") for d in documents)
    proj_member_count: Counter = Counter()
    for p in projects:
        for m in p.get("team_members", []):
            proj_member_count[m] += 1

    for emp in employees:
        eid = emp["id"]
        skills_list = emp.get("skills", [])
        skill_breadth = len(skills_list)
        skill_depth = sum(
            (s.get("level", 1) if isinstance(s, dict) else 1) for s in skills_list
        ) / max(skill_breadth, 1)
        docs = doc_author_count.get(eid, 0)
        projs = proj_member_count.get(eid, 0)
        exp = emp.get("experience_years", 1)

        score = (
            skill_breadth * 1.5 +
            skill_depth * 2.0 +
            projs * 3.0 +
            docs * 2.5 +
            (exp ** 0.5) * 1.0
        )
        expert_scores.append({
            "id": eid,
            "name": emp["name"],
            "department": emp.get("department", ""),
            "role": emp.get("role", ""),
            "influence_score": round(score, 2),
            "skill_count": skill_breadth,
            "avg_skill_level": round(skill_depth, 2),
            "document_count": docs,
            "project_count": projs,
        })

    expert_scores.sort(key=lambda x: x["influence_score"], reverse=True)

    save_json({
        "computed_at": datetime.utcnow().isoformat(),
        "engine": "Python",
        "total_experts": len(expert_scores),
        "rankings": expert_scores[:50],
    }, "expert_rankings.json")

    # ── 4. Department Analytics ────────────────────────────────────
    dept_stats = defaultdict(lambda: {
        "count": 0, "avg_experience": 0, "total_exp": 0,
        "skills": Counter(), "locations": Counter()
    })

    for emp in employees:
        dept = emp.get("department", "Unknown")
        dept_stats[dept]["count"] += 1
        dept_stats[dept]["total_exp"] += emp.get("experience_years", 0)
        dept_stats[dept]["locations"][emp.get("location", "Unknown")] += 1
        for s in emp.get("skills", []):
            name = s["name"] if isinstance(s, dict) else s
            dept_stats[dept]["skills"][name] += 1

    dept_report = []
    for dept, stats in dept_stats.items():
        dept_report.append({
            "department": dept,
            "headcount": stats["count"],
            "avg_experience": round(stats["total_exp"] / max(stats["count"], 1), 1),
            "top_skills": [
                {"skill": s, "count": c}
                for s, c in stats["skills"].most_common(8)
            ],
            "locations": [
                {"location": l, "count": c}
                for l, c in stats["locations"].most_common(5)
            ],
        })
    dept_report.sort(key=lambda x: x["headcount"], reverse=True)

    save_json({
        "computed_at": datetime.utcnow().isoformat(),
        "engine": "Python",
        "total_departments": len(dept_report),
        "departments": dept_report,
    }, "department_analytics.json")

    # ── 5. Project Analytics ───────────────────────────────────────
    status_dist = Counter(p.get("status", "Unknown") for p in projects)
    priority_dist = Counter(p.get("priority", "Unknown") for p in projects)
    domain_dist = Counter(p.get("domain", "Unknown") for p in projects)

    tech_freq: Counter = Counter()
    for p in projects:
        for sk in p.get("required_skills", []):
            tech_freq[sk if isinstance(sk, str) else sk.get("name", "")] += 1

    save_json({
        "computed_at": datetime.utcnow().isoformat(),
        "engine": "Python",
        "total_projects": len(projects),
        "status_distribution": [
            {"status": s, "count": c} for s, c in status_dist.most_common()
        ],
        "priority_distribution": [
            {"priority": p, "count": c} for p, c in priority_dist.most_common()
        ],
        "domain_distribution": [
            {"domain": d, "count": c} for d, c in domain_dist.most_common()
        ],
        "top_technologies": [
            {"tech": t, "project_count": c} for t, c in tech_freq.most_common(15)
        ],
    }, "project_analytics.json")


def main():
    print("\n⚡ Nexora Batch Analytics Engine\n")

    # Try PySpark first, fall back to Python
    spark_ok = run_with_spark()

    # Always run Python analytics (more detailed)
    run_python_analytics()

    print(f"\n✅ All analytics saved to {OUTPUT_DIR.resolve()}/")


if __name__ == "__main__":
    main()
