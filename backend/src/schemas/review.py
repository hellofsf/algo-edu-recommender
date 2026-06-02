"""Review and learning Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


# --- Review Record Schemas ---


class ReviewRecordBase(BaseModel):
    """Base review record schema."""

    knowledge_node_id: str
    quality: int = Field(..., ge=0, le=5)


class ReviewRecordCreate(ReviewRecordBase):
    """Schema for creating a review record."""

    pass


class ReviewScheduleRequest(BaseModel):
    """Request schema for scheduling a review."""

    knowledge_node_id: str
    quality: int = Field(..., ge=0, le=5, description="Review quality: 0-2 = fail/reset, 3 = okay, 4-5 = good")


class DueReviewItem(BaseModel):
    """Schema for an item due for review."""

    knowledge_node_id: str
    title: str
    category: str | None = None
    difficulty: str | None = None
    due_date: datetime
    days_overdue: int = 0
    current_interval: int = 0
    current_ease_factor: float = 2.5
    current_repetitions: int = 0
    mastery_level: float = 0.0


class ReviewStatsResponse(BaseModel):
    """Response schema for review statistics."""

    user_id: str
    total_reviews: int
    total_learning_time: int  # minutes
    nodes_mastered: int
    current_streak: int
    longest_streak: int
    due_today: int
    due_this_week: int
    avg_ease_factor: float = 2.5


# --- Forgetting Curve Schemas ---


class ForgettingCurvePoint(BaseModel):
    """Single point on the forgetting curve."""

    days: float
    retention_rate: float  # 0.0 - 1.0
    label: str


class ForgettingCurveResponse(BaseModel):
    """Response schema for forgetting curve data."""

    node_id: str
    title: str
    current_interval: int
    current_ease_factor: float
    current_repetitions: int
    predicted_points: list[ForgettingCurvePoint]
    optimal_review_points: list[ForgettingCurvePoint]


# --- Learning Record Schemas ---


class LearningRecordCreate(BaseModel):
    """Schema for creating a learning record."""

    knowledge_node_id: str
    time_spent_minutes: int = Field(default=0, ge=0)
    action: str = Field(
        default="learn",
        pattern="^(learn|review|complete|skip)$",
    )


class LearningRecordResponse(BaseModel):
    """Response schema for learning record."""

    id: str
    user_id: str
    knowledge_node_id: str
    action: str
    time_spent_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningPathItem(BaseModel):
    """Single item in a learning path."""

    node_id: str
    title: str
    category: str | None = None
    difficulty: str | None = None
    depth: int = 0
    is_mastered: bool = False
    is_learned: bool = False
    estimated_time_minutes: int = 30


class LearningPathResponse(BaseModel):
    """Response schema for a learning path."""

    start_node_id: str
    target_node_id: str
    path: list[LearningPathItem]
    total_nodes: int
    estimated_total_time: int  # minutes
    prerequisite_count: int
