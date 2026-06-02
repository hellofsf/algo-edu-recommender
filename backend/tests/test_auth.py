"""Tests for authentication endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient

from src.models.user import User
from src.core.security import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_password_returns_hash(self):
        """Test that hash_password returns a hash."""
        password = "TestPass123"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = "TestPass123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password."""
        password = "TestPass123"
        hashed = hash_password(password)
        assert verify_password("WrongPassword", hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = hash_password("Password1")
        hash2 = hash_password("Password2")
        assert hash1 != hash2


class TestAuthEndpoints:
    """Test authentication API endpoints."""

    @pytest.mark.asyncio
    async def test_register_validation_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "TestPass123",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_register_validation_password_short(self, client: AsyncClient):
        """Test registration with too short password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_validation_password_no_uppercase(self, client: AsyncClient):
        """Test registration with password lacking uppercase."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "nouppercase123",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_validation(self, client: AsyncClient):
        """Test login with missing fields."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_refresh_token_validation(self, client: AsyncClient):
        """Test refresh token with missing field."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={},
        )
        assert response.status_code == 422


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_liveness(self, client: AsyncClient):
        """Test liveness probe endpoint."""
        response = await client.get("/api/v1/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    @pytest.mark.asyncio
    async def test_health_endpoint_structure(self, client: AsyncClient):
        """Test health endpoint returns expected structure."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert "postgresql" in data["services"]
        assert "redis" in data["services"]
        assert "neo4j" in data["services"]


class TestRootEndpoint:
    """Test root endpoint."""

    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AlgoEdu Recommender API"
        assert "version" in data
        assert "docs" in data


class TestUserEndpoints:
    """Test user endpoints (requires auth)."""

    @pytest.mark.asyncio
    async def test_me_requires_auth(self, client: AsyncClient):
        """Test /me endpoint requires authentication."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 403  # No credentials provided

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client: AsyncClient):
        """Test /me endpoint with invalid token."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_progress_requires_auth(self, client: AsyncClient):
        """Test /me/progress endpoint requires authentication."""
        response = await client.get("/api/v1/users/me/progress")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_stats_requires_auth(self, client: AsyncClient):
        """Test /me/stats endpoint requires authentication."""
        response = await client.get("/api/v1/users/me/stats")
        assert response.status_code == 403
