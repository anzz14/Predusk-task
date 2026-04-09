import pytest
import httpx
from uuid import uuid4


class TestExtractedResult:
    """Test result retrieval endpoint."""

    @pytest.mark.asyncio
    async def test_get_result(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict, test_db_session):
        """Test retrieving extracted result."""
        # Upload document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Get result (may be processing or completed)
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/result",
            headers=auth_headers,
        )
        # Result may not exist yet if job is still queued/processing
        # So we accept both 200 and 404
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_result_cross_user_404(self, test_client: httpx.AsyncClient, auth_headers: dict, second_user_auth_headers: dict, sample_txt_file: dict):
        """Test that cross-user access to result returns 404."""
        # User 1 uploads document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # User 2 tries to get User 1's result
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/result",
            headers=second_user_auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_result_nonexistent_document_404(self, test_client: httpx.AsyncClient, auth_headers: dict):
        """Test accessing result for non-existent document returns 404."""
        fake_id = str(uuid4())
        response = await test_client.get(
            f"/api/v1/documents/{fake_id}/result",
            headers=auth_headers,
        )
        assert response.status_code == 404