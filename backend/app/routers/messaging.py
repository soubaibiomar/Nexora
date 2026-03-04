"""
Messaging API Router
Direct messaging between professionals.
Includes WebSocket support for real-time message delivery.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import random

from ..ws_manager import ws_messaging

router = APIRouter(prefix="/api/messaging", tags=["Messaging"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


class SendMessage(BaseModel):
    conversation_id: str = ""
    recipient_id: str = ""
    content: str


_conversations: List[dict] = []
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


def _init_messaging():
    global _conversations, _initialized
    if _initialized:
        return
    employees = _load_employees()
    if not employees:
        _initialized = True
        return

    message_templates = [
        [
            "Hi! I saw your recent post about cloud architecture. Really interesting insights!",
            "Thanks! Happy to discuss further. Are you working on something similar?",
            "Yes, we're migrating our services to Kubernetes. Would love your advice.",
            "Sure! I've done a few K8s migrations. The trickiest part is usually networking.",
            "That's exactly what we're struggling with. Service mesh or native K8s networking?",
            "I'd recommend starting with native, then add Istio if you need traffic management.",
            "That makes a lot of sense. Could we set up a quick call this week?",
            "Absolutely! How about Thursday at 2pm? I'll send a calendar invite.",
        ],
        [
            "Hey, are you attending the tech summit next week?",
            "Yes! Looking forward to the ML workshop. You?",
            "Same! Let's grab coffee there.",
            "Sounds great! I also want to check out the DevOps track.",
            "Oh yes, the CI/CD automation talk looks promising.",
            "I heard the speaker is from Google. Should be insightful.",
            "Let's meet at the registration desk at 9am?",
            "Perfect, see you there! 🎉",
        ],
        [
            "Congratulations on the promotion! Well deserved.",
            "Thank you so much! It's been a great journey.",
            "Let's catch up soon and celebrate!",
            "Definitely! How about dinner this Saturday?",
            "That works for me. Any restaurant preference?",
            "There's a great new Italian place downtown. I'll send you the link.",
            "Sounds perfect! Looking forward to it.",
        ],
        [
            "Quick question about the API design patterns doc you shared.",
            "Sure, what would you like to know?",
            "Is the gateway pattern still recommended for microservices?",
            "Yes, especially with BFF (Backend for Frontend) approach.",
            "Interesting. Does it handle versioning well?",
            "We use URL versioning with the gateway. Works great for backwards compatibility.",
            "Thanks! This is really helpful. I'll update our architecture doc.",
            "Happy to review it when you're done!",
        ],
        [
            "Happy work anniversary! 🎉",
            "Thanks! Time really flies.",
            "We should plan a team dinner soon!",
            "Great idea! I know a perfect place.",
            "Is everyone available next Friday evening?",
            "I'll check with the team and create a poll.",
            "Perfect. Let me know and I'll make the reservation!",
        ],
    ]

    now = datetime.utcnow()
    for i, templates in enumerate(message_templates):
        if i >= len(employees) - 1:
            break
        emp = employees[i + 1]
        messages = []
        for j, text in enumerate(templates):
            messages.append({
                "id": str(uuid.uuid4()),
                "sender": "You" if j % 2 == 0 else emp.get("name"),
                "sender_id": "current_user" if j % 2 == 0 else emp.get("id"),
                "content": text,
                "timestamp": (now - timedelta(hours=(len(templates) - j) * 2 + i * 24)).isoformat(),
                "read": True,
            })

        _conversations.append({
            "id": str(uuid.uuid4()),
            "participant_id": emp.get("id"),
            "participant_name": emp.get("name"),
            "participant_role": emp.get("role"),
            "participant_department": emp.get("department"),
            "participant_avatar": f"https://ui-avatars.com/api/?name={emp.get('name', '').replace(' ', '+')}&background=0A66C2&color=fff&size=128&bold=true",
            "last_message": messages[-1]["content"],
            "last_timestamp": messages[-1]["timestamp"],
            "unread": 1 if i < 2 else 0,
            "messages": messages,
            "online": random.choice([True, False]),
        })

    _initialized = True


@router.get("/conversations")
async def get_conversations():
    _init_messaging()
    convos = []
    for c in _conversations:
        convos.append({
            "id": c["id"],
            "participant_id": c["participant_id"],
            "participant_name": c["participant_name"],
            "participant_role": c["participant_role"],
            "participant_department": c["participant_department"],
            "participant_avatar": c.get("participant_avatar", ""),
            "last_message": c["last_message"],
            "last_timestamp": c["last_timestamp"],
            "unread": c["unread"],
            "online": c["online"],
        })
    return {"conversations": sorted(convos, key=lambda x: x["last_timestamp"], reverse=True)}


@router.get("/conversations/{conversation_id}")
async def get_messages(conversation_id: str):
    _init_messaging()
    for c in _conversations:
        if c["id"] == conversation_id:
            c["unread"] = 0
            return {
                "conversation_id": c["id"],
                "participant_name": c["participant_name"],
                "participant_role": c["participant_role"],
                "participant_avatar": c.get("participant_avatar", ""),
                "online": c["online"],
                "messages": c["messages"],
            }
    return {"error": "Conversation not found"}


@router.post("/send")
async def send_message(msg: SendMessage):
    _init_messaging()
    # Find or create conversation
    target_conv = None
    for c in _conversations:
        if c["id"] == msg.conversation_id or c["participant_id"] == msg.recipient_id:
            target_conv = c
            break

    if not target_conv:
        employees = _load_employees()
        target = None
        for emp in employees:
            if emp.get("id") == msg.recipient_id:
                target = emp
                break
        if not target:
            return {"error": "Recipient not found"}

        target_conv = {
            "id": str(uuid.uuid4()),
            "participant_id": target.get("id"),
            "participant_name": target.get("name"),
            "participant_role": target.get("role"),
            "participant_department": target.get("department"),
            "last_message": "",
            "last_timestamp": "",
            "unread": 0,
            "messages": [],
            "online": random.choice([True, False]),
        }
        _conversations.append(target_conv)

    new_msg = {
        "id": str(uuid.uuid4()),
        "sender": "You",
        "sender_id": "current_user",
        "content": msg.content,
        "timestamp": datetime.utcnow().isoformat(),
        "read": True,
    }
    target_conv["messages"].append(new_msg)
    target_conv["last_message"] = msg.content
    target_conv["last_timestamp"] = new_msg["timestamp"]

    # ── Real-time push via WebSocket ──
    recipient_id = target_conv.get("participant_id", "")
    if recipient_id:
        await ws_messaging.send_personal(recipient_id, {
            "type": "new_message",
            "conversation_id": target_conv["id"],
            "message": new_msg,
        })

    return new_msg


# ── WebSocket Endpoint ─────────────────────────────────────────────

@router.websocket("/ws/{user_id}")
async def messaging_websocket(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time messaging.
    Clients connect with ws://localhost:8000/api/messaging/ws/{user_id}
    """
    await ws_messaging.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WS messages (e.g., typing indicators)
            payload = json.loads(data)
            if payload.get("type") == "typing":
                # Broadcast typing indicator to the other participant
                recipient = payload.get("recipient_id")
                if recipient:
                    await ws_messaging.send_personal(recipient, {
                        "type": "typing",
                        "user_id": user_id,
                    })
    except WebSocketDisconnect:
        ws_messaging.disconnect(websocket, user_id)

