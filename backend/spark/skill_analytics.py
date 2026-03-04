"""
Spark Skill Analytics Job
PySpark batch job for skill trend analysis, department-level
skill distribution, and adoption rate computation.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, explode, count, avg, desc, collect_list,
    struct, lit, when, size, round as spark_round
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    ArrayType, FloatType
)
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"


def create_spark_session():
    """Create a local Spark session for batch processing."""
    return (
        SparkSession.builder
        .appName("ExpertLink-SkillAnalytics")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def load_jsonl_to_df(spark, filename):
    """Load a JSONL file into a Spark DataFrame."""
    filepath = str(DATA_DIR / filename)
    return spark.read.json(filepath)


def run_skill_analytics():
    """Execute the full skill analytics pipeline."""
    spark = create_spark_session()

    try:
        # ── Load data ──────────────────────────────────────────────
        employees_df = load_jsonl_to_df(spark, "employees.jsonl")
        skills_df = load_jsonl_to_df(spark, "skills.jsonl")

        # ── 1. Skill frequency analysis ────────────────────────────
        # Explode skills array from employees
        emp_skills = employees_df.select(
            col("id").alias("employee_id"),
            col("name").alias("employee_name"),
            col("department"),
            explode(col("skills")).alias("skill_info")
        )

        # Extract skill name and level
        skill_details = emp_skills.select(
            "employee_id", "employee_name", "department",
            col("skill_info.name").alias("skill_name"),
            col("skill_info.level").alias("skill_level")
        )

        # Skill frequency
        skill_freq = (
            skill_details
            .groupBy("skill_name")
            .agg(
                count("*").alias("expert_count"),
                avg("skill_level").alias("avg_level"),
            )
            .orderBy(desc("expert_count"))
        )

        # ── 2. Department-level skill distribution ─────────────────
        dept_skills = (
            skill_details
            .groupBy("department", "skill_name")
            .agg(
                count("*").alias("count"),
                avg("skill_level").alias("avg_level"),
            )
            .orderBy("department", desc("count"))
        )

        # ── 3. Skill co-occurrence matrix ──────────────────────────
        # Find pairs of skills that frequently co-occur
        skill_pairs = (
            skill_details.alias("a")
            .join(
                skill_details.alias("b"),
                (col("a.employee_id") == col("b.employee_id")) &
                (col("a.skill_name") < col("b.skill_name"))
            )
            .groupBy(
                col("a.skill_name").alias("skill_1"),
                col("b.skill_name").alias("skill_2")
            )
            .agg(count("*").alias("co_occurrence"))
            .orderBy(desc("co_occurrence"))
            .limit(50)
        )

        # ── 4. Expert scoring ──────────────────────────────────────
        expert_scores = (
            skill_details
            .groupBy("employee_id", "employee_name", "department")
            .agg(
                count("*").alias("num_skills"),
                avg("skill_level").alias("avg_skill_level"),
            )
            .withColumn(
                "expert_score",
                spark_round(col("num_skills") * col("avg_skill_level"), 2)
            )
            .orderBy(desc("expert_score"))
        )

        # ── Collect results ────────────────────────────────────────
        results = {
            "skill_frequency": [row.asDict() for row in skill_freq.collect()],
            "department_skills": [row.asDict() for row in dept_skills.limit(100).collect()],
            "skill_co_occurrence": [row.asDict() for row in skill_pairs.collect()],
            "expert_scores": [row.asDict() for row in expert_scores.limit(50).collect()],
            "total_records_processed": employees_df.count(),
        }

        # Save results
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / "skill_analytics_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"Results saved to {output_path}")
        return results

    finally:
        spark.stop()


if __name__ == "__main__":
    run_skill_analytics()
