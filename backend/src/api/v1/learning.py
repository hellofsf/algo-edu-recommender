"""Learning path and history API routes."""

from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DbSession
from src.models.review import LearningStats
from src.schemas.review import (
    LearningRecordCreate,
    LearningRecordResponse,
    LearningPathResponse,
    LearningPathItem,
)
from src.services.recommendation import RecommendationService
from src.services.knowledge import KnowledgeService

router = APIRouter(prefix="/learning", tags=["Learning"])


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()


def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()


@router.post(
    "/record",
    response_model=LearningRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record learning activity",
    description="Record a learning activity (learn, review, complete, skip) for a node.",
)
async def create_learning_record(
    data: LearningRecordCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> LearningRecordResponse:
    """Record a learning activity."""
    record_id = str(uuid4())
    now = datetime.now(timezone.utc)

    # Update learning stats
    result = await db.execute(
        select(LearningStats).where(LearningStats.user_id == current_user.id)
    )
    stats = result.scalar_one_or_none()

    if stats:
        stats.total_learning_time += data.time_spent_minutes
        if data.action == "complete":
            stats.nodes_mastered += 1
    else:
        stats = LearningStats(
            user_id=current_user.id,
            total_learning_time=data.time_spent_minutes,
            nodes_mastered=1 if data.action == "complete" else 0,
            current_streak=1,
            longest_streak=1,
            last_review_date=now,
        )
        db.add(stats)

    await db.commit()

    return LearningRecordResponse(
        id=record_id,
        user_id=current_user.id,
        knowledge_node_id=data.knowledge_node_id,
        action=data.action,
        time_spent_minutes=data.time_spent_minutes,
        created_at=now,
    )


@router.get(
    "/history",
    response_model=list[LearningRecordResponse],
    summary="Get learning history",
    description="Get learning history for the current user.",
)
async def get_learning_history(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[LearningRecordResponse]:
    """
    Get learning history (simplified - returns stats as records).

    In production, this would query a dedicated LearningRecord table.
    """
    # For now, derive history from ReviewRecord
    from src.models.review import ReviewRecord
    result = await db.execute(
        select(ReviewRecord)
        .where(ReviewRecord.user_id == current_user.id)
        .order_by(ReviewRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    records = result.scalars().all()

    return [
        LearningRecordResponse(
            id=r.id,
            user_id=r.user_id,
            knowledge_node_id=r.knowledge_node_id,
            action="review",
            time_spent_minutes=0,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get(
    "/path",
    response_model=LearningPathResponse,
    summary="Get learning path",
    description="Get a prerequisite learning path between two nodes.",
)
async def get_learning_path(
    current_user: CurrentUser,
    db: DbSession,
    start_node_id: str = Query(..., description="Starting node ID"),
    target_node_id: str = Query(..., description="Target node ID"),
) -> LearningPathResponse:
    """Get the learning path from start to target node."""
    rec_service = get_recommendation_service()
    knowledge_service = get_knowledge_service()

    # Get path node IDs
    path_ids = await rec_service.get_learning_path(start_node_id, target_node_id)

    # Get user mastery data
    from src.models.review import ReviewRecord
    result = await db.execute(
        select(ReviewRecord).where(ReviewRecord.user_id == current_user.id)
    )
    records = result.scalars().all()
    mastery_map = {r.knowledge_node_id: r.mastery_level for r in records}

    # Build path items
    path_items = []
    total_time = 0
    for i, node_id in enumerate(path_ids):
        try:
            node = await knowledge_service.get_node(node_id)
            mastery = mastery_map.get(node_id, 0.0)
            path_items.append(
                LearningPathItem(
                    node_id=node_id,
                    title=node.title,
                    category=node.category,
                    difficulty=node.difficulty,
                    depth=i,
                    is_mastered=mastery >= 0.8,
                    is_learned=mastery > 0.0,
                    estimated_time_minutes=30,  # default estimate
                )
            )
            total_time += 30
        except ValueError:
            continue

    return LearningPathResponse(
        start_node_id=start_node_id,
        target_node_id=target_node_id,
        path=path_items,
        total_nodes=len(path_items),
        estimated_total_time=total_time,
        prerequisite_count=len(path_items),
    )


@router.get(
    "/recommendations",
    response_model=list[dict],
    summary="Get forgetting-driven recommendations",
    description="Get personalized recommendations based on forgetting curve analysis.",
)
async def get_recommendations(
    current_user: CurrentUser,
    limit: int = Query(default=10, ge=1, le=30),
) -> list[dict]:
    """Get forgetting-driven review recommendations."""
    rec_service = get_recommendation_service()
    return await rec_service.get_forgetting_driven_recommendations(
        current_user.id, limit
    )
