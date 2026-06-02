"""Review scheduling and statistics API routes."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DbSession
from src.db.session import get_db
from src.models.review import ReviewRecord, LearningStats
from src.schemas.review import (
    DueReviewItem,
    ReviewScheduleRequest,
    ReviewStatsResponse,
    ForgettingCurveResponse,
    ForgettingCurvePoint,
)
from src.services.ebbinghaus import EbbinghausScheduler
from src.services.knowledge import KnowledgeService

router = APIRouter(prefix="/review", tags=["Review"])


def get_ebbinghaus() -> EbbinghausScheduler:
    return EbbinghausScheduler()


def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()


@router.get(
    "/due",
    response_model=list[DueReviewItem],
    summary="Get due reviews",
    description="Get all knowledge nodes due for review for the current user.",
)
async def get_due_reviews(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = 20,
) -> list[DueReviewItem]:
    """Get all due review items for the user."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ReviewRecord)
        .where(
            and_(
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.next_review_date <= now,
            )
        )
        .order_by(ReviewRecord.next_review_date.asc())
        .limit(limit)
    )
    records = result.scalars().all()

    knowledge_service = get_knowledge_service()
    items = []
    for record in records:
        try:
            node = await knowledge_service.get_node(record.knowledge_node_id)
            days_overdue = (now - record.next_review_date).days
            items.append(
                DueReviewItem(
                    knowledge_node_id=record.knowledge_node_id,
                    title=node.title,
                    category=node.category,
                    difficulty=node.difficulty,
                    due_date=record.next_review_date,
                    days_overdue=max(0, days_overdue),
                    current_interval=record.interval,
                    current_ease_factor=record.ease_factor,
                    current_repetitions=record.repetitions,
                    mastery_level=record.mastery_level,
                )
            )
        except ValueError:
            # Node might have been deleted, skip it
            continue

    return items


@router.get(
    "/curve/{node_id}",
    response_model=ForgettingCurveResponse,
    summary="Get forgetting curve",
    description="Get predicted forgetting curve for a specific knowledge node.",
)
async def get_forgetting_curve(
    node_id: str,
    current_user: CurrentUser,
    db: DbSession,
) -> ForgettingCurveResponse:
    """Get forgetting curve data for a node."""
    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.knowledge_node_id == node_id,
            )
        )
    )
    record = result.scalar_one_or_none()

    ebbinghaus = get_ebbinghaus()
    knowledge_service = get_knowledge_service()

    try:
        node = await knowledge_service.get_node(node_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge node not found: {node_id}",
        )

    interval = record.interval if record else 0
    ef = record.ease_factor if record else 2.5
    reps = record.repetitions if record else 0

    predicted = ebbinghaus.get_forgetting_curve_points(interval, ef, reps)
    optimal = ebbinghaus.get_optimal_review_points(interval, ef, reps)

    return ForgettingCurveResponse(
        node_id=node_id,
        title=node.title,
        current_interval=interval,
        current_ease_factor=ef,
        current_repetitions=reps,
        predicted_points=[
            ForgettingCurvePoint(
                days=p["days"],
                retention_rate=p["retention_rate"],
                label=p["label"],
            )
            for p in predicted
        ],
        optimal_review_points=[
            ForgettingCurvePoint(
                days=p["days"],
                retention_rate=p["retention_rate"],
                label=p["label"],
            )
            for p in optimal
        ],
    )


