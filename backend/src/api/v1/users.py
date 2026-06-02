"""User API routes."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, AuthSvc
from src.schemas.user import (
    UserProfileResponse,
    UserProgressResponse,
    UserStatsResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user.",
)
async def get_me(current_user: CurrentUser) -> UserProfileResponse:
    """Get current user profile."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
    )


@router.get(
    "/me/progress",
    response_model=UserProgressResponse,
    summary="Get user learning progress",
    description="Get learning progress including problems solved, streaks, and weak areas.",
)
async def get_progress(
    current_user: CurrentUser,
    auth_service: AuthSvc,
) -> UserProgressResponse:
    """Get user learning progress."""
    # TODO: Fetch from Neo4j or Redis cache
    return UserProgressResponse(
        user_id=current_user.id,
        problems_solved=0,
        total_solved=0,
        current_streak=0,
        longest_streak=0,
        weak_areas=[],
        strong_areas=[],
        recent_activity=[],
    )


@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
    summary="Get user statistics",
    description="Get aggregated statistics including solved problems by difficulty.",
)
async def get_stats(
    current_user: CurrentUser,
    auth_service: AuthSvc,
) -> UserStatsResponse:
    """Get user statistics."""
    # TODO: Fetch from Neo4j or Redis cache
    return UserStatsResponse(
        user_id=current_user.id,
        total_problems=0,
        easy_solved=0,
        medium_solved=0,
        hard_solved=0,
        total_time_spent=0,
        submission_count=0,
        acceptance_rate=0.0,
    )
