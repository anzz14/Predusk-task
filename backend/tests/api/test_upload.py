import pytest
import httpx
import io
from uuid import uuid4


class TestDocumentUpload:
    """Test document upload endpoint."""

    @pytest.mark.asyncio
    async def test_upload_success(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test successful file upload returns 201."""
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"]
        assert data["original_filename"] == sample_txt_file["filename"]
        assert data["status"] == "queued"

    @pytest.mark.asyncio
    async def test_upload_without_auth(self, test_client: httpx.AsyncClient, sample_txt_file: dict):
        """Test upload without auth returns 401."""
        files = {"file": (sample_txt_file["filename"], sample_txt_file["content"])}
        response = await test_client.post(
            "/api/v1/documents/upload",
            files=files,
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_pdf_rejected(self, test_client: httpx.AsyncClient, auth_headers: dict):
        """Test that PDF files are rejected with 422."""
        pdf_content = b"%PDF-1.4 fake pdf"
        files = {"file": ("document.pdf", pdf_content)}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_upload_oversized_file(self, test_client: httpx.AsyncClient, auth_headers: dict):
        """Test that oversized files return 413."""
        # Create 6MB file (assuming 5MB limit)
        oversized_content = b"x" * (6 * 1024 * 1024)
        files = {"file": ("large.txt", oversized_content)}
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files=files,
        )
        assert response.status_code == 413

    @pytest.mark.asyncio
    async def test_upload_missing_file(self, test_client: httpx.AsyncClient, auth_headers: dict):
        """Test upload without file field returns 422."""
        response = await test_client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_upload_bulk_list(self, test_client: httpx.AsyncClient, auth_headers: dict, sample_txt_file: dict):
        """Test bulk upload and retrieve document list."""
        # Upload 3 documents
        for i in range(3):
            files = {"file": (f"file{i}.txt", sample_txt_file["content"])}
            response = await test_client.post(
                "/api/v1/documents/upload",
                headers=auth_headers,
                files=files,
            )
            assert response.status_code == 201

        # Get documents list
        response = await test_client.get("/api/v1/documents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3