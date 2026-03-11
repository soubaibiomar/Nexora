"""
Tests for Feed, Network, Jobs, Workspace, Learning, and Graph routers.
Covers the major endpoints of each router.
"""


# ── Feed Router ────────────────────────────────────────────────────
class TestFeedRouter:
    """Tests for the Feed API."""

    def test_get_feed(self, client):
        """GET /api/feed returns a list of posts."""
        response = client.get("/api/feed")
        assert response.status_code == 200

    def test_create_post(self, client):
        """POST /api/feed/posts creates a new post."""
        response = client.post("/api/feed/posts", json={
            "content": "This is a test post",
            "post_type": "text",
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("content") == "This is a test post"


# ── Network Router ─────────────────────────────────────────────────
class TestNetworkRouter:
    """Tests for the Network API."""

    def test_get_suggestions(self, client):
        """GET /api/network/suggestions returns people suggestions."""
        response = client.get("/api/network/suggestions")
        assert response.status_code == 200

    def test_get_connections(self, client):
        """GET /api/network/connections returns current connections."""
        response = client.get("/api/network/connections")
        assert response.status_code == 200

    def test_get_pending(self, client):
        """GET /api/network/pending returns pending requests."""
        response = client.get("/api/network/pending")
        assert response.status_code == 200

    def test_get_network_stats(self, client):
        """GET /api/network/stats returns network statistics."""
        response = client.get("/api/network/stats")
        assert response.status_code == 200


# ── Jobs Router ────────────────────────────────────────────────────
class TestJobsRouter:
    """Tests for the Jobs API."""

    def test_get_jobs(self, client):
        """GET /api/jobs returns a list of jobs."""
        response = client.get("/api/jobs")
        assert response.status_code == 200

    def test_get_recommended_jobs(self, client):
        """GET /api/jobs/recommended returns recommended jobs."""
        response = client.get("/api/jobs/recommended")
        assert response.status_code == 200

    def test_get_jobs_with_filters(self, client):
        """GET /api/jobs with department filter."""
        response = client.get("/api/jobs", params={"department": "Engineering"})
        assert response.status_code == 200


# ── Workspace Router ──────────────────────────────────────────────
class TestWorkspaceRouter:
    """Tests for the Workspace API."""

    def test_get_workspaces(self, client):
        """GET /api/workspaces returns a list of workspaces."""
        response = client.get("/api/workspaces")
        assert response.status_code == 200

    def test_create_workspace(self, client):
        """POST /api/workspaces creates a new workspace."""
        response = client.post("/api/workspaces", json={
            "name": "Test Workspace",
            "description": "A workspace for testing",
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("name") == "Test Workspace"


# ── Learning Router ────────────────────────────────────────────────
class TestLearningRouter:
    """Tests for the Learning API."""

    def test_get_skills_list(self, client):
        """GET /api/learning/skills/list returns available skills."""
        response = client.get("/api/learning/skills/list")
        assert response.status_code == 200

    def test_generate_learning_path(self, client):
        """POST /api/learning/path generates a learning path."""
        response = client.post("/api/learning/path", json={
            "current_skills": ["Python", "SQL"],
            "target_skill": "Machine Learning",
        })
        assert response.status_code == 200


# ── Graph Router ───────────────────────────────────────────────────
class TestGraphRouter:
    """Tests for the Graph API."""

    def test_get_graph_nodes(self, client):
        """GET /api/graph/nodes returns graph nodes."""
        response = client.get("/api/graph/nodes")
        assert response.status_code == 200

    def test_get_graph_stats(self, client):
        """GET /api/graph/stats returns graph statistics."""
        response = client.get("/api/graph/stats")
        assert response.status_code == 200
