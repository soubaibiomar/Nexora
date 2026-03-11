"""
Tests for the Experts Router.
Covers search (with and without filters), profile retrieval, locations, and departments.
"""


class TestExpertSearch:
    """Tests for GET /api/experts/search."""

    def test_search_no_filters(self, client):
        """Search experts with no filters returns a list."""
        response = client.get("/api/experts/search")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_with_query(self, client):
        """Search experts with a text query."""
        response = client.get("/api/experts/search", params={"q": "engineer"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_with_department(self, client):
        """Search experts filtered by department."""
        response = client.get("/api/experts/search", params={"department": "Engineering"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_with_limit(self, client):
        """Search respects the limit parameter."""
        response = client.get("/api/experts/search", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_search_with_skip(self, client):
        """Search with skip for pagination."""
        response = client.get("/api/experts/search", params={"skip": 0, "limit": 5})
        assert response.status_code == 200


class TestExpertLocations:
    """Tests for GET /api/experts/locations/list."""

    def test_get_locations(self, client):
        """Returns a list of location strings."""
        response = client.get("/api/experts/locations/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestExpertDepartments:
    """Tests for GET /api/experts/departments/list."""

    def test_get_departments(self, client):
        """Returns a list of department strings."""
        response = client.get("/api/experts/departments/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
