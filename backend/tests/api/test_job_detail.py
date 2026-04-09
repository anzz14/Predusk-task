import pytest
import httpx
from uuid import uuid4


class TestJobDetail:
    """Test job detail endpoint."""

    @pytest.mark.asyncio
    async def test_get_job_detail(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test retrieving job detail."""
        # Upload document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Get job detail
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/job",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"]
        assert data["document_id"] == doc_id
        assert data["status"] in ["queued", "processing", "completed", "failed"]

    @pytest.mark.asyncio
    async def test_job_detail_cross_user_404(self, test_client: httpx.AsyncClient, auth_headers: dict, second_user_auth_headers: dict, sample_txt_file: dict):
        """Test that cross-user access to job returns 404."""
        # User 1 uploads document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # User 2 tries to get User 1's job
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/job",
            headers=second_user_auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_nonexistent_job_404(self, test_client: httpx.AsyncClient, auth_headers: dict):
        """Test accessing non-existent job returns 404."""
        fake_id = str(uuid4())
        response = await test_client.get(
            f"/api/v1/documents/{fake_id}/job",
            headers=auth_headers,
        )
        assert response.status_code == 404