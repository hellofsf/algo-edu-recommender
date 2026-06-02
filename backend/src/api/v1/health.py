"""Health check API routes."""

from datetime import datetime, timezone
from enum import Enum

from fastapi import APIRouter
from pydantic import BaseModel

from src.db.session import check_postgres, get_redis
from src.db.neo4j import check_neo4j

router = APIRouter(prefix="/health", tags=["Health"])


class ServiceStatus(str, Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceHealth(BaseModel):
    """Health status of a single service."""
    status: ServiceStatus
    latency_ms: float | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Overall health check response."""
    status: ServiceStatus
    timestamp: datetime
    services: dict[str, ServiceHealth]


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Check health of all backend services (PostgreSQL, Redis, Neo4j).",
)
async def health_check() -> HealthResponse:
    """Check health of all backend services."""
    import time

    services: dict[str, ServiceHealth] = {}
    all_healthy = True

    # Check PostgreSQL
    try:
        start = time.perf_counter()
        pg_healthy = await check_postgres()
        latency = (time.perf_counter() - start) * 1000
        services["postgresql"] = ServiceHealth(
            status=ServiceStatus.HEALTHY if pg_healthy else ServiceStatus.UNHEALTHY,
            latency_ms=round(latency, 2),
        )
        if not pg_healthy:
            all_healthy = False
    except Exception as e:
        services["postgresql"] = ServiceHealth(
            status=ServiceStatus.UNHEALTHY,
            error=str(e),
        )
        all_healthy = False

    # Check Redis
    try:
        start = time.perf_counter()
        redis = await get_redis()
        await redis.ping()
        latency = (time.perf_counter() - start) * 1000
        services["redis"] = ServiceHealth(
            status=ServiceStatus.HEALTHY,
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        services["redis"] = ServiceHealth(
            status=ServiceStatus.UNHEALTHY,
            error=str(e),
        )
        all_healthy = False

    # Check Neo4j
    try:
        start = time.perf_counter()
        neo4j_healthy = await check_neo4j()
        latency = (time.perf_counter() - start) * 1000
        services["neo4j"] = ServiceHealth(
            status=ServiceStatus.HEALTHY if neo4j_healthy else ServiceStatus.UNHEALTHY,
            latency_ms=round(latency, 2),
        )
        if not neo4j_healthy:
            all_healthy = False
    except Exception as e:
        services["neo4j"] = ServiceHealth(
            status=ServiceStatus.UNHEALTHY,
            error=str(e),
        )
        all_healthy = False

    return HealthResponse(
        status=ServiceStatus.HEALTHY if all_healthy else ServiceStatus.UNHEALTHY,
        timestamp=datetime.now(timezone.utc),
        services=services,
    )


@router.get(
    "/live",
    summary="Liveness probe",
    description="Simple liveness check - returns 200 if app is running.",
)
async def liveness() -> dict[str, str]:
    """Liveness probe endpoint."""
    return {"status": "alive"}


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Readiness check - returns 200 if all services are ready.",
)
async def readiness() -> dict[str, str]:
    """Readiness probe endpoint."""
    pg_healthy = await check_postgres()
    if not pg_healthy:
        return {"status": "not_ready", "reason": "PostgreSQL unavailable"}
    return {"status": "ready"}
