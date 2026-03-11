"""
Kafka-style Data Ingestion Pipeline Simulator
Simulates real-time event streaming for employee, project, and document updates.
No actual Kafka dependency — demonstrates the architecture pattern.
"""

import time
import uuid
import random
from datetime import datetime
from collections import deque
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


# ── Event models ───────────────────────────────────────────────────

class IngestEvent(BaseModel):
    event_type: str  # "employee_update", "project_created", "document_added"
    payload: Dict[str, Any]


class BatchIngestRequest(BaseModel):
    events: List[IngestEvent]


# ── In-memory event queue (simulates Kafka topic partitions) ──────

_event_queue: deque = deque(maxlen=10000)
_processed_events: List[Dict[str, Any]] = []
_pipeline_metrics = {
    "total_ingested": 0,
    "total_processed": 0,
    "total_failed": 0,
    "events_per_second": 0.0,
    "avg_latency_ms": 0.0,
    "started_at": None,
    "last_event_at": None,
    "partitions": {
        "employee_updates": {"count": 0, "lag": 0},
        "project_events": {"count": 0, "lag": 0},
        "document_events": {"count": 0, "lag": 0},
    },
}


def _process_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate event processing with random latency."""
    start = time.time()

    # Simulate processing time (5–50ms)
    latency = random.uniform(5, 50)
    time.sleep(latency / 1000)

    result = {
        "event_id": event["id"],
        "event_type": event["event_type"],
        "status": "processed",
        "processed_at": datetime.utcnow().isoformat(),
        "latency_ms": round(latency, 2),
    }

    # Simulate occasional failures (2% rate)
    if random.random() < 0.02:
        result["status"] = "failed"
        result["error"] = "Simulated processing error — would retry in production"
        _pipeline_metrics["total_failed"] += 1
    else:
        _pipeline_metrics["total_processed"] += 1

    return result


# ── Endpoints ──────────────────────────────────────────────────────

@router.post("/ingest")
async def ingest_event(event: IngestEvent):
    """
    Ingest a single event into the pipeline.
    Simulates Kafka producer → topic → consumer pattern.
    """
    if _pipeline_metrics["started_at"] is None:
        _pipeline_metrics["started_at"] = datetime.utcnow().isoformat()

    evt = {
        "id": str(uuid.uuid4()),
        "event_type": event.event_type,
        "payload": event.payload,
        "ingested_at": datetime.utcnow().isoformat(),
        "partition": _get_partition(event.event_type),
    }
    _event_queue.append(evt)
    _pipeline_metrics["total_ingested"] += 1
    _pipeline_metrics["last_event_at"] = evt["ingested_at"]

    # Update partition metrics
    partition = evt["partition"]
    if partition in _pipeline_metrics["partitions"]:
        _pipeline_metrics["partitions"][partition]["count"] += 1
        _pipeline_metrics["partitions"][partition]["lag"] += 1

    # Process immediately (simulates consumer)
    result = _process_event(evt)
    _processed_events.append(result)

    # Update partition lag
    if result["status"] == "processed" and partition in _pipeline_metrics["partitions"]:
        _pipeline_metrics["partitions"][partition]["lag"] = max(
            0, _pipeline_metrics["partitions"][partition]["lag"] - 1
        )

    return {
        "status": "accepted",
        "event_id": evt["id"],
        "partition": evt["partition"],
        "processing_result": result,
    }


@router.post("/ingest-batch")
async def ingest_batch(request: BatchIngestRequest):
    """
    Ingest a batch of events (simulates Kafka batch producer).
    Processes all events sequentially with throughput metrics.
    """
    if _pipeline_metrics["started_at"] is None:
        _pipeline_metrics["started_at"] = datetime.utcnow().isoformat()

    start = time.time()
    results = []

    for event in request.events:
        evt = {
            "id": str(uuid.uuid4()),
            "event_type": event.event_type,
            "payload": event.payload,
            "ingested_at": datetime.utcnow().isoformat(),
            "partition": _get_partition(event.event_type),
        }
        _event_queue.append(evt)
        _pipeline_metrics["total_ingested"] += 1

        partition = evt["partition"]
        if partition in _pipeline_metrics["partitions"]:
            _pipeline_metrics["partitions"][partition]["count"] += 1

        result = _process_event(evt)
        _processed_events.append(result)
        results.append(result)

    elapsed = time.time() - start
    throughput = len(request.events) / max(elapsed, 0.001)
    _pipeline_metrics["events_per_second"] = round(throughput, 2)
    _pipeline_metrics["last_event_at"] = datetime.utcnow().isoformat()
    _pipeline_metrics["avg_latency_ms"] = round(
        sum(r["latency_ms"] for r in results) / max(len(results), 1), 2
    )

    return {
        "status": "batch_complete",
        "events_processed": len(results),
        "elapsed_seconds": round(elapsed, 3),
        "throughput_eps": round(throughput, 2),
        "avg_latency_ms": _pipeline_metrics["avg_latency_ms"],
        "results": results[-5:],  # Return last 5 for brevity
    }


@router.get("/status")
async def get_pipeline_status():
    """
    Get current pipeline status, throughput metrics, and partition health.
    """
    uptime = None
    if _pipeline_metrics["started_at"]:
        started = datetime.fromisoformat(_pipeline_metrics["started_at"])
        uptime = (datetime.utcnow() - started).total_seconds()

    return {
        "status": "running" if _pipeline_metrics["started_at"] else "idle",
        "uptime_seconds": round(uptime, 1) if uptime else None,
        "total_ingested": _pipeline_metrics["total_ingested"],
        "total_processed": _pipeline_metrics["total_processed"],
        "total_failed": _pipeline_metrics["total_failed"],
        "success_rate": round(
            _pipeline_metrics["total_processed"] /
            max(_pipeline_metrics["total_ingested"], 1) * 100, 2
        ),
        "events_per_second": _pipeline_metrics["events_per_second"],
        "avg_latency_ms": _pipeline_metrics["avg_latency_ms"],
        "queue_depth": len(_event_queue),
        "partitions": _pipeline_metrics["partitions"],
        "last_event_at": _pipeline_metrics["last_event_at"],
    }


@router.get("/metrics")
async def get_pipeline_metrics():
    """
    Detailed pipeline metrics including event type breakdown and latency histogram.
    """
    # Event type breakdown
    type_counts: Dict[str, int] = {}
    for evt in _event_queue:
        t = evt.get("event_type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    # Latency histogram from processed events
    latencies = [r["latency_ms"] for r in _processed_events[-100:]]
    histogram = {"0-10ms": 0, "10-20ms": 0, "20-30ms": 0, "30-40ms": 0, "40-50ms": 0, "50ms+": 0}
    for l in latencies:
        if l < 10: histogram["0-10ms"] += 1
        elif l < 20: histogram["10-20ms"] += 1
        elif l < 30: histogram["20-30ms"] += 1
        elif l < 40: histogram["30-40ms"] += 1
        elif l < 50: histogram["40-50ms"] += 1
        else: histogram["50ms+"] += 1

    return {
        "event_type_breakdown": type_counts,
        "latency_histogram": histogram,
        "recent_events": _processed_events[-10:],
        "total_events_in_queue": len(_event_queue),
        "pipeline_health": "healthy" if _pipeline_metrics["total_failed"] / max(_pipeline_metrics["total_ingested"], 1) < 0.05 else "degraded",
    }


@router.post("/simulate")
async def simulate_stream(
    count: int = Query(50, ge=1, le=500),
):
    """
    Simulate a burst of streaming events for demo purposes.
    Generates realistic employee updates, project events, and document additions.
    """
    events = []
    event_templates = [
        {"event_type": "employee_update", "payload": {"action": "skill_added", "skill": "Python", "level": 4}},
        {"event_type": "employee_update", "payload": {"action": "role_change", "new_role": "Senior Developer"}},
        {"event_type": "project_created", "payload": {"name": "New Analytics Dashboard", "tech": ["React", "Python"]}},
        {"event_type": "document_added", "payload": {"title": "ML Best Practices", "topic": "Machine Learning"}},
        {"event_type": "employee_update", "payload": {"action": "department_transfer", "to": "AI Research"}},
        {"event_type": "project_created", "payload": {"name": "Cloud Migration Phase 3", "tech": ["AWS", "Terraform"]}},
        {"event_type": "document_added", "payload": {"title": "Security Audit Report", "topic": "Security"}},
    ]

    for _ in range(count):
        template = random.choice(event_templates)
        events.append(IngestEvent(**template))

    # Process all events
    request = BatchIngestRequest(events=events)
    result = await ingest_batch(request)
    return {
        "simulation": "complete",
        "events_generated": count,
        **result,
    }


# ── Helpers ────────────────────────────────────────────────────────

def _get_partition(event_type: str) -> str:
    if "employee" in event_type:
        return "employee_updates"
    elif "project" in event_type:
        return "project_events"
    elif "document" in event_type:
        return "document_events"
    return "employee_updates"
