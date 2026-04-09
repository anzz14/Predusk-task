import asyncio
import os
import tempfile
from typing import AsyncGenerator

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.config import settings


@pytest.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates an isolated test database session.
    Uses ROLLBACK for transaction isolation - faster than DELETE and guarantees full isolation.
    """
    # Create test engine
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )

    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    TestSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with TestSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            finally:
                # Rollback all changes after test
                await session.rollback()

    # Clean up - drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def test_client(test_db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Creates an AsyncClient with get_db dependency overridden to use test_db_session.
    """
    def override_get_db():
        return test_db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(test_client: httpx.AsyncClient) -> dict[str, str]:
    """
    Registers a test user, logs in, and returns auth headers with Bearer token.
    """
    # Register
    register_response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "SecurePassword123",
        },
    )
    assert register_response.status_code == 201

    # Login
    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "SecurePassword123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def second_user_auth_headers(test_client: httpx.AsyncClient) -> dict[str, str]:
    """
    Registers a second test user and returns auth headers.
    Used for cross-user isolation tests.
    """
    # Register second user
    register_response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "seconduser@example.com",
            "password": "SecurePassword456",
        },
    )
    assert register_response.status_code == 201

    # Login
    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "seconduser@example.com",
            "password": "SecurePassword456",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_txt_file():
    """
    Creates a temporary .txt file with sample content for upload tests.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(
            "This is a sample text document for testing. "
            "It contains multiple sentences for analysis. "
            "The readability and keyword extraction should work correctly. "
            "Python is a popular programming language. "
            "Data science and machine learning are important fields. "
        )
        temp_path = f.name

    yield {
        "filename": "sample.txt",
        "path": temp_path,
        "content": open(temp_path, 'rb').read(),
    }

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def event_loop():
    """
    Create an event loop for async tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()