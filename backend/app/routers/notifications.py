"""
Notifications API Router
Activity and social notifications.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from fastapi import APIRouter
import random

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

DATA_DIR = Path(__file__).parent.parent.parent / "data"

_notifications: List[dict] = []
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


def _init_notifications():
    global _notifications, _initialized
    if _initialized:
        return

    employees = _load_employees()
    if not employees:
        _initialized = True
        return

    now = datetime.utcnow()
    templates = [
        {"type": "connection", "text": "{name} accepted your connection request."},
        {"type": "like", "text": "{name} liked your post about cloud architecture."},
        {"type": "comment", "text": "{name} commented on your post: 'Great insights!'"},
        {"type": "endorsement", "text": "{name} endorsed you for Python."},
        {"type": "view", "text": "{name} viewed your profile."},
        {"type": "job", "text": "New job matching your profile: Senior Developer at ExpertLink."},
        {"type": "mention", "text": "{name} mentioned you in a post."},
        {"type": "birthday", "text": "🎂 It's {name}'s birthday today! Say happy birthday."},
        {"type": "anniversary", "text": "🎉 {name} is celebrating 3 years at the company!"},
        {"type": "connection", "text": "{name} wants to connect with you."},
        {"type": "like", "text": "{name} and 5 others liked your article."},
        {"type": "share", "text": "{name} shared your post."},
        {"type": "recommendation", "text": "{name} wrote you a recommendation."},
        {"type": "skill", "text": "Your skill in React was endorsed by {name} and 3 others."},
        {"type": "post", "text": "{name} posted for the first time in a while."},
    ]

    for i, tmpl in enumerate(templates):
        emp = employees[i % len(employees)]
        _notifications.append({
            "id": str(uuid.uuid4()),
            "type": tmpl["type"],
            "text": tmpl["text"].format(name=emp.get("name", "Someone")),
            "actor_id": emp.get("id"),
            "actor_name": emp.get("name"),
            "actor_role": emp.get("role"),
            "created_at": (now - timedelta(hours=i * 4 + random.randint(0, 3))).isoformat(),
            "read": i > 5,
        })

    _initialized = True


@router.get("")
async def get_notifications(unread_only: bool = False):
    _init_notifications()
    notifs = _notifications
    if unread_only:
        notifs = [n for n in notifs if not n["read"]]
    sorted_notifs = sorted(notifs, key=lambda n: n["created_at"], reverse=True)
    return {
        "notifications": sorted_notifs,
        "total": len(sorted_notifs),
        "unread_count": sum(1 for n in _notifications if not n["read"]),
    }


@router.put("/{notification_id}/read")
async def mark_read(notification_id: str):
    _init_notifications()
    for n in _notifications:
        if n["id"] == notification_id:
            n["read"] = True
            return {"status": "read"}
    return {"error": "Notification not found"}


@router.put("/read-all")
async def mark_all_read():
    _init_notifications()
    for n in _notifications:
        n["read"] = True
    return {"status": "all_read"}
