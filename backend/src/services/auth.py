"""Authentication service."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.auth import (
    UserRegisterRequest,
    TokenResponse,
)
from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.db.neo4j import neo4j_execute_query, neo4j_execute_write
from src.config import get_settings

settings = get_settings()


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """Find user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Find user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Find user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def register(self, data: UserRegisterRequest) -> User:
        """Register a new user."""
        # Check if email already exists
        if await self.get_user_by_email(data.email):
            raise ValueError("Email already registered")

        # Check if username already exists
        if await self.get_user_by_username(data.username):
            raise ValueError("Username already taken")

        # Create user
        user = User(
            email=data.email.lower(),
            username=data.username.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        await self.db.flush()

        # Create user node in Neo4j
        await self._create_neo4j_user_node(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def _create_neo4j_user_node(self, user: User) -> None:
        """Create user node in Neo4j graph database."""
        cypher = """
        CREATE (u:User {
            id: $user_id,
            email: $email,
            username: $username,
            created_at: datetime($created_at)
        })
        """
        await neo4j_execute_write(
            cypher,
            {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "created_at": user.created_at.isoformat(),
            },
        )

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    def refresh_tokens(self, refresh_token: str) -> TokenResponse | None:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        if not payload:
            return None

        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return TokenResponse(
            access_token=create_access_token({
                "sub": user_id,
                "email": payload.get("email"),
                "username": payload.get("username"),
            }),
            refresh_token=refresh_token,  # Return same refresh token
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def get_current_user(self, token_data: dict[str, Any]) -> User | None:
        """Get current user from token data."""
        user_id = token_data.get("sub")
        if not user_id:
            return None
        return await self.get_user_by_id(user_id)
