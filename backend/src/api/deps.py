"""API dependency injection."""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.services.auth import AuthService
from src.core.security import decode_token

security = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """Extract and validate user ID from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    """Get AuthService instance."""
    return AuthService(db)


async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Any:
    """Get current authenticated user."""
    from src.models.user import User
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Type aliases for cleaner route signatures
CurrentUser = Annotated[Any, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
