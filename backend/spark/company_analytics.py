"""
Spark Company Analytics Pipeline
PySpark batch job for company data analysis: industry distribution,
tech stack trends, company-skill matching for job recommendations.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, explode, count, avg, desc, collect_list, sum as spark_sum,
    struct, lit, when, size, round as spark_round, min as spark_min,
    max as spark_max, array_distinct, flatten
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    ArrayType, FloatType, DoubleType
)
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"


def create_spark_session():
    """Create a local Spark session for company analytics."""
    return (
        SparkSession.builder
        .appName("ExpertLink-CompanyAnalytics")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def run_company_analytics():
    """Execute the company analytics pipeline."""
    spark = create_spark_session()

    try:
        # ── Load data ──────────────────────────────────────────────
        companies_df = spark.read.json(str(DATA_DIR / "companies.jsonl"))
        employees_df = spark.read.json(str(DATA_DIR / "employees.jsonl"))

        print(f"Loaded {companies_df.count()} companies, {employees_df.count()} employees")

        # ── 1. Industry distribution ──────────────────────────────
        industry_stats = (
            companies_df
            .groupBy("industry")
            .agg(
                count("*").alias("company_count"),
                spark_round(avg("rating"), 2).alias("avg_rating"),
                spark_sum("open_roles").alias("total_open_roles"),
                spark_sum("employees").alias("total_employees"),
                spark_round(avg("employees"), 0).alias("avg_company_size"),
            )
            .orderBy(desc("company_count"))
        )

        # ── 2. Company size distribution ──────────────────────────
        size_dist = (
            companies_df
            .groupBy("size")
            .agg(
                count("*").alias("count"),
                spark_round(avg("rating"), 2).alias("avg_rating"),
                spark_round(avg("employees"), 0).alias("avg_employees"),
            )
            .orderBy(desc("count"))
        )

        # ── 3. Tech stack analysis ────────────────────────────────
        # Explode tech_stack arrays and count frequency
        tech_freq = (
            companies_df
            .select(explode(col("tech_stack")).alias("technology"))
            .groupBy("technology")
            .agg(count("*").alias("company_count"))
            .orderBy(desc("company_count"))
        )

        # ── 4. Tech stack by industry ─────────────────────────────
        tech_by_industry = (
            companies_df
            .select("industry", explode(col("tech_stack")).alias("technology"))
            .groupBy("industry", "technology")
            .agg(count("*").alias("count"))
            .orderBy("industry", desc("count"))
        )

        # Top 5 technologies per industry
        from pyspark.sql.window import Window
        from pyspark.sql.functions import row_number

        window = Window.partitionBy("industry").orderBy(desc("count"))
        top_tech_by_industry = (
            tech_by_industry
            .withColumn("rank", row_number().over(window))
            .filter(col("rank") <= 5)
            .select("industry", "technology", "count")
        )

        # ── 5. Geographic distribution ────────────────────────────
        geo_dist = (
            companies_df
            .groupBy("location")
            .agg(
                count("*").alias("company_count"),
                spark_sum("employees").alias("total_employees"),
                spark_sum("open_roles").alias("total_open_roles"),
            )
            .orderBy(desc("company_count"))
        )

        # ── 6. Company-skill matching ─────────────────────────────
        # Match company tech stacks with employee skills for recommendation
        # Explode employee skills
        emp_skills = (
            employees_df
            .select(
                col("id").alias("employee_id"),
                col("name").alias("employee_name"),
                explode(col("skills")).alias("skill_info")
            )
            .select(
                "employee_id", "employee_name",
                col("skill_info.name").alias("skill_name"),
                col("skill_info.level").alias("skill_level")
            )
        )

        # Explode company tech stacks
        company_techs = (
            companies_df
            .select(
                col("id").alias("company_id"),
                col("name").alias("company_name"),
                col("industry"),
                col("rating"),
                col("open_roles"),
                explode(col("tech_stack")).alias("technology")
            )
        )

        # Cross-match: for each employee, find companies with matching tech
        skill_matches = (
            emp_skills.alias("e")
            .join(
                company_techs.alias("c"),
                col("e.skill_name") == col("c.technology"),
                "inner"
            )
            .groupBy("employee_id", "employee_name", "company_id", "company_name", "industry")
            .agg(
                count("*").alias("matching_skills"),
                collect_list("skill_name").alias("matched_skills"),
            )
            .orderBy(desc("matching_skills"))
        )

        # ── 7. Company rankings ───────────────────────────────────
        company_rankings = (
            companies_df
            .select(
                "id", "name", "industry", "rating",
                "employees", "open_roles", "location",
                size(col("tech_stack")).alias("tech_diversity"),
                size(col("specialties")).alias("specialty_count"),
            )
            .withColumn(
                "attractiveness_score",
                spark_round(
                    col("rating") * 20 +
                    col("tech_diversity") * 2 +
                    when(col("open_roles") > 30, 15)
                    .when(col("open_roles") > 15, 10)
                    .otherwise(5) +
                    col("specialty_count") * 3,
                    2
                )
            )
            .orderBy(desc("attractiveness_score"))
        )

        # ── Collect results ────────────────────────────────────────
        results = {
            "total_companies": companies_df.count(),
            "total_open_roles": int(
                companies_df.agg(spark_sum("open_roles")).collect()[0][0] or 0
            ),
            "industry_stats": [
                row.asDict() for row in industry_stats.collect()
            ],
            "size_distribution": [
                row.asDict() for row in size_dist.collect()
            ],
            "tech_stack_frequency": [
                row.asDict() for row in tech_freq.limit(30).collect()
            ],
            "tech_by_industry": [
                row.asDict() for row in top_tech_by_industry.collect()
            ],
            "geographic_distribution": [
                row.asDict() for row in geo_dist.collect()
            ],
            "company_rankings": [
                row.asDict() for row in company_rankings.limit(50).collect()
            ],
            "skill_match_samples": [
                row.asDict() for row in skill_matches.limit(100).collect()
            ],
        }

        # ── Also save full company list for API consumption ───────
        all_companies = [
            row.asDict() for row in companies_df.collect()
        ]

        # ── Save results ──────────────────────────────────────────
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        analytics_path = OUTPUT_DIR / "company_analytics_results.json"
        with open(analytics_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        companies_path = OUTPUT_DIR / "companies_catalog.json"
        with open(companies_path, "w", encoding="utf-8") as f:
            json.dump(all_companies, f, indent=2, default=str)

        print(f"Analytics saved to {analytics_path}")
        print(f"Company catalog saved to {companies_path}")
        print(f"Processed {results['total_companies']} companies with {results['total_open_roles']} open roles")

        return results

    finally:
        spark.stop()


if __name__ == "__main__":
    run_company_analytics()
