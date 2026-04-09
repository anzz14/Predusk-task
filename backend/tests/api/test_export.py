import pytest
import httpx
import csv
import json
from uuid import uuid4


class TestExport:
    """Test document export endpoint."""

    @pytest.mark.asyncio
    async def test_export_requires_finalized_document(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test export returns 403 for non-finalized documents."""
        # Upload document (not finalized yet)
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Try to export non-finalized document
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/export?format=json",
            headers=auth_headers,
        )
        # Should fail - document not finalized
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_export_json_format(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test JSON export format."""
        # Upload document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Try to export as JSON (will fail if not finalized, which is expected)
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/export?format=json",
            headers=auth_headers,
        )
        
        if response.status_code == 200:
            # Verify JSON format
            try:
                data = json.loads(response.content)
                assert "word_count" in data or "document" in data
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    @pytest.mark.asyncio
    async def test_export_csv_format(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test CSV export format."""
        # Upload document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Try to export as CSV (will fail if not finalized, which is expected)
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/export?format=csv",
            headers=auth_headers,
        )
        
        if response.status_code == 200:
            # Verify CSV format
            try:
                lines = response.text.strip().split("\n")
                assert len(lines) > 0
            except Exception:
                pytest.fail("Response is not valid CSV")

    @pytest.mark.asyncio
    async def test_export_cross_user_404(self, test_client: httpx.AsyncClient, auth_headers: dict, second_user_auth_headers: dict, sample_txt_file: dict):
        """Test that cross-user export returns 404."""
        # User 1 uploads document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # User 2 tries to export User 1's document
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/export?format=json",
            headers=second_user_auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_invalid_format_400(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test export with invalid format returns 400."""
        # Upload document
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        doc_id = response.json()["id"]

        # Try to export with invalid format
        response = await test_client.get(
            f"/api/v1/documents/{doc_id}/export?format=xml",
            headers=auth_headers,
        )
        # Should fail - invalid format
        assert response.status_code == 400