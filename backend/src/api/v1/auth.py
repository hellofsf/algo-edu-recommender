"""Authentication API routes."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import AuthSvc
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    TokenResponse,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and return authentication tokens.",
)
async def register(
    data: UserRegisterRequest,
    auth_service: AuthSvc,
) -> TokenResponse:
    """Register a new user."""
    try:
        user = await auth_service.register(data)
        return auth_service.create_tokens(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user with email and password, return tokens.",
)
async def login(
    data: UserLoginRequest,
    auth_service: AuthSvc,
) -> TokenResponse:
    """Authenticate user and return tokens."""
    user = await auth_service.authenticate(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Use refresh token to obtain new access token.",
)
async def refresh_token(
    data: TokenRefreshRequest,
    auth_service: AuthSvc,
) -> TokenResponse:
    """Refresh access token using refresh token."""
    tokens = auth_service.refresh_tokens(data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tokens
