"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.db.session import init_db, close_db, init_redis, close_redis
from src.db.neo4j import get_neo4j_driver, close_neo4j
from src.core.rate_limit import RateLimitMiddleware
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
from src.api.v1.health import router as health_router
from src.api.v1.knowledge import router as knowledge_router
from src.api.v1.graph import router as graph_router
from src.api.v1.review import router as review_router
from src.api.v1.learning import router as learning_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    await init_redis()
    # Warm up Neo4j driver
    await get_neo4j_driver()
    yield
    # Shutdown
    await close_redis()
    await close_neo4j()
    await close_db()


app = FastAPI(
    title="AlgoEdu Recommender API",
    description="Algorithm Education Recommendation System Backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(review_router, prefix="/api/v1")
app.include_router(learning_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "AlgoEdu Recommender API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
