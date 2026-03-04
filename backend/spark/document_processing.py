"""
Spark Document Processing Job
PySpark batch job for large-scale document analysis:
word frequency, TF-IDF at Spark scale, and document similarity.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, explode, split, lower, trim, count, desc,
    length, avg, sum as spark_sum, when, lit, udf,
    collect_list, size, round as spark_round
)
from pyspark.sql.types import StringType, FloatType
from pyspark.ml.feature import (
    Tokenizer, StopWordsRemover, CountVectorizer,
    IDF, HashingTF
)
from pyspark.ml import Pipeline
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"


def create_spark_session():
    return (
        SparkSession.builder
        .appName("ExpertLink-DocumentProcessing")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def run_document_processing():
    """Execute document processing pipeline."""
    spark = create_spark_session()

    try:
        # ── Load documents ─────────────────────────────────────────
        docs_df = spark.read.json(str(DATA_DIR / "documents.jsonl"))

        # ── 1. Basic document statistics ───────────────────────────
        doc_stats = {
            "total_documents": docs_df.count(),
            "documents_by_type": [
                row.asDict() for row in
                docs_df.groupBy("type").agg(count("*").alias("count"))
                .orderBy(desc("count")).collect()
            ],
            "documents_by_topic": [
                row.asDict() for row in
                docs_df.groupBy("topic").agg(
                    count("*").alias("count"),
                    avg("rating").alias("avg_rating"),
                    avg("views").alias("avg_views"),
                ).orderBy(desc("count")).collect()
            ],
        }

        # ── 2. Text analysis with Spark ML pipeline ───────────────
        # Prepare text column
        text_df = docs_df.filter(col("title").isNotNull()).select(
            col("id"),
            col("title"),
            col("topic"),
            col("type"),
            lower(col("title")).alias("text")
        )

        # Tokenize
        tokenizer = Tokenizer(inputCol="text", outputCol="words")
        remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")

        pipeline = Pipeline(stages=[tokenizer, remover])
        model = pipeline.fit(text_df)
        processed = model.transform(text_df)

        # ── 3. Word frequency across all documents ────────────────
        all_words = (
            processed
            .select(explode(col("filtered_words")).alias("word"))
            .filter(length(col("word")) > 2)
            .groupBy("word")
            .agg(count("*").alias("frequency"))
            .orderBy(desc("frequency"))
            .limit(50)
        )

        doc_stats["top_words"] = [row.asDict() for row in all_words.collect()]

        # ── 4. Topic-level word analysis ──────────────────────────
        topic_words = (
            processed
            .select("topic", explode(col("filtered_words")).alias("word"))
            .filter(length(col("word")) > 2)
            .groupBy("topic", "word")
            .agg(count("*").alias("frequency"))
            .orderBy("topic", desc("frequency"))
        )

        # Get top 10 words per topic
        from pyspark.sql.window import Window
        from pyspark.sql.functions import row_number

        window = Window.partitionBy("topic").orderBy(desc("frequency"))
        top_topic_words = (
            topic_words
            .withColumn("rank", row_number().over(window))
            .filter(col("rank") <= 10)
            .select("topic", "word", "frequency")
        )

        doc_stats["topic_keywords"] = [row.asDict() for row in top_topic_words.collect()]

        # ── 5. Rating and views distribution ──────────────────────
        rating_dist = (
            docs_df
            .filter(col("rating").isNotNull())
            .select(
                when(col("rating") >= 4.5, "Excellent")
                .when(col("rating") >= 3.5, "Good")
                .when(col("rating") >= 2.5, "Average")
                .otherwise("Below Average")
                .alias("rating_category")
            )
            .groupBy("rating_category")
            .agg(count("*").alias("count"))
            .orderBy(desc("count"))
        )

        doc_stats["rating_distribution"] = [row.asDict() for row in rating_dist.collect()]

        # ── Save results ──────────────────────────────────────────
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / "document_processing_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc_stats, f, indent=2, default=str)

        print(f"Results saved to {output_path}")
        return doc_stats

    finally:
        spark.stop()


if __name__ == "__main__":
    run_document_processing()
