"""
Gamification API Router
Badges, endorsements, and leaderboard for knowledge sharing incentives.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/gamification", tags=["Gamification"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


# ── Pydantic Models ────────────────────────────────────────────────

class EndorseRequest(BaseModel):
    endorser_id: str = "current_user"
    target_expert_id: str
    skill_name: str


# ── In-Memory Data ─────────────────────────────────────────────────

_endorsements: List[Dict[str, Any]] = []
_badges: List[Dict[str, Any]] = []
_initialized = False

BADGE_DEFINITIONS = [
    {"id": "top_mentor", "name": "Top Mentor", "icon": "🏆", "description": "Mentored 5+ colleagues", "threshold": 5, "category": "mentorship"},
    {"id": "fast_learner", "name": "Fast Learner", "icon": "⚡", "description": "Completed 3+ learning paths", "threshold": 3, "category": "learning"},
    {"id": "knowledge_contributor", "name": "Knowledge Contributor", "icon": "📚", "description": "Authored 10+ documents", "threshold": 10, "category": "contribution"},
    {"id": "connector", "name": "Super Connector", "icon": "🔗", "description": "Connected with 20+ professionals", "threshold": 20, "category": "networking"},
    {"id": "skill_champion", "name": "Skill Champion", "icon": "🎯", "description": "Endorsed by 10+ peers", "threshold": 10, "category": "endorsement"},
    {"id": "innovator", "name": "Innovator", "icon": "💡", "description": "First to adopt 3+ emerging skills", "threshold": 3, "category": "innovation"},
    {"id": "team_player", "name": "Team Player", "icon": "🤝", "description": "Endorsed skills of 15+ colleagues", "threshold": 15, "category": "collaboration"},
    {"id": "rising_star", "name": "Rising Star", "icon": "🌟", "description": "Top growth in expertise level", "threshold": 1, "category": "growth"},
]


def _load_employees():
    path = DATA_DIR / "employees.jsonl"
    employees = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    employees.append(json.loads(line))
    return employees


def _init_gamification():
    global _endorsements, _badges, _initialized
    if _initialized:
        return

    employees = _load_employees()
    if not employees:
        _initialized = True
        return

    skills_sample = ["Python", "React", "Docker", "Kubernetes", "Machine Learning",
                     "TypeScript", "Neo4j", "FastAPI", "AWS", "Data Science"]

    import random
    # Generate seed endorsements
    for i in range(min(40, len(employees) * 3)):
        endorser = random.choice(employees)
        target = random.choice(employees)
        while target.get("id") == endorser.get("id"):
            target = random.choice(employees)

        _endorsements.append({
            "id": str(uuid.uuid4()),
            "endorser_id": endorser.get("id"),
            "endorser_name": endorser.get("name"),
            "target_expert_id": target.get("id"),
            "target_expert_name": target.get("name"),
            "skill_name": random.choice(skills_sample),
            "created_at": datetime.utcnow().isoformat(),
        })

    # Assign badges based on endorsement counts
    endorsement_counts: Dict[str, int] = {}
    for e in _endorsements:
        tid = e["target_expert_id"]
        endorsement_counts[tid] = endorsement_counts.get(tid, 0) + 1

    for emp in employees:
        eid = emp.get("id", "")
        count = endorsement_counts.get(eid, 0)

        # Assign badges based on thresholds / heuristics
        assigned = []
        if count >= 10:
            assigned.append("skill_champion")
        if count >= 5:
            assigned.append("top_mentor")
        if emp.get("experience_years", 0) <= 2 and count >= 3:
            assigned.append("rising_star")

        # Give endorsers the team_player badge
        given_count = sum(1 for e in _endorsements if e["endorser_id"] == eid)
        if given_count >= 10:
            assigned.append("team_player")

        for badge_id in assigned:
            badge_def = next((b for b in BADGE_DEFINITIONS if b["id"] == badge_id), None)
            if badge_def:
                _badges.append({
                    "id": str(uuid.uuid4()),
                    "expert_id": eid,
                    "expert_name": emp.get("name"),
                    "badge_id": badge_def["id"],
                    "badge_name": badge_def["name"],
                    "badge_icon": badge_def["icon"],
                    "badge_description": badge_def["description"],
                    "badge_category": badge_def["category"],
                    "awarded_at": datetime.utcnow().isoformat(),
                })

    _initialized = True


# ── Endpoints ──────────────────────────────────────────────────────

@router.get("/badges")
async def get_all_badges():
    """Get all available badge definitions."""
    return {"badges": BADGE_DEFINITIONS}


@router.get("/badges/{expert_id}")
async def get_expert_badges(expert_id: str):
    """Get badges earned by a specific expert."""
    _init_gamification()
    expert_badges = [b for b in _badges if b["expert_id"] == expert_id]
    return {"expert_id": expert_id, "badges": expert_badges, "total": len(expert_badges)}


@router.get("/endorsements/{expert_id}")
async def get_expert_endorsements(expert_id: str):
    """Get all endorsements received by a specific expert."""
    _init_gamification()
    expert_endorse = [e for e in _endorsements if e["target_expert_id"] == expert_id]

    # Aggregate by skill
    skill_counts: Dict[str, Dict] = {}
    for e in expert_endorse:
        skill = e["skill_name"]
        if skill not in skill_counts:
            skill_counts[skill] = {"skill": skill, "count": 0, "endorsers": []}
        skill_counts[skill]["count"] += 1
        skill_counts[skill]["endorsers"].append(e["endorser_name"])

    skills_sorted = sorted(skill_counts.values(), key=lambda x: x["count"], reverse=True)
    return {
        "expert_id": expert_id,
        "endorsements": skills_sorted,
        "total_endorsements": len(expert_endorse),
    }


@router.post("/endorse")
async def endorse_skill(request: EndorseRequest):
    """Endorse an expert's skill. Creates an endorsement relationship."""
    _init_gamification()

    # Check for duplicate
    existing = [
        e for e in _endorsements
        if e["endorser_id"] == request.endorser_id
        and e["target_expert_id"] == request.target_expert_id
        and e["skill_name"] == request.skill_name
    ]
    if existing:
        return {"error": "You have already endorsed this skill for this expert."}

    employees = _load_employees()
    target = next((e for e in employees if e.get("id") == request.target_expert_id), None)
    endorser = next((e for e in employees if e.get("id") == request.endorser_id), None)

    new_endorsement = {
        "id": str(uuid.uuid4()),
        "endorser_id": request.endorser_id,
        "endorser_name": endorser.get("name", "You") if endorser else "You",
        "target_expert_id": request.target_expert_id,
        "target_expert_name": target.get("name", "Unknown") if target else "Unknown",
        "skill_name": request.skill_name,
        "created_at": datetime.utcnow().isoformat(),
    }
    _endorsements.append(new_endorsement)
    return {"status": "endorsed", "endorsement": new_endorsement}


@router.get("/leaderboard")
async def get_leaderboard():
    """Get the top endorsed experts (leaderboard)."""
    _init_gamification()

    # Count endorsements per expert
    expert_scores: Dict[str, Dict] = {}
    for e in _endorsements:
        tid = e["target_expert_id"]
        if tid not in expert_scores:
            expert_scores[tid] = {
                "expert_id": tid,
                "expert_name": e["target_expert_name"],
                "endorsement_count": 0,
                "badge_count": 0,
            }
        expert_scores[tid]["endorsement_count"] += 1

    # Add badge counts
    for b in _badges:
        eid = b["expert_id"]
        if eid in expert_scores:
            expert_scores[eid]["badge_count"] += 1

    # Sort by endorsements
    leaderboard = sorted(expert_scores.values(), key=lambda x: x["endorsement_count"], reverse=True)
    return {"leaderboard": leaderboard[:20]}
