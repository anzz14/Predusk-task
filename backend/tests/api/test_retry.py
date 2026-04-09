import pytest
import httpx
from uuid import uuid4


class TestJobRetry:
    """Test job retry endpoint with status guards."""

    @pytest.mark.asyncio
    async def test_retry_only_available_for_failed_jobs(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test that retry is only allowed for failed jobs; returns 400 for other statuses."""
        # Upload document (creates queued job)
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Try to retry queued job (not allowed)
        response = await test_client.post(
            f"/api/v1/documents/{doc_id}/retry",
            headers=auth_headers,
        )
        # Should fail because job is in queued state, not failed
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_retry_cross_user_404(self, test_client: httpx.AsyncClient, auth_headers: dict, second_user_auth_headers: dict, sample_txt_file: dict):
        """Test that cross-user retry returns 404."""
        # User 1 uploads document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # User 2 tries to retry User 1's job
        response = await test_client.post(
            f"/api/v1/documents/{doc_id}/retry",
            headers=second_user_auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_retry_nonexistent_job_404(self, test_client: httpx.AsyncClient, auth_headers: dict):
        """Test retrying non-existent job returns 404."""
        fake_id = str(uuid4())
        response = await test_client.post(
            f"/api/v1/documents/{fake_id}/retry",
            headers=auth_headers,
        )
        assert response.status_code == 404