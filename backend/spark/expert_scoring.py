"""
Spark Expert Scoring Job
PySpark batch job for computing expert influence scores
using a PageRank-like algorithm based on skill diversity,
expertise level, and document contributions.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, sum as spark_sum, desc,
    when, lit, round as spark_round, size, explode
)
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"


def create_spark_session():
    return (
        SparkSession.builder
        .appName("ExpertLink-ExpertScoring")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def run_expert_scoring():
    """Compute expert influence scores."""
    spark = create_spark_session()

    try:
        # ── Load data ──────────────────────────────────────────────
        employees_df = spark.read.json(str(DATA_DIR / "employees.jsonl"))
        documents_df = spark.read.json(str(DATA_DIR / "documents.jsonl"))

        # ── 1. Skill-based scoring ─────────────────────────────────
        emp_skills = employees_df.select(
            col("id").alias("employee_id"),
            col("name").alias("employee_name"),
            col("department"),
            col("role"),
            col("experience_years"),
            col("expertise_level"),
            explode(col("skills")).alias("skill_info")
        )

        skill_scores = (
            emp_skills
            .groupBy("employee_id", "employee_name", "department", "role",
                      "experience_years", "expertise_level")
            .agg(
                count("*").alias("num_skills"),
                avg(col("skill_info.level")).alias("avg_skill_level"),
            )
        )

        # ── 2. Document contribution scoring ──────────────────────
        doc_counts = (
            documents_df
            .filter(col("author").isNotNull())
            .groupBy(col("author").alias("author_id"))
            .agg(
                count("*").alias("num_documents"),
                avg("rating").alias("avg_doc_rating"),
                spark_sum("views").alias("total_views"),
            )
        )

        # ── 3. Composite scoring ──────────────────────────────────
        # Join skill scores with document contributions
        scored = (
            skill_scores
            .join(doc_counts, skill_scores.employee_id == doc_counts.author_id, "left")
            .fillna(0, subset=["num_documents", "avg_doc_rating", "total_views"])
        )

        # Compute composite PageRank-like score
        # Score = (skill_diversity * 0.25) + (avg_skill_level * 0.25) +
        #         (experience * 0.15) + (doc_contributions * 0.2) + (doc_quality * 0.15)
        final_scores = scored.withColumn(
            "influence_score",
            spark_round(
                (col("num_skills") * lit(0.25)) +
                (col("avg_skill_level") * lit(0.25)) +
                (when(col("experience_years").isNull(), lit(0))
                 .otherwise(col("experience_years") / lit(10)) * lit(0.15)) +
                (col("num_documents") * lit(0.2)) +
                (col("avg_doc_rating") * lit(0.15)),
                4
            )
        ).orderBy(desc("influence_score"))

        # ── 4. Tier classification ────────────────────────────────
        tiered = final_scores.withColumn(
            "tier",
            when(col("influence_score") >= 3.0, "🏆 Expert Leader")
            .when(col("influence_score") >= 2.0, "⭐ Senior Expert")
            .when(col("influence_score") >= 1.0, "📈 Rising Expert")
            .otherwise("🌱 Developing Expert")
        )

        # ── Collect results ───────────────────────────────────────
        rankings = [row.asDict() for row in tiered.limit(50).collect()]

        # Tier distribution
        tier_dist = [
            row.asDict() for row in
            tiered.groupBy("tier")
            .agg(count("*").alias("count"))
            .orderBy(desc("count"))
            .collect()
        ]

        # Department rankings
        dept_rankings = [
            row.asDict() for row in
            tiered.groupBy("department")
            .agg(
                count("*").alias("num_experts"),
                avg("influence_score").alias("avg_score"),
            )
            .orderBy(desc("avg_score"))
            .collect()
        ]

        results = {
            "expert_rankings": rankings,
            "tier_distribution": tier_dist,
            "department_rankings": dept_rankings,
            "total_experts_scored": employees_df.count(),
        }

        # Save
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / "expert_scoring_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Results saved to {output_path}")
        return results

    finally:
        spark.stop()


if __name__ == "__main__":
    run_expert_scoring()
