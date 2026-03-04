"""
Network / Connections API Router
Professional networking features: connection suggestions, requests, and management.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
import random
from urllib.parse import quote

def _make_avatar(name: str) -> str:
    return f"https://ui-avatars.com/api/?name={quote(name)}&background=0A66C2&color=fff&size=128&bold=true"

router = APIRouter(prefix="/api/network", tags=["Network"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


class ConnectionRequest(BaseModel):
    target_id: str
    message: str = ""


_connections: dict = {}
_pending: List[dict] = []
_initialized = False


def _load_employees():
    path = DATA_DIR / "employees.jsonl"
    employees = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    employees.append(json.loads(line))
    return employees


def _init_network():
    global _connections, _pending, _initialized
    if _initialized:
        return
    employees = _load_employees()
    if not employees:
        _initialized = True
        return

    # Create some pending connection requests
    for emp in employees[5:10]:
        _pending.append({
            "id": str(uuid.uuid4()),
            "from_id": emp.get("id"),
            "from_name": emp.get("name"),
            "from_role": emp.get("role"),
            "from_department": emp.get("department"),
            "from_location": emp.get("location", ""),
            "from_avatar": _make_avatar(emp.get("name", "")),
            "message": f"Hi! I'd love to connect and learn more about your work in {emp.get('department', 'our field')}.",
            "sent_at": (datetime.utcnow() - timedelta(days=random.randint(1, 7))).isoformat(),
            "status": "pending",
            "mutual_connections": random.randint(2, 15),
        })

    # Create existing connections
    for emp in employees[:20]:
        _connections[emp.get("id")] = {
            "id": emp.get("id"),
            "name": emp.get("name"),
            "role": emp.get("role"),
            "department": emp.get("department"),
            "location": emp.get("location", ""),
            "avatar_url": _make_avatar(emp.get("name", "")),
            "connected_at": (datetime.utcnow() - timedelta(days=random.randint(30, 365))).isoformat(),
        }

    _initialized = True


@router.get("/suggestions")
async def get_suggestions(limit: int = 12):
    _init_network()
    employees = _load_employees()
    connected_ids = set(_connections.keys())

    suggestions = []
    for emp in employees:
        if emp.get("id") not in connected_ids and len(suggestions) < limit:
            suggestions.append({
                "id": emp.get("id"),
                "name": emp.get("name"),
                "role": emp.get("role"),
                "department": emp.get("department"),
                "location": emp.get("location", ""),
                "avatar_url": _make_avatar(emp.get("name", "")),
                "experience_years": emp.get("experience_years", 0),
                "mutual_connections": random.randint(1, 20),
                "reason": f"Works in {emp.get('department', 'your field')}",
            })
    return {"suggestions": suggestions}


@router.get("/connections")
async def get_connections(skip: int = 0, limit: int = 20):
    _init_network()
    conns = list(_connections.values())
    return {
        "connections": conns[skip:skip + limit],
        "total": len(conns),
    }


@router.get("/pending")
async def get_pending():
    _init_network()
    return {"requests": _pending}


@router.post("/connect")
async def send_connection(req: ConnectionRequest):
    _init_network()
    employees = _load_employees()
    target = None
    for emp in employees:
        if emp.get("id") == req.target_id:
            target = emp
            break

    if not target:
        return {"error": "User not found"}

    # Auto-accept for demo
    _connections[target["id"]] = {
        "id": target.get("id"),
        "name": target.get("name"),
        "role": target.get("role"),
        "department": target.get("department"),
        "location": target.get("location", ""),
        "avatar_url": _make_avatar(target.get("name", "")),
        "connected_at": datetime.utcnow().isoformat(),
    }
    return {"status": "connected", "connection": _connections[target["id"]]}


@router.post("/accept/{request_id}")
async def accept_request(request_id: str):
    _init_network()
    for i, req in enumerate(_pending):
        if req["id"] == request_id:
            req["status"] = "accepted"
            _connections[req["from_id"]] = {
                "id": req["from_id"],
                "name": req["from_name"],
                "role": req["from_role"],
                "department": req["from_department"],
                "location": req.get("from_location", ""),
                "avatar_url": _make_avatar(req.get("from_name", "")),
                "connected_at": datetime.utcnow().isoformat(),
            }
            _pending.pop(i)
            return {"status": "accepted"}
    return {"error": "Request not found"}


@router.get("/stats")
async def get_network_stats():
    _init_network()
    return {
        "total_connections": len(_connections),
        "pending_requests": len(_pending),
        "profile_views": random.randint(50, 300),
        "search_appearances": random.randint(100, 500),
    }
