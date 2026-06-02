"""User Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str
    full_name: str | None = None


class UserResponse(UserBase):
    """Response schema for user data."""

    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(UserBase):
    """Response schema for user profile."""

    id: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProgressResponse(BaseModel):
    """Response schema for user learning progress."""

    user_id: str
    problems_solved: int = 0
    total_solved: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    weak_areas: list[str] = []
    strong_areas: list[str] = []
    recent_activity: list[dict] = []


class UserStatsResponse(BaseModel):
    """Response schema for aggregated user statistics."""

    user_id: str
    total_problems: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_time_spent: int = 0  # minutes
    submission_count: int = 0
    acceptance_rate: float = 0.0
