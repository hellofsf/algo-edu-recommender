"""Learning path recommendation service."""

from typing import Any

from src.db.neo4j import neo4j_execute_query, neo4j_execute_write
from src.services.ebbinghaus import EbbinghausScheduler


class RecommendationService:
    """Service for learning path and review recommendations."""

    def __init__(self):
        self.ebbinghaus = EbbinghausScheduler()

    async def get_learning_path(
        self, start_node_id: str, target_node_id: str
    ) -> list[str]:
        """
        Get shortest prerequisite learning path from start to target.

        Uses Neo4j BFS-style traversal to find the prerequisite chain.
        """
        cypher = """
        MATCH (start:KnowledgeNode {node_id: $start_id}),
              (target:KnowledgeNode {node_id: $target_id})
        MATCH path = (start)-[:PREREQUISITE*1..20]->(target)
        WITH path, length(path) AS path_length
        ORDER BY path_length ASC
        LIMIT 1
        WITH [n IN nodes(path) | n.node_id] AS path_ids
        RETURN path_ids
        """
        records = await neo4j_execute_query(
            cypher, {"start_id": start_node_id, "target_id": target_node_id}
        )
        if records and records[0].get("path_ids"):
            return records[0]["path_ids"]

        # Fallback: try reverse path (target is prerequisite of start)
        cypher2 = """
        MATCH (start:KnowledgeNode {node_id: $start_id}),
              (target:KnowledgeNode {node_id: $target_id})
        MATCH path = (target)-[:PREREQUISITE*1..20]->(start)
        WITH path, length(path) AS path_length
        ORDER BY path_length ASC
        LIMIT 1
        WITH [n IN nodes(path) | n.node_id] AS path_ids
        RETURN path_ids
        """
        records2 = await neo4j_execute_query(
            cypher2, {"start_id": start_node_id, "target_id": target_node_id}
        )
        if records2 and records2[0].get("path_ids"):
            return records2[0]["path_ids"]

        return [start_node_id, target_node_id]

    async def get_forgetting_driven_recommendations(
        self, user_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Recommend nodes based on forgetting curve analysis.

        Prioritizes nodes where:
        1. Retention has dropped significantly (forgotten)
        2. Review is overdue
        3. High-impact nodes (many dependents)
        """
        cypher = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[r:ReviewRecord]->(n:KnowledgeNode)
        WITH u, n, r,
             CASE WHEN r.next_review_date IS NULL THEN datetime()
                  ELSE r.next_review_date END AS next_review,
             CASE WHEN r.quality IS NULL THEN 0 ELSE r.quality END AS quality,
             CASE WHEN r.ease_factor IS NULL THEN 2.5 ELSE r.ease_factor END AS ef,
             CASE WHEN r.interval IS NULL THEN 0 ELSE r.interval END AS interval,
             CASE WHEN r.repetitions IS NULL THEN 0 ELSE r.repetitions END AS reps,
             CASE WHEN r.mastery_level IS NULL THEN 0.0 ELSE r.mastery_level END AS mastery
        WITH n, next_review, quality, ef, interval, reps, mastery,
             duration.between(datetime(), next_review).days AS days_diff
        WHERE n IS NOT NULL
        WITH n, quality, ef, interval, reps, mastery, days_diff,
             CASE WHEN days_diff <= 0 THEN 1 ELSE 0 END AS is_overdue,
             CASE WHEN days_diff <= 0 THEN abs(days_diff) ELSE 0 END AS overdue_days
        ORDER BY is_overdue DESC, overdue_days DESC, mastery ASC
        LIMIT $limit
        OPTIONAL MATCH (n)<-[:PREREQUISITE]-(dep)
        WITH n, quality, ef, interval, reps, mastery, is_overdue, overdue_days,
             count(dep) AS dependent_count
        RETURN n.node_id AS node_id,
               n.title AS title,
               n.category AS category,
               n.difficulty AS difficulty,
               mastery AS mastery_level,
               quality,
               ef,
               interval,
               reps,
               overdue_days,
               dependent_count,
               CASE WHEN is_overdue = 1 THEN 'overdue'
                    WHEN mastery < 0.5 THEN 'weak'
                    ELSE 'review_due' END AS reason
        """
        records = await neo4j_execute_query(cypher, {"user_id": user_id, "limit": limit})
        return [dict(r) for r in records]

    async def get_prerequisite_chain(
        self, node_id: str, include_mastery: bool = False, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all prerequisites for a node in topological order.

        Args:
            node_id: Target node ID.
            include_mastery: Include user mastery data.
            user_id: User ID for mastery lookup.
        """
        cypher = """
        MATCH (target:KnowledgeNode {node_id: $node_id})
        MATCH path = (pre:KnowledgeNode)-[:PREREQUISITE*1..10]->(target)
        WITH pre, min(length(path)) AS depth
        ORDER BY depth ASC
        WITH collect(DISTINCT pre) AS prerequisites
        UNWIND prerequisites AS pre
        OPTIONAL MATCH (pre)-[:PREREQUISITE]->(next)
        WITH pre, prerequisites, count(next) AS has_dependent
        RETURN pre.node_id AS node_id,
               pre.title AS title,
               pre.category AS category,
               pre.difficulty AS difficulty,
               1 AS depth,
               has_dependent > 0 AS has_dependent
        """
        if user_id:
            cypher = cypher.replace(
                "RETURN pre.node_id",
                "OPTIONAL MATCH (u:User {id: $user_id})-[:ReviewRecord]->(pre) "
                "WITH pre, u, prerequisites, has_dependent "
                "RETURN pre.node_id",
            )
            cypher = cypher.replace(
                "has_dependent > 0 AS has_dependent",
                "CASE WHEN r.mastery_level IS NULL THEN 0.0 ELSE r.mastery_level END AS mastery_level, "
                "has_dependent > 0 AS has_dependent",
            )
            records = await neo4j_execute_query(
                cypher, {"node_id": node_id, "user_id": user_id}
            )
        else:
            records = await neo4j_execute_query(cypher, {"node_id": node_id})

        return [dict(r) for r in records]
