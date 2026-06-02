"""Knowledge graph Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


# --- Knowledge Node Schemas ---


class KnowledgeNodeBase(BaseModel):
    """Base knowledge node schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    difficulty: str | None = Field(default=None, pattern="^(easy|medium|hard)$")
    content: str | None = None
    code_template: str | None = None
    time_complexity: str | None = None
    space_complexity: str | None = None


class KnowledgeNodeCreate(KnowledgeNodeBase):
    """Schema for creating a knowledge node."""

    node_id: str | None = Field(default=None, max_length=100)


class KnowledgeNodeUpdate(BaseModel):
    """Schema for updating a knowledge node."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    difficulty: str | None = Field(default=None, pattern="^(easy|medium|hard)$")
    content: str | None = None
    code_template: str | None = None
    time_complexity: str | None = None
    space_complexity: str | None = None
    mastery_level: float | None = Field(default=None, ge=0.0, le=1.0)


class KnowledgeNodeResponse(KnowledgeNodeBase):
    """Response schema for knowledge node."""

    node_id: str
    mastery_level: float = 0.0
    prerequisite_count: int = 0
    dependent_count: int = 0
    review_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Knowledge Link Schemas ---


class KnowledgeLinkCreate(BaseModel):
    """Schema for creating a knowledge link."""

    source_id: str = Field(..., max_length=100)
    target_id: str = Field(..., max_length=100)
    rel_type: str = Field(default="PREREQUISITE", max_length=50)


class KnowledgeLinkResponse(BaseModel):
    """Response schema for knowledge link."""

    source_id: str
    target_id: str
    rel_type: str

    model_config = {"from_attributes": True}


# --- Graph Search Schemas ---


class SearchResult(BaseModel):
    """Single search result item."""

    node_id: str
    title: str
    description: str | None = None
    category: str | None = None
    difficulty: str | None = None
    score: float = 0.0
    matched_fields: list[str] = []


class GraphSearchRequest(BaseModel):
    """Request schema for graph search."""

    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)
    category: str | None = None
    difficulty: str | None = Field(default=None, pattern="^(easy|medium|hard)$")


class GraphSearchResponse(BaseModel):
    """Response schema for graph search."""

    query: str
    results: list[SearchResult]
    total: int
    search_type: str = "hybrid"  # "vector", "graph", "hybrid"


# --- Subgraph Schemas ---


class SubgraphRequest(BaseModel):
    """Request schema for subgraph extraction."""

    node_ids: list[str] = Field(..., min_length=1, max_length=50)
    depth: int = Field(default=1, ge=0, le=3)


class SubgraphNode(BaseModel):
    """Node in a subgraph response."""

    node_id: str
    title: str
    category: str | None = None
    difficulty: str | None = None
    mastery_level: float = 0.0


class SubgraphLink(BaseModel):
    """Link in a subgraph response."""

    source_id: str
    target_id: str
    rel_type: str


class SubgraphResponse(BaseModel):
    """Response schema for subgraph."""

    nodes: list[SubgraphNode]
    links: list[SubgraphLink]
    total_nodes: int
    total_links: int


# --- Graph Overview Schemas ---


class CategoryStats(BaseModel):
    """Statistics for a single category."""

    name: str
    node_count: int
    avg_difficulty: float | None = None


class GraphOverviewResponse(BaseModel):
    """Response schema for graph overview."""

    total_nodes: int
    total_links: int
    categories: list[CategoryStats]
    difficulty_distribution: dict[str, int]
    most_connected_nodes: list[dict]  # top 10 by degree
