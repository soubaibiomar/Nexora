"""
Team Workspaces API Router
Private collaborative project spaces with real-time chat, voice/video calls,
members, and progress tracking. All workspaces are private — only members can access.
"""

import json
import uuid
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from ..ws_manager import ConnectionManager
from ..auth_guards import require_auth

router = APIRouter(prefix="/api/workspaces", tags=["Workspaces"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

# Dedicated WS managers
ws_workspaces = ConnectionManager()


# ── Pydantic Models ────────────────────────────────────────────────

class CreateWorkspace(BaseModel):
    name: str
    description: str = ""
    member_ids: List[str] = []


class SendWorkspaceMessage(BaseModel):
    content: str
    sender_name: str = "You"


class PostProgress(BaseModel):
    title: str
    description: str = ""
    status: str = "in_progress"  # in_progress, completed, blocked


class StartCall(BaseModel):
    call_type: str = "voice"  # voice or video


class JoinByCode(BaseModel):
    code: str


# ── In-Memory Data ─────────────────────────────────────────────────

_workspaces: List[dict] = []
_invite_codes: dict = {}  # code -> workspace_id
_active_calls: dict = {}  # workspace_id -> call state
_initialized = False


def _generate_invite_code(length: int = 8) -> str:
    """Generate a unique alphanumeric invite code."""
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(chars) for _ in range(length))
        if code not in _invite_codes:
            return code


def _load_employees():
    path = DATA_DIR / "employees.jsonl"
    employees = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    employees.append(json.loads(line))
    return employees


def _is_member(ws: dict, user_id: str = "current_user") -> bool:
    """Check if a user is a member of a workspace."""
    return any(m["id"] == user_id for m in ws["members"])


def _get_workspace_or_403(workspace_id: str, user_id: str = "current_user"):
    """Get workspace if user is a member, else raise 403."""
    _init_workspaces()
    for ws in _workspaces:
        if ws["id"] == workspace_id:
            if not _is_member(ws, user_id):
                raise HTTPException(
                    status_code=403,
                    detail="Access denied. This workspace is private — members only."
                )
            return ws
    raise HTTPException(status_code=404, detail="Workspace not found")


def _init_workspaces():
    global _workspaces, _initialized
    if _initialized:
        return
    employees = _load_employees()
    if not employees:
        _initialized = True
        return

    now = datetime.utcnow()

    # Seed workspace definitions
    seed_data = [
        {
            "name": "Cloud Migration Sprint",
            "description": "Migrating legacy services to Kubernetes & AWS. Q2 delivery target.",
            "color": "#6C63FF",
            "members_slice": (0, 5),
            "messages": [
                ("Hey team! Welcome to the Cloud Migration workspace.", 0),
                ("Thanks for setting this up! Where should we start?", 1),
                ("I've drafted the migration plan — see the progress tab.", 0),
                ("Great. I'll take on the CI/CD pipeline setup.", 2),
                ("I can handle the database migration scripts.", 3),
                ("Perfect. Let's sync daily at 10am. I'll schedule it.", 0),
                ("Should we containerize the auth service first?", 1),
                ("Yes, that's the easiest win. I'll pair with you on it.", 4),
                ("Pushed the first Dockerfile. Ready for review.", 1),
                ("LGTM! Merging now. Great progress team! 🚀", 0),
            ],
            "progress": [
                ("Migration Plan Drafted", "Initial architecture and timeline documented", "completed", 5),
                ("Auth Service Containerized", "Dockerfile + K8s manifests ready", "completed", 3),
                ("CI/CD Pipeline Setup", "GitHub Actions workflow for staging deploys", "in_progress", 1),
                ("Database Migration Scripts", "PostgreSQL → RDS migration scripts", "in_progress", 0),
            ],
        },
        {
            "name": "AI Chatbot v2",
            "description": "Building the next-gen AI chatbot with RAG and multi-turn conversations.",
            "color": "#10B981",
            "members_slice": (2, 6),
            "messages": [
                ("Team, let's kick off the chatbot v2 project!", 0),
                ("Excited! I've been researching RAG architectures.", 1),
                ("Should we use LangChain or build custom?", 2),
                ("Let's go custom — more control over retrieval.", 0),
                ("I'll set up the vector database. Pinecone or Weaviate?", 3),
                ("Weaviate — it's open source and we can self-host.", 1),
                ("Cool. I'll start on the conversation memory module.", 2),
                ("First prototype is running! Check it out on staging.", 0),
            ],
            "progress": [
                ("Research Complete", "Evaluated RAG frameworks and vector DBs", "completed", 6),
                ("Vector DB Setup", "Weaviate cluster deployed on staging", "completed", 4),
                ("Retrieval Pipeline", "Document chunking and embedding pipeline", "in_progress", 2),
                ("Multi-turn Memory", "Conversation context management", "blocked", 0),
            ],
        },
        {
            "name": "Mobile App Redesign",
            "description": "Complete UI/UX overhaul of the mobile app with new design system.",
            "color": "#F59E0B",
            "members_slice": (1, 5),
            "messages": [
                ("Hey everyone! The new design system is ready in Figma.", 0),
                ("Looks amazing! Love the new color palette.", 1),
                ("I'll start implementing the component library.", 2),
                ("Should we use React Native Paper or custom?", 3),
                ("Custom components — we need full control over animations.", 0),
                ("Agreed. I'll handle the navigation overhaul.", 1),
                ("The home screen prototype is live on TestFlight! 📱", 2),
            ],
            "progress": [
                ("Design System Finalized", "Figma components, tokens, and guidelines", "completed", 8),
                ("Component Library", "Core UI components implemented", "in_progress", 3),
                ("Navigation Overhaul", "New tab-based navigation with gestures", "in_progress", 1),
                ("Home Screen Redesign", "New layout with activity feed", "completed", 2),
            ],
        },
    ]

    for ws_def in seed_data:
        ws_id = str(uuid.uuid4())
        start, end = ws_def["members_slice"]
        members_pool = employees[start:end] if len(employees) >= end else employees[:4]

        # Build members list — always include current_user as a member
        members = [{
            "id": "current_user",
            "name": "You",
            "role": "Workspace Admin",
            "department": "",
            "avatar": "https://ui-avatars.com/api/?name=You&background=6C63FF&color=fff&size=128&bold=true",
            "online": True,
            "joined_at": (now - timedelta(days=15)).isoformat(),
        }]
        for i, emp in enumerate(members_pool):
            members.append({
                "id": emp.get("id", f"emp-{i}"),
                "name": emp.get("name", f"Member {i+1}"),
                "role": emp.get("role", "Engineer"),
                "department": emp.get("department", "Engineering"),
                "avatar": f"https://ui-avatars.com/api/?name={emp.get('name', 'User').replace(' ', '+')}&background={ws_def['color'][1:]}&color=fff&size=128&bold=true",
                "online": i < 3,  # first 3 online
                "joined_at": (now - timedelta(days=14 - i)).isoformat(),
            })

        # Build messages
        messages = []
        for j, (text, sender_idx) in enumerate(ws_def["messages"]):
            sender = members[(sender_idx + 1) % len(members)]  # +1 to skip "You"
            messages.append({
                "id": str(uuid.uuid4()),
                "sender_id": sender["id"],
                "sender_name": sender["name"],
                "sender_avatar": sender["avatar"],
                "content": text,
                "timestamp": (now - timedelta(hours=(len(ws_def["messages"]) - j) * 3)).isoformat(),
            })

        # Build progress items
        progress = []
        for title, desc, status, days_ago in ws_def["progress"]:
            progress.append({
                "id": str(uuid.uuid4()),
                "title": title,
                "description": desc,
                "status": status,
                "created_at": (now - timedelta(days=days_ago)).isoformat(),
                "author": members[1]["name"],
            })

        invite_code = _generate_invite_code()
        _invite_codes[invite_code] = ws_id

        _workspaces.append({
            "id": ws_id,
            "name": ws_def["name"],
            "description": ws_def["description"],
            "color": ws_def["color"],
            "is_private": True,
            "invite_code": invite_code,
            "created_at": (now - timedelta(days=14)).isoformat(),
            "members": members,
            "messages": messages,
            "progress": progress,
        })

    _initialized = True


# ── REST Endpoints ─────────────────────────────────────────────────

@router.get("")
async def list_workspaces(_user: dict = Depends(require_auth)):
    """List workspaces visible to the current user (member-only)."""
    _init_workspaces()
    result = []
    for ws in _workspaces:
        # Private: only show workspaces where user is a member
        if not _is_member(ws, "current_user"):
            continue
        result.append({
            "id": ws["id"],
            "name": ws["name"],
            "description": ws["description"],
            "color": ws["color"],
            "is_private": ws.get("is_private", True),
            "created_at": ws["created_at"],
            "member_count": len(ws["members"]),
            "message_count": len(ws["messages"]),
            "progress_count": len(ws["progress"]),
            "members_preview": ws["members"][:5],
            "last_activity": ws["messages"][-1]["timestamp"] if ws["messages"] else ws["created_at"],
            "active_call": _active_calls.get(ws["id"]),
        })
    return {"workspaces": sorted(result, key=lambda x: x["last_activity"], reverse=True)}


@router.post("")
async def create_workspace(data: CreateWorkspace, _user: dict = Depends(require_auth)):
    """Create a new private workspace."""
    _init_workspaces()
    employees = _load_employees()

    members = []
    for emp in employees:
        if emp.get("id") in data.member_ids:
            members.append({
                "id": emp["id"],
                "name": emp.get("name", "Unknown"),
                "role": emp.get("role", "Member"),
                "department": emp.get("department", ""),
                "avatar": f"https://ui-avatars.com/api/?name={emp.get('name', 'User').replace(' ', '+')}&background=6C63FF&color=fff&size=128&bold=true",
                "online": False,
                "joined_at": datetime.utcnow().isoformat(),
            })

    # Always add current user as the creator/admin
    members.insert(0, {
        "id": "current_user",
        "name": "You",
        "role": "Workspace Admin",
        "department": "",
        "avatar": "https://ui-avatars.com/api/?name=You&background=6C63FF&color=fff&size=128&bold=true",
        "online": True,
        "joined_at": datetime.utcnow().isoformat(),
    })

    invite_code = _generate_invite_code()
    ws_id = str(uuid.uuid4())
    _invite_codes[invite_code] = ws_id

    ws = {
        "id": ws_id,
        "name": data.name,
        "description": data.description,
        "color": "#6C63FF",
        "is_private": True,
        "invite_code": invite_code,
        "created_at": datetime.utcnow().isoformat(),
        "members": members,
        "messages": [],
        "progress": [],
    }
    _workspaces.append(ws)
    return ws


@router.get("/{workspace_id}")
async def get_workspace(workspace_id: str, _user: dict = Depends(require_auth)):
    """Get full workspace details (members only)."""
    ws = _get_workspace_or_403(workspace_id)
    return {**ws, "active_call": _active_calls.get(workspace_id)}


# ── Invite / Join-by-Code Endpoints ────────────────────────────────

@router.get("/{workspace_id}/invite")
async def get_invite_code(workspace_id: str, _user: dict = Depends(require_auth)):
    """Get or regenerate the invite code for a workspace (members only)."""
    ws = _get_workspace_or_403(workspace_id)
    code = ws.get("invite_code")
    if not code:
        code = _generate_invite_code()
        ws["invite_code"] = code
        _invite_codes[code] = workspace_id
    return {
        "code": code,
        "workspace_id": workspace_id,
        "workspace_name": ws["name"],
        "link": f"/workspaces/join/{code}",
    }


@router.post("/{workspace_id}/invite/regenerate")
async def regenerate_invite_code(workspace_id: str, _user: dict = Depends(require_auth)):
    """Regenerate the invite code (revokes old one). Members only."""
    ws = _get_workspace_or_403(workspace_id)
    # Revoke old code
    old_code = ws.get("invite_code")
    if old_code and old_code in _invite_codes:
        del _invite_codes[old_code]
    # Generate new
    new_code = _generate_invite_code()
    ws["invite_code"] = new_code
    _invite_codes[new_code] = workspace_id
    return {
        "code": new_code,
        "workspace_id": workspace_id,
        "workspace_name": ws["name"],
        "link": f"/workspaces/join/{new_code}",
    }


@router.delete("/{workspace_id}/invite")
async def revoke_invite(workspace_id: str, _user: dict = Depends(require_auth)):
    """Revoke the invite code for a workspace. Members only."""
    ws = _get_workspace_or_403(workspace_id)
    old_code = ws.get("invite_code")
    if old_code and old_code in _invite_codes:
        del _invite_codes[old_code]
    ws["invite_code"] = None
    return {"message": "Invite code revoked"}


@router.get("/join/{code}/preview")
async def preview_workspace_by_code(code: str, _user: dict = Depends(require_auth)):
    """Preview workspace info from an invite code (no membership required)."""
    _init_workspaces()
    code = code.upper().strip()
    ws_id = _invite_codes.get(code)
    if not ws_id:
        raise HTTPException(status_code=404, detail="Invalid or expired invite code")
    ws = None
    for w in _workspaces:
        if w["id"] == ws_id:
            ws = w
            break
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    already_member = _is_member(ws, "current_user")
    return {
        "workspace_id": ws["id"],
        "name": ws["name"],
        "description": ws["description"],
        "color": ws.get("color", "#6C63FF"),
        "member_count": len(ws["members"]),
        "members_preview": [{"name": m["name"], "avatar": m["avatar"]} for m in ws["members"][:5]],
        "already_member": already_member,
    }


@router.post("/join/{code}")
async def join_workspace_by_code(code: str, _user: dict = Depends(require_auth)):
    """Join a workspace using an invite code."""
    _init_workspaces()
    code = code.upper().strip()
    ws_id = _invite_codes.get(code)
    if not ws_id:
        raise HTTPException(status_code=404, detail="Invalid or expired invite code")
    ws = None
    for w in _workspaces:
        if w["id"] == ws_id:
            ws = w
            break
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check if already a member
    if _is_member(ws, "current_user"):
        return {"message": "Already a member", "workspace_id": ws["id"], "already_member": True}

    # Add user as member
    ws["members"].append({
        "id": "current_user",
        "name": "You",
        "role": "Member",
        "department": "",
        "avatar": "https://ui-avatars.com/api/?name=You&background=6C63FF&color=fff&size=128&bold=true",
        "online": True,
        "joined_at": datetime.utcnow().isoformat(),
    })

    # Add a system message
    ws["messages"].append({
        "id": str(uuid.uuid4()),
        "sender_id": "system",
        "sender_name": "System",
        "sender_avatar": "",
        "content": "📨 A new member joined via invite link!",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return {"message": "Joined successfully", "workspace_id": ws["id"], "already_member": False}


@router.post("/{workspace_id}/messages")
async def send_workspace_message(workspace_id: str, msg: SendWorkspaceMessage, _user: dict = Depends(require_auth)):
    """Send a message in a workspace chat (members only)."""
    ws = _get_workspace_or_403(workspace_id)
    new_msg = {
        "id": str(uuid.uuid4()),
        "sender_id": "current_user",
        "sender_name": msg.sender_name,
        "sender_avatar": "https://ui-avatars.com/api/?name=You&background=6C63FF&color=fff&size=128&bold=true",
        "content": msg.content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    ws["messages"].append(new_msg)

    # Broadcast to connected workspace users
    await ws_workspaces.broadcast({
        "type": "workspace_message",
        "workspace_id": workspace_id,
        "message": new_msg,
    })

    return new_msg


@router.get("/{workspace_id}/progress")
async def get_progress(workspace_id: str, _user: dict = Depends(require_auth)):
    """Get progress updates (members only)."""
    ws = _get_workspace_or_403(workspace_id)
    return {"progress": ws["progress"]}


@router.post("/{workspace_id}/progress")
async def post_progress(workspace_id: str, data: PostProgress, _user: dict = Depends(require_auth)):
    """Post a progress update (members only)."""
    ws = _get_workspace_or_403(workspace_id)
    item = {
        "id": str(uuid.uuid4()),
        "title": data.title,
        "description": data.description,
        "status": data.status,
        "created_at": datetime.utcnow().isoformat(),
        "author": "You",
    }
    ws["progress"].append(item)
    return item


# ── Call Management Endpoints ──────────────────────────────────────

@router.post("/{workspace_id}/call/start")
async def start_call(workspace_id: str, data: StartCall, _user: dict = Depends(require_auth)):
    """Start a voice or video call in a workspace (members only)."""
    ws = _get_workspace_or_403(workspace_id)

    if workspace_id in _active_calls:
        return _active_calls[workspace_id]

    call = {
        "id": str(uuid.uuid4()),
        "workspace_id": workspace_id,
        "call_type": data.call_type,
        "status": "active",
        "started_at": datetime.utcnow().isoformat(),
        "started_by": "You",
        "participants": [{
            "id": "current_user",
            "name": "You",
            "avatar": "https://ui-avatars.com/api/?name=You&background=6C63FF&color=fff&size=128&bold=true",
            "joined_at": datetime.utcnow().isoformat(),
            "is_muted": False,
            "is_video_on": data.call_type == "video",
        }],
    }
    _active_calls[workspace_id] = call

    # Notify workspace members about the call
    await ws_workspaces.broadcast({
        "type": "call_started",
        "workspace_id": workspace_id,
        "call": call,
    })

    return call


@router.post("/{workspace_id}/call/join")
async def join_call(workspace_id: str, _user: dict = Depends(require_auth)):
    """Join an active call in a workspace."""
    ws = _get_workspace_or_403(workspace_id)

    if workspace_id not in _active_calls:
        raise HTTPException(status_code=404, detail="No active call in this workspace")

    call = _active_calls[workspace_id]

    # Check if user already in the call
    if not any(p["id"] == "current_user" for p in call["participants"]):
        call["participants"].append({
            "id": "current_user",
            "name": "You",
            "avatar": "https://ui-avatars.com/api/?name=You&background=6C63FF&color=fff&size=128&bold=true",
            "joined_at": datetime.utcnow().isoformat(),
            "is_muted": False,
            "is_video_on": call["call_type"] == "video",
        })

    return call


@router.post("/{workspace_id}/call/end")
async def end_call(workspace_id: str, _user: dict = Depends(require_auth)):
    """End the active call in a workspace."""
    ws = _get_workspace_or_403(workspace_id)

    if workspace_id not in _active_calls:
        raise HTTPException(status_code=404, detail="No active call to end")

    call = _active_calls.pop(workspace_id)
    call["status"] = "ended"
    call["ended_at"] = datetime.utcnow().isoformat()

    # Notify members
    await ws_workspaces.broadcast({
        "type": "call_ended",
        "workspace_id": workspace_id,
    })

    return call


@router.get("/{workspace_id}/call")
async def get_call_status(workspace_id: str, _user: dict = Depends(require_auth)):
    """Get current call status for a workspace."""
    ws = _get_workspace_or_403(workspace_id)
    call = _active_calls.get(workspace_id)
    if call:
        return call
    return {"status": "no_active_call"}


@router.post("/{workspace_id}/call/simulate-join")
async def simulate_members_join(workspace_id: str, _user: dict = Depends(require_auth)):
    """Simulate other workspace members joining the call (for demo)."""
    ws = _get_workspace_or_403(workspace_id)

    if workspace_id not in _active_calls:
        raise HTTPException(status_code=404, detail="No active call")

    call = _active_calls[workspace_id]
    # Add up to 3 online members who aren't already in the call
    online_members = [m for m in ws["members"]
                      if m["online"] and m["id"] != "current_user"
                      and not any(p["id"] == m["id"] for p in call["participants"])]

    for member in online_members[:3]:
        call["participants"].append({
            "id": member["id"],
            "name": member["name"],
            "avatar": member["avatar"],
            "joined_at": datetime.utcnow().isoformat(),
            "is_muted": False,
            "is_video_on": call["call_type"] == "video",
        })

    return call


# ── WebSocket Endpoint ─────────────────────────────────────────────

@router.websocket("/ws/{workspace_id}/{user_id}")
async def workspace_websocket(websocket: WebSocket, workspace_id: str, user_id: str):
    """
    WebSocket for real-time workspace chat and call signals.
    Connect: ws://localhost:8000/api/workspaces/ws/{workspace_id}/{user_id}
    """
    ws_key = f"{workspace_id}:{user_id}"
    await ws_workspaces.connect(websocket, ws_key)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            if payload.get("type") == "typing":
                for key in list(ws_workspaces.active_connections.keys()):
                    if key.startswith(f"{workspace_id}:") and key != ws_key:
                        await ws_workspaces.send_personal(key, {
                            "type": "typing",
                            "user_id": user_id,
                            "workspace_id": workspace_id,
                        })
    except WebSocketDisconnect:
        ws_workspaces.disconnect(websocket, ws_key)
