import pytest
import httpx
from uuid import uuid4


class TestDocumentListing:
    """Test document listing and filtering."""

    @pytest.mark.asyncio
    async def test_list_documents(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test listing documents for authenticated user."""
        # Upload a document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )

        response = await test_client.get("/api/v1/documents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    @pytest.mark.asyncio
    async def test_cross_user_isolation(self, test_client: httpx.AsyncClient, auth_headers: dict, second_user_auth_headers: dict, sample_txt_file: dict):
        """Test that users only see their own documents."""
        # User 1 uploads document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201

        # User 1 sees their document
        response = await test_client.get("/api/v1/documents", headers=auth_headers)
        user1_count = response.json()["total"]

        # User 2 should see 0 documents (different user)
        response = await test_client.get("/api/v1/documents", headers=second_user_auth_headers)
        user2_count = response.json()["total"]
        assert user2_count == 0
        assert user1_count > 0

    @pytest.mark.asyncio
    async def test_status_filter(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test filtering documents by status."""
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )

        # Filter by queued status
        response = await test_client.get(
            "/api/v1/documents?status=queued",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert all(doc["status"] == "queued" for doc in data["items"])

    @pytest.mark.asyncio
    async def test_search_filter(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test searching documents by filename."""
        files = {"file": ("unique_test_document.txt", sample_txt_file["content"])}
        await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )

        # Search for document
        response = await test_client.get(
            "/api/v1/documents?search=unique",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0
        assert "unique" in data["items"][0]["original_filename"].lower()

    @pytest.mark.asyncio
    async def test_sort_order(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test sorting documents by different fields."""
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )

        # Sort by created_at descending
        response = await test_client.get(
            "/api/v1/documents?sort_by=created_at&sort_order=desc",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        if len(data["items"]) > 1:
            # Verify descending order
            for i in range(len(data["items"]) - 1):
                assert data["items"][i]["created_at"] >= data["items"][i + 1]["created_at"]

    @pytest.mark.asyncio
    async def test_pagination(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test document list pagination."""
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )

        response = await test_client.get(
            "/api/v1/documents?page=1&page_size=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10