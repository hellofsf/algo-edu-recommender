"""Pytest fixtures and configuration."""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.db.session import async_session_factory
from src.models.user import User
from src.core.security import hash_password, create_access_token


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncMock, None]:
    """Create a mock database session for testing."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    yield session


@pytest_asyncio.fixture
async def test_user() -> User:
    """Create a test user."""
    return User(
        id="test-user-id",
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("TestPass123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """Create authorization headers with valid token."""
    token = create_access_token({
        "sub": test_user.id,
        "email": test_user.email,
        "username": test_user.username,
    })
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.pipeline = MagicMock(return_value=mock)
    mock.zremrangebyscore = AsyncMock()
    mock.zadd = AsyncMock()
    mock.zcard = AsyncMock()
    mock.expire = AsyncMock()
    mock.execute = AsyncMock(return_value=[0, 0, 1, True])
    return mock


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver."""
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_session.run = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()
    mock_driver.session = MagicMock(return_value=mock_session)
    return mock_driver