@router.post(
    "/schedule",
    response_model=dict,
    summary="Schedule a review",
    description="Submit a review result and get the next review schedule (SM-2 algorithm).",
)
async def schedule_review(
    request: ReviewScheduleRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> dict:
    """Submit a review and get the next scheduled review."""
    ebbinghaus = get_ebbinghaus()

    # Find or create review record
    result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.knowledge_node_id == request.knowledge_node_id,
            )
        )
    )
    record = result.scalar_one_or_none()

    if record:
        # Update existing record
        current_interval = record.interval
        current_ef = record.ease_factor
        current_reps = record.repetitions
    else:
        # Create new record
        record = ReviewRecord(
            user_id=current_user.id,
            knowledge_node_id=request.knowledge_node_id,
            ease_factor=2.5,
            interval=0,
            repetitions=0,
            next_review_date=datetime.now(timezone.utc),
            mastery_level=0.0,
        )
        db.add(record)
        current_interval = 0
        current_ef = 2.5
        current_reps = 0

    # Calculate next review using SM-2
    schedule = ebbinghaus.calculate_next_review(
        repetitions=current_reps,
        interval=max(1, current_interval),
        quality=request.quality,
        current_ef=current_ef,
    )

    # Update record
    record.quality = request.quality
    record.interval = schedule["new_interval"]
    record.ease_factor = schedule["new_ef"]
    record.repetitions = schedule["new_repetitions"]
    record.next_review_date = datetime.fromisoformat(schedule["next_review_date"])
    record.mastery_level = schedule["mastery_level"]
    record.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)

    # Update learning stats
    await _update_learning_stats(db, current_user.id)

    return {
        "knowledge_node_id": request.knowledge_node_id,
        "next_review_date": schedule["next_review_date"],
        "new_interval": schedule["new_interval"],
        "new_ease_factor": schedule["new_ef"],
        "new_repetitions": schedule["new_repetitions"],
        "mastery_level": schedule["mastery_level"],
    }


@router.get(
    "/stats",
    response_model=ReviewStatsResponse,
    summary="Get review statistics",
    description="Get aggregated review and learning statistics for the user.",
)
async def get_review_stats(
    current_user: CurrentUser,
    db: DbSession,
) -> ReviewStatsResponse:
    """Get review statistics."""
    result = await db.execute(
        select(LearningStats).where(LearningStats.user_id == current_user.id)
    )
    stats = result.scalar_one_or_none()

    # Count due reviews
    now = datetime.now(timezone.utc)
    due_result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.next_review_date <= now,
            )
        )
    )
    due_today = len(due_result.scalars().all())

    # Count due this week
    week_later = now + datetime.timedelta(days=7)
    week_result = await db.execute(
        select(ReviewRecord).where(
            and_(
                ReviewRecord.user_id == current_user.id,
                ReviewRecord.next_review_date <= week_later,
            )
        )
    )
    due_this_week = len(week_result.scalars().all())

    if stats:
        return ReviewStatsResponse(
            user_id=current_user.id,
            total_reviews=stats.total_reviews,
            total_learning_time=stats.total_learning_time,
            nodes_mastered=stats.nodes_mastered,
            current_streak=stats.current_streak,
            longest_streak=stats.longest_streak,
            due_today=due_today,
            due_this_week=due_this_week,
        )

    return ReviewStatsResponse(
        user_id=current_user.id,
        total_reviews=0,
        total_learning_time=0,
        nodes_mastered=0,
        current_streak=0,
        longest_streak=0,
        due_today=due_today,
        due_this_week=due_this_week,
    )


async def _update_learning_stats(db: AsyncSession, user_id: str) -> None:
    """Update learning statistics after a review."""
    from datetime import datetime as dt, timezone as tz

    result = await db.execute(
        select(LearningStats).where(LearningStats.user_id == user_id)
    )
    stats = result.scalar_one_or_none()

    if stats:
        stats.total_reviews += 1
        stats.last_review_date = dt.now(tz.utc)
        # Update streak
        today = dt.now(tz.utc).date()
        if stats.last_review_date:
            last_date = stats.last_review_date.date()
            if (today - last_date).days == 1:
                stats.current_streak += 1
            elif (today - last_date).days > 1:
                stats.current_streak = 1
        stats.longest_streak = max(stats.longest_streak, stats.current_streak)
    else:
        stats = LearningStats(
            user_id=user_id,
            total_reviews=1,
            current_streak=1,
            longest_streak=1,
            last_review_date=dt.now(tz.utc),
        )
        db.add(stats)

    await db.flush()
