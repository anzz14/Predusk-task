import pytest
import httpx
from datetime import datetime, timedelta
import jwt
from app.config import settings


class TestAuthRegister:
    """Test user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, test_client: httpx.AsyncClient):
        """Test successful user registration."""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"]
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_short_password(self, test_client: httpx.AsyncClient):
        """Test registration fails with 422 on short password (< 8 chars)."""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "short",  # Less than 8 characters
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, test_client: httpx.AsyncClient):
        """Test registration fails with 422 on invalid email format."""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePassword123",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, test_client: httpx.AsyncClient):
        """Test registration fails with 409 on duplicate email."""
        response1 = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "SecurePassword123",
            },
        )
        assert response1.status_code == 201

        response2 = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "SecurePassword456",
            },
        )
        assert response2.status_code == 409


class TestAuthLogin:
    """Test user login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, auth_headers: dict):
        """Test successful login returns access token."""
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, test_client: httpx.AsyncClient):
        """Test login fails with 401 on wrong password."""
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "CorrectPassword123",
            },
        )

        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "WrongPassword123",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, test_client: httpx.AsyncClient):
        """Test login fails with 401 for non-existent user."""
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "AnyPassword123",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_returns_access_token(self, test_client: httpx.AsyncClient):
        """Test that login response includes access_token."""
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "tokentest@example.com",
                "password": "SecurePassword123",
            },
        )

        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "tokentest@example.com",
                "password": "SecurePassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestAuthJWT:
    """Test JWT token validation and expiry."""

    @pytest.mark.asyncio
    async def test_expired_jwt_fails(self, test_client: httpx.AsyncClient):
        """Test that expired JWT is rejected with 401."""
        expired_payload = {
            "sub": "test-user-id",
            "exp": datetime.utcnow() - timedelta(hours=1),
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await test_client.get("/api/v1/documents", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_jwt_format_fails(self, test_client: httpx.AsyncClient):
        """Test that invalid JWT format is rejected."""
        headers = {"Authorization": "Bearer invalid.token.format"}
        response = await test_client.get("/api/v1/documents", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_authorization_header(self, test_client: httpx.AsyncClient):
        """Test that missing auth header returns 401."""
        response = await test_client.get("/api/v1/documents")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_jwt_allowed(self, test_client: httpx.AsyncClient, auth_headers: dict):
        """Test that valid JWT is accepted."""
        response = await test_client.get("/api/v1/documents", headers=auth_headers)
        assert response.status_code != 401