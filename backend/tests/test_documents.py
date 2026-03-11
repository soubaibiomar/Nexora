"""
Tests for the Documents Router.
Covers document search, types list, and document retrieval.
"""


class TestDocumentSearch:
    """Tests for GET /api/documents/search."""

    def test_search_no_filters(self, client):
        """Search documents with no filters returns a list."""
        response = client.get("/api/documents/search")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_with_query(self, client):
        """Search documents with a text query."""
        response = client.get("/api/documents/search", params={"q": "python"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_with_type_filter(self, client):
        """Search documents filtered by type."""
        response = client.get("/api/documents/search", params={"type": "Tutorial"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_with_limit(self, client):
        """Search respects the limit parameter."""
        response = client.get("/api/documents/search", params={"limit": 3})
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3


class TestDocumentTypes:
    """Tests for GET /api/documents/types/list."""

    def test_get_types(self, client):
        """Returns a list of document types."""
        response = client.get("/api/documents/types/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
