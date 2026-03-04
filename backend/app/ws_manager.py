"""
WebSocket Connection Manager
Manages real-time WebSocket connections for messaging and notifications.
"""

from typing import Dict, List, Any
from fastapi import WebSocket
import json


class ConnectionManager:
    """Manages active WebSocket connections per user."""

    def __init__(self):
        # Map of user_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                ws for ws in self.active_connections[user_id] if ws != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal(self, user_id: str, message: dict):
        """Send a message to a specific user's connections."""
        if user_id in self.active_connections:
            data = json.dumps(message)
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_text(data)
                except Exception:
                    pass

    async def broadcast(self, message: dict, exclude_user: str = None):
        """Broadcast a message to all connected users."""
        data = json.dumps(message)
        for user_id, connections in self.active_connections.items():
            if user_id == exclude_user:
                continue
            for ws in connections:
                try:
                    await ws.send_text(data)
                except Exception:
                    pass

    def get_online_users(self) -> List[str]:
        """Return list of currently connected user IDs."""
        return list(self.active_connections.keys())


# Global singleton instances
ws_messaging = ConnectionManager()
ws_notifications = ConnectionManager()
