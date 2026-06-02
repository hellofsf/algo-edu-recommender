"""Knowledge nodes and links API routes."""

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser
from src.schemas.knowledge import (
    KnowledgeNodeCreate,
    KnowledgeNodeUpdate,
    KnowledgeNodeResponse,
    KnowledgeLinkCreate,
    KnowledgeLinkResponse,
    GraphSearchRequest,
    GraphSearchResponse,
    SearchResult,
)
from src.services.knowledge import KnowledgeService
from src.services.graph_rag import GraphRAGService

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


# --- Dependency factories (lazy) ---

def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()


def get_graph_rag_service() -> GraphRAGService:
    return GraphRAGService()


# --- Knowledge Node Routes ---


@router.post(
    "/nodes",
    response_model=KnowledgeNodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a knowledge node",
    description="Create a new knowledge node in the graph.",
)
async def create_node(
    data: KnowledgeNodeCreate,
    current_user: CurrentUser,
) -> KnowledgeNodeResponse:
    """Create a new knowledge node."""
    service = get_knowledge_service()
    return await service.create_node(data)


@router.get(
    "/nodes",
    response_model=dict,
    summary="List knowledge nodes",
    description="List knowledge nodes with pagination and optional filters.",
)
async def list_nodes(
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: str | None = None,
    difficulty: str | None = None,
) -> dict:
    """List knowledge nodes."""
    service = get_knowledge_service()
    return await service.list_nodes(
        page=page, page_size=page_size, category=category, difficulty=difficulty
    )


@router.get(
    "/nodes/{node_id}",
    response_model=KnowledgeNodeResponse,
    summary="Get a knowledge node",
    description="Get a single knowledge node by its ID.",
)
async def get_node(
    node_id: str,
    current_user: CurrentUser,
) -> KnowledgeNodeResponse:
    """Get a knowledge node by ID."""
    service = get_knowledge_service()
    try:
        return await service.get_node(node_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/nodes/{node_id}",
    response_model=KnowledgeNodeResponse,
    summary="Update a knowledge node",
    description="Update a knowledge node's properties.",
)
async def update_node(
    node_id: str,
    data: KnowledgeNodeUpdate,
    current_user: CurrentUser,
) -> KnowledgeNodeResponse:
    """Update a knowledge node."""
    service = get_knowledge_service()
    try:
        return await service.update_node(node_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/nodes/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a knowledge node",
    description="Delete a knowledge node and all its relationships.",
)
async def delete_node(
    node_id: str,
    current_user: CurrentUser,
) -> None:
    """Delete a knowledge node."""
    service = get_knowledge_service()
    await service.delete_node(node_id)


# --- Search & Links Routes ---


@router.post(
    "/search",
    response_model=GraphSearchResponse,
    summary="Hybrid graph search",
    description="Search knowledge nodes using hybrid vector+graph retrieval.",
)
async def search_nodes(
    request: GraphSearchRequest,
    current_user: CurrentUser,
) -> GraphSearchResponse:
    """Hybrid graph RAG search."""
    service = get_graph_rag_service()
    results = await service.search(request.query, request.top_k)

    search_results = [
        SearchResult(
            node_id=r.get("node_id", ""),
            title=r.get("title", ""),
            description=r.get("description"),
            category=r.get("category"),
            difficulty=r.get("difficulty"),
            score=r.get("score", 0.0),
            matched_fields=r.get("matched_fields", []),
        )
        for r in results
    ]

    return GraphSearchResponse(
        query=request.query,
        results=search_results,
        total=len(search_results),
        search_type="hybrid",
    )


@router.post(
    "/links",
    response_model=KnowledgeLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a knowledge link",
    description="Create a relationship between two knowledge nodes.",
)
async def create_link(
    data: KnowledgeLinkCreate,
    current_user: CurrentUser,
) -> KnowledgeLinkResponse:
    """Create a knowledge link."""
    service = get_knowledge_service()
    await service.create_link(data.source_id, data.target_id, data.rel_type)
    return KnowledgeLinkResponse(
        source_id=data.source_id,
        target_id=data.target_id,
        rel_type=data.rel_type,
    )
