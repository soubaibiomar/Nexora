"""
Tests for the Dashboard Router.
Covers stats, top skills, skill distribution, departments, and other analytics endpoints.
"""


class TestDashboardStats:
    """Tests for GET /api/dashboard/stats."""

    def test_get_stats(self, client):
        """Returns general statistics."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

    def test_get_top_skills(self, client):
        """Returns top skills list."""
        response = client.get("/api/dashboard/top-skills")
        assert response.status_code == 200

    def test_get_top_skills_with_limit(self, client):
        """Top skills with a custom limit."""
        response = client.get("/api/dashboard/top-skills", params={"limit": 5})
        assert response.status_code == 200

    def test_get_skill_distribution(self, client):
        """Returns skill distribution data."""
        response = client.get("/api/dashboard/skill-distribution")
        assert response.status_code == 200

    def test_get_departments(self, client):
        """Returns department stats."""
        response = client.get("/api/dashboard/departments")
        assert response.status_code == 200

    def test_get_project_status(self, client):
        """Returns project status breakdown."""
        response = client.get("/api/dashboard/project-status")
        assert response.status_code == 200

    def test_get_collaboration_rate(self, client):
        """Returns collaboration rate."""
        response = client.get("/api/dashboard/collaboration-rate")
        assert response.status_code == 200

    def test_get_knowledge_silos(self, client):
        """Returns knowledge silo data."""
        response = client.get("/api/dashboard/knowledge-silos")
        assert response.status_code == 200

    def test_get_skill_gaps(self, client):
        """Returns skill gap data."""
        response = client.get("/api/dashboard/skill-gaps")
        assert response.status_code == 200
