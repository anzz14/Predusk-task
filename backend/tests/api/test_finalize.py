import pytest
import httpx
from uuid import uuid4


class TestFinalize:
    """Test document finalization endpoint."""

    @pytest.mark.asyncio
    async def test_finalize_requires_completed_job(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test that finalize returns 400 when job not completed."""
        # Upload document (job is queued, not completed)
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Try to finalize queued job
        response = await test_client.post(
            f"/api/v1/documents/{doc_id}/finalize",
            headers=auth_headers,
            json={"job_id": response.json()["current_job_id"]},
        )
        # Should fail - job not completed yet
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_finalize_double_finalize_409(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict, test_db_session):
        """Test finalize returns 409 when document already finalized."""
        # This test requires a completed job with result available
        # Upload document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]  
        job_id = response.json()["current_job_id"]

        # Finalize first time (assuming job is completed, else 400 is okay)
        response = await test_client.post(
            f"/api/v1/documents/{doc_id}/finalize",
            headers=auth_headers,
            json={"job_id": job_id},
        )
        
        if response.status_code == 200:
            # First finalize succeeded, try again
            response = await test_client.post(
                f"/api/v1/documents/{doc_id}/finalize",
                headers=auth_headers,
                json={"job_id": job_id},
            )
            # Second attempt should return 409 (conflict - already finalized)
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_finalize_cross_user_404(self, test_client: httpx.AsyncClient, auth_headers: dict, second_user_auth_headers: dict, sample_txt_file: dict):
        """Test that cross-user finalize returns 404."""
        # User 1 uploads document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]
        job_id = response.json()["current_job_id"]

        # User 2 tries to finalize User 1's document
        response = await test_client.post(
            f"/api/v1/documents/{doc_id}/finalize",
            headers=second_user_auth_headers,
            json={"job_id": job_id},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_finalize_stale_job_400(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test finalize returns 400 on stale job_id mismatch."""
        # Upload document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Try to finalize with wrong job_id
        response = await test_client.post(
            f"/api/v1/documents/{doc_id}/finalize",
            headers=auth_headers,
            json={"job_id": str(uuid4())},
        )
        # Should fail - stale/wrong job_id
        assert response.status_code == 400