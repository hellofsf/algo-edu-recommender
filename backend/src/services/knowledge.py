"""Knowledge graph service."""

from typing import Any

from src.db.neo4j import neo4j_execute_query, neo4j_execute_write
from src.schemas.knowledge import (
    KnowledgeNodeCreate,
    KnowledgeNodeUpdate,
    KnowledgeNodeResponse,
    PaginationParams,
)


class KnowledgeService:
    """Service for knowledge graph operations."""

    async def create_node(self, data: KnowledgeNodeCreate) -> KnowledgeNodeResponse:
        """Create a new knowledge node in Neo4j."""
        node_id = data.node_id or data.title.lower().replace(" ", "-")
        cypher = """
        CREATE (n:KnowledgeNode {
            node_id: $node_id,
            title: $title,
            description: $description,
            category: $category,
            difficulty: $difficulty,
            content: $content,
            code_template: $code_template,
            time_complexity: $time_complexity,
            space_complexity: $space_complexity,
            mastery_level: 0.0,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN n.node_id AS node_id,
               n.title AS title,
               n.description AS description,
               n.category AS category,
               n.difficulty AS difficulty,
               n.content AS content,
               n.code_template AS code_template,
               n.time_complexity AS time_complexity,
               n.space_complexity AS space_complexity,
               n.mastery_level AS mastery_level,
               n.created_at AS created_at,
               n.updated_at AS updated_at
        """
        params = {
            "node_id": node_id,
            "title": data.title,
            "description": data.description,
            "category": data.category,
            "difficulty": data.difficulty,
            "content": data.content,
            "code_template": data.code_template,
            "time_complexity": data.time_complexity,
            "space_complexity": data.space_complexity,
        }
        records = await neo4j_execute_query(cypher, params)
        if not records:
            raise RuntimeError("Failed to create knowledge node")
        return self._record_to_response(records[0])

    async def get_node(self, node_id: str) -> KnowledgeNodeResponse:
        """Get a knowledge node by ID."""
        cypher = """
        MATCH (n:KnowledgeNode {node_id: $node_id})
        OPTIONAL MATCH (n)-[r:PREREQUISITE]->(pre)
        OPTIONAL MATCH (n)<-[r2:PREREQUISITE]-(dep)
        OPTIONAL MATCH (rr:ReviewRecord {knowledge_node_id: $node_id})
        RETURN n.node_id AS node_id,
               n.title AS title,
               n.description AS description,
               n.category AS category,
               n.difficulty AS difficulty,
               n.content AS content,
               n.code_template AS code_template,
               n.time_complexity AS time_complexity,
               n.space_complexity AS space_complexity,
               n.mastery_level AS mastery_level,
               n.created_at AS created_at,
               n.updated_at AS updated_at,
               COUNT(DISTINCT pre) AS prerequisite_count,
               COUNT(DISTINCT dep) AS dependent_count,
               COUNT(DISTINCT rr) AS review_count
        """
        records = await neo4j_execute_query(cypher, {"node_id": node_id})
        if not records:
            raise ValueError(f"Knowledge node not found: {node_id}")
        return self._record_to_response(records[0])

    async def list_nodes(
        self,
        page: int = 1,
        page_size: int = 20,
        category: str | None = None,
        difficulty: str | None = None,
    ) -> dict[str, Any]:
        """List knowledge nodes with pagination."""
        params: dict[str, Any] = {"offset": (page - 1) * page_size, "limit": page_size}
        where_clauses = []
        if category:
            where_clauses.append("n.category = $category")
            params["category"] = category
        if difficulty:
            where_clauses.append("n.difficulty = $difficulty")
            params["difficulty"] = difficulty

        where_str = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        cypher = f"""
        MATCH (n:KnowledgeNode)
        {where_str}
        WITH n ORDER BY n.created_at DESC
        WITH collect(n) AS all_nodes, count(n) AS total
        UNWIND all_nodes[{params["offset"]}:{params["offset"] + params["limit"]}] AS node
        OPTIONAL MATCH (node)-[:PREREQUISITE]->(pre)
        OPTIONAL MATCH (node)<-[:PREREQUISITE]-(dep)
        RETURN [n IN all_nodes | n.node_id] AS all_ids,
               [n IN all_nodes | {{node_id: n.node_id, title: n.title, category: n.category, difficulty: n.difficulty}}] AS items,
               total
        """
        records = await neo4j_execute_query(cypher, params)
        if not records:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}
        return {
            "items": records[0].get("items", []),
            "total": records[0].get("total", 0),
            "page": page,
            "page_size": page_size,
        }

    async def update_node(
        self, node_id: str, data: KnowledgeNodeUpdate
    ) -> KnowledgeNodeResponse:
        """Update a knowledge node."""
        set_clauses = ["n.updated_at = datetime()"]
        params: dict[str, Any] = {"node_id": node_id}

        for field, value in data.model_dump(exclude_unset=True).items():
            set_clauses.append(f"n.{field} = ${field}")
            params[field] = value

        cypher = f"""
        MATCH (n:KnowledgeNode {{node_id: $node_id}})
        SET {", ".join(set_clauses)}
        RETURN n.node_id AS node_id,
               n.title AS title,
               n.description AS description,
               n.category AS category,
               n.difficulty AS difficulty,
               n.content AS content,
               n.code_template AS code_template,
               n.time_complexity AS time_complexity,
               n.space_complexity AS space_complexity,
               n.mastery_level AS mastery_level,
               n.created_at AS created_at,
               n.updated_at AS updated_at
        """
        records = await neo4j_execute_query(cypher, params)
        if not records:
            raise ValueError(f"Knowledge node not found: {node_id}")
        return self._record_to_response(records[0])

    async def delete_node(self, node_id: str) -> bool:
        """Delete a knowledge node and its relationships."""
        cypher = """
        MATCH (n:KnowledgeNode {node_id: $node_id})
        DETACH DELETE n
        RETURN count(n) AS deleted
        """
        await neo4j_execute_write(cypher, {"node_id": node_id})
        return True

    async def create_link(
        self, source_id: str, target_id: str, rel_type: str = "PREREQUISITE"
    ) -> bool:
        """Create a relationship between two knowledge nodes."""
        cypher = f"""
        MATCH (a:KnowledgeNode {{node_id: $source_id}})
        MATCH (b:KnowledgeNode {{node_id: $target_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        RETURN count(r) AS created
        """
        await neo4j_execute_write(cypher, {"source_id": source_id, "target_id": target_id})
        return True

    async def search_nodes(self, keyword: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search knowledge nodes by keyword."""
        cypher = """
        MATCH (n:KnowledgeNode)
        WHERE n.title CONTAINS $keyword
           OR n.description CONTAINS $keyword
           OR n.category CONTAINS $keyword
        RETURN n.node_id AS node_id,
               n.title AS title,
               n.description AS description,
               n.category AS category,
               n.difficulty AS difficulty,
               n.mastery_level AS mastery_level
        LIMIT $limit
        """
        records = await neo4j_execute_query(
            cypher, {"keyword": keyword, "limit": limit}
        )
        return [dict(r) for r in records]

    def _record_to_response(self, record: dict[str, Any]) -> KnowledgeNodeResponse:
        """Convert a Neo4j record to a KnowledgeNodeResponse."""
        created_at = record.get("created_at")
        updated_at = record.get("updated_at")
        return KnowledgeNodeResponse(
            node_id=record.get("node_id", ""),
            title=record.get("title", ""),
            description=record.get("description"),
            category=record.get("category"),
            difficulty=record.get("difficulty"),
            content=record.get("content"),
            code_template=record.get("code_template"),
            time_complexity=record.get("time_complexity"),
            space_complexity=record.get("space_complexity"),
            mastery_level=record.get("mastery_level", 0.0),
            prerequisite_count=record.get("prerequisite_count", 0),
            dependent_count=record.get("dependent_count", 0),
            review_count=record.get("review_count", 0),
            created_at=created_at,
            updated_at=updated_at,
        )
