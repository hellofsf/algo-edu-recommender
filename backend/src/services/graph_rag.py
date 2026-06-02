"""Graph RAG (Retrieval-Augmented Generation) service."""

from typing import Any

from src.db.neo4j import neo4j_execute_query
from src.schemas.knowledge import GraphSearchRequest, SearchResult


class GraphRAGService:
    """Service for Graph RAG hybrid search combining vector and graph expansion."""

    async def search(
        self, query: str, top_k: int = 10
    ) -> list[dict[str, Any]]:
        """
        Hybrid search combining keyword/BM25-style matching and graph expansion.

        Uses Reciprocal Rank Fusion (RRF) to combine results from:
        1. Keyword search on title/description
        2. Graph expansion from matched nodes
        """
        # Step 1: Vector-like keyword search
        vector_results = await self._vector_search(query, top_k * 2)

        # Step 2: Graph expansion from top matched nodes
        if vector_results:
            top_node_ids = [r["node_id"] for r in vector_results[:5]]
            graph_results = await self._graph_expand(top_node_ids, top_k * 2)
        else:
            graph_results = []

        # Step 3: RRF fusion
        fused = await self._rrf_fusion(vector_results, graph_results, k=60)
        return fused[:top_k]

    async def _vector_search(
        self, query: str, top_k: int
    ) -> list[dict[str, Any]]:
        """
        Keyword-based semantic search simulation.
        In production, this would use Neo4j vector index or external embedding service.
        """
        keywords = query.lower().split()
        keyword_filters = " OR ".join(
            [f"(n.title CONTAINS $kw{i} OR n.description CONTAINS $kw{i})" for i in range(len(keywords))]
        )
        params = {f"kw{i}": kw for i, kw in enumerate(keywords)}
        params["top_k"] = top_k

        if not keywords:
            cypher = f"""
            MATCH (n:KnowledgeNode)
            RETURN n.node_id AS node_id,
                   n.title AS title,
                   n.description AS description,
                   n.category AS category,
                   n.difficulty AS difficulty,
                   1.0 AS score,
                   [] AS matched_fields
            LIMIT $top_k
            """
        else:
            cypher = f"""
            MATCH (n:KnowledgeNode)
            WHERE {keyword_filters}
            WITH n,
                 [i IN range(0, {len(keywords)}-1) |
                  CASE
                    WHEN n.title CONTAINS $kw{{i}} THEN 2.0
                    WHEN n.description CONTAINS $kw{{i}} THEN 1.0
                    ELSE 0.0
                  END] AS field_scores
            WITH n, reduce(s = 0.0, x IN field_scores | s + x) AS total_score,
                 [i IN range(0, {len(keywords)}-1) |
                  CASE WHEN field_scores[i] > 0 THEN
                    CASE WHEN i % 2 == 0 THEN 'title' ELSE 'description' END
                  END] AS matched
            WHERE total_score > 0
            RETURN n.node_id AS node_id,
                   n.title AS title,
                   n.description AS description,
                   n.category AS category,
                   n.difficulty AS difficulty,
                   total_score AS score,
                   [m IN matched WHERE m IS NOT NULL] AS matched_fields
            ORDER BY score DESC
            LIMIT $top_k
            """
        records = await neo4j_execute_query(cypher, params)
        return [dict(r) for r in records]

    async def _graph_expand(
        self, node_ids: list[str], top_k: int
    ) -> list[dict[str, Any]]:
        """Expand from seed nodes via PREREQUISITE relationships."""
        if not node_ids:
            return []

        cypher = """
        MATCH (seed:KnowledgeNode {node_id: $seed_id})
        OPTIONAL MATCH (seed)-[:PREREQUISITE]->(pre:KnowledgeNode)
        OPTIONAL MATCH (seed)<-[:PREREQUISITE]-(dep:KnowledgeNode)
        WITH seed, pre, dep
        UNWIND [seed, pre, dep] AS n
        WHERE n IS NOT NULL
        WITH n, CASE WHEN n.node_id = $seed_id THEN 2.0 ELSE 1.0 END AS score
        RETURN n.node_id AS node_id,
               n.title AS title,
               n.description AS description,
               n.category AS category,
               n.difficulty AS difficulty,
               score AS score,
               [] AS matched_fields
        LIMIT $top_k
        """
        all_results = []
        for seed_id in node_ids:
            records = await neo4j_execute_query(
                cypher, {"seed_id": seed_id, "top_k": top_k}
            )
            all_results.extend([dict(r) for r in records])
        return all_results

    async def _rrf_fusion(
        self,
        vector_results: list[dict[str, Any]],
        graph_results: list[dict[str, Any]],
        k: int = 60,
    ) -> list[dict[str, Any]]:
        """
        Reciprocal Rank Fusion to combine ranked lists.

        RRF score = sum(1 / (k + rank)) for each result appearing in lists.
        """
        scores: dict[str, dict[str, Any]] = {}

        for rank, item in enumerate(vector_results):
            node_id = item["node_id"]
            if node_id not in scores:
                scores[node_id] = {**item, "score": 0.0}
            scores[node_id]["score"] += 1 / (k + rank + 1)
            if "matched_fields" not in scores[node_id]:
                scores[node_id]["matched_fields"] = list(item.get("matched_fields", []))

        for rank, item in enumerate(graph_results):
            node_id = item["node_id"]
            if node_id not in scores:
                scores[node_id] = {**item, "score": 0.0}
            scores[node_id]["score"] += 1 / (k + rank + 1)

        fused = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return fused
