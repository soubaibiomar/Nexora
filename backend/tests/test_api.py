"""
Unit Tests for AI Router and WebSocket Messaging
Tests the chatbot endpoint, model stats, and messaging WebSocket connections.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app

client = TestClient(app)


# ── AI Router Tests ────────────────────────────────────────────────

class TestAIRouter:
    """Tests for the AI/ML API router."""

    def test_chatbot_endpoint(self):
        """Test chatbot responds with valid structure."""
        response = client.post("/api/ai/chatbot", json={"message": "Hello"})
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_chatbot_with_skill_query(self):
        """Test chatbot handles skill-related queries."""
        response = client.post("/api/ai/chatbot", json={"message": "Who knows Python?"})
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_recommend_experts(self):
        """Test expert recommendation endpoint."""
        response = client.post(
            "/api/ai/recommend-experts",
            json={"query": "machine learning", "top_k": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_results" in data

    def test_model_stats(self):
        """Test model stats endpoint returns valid structure."""
        response = client.get("/api/ai/model-stats")
        assert response.status_code == 200
        data = response.json()
        assert "recommender" in data or "classifier" in data

    def test_skill_trends(self):
        """Test skill trends endpoint."""
        response = client.get("/api/ai/skill-trends")
        assert response.status_code == 200


# ── Messaging Router Tests ─────────────────────────────────────────

class TestMessagingRouter:
    """Tests for the Messaging API router."""

    def test_get_conversations(self):
        """Test fetching conversations."""
        response = client.get("/api/messaging/conversations")
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)

    def test_send_message(self):
        """Test sending a message."""
        # First get conversations to find an ID
        convos_response = client.get("/api/messaging/conversations")
        convos = convos_response.json().get("conversations", [])
        if convos:
            convo_id = convos[0]["id"]
            response = client.post(
                "/api/messaging/send",
                json={"conversation_id": convo_id, "content": "Test message"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("content") == "Test message"

    def test_get_messages(self):
        """Test fetching messages for a conversation."""
        convos_response = client.get("/api/messaging/conversations")
        convos = convos_response.json().get("conversations", [])
        if convos:
            convo_id = convos[0]["id"]
            response = client.get(f"/api/messaging/conversations/{convo_id}")
            assert response.status_code == 200
            data = response.json()
            assert "messages" in data


# ── Gamification Router Tests ──────────────────────────────────────

class TestGamificationRouter:
    """Tests for the Gamification API router."""

    def test_get_badge_definitions(self):
        """Test fetching all badge definitions."""
        response = client.get("/api/gamification/badges")
        assert response.status_code == 200
        data = response.json()
        assert "badges" in data
        assert len(data["badges"]) > 0

    def test_get_leaderboard(self):
        """Test fetching leaderboard."""
        response = client.get("/api/gamification/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data


# ── Dashboard / Analytics Tests ────────────────────────────────────

class TestDashboardRouter:
    """Tests for Dashboard and Analytics endpoints."""

    def test_predict_shortages(self):
        """Test skill shortage prediction endpoint."""
        response = client.get("/api/dashboard/predict-shortages")
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "critical_shortages" in data

    def test_skill_trend_data(self):
        """Test skill trend data endpoint."""
        response = client.get("/api/dashboard/skill-trends")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
        assert "quarters" in data

    def test_global_stats(self):
        """Test global stats endpoint."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200


# ── Notification Tests ─────────────────────────────────────────────

class TestNotificationRouter:
    """Tests for Notification router."""

    def test_get_notifications(self):
        """Test fetching notifications."""
        response = client.get("/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data

    def test_mark_all_read(self):
        """Test marking all notifications as read."""
        response = client.put("/api/notifications/read-all")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "all_read"


# ── Health Check ───────────────────────────────────────────────────

class TestHealthCheck:
    """Test app health and root endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "Gamification (Badges & Endorsements)" in data["features"]

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
