"""Graph analysis and visualization API routes."""

from fastapi import APIRouter, Query, HTTPException, status

from src.api.deps import CurrentUser
from src.db.neo4j import neo4j_execute_query
from src.schemas.knowledge import (
    SubgraphRequest,
    SubgraphResponse,
    SubgraphNode,
    SubgraphLink,
    GraphOverviewResponse,
    CategoryStats,
)

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.post(
    "/subgraph",
    response_model=SubgraphResponse,
    summary="Get subgraph",
    description="Extract a subgraph centered on given nodes with configurable depth.",
)
async def get_subgraph(
    request: SubgraphRequest,
    current_user: CurrentUser,
) -> SubgraphResponse:
    """Get subgraph around specified nodes."""
    node_ids = request.node_ids
    depth = request.depth

    # Build depth-based path pattern
    if depth == 0:
        cypher = """
        UNWIND $node_ids AS nid
        MATCH (n:KnowledgeNode {node_id: nid})
        OPTIONAL MATCH (n)-[r:PREREQUISITE]-(other:KnowledgeNode)
        WHERE other.node_id IN $node_ids
        RETURN DISTINCT n, other, r
        """
    else:
        cypher = f"""
        UNWIND $node_ids AS seed_id
        MATCH (seed:KnowledgeNode {{node_id: seed_id}})
        CALL {{
            WITH seed
            MATCH path = (seed)-[:PREREQUISITE*0..{depth}]-(n:KnowledgeNode)
            RETURN DISTINCT n, seed
        }}
        WITH collect(DISTINCT n) AS all_nodes, collect(DISTINCT seed) AS seeds
        UNWIND all_nodes AS node
        OPTIONAL MATCH (node)-[r:PREREQUISITE]-(related:KnowledgeNode)
        WHERE related IN all_nodes
        RETURN node, collect(DISTINCT related) AS related_nodes,
               collect(DISTINCT r) AS rels
        """
    params = {"node_ids": node_ids, "depth": depth}

    records = await neo4j_execute_query(cypher, params)

    # Deduplicate nodes and links
    nodes_map: dict[str, SubgraphNode] = {}
    links_set: set[tuple[str, str, str]] = set()

    for record in records:
        node_data = record.get("node")
        if node_data and node_data.get("node_id"):
            nid = node_data["node_id"]
            if nid not in nodes_map:
                nodes_map[nid] = SubgraphNode(
                    node_id=nid,
                    title=node_data.get("title", ""),
                    category=node_data.get("category"),
                    difficulty=node_data.get("difficulty"),
                    mastery_level=node_data.get("mastery_level", 0.0),
                )

        related = record.get("related_nodes", [])
        rels = record.get("rels", [])
        for i, rel in enumerate(rels):
            if rel and i < len(related):
                related_node = related[i]
                if related_node and node_data:
                    src = node_data.get("node_id")
                    tgt = related_node.get("node_id")
                    rel_type = rel.get("type", "PREREQUISITE")
                    if src and tgt:
                        key = tuple(sorted([src, tgt])) + (rel_type,)
                        links_set.add(key)

    nodes = list(nodes_map.values())
    links = [
        SubgraphLink(
            source_id=link[0],
            target_id=link[1],
            rel_type=link[2],
        )
        for link in links_set
    ]

    return SubgraphResponse(
        nodes=nodes,
        links=links,
        total_nodes=len(nodes),
        total_links=len(links),
    )


@router.get(
    "/overview",
    response_model=GraphOverviewResponse,
    summary="Get graph overview",
    description="Get overview statistics of the entire knowledge graph.",
)
async def get_overview(
    current_user: CurrentUser,
) -> GraphOverviewResponse:
    """Get overall graph statistics."""
    # Total counts
    stats_cypher = """
    MATCH (n:KnowledgeNode)
    RETURN count(n) AS total_nodes
    """
    link_cypher = """
    MATCH ()-[r:PREREQUISITE]->()
    RETURN count(r) AS total_links
    """
    cat_cypher = """
    MATCH (n:KnowledgeNode)
    WITH n.category AS cat, count(n) AS cnt,
         avg(CASE n.difficulty
             WHEN 'easy' THEN 1 WHEN 'medium' THEN 2 WHEN 'hard' THEN 3
             ELSE 2 END) AS avg_d
    WHERE cat IS NOT NULL
    RETURN cat AS name, cnt AS node_count, avg_d AS avg_difficulty
    ORDER BY cnt DESC
    """
    diff_cypher = """
    MATCH (n:KnowledgeNode)
    WITH n.difficulty AS diff, count(n) AS cnt
    RETURN diff, cnt
    """
    degree_cypher = """
    MATCH (n:KnowledgeNode)
    OPTIONAL MATCH (n)-[:PREREQUISITE]->(pre)
    OPTIONAL MATCH (n)<-[:PREREQUISITE]-(dep)
    WITH n, count(pre) + count(dep) AS degree
    ORDER BY degree DESC
    LIMIT 10
    RETURN n.node_id AS node_id, n.title AS title, degree
    """

    stats_records = await neo4j_execute_query(stats_cypher, {})
    link_records = await neo4j_execute_query(link_cypher, {})
    cat_records = await neo4j_execute_query(cat_cypher, {})
    diff_records = await neo4j_execute_query(diff_cypher, {})
    degree_records = await neo4j_execute_query(degree_cypher, {})

    total_nodes = stats_records[0]["total_nodes"] if stats_records else 0
    total_links = link_records[0]["total_links"] if link_records else 0

    categories = [
        CategoryStats(
            name=r["name"],
            node_count=r["node_count"],
            avg_difficulty=round(r["avg_difficulty"], 2) if r.get("avg_difficulty") else None,
        )
        for r in cat_records
    ]

    difficulty_distribution = {}
    for r in diff_records:
        if r.get("diff"):
            difficulty_distribution[r["diff"]] = r["cnt"]

    most_connected = [
        {"node_id": r["node_id"], "title": r["title"], "degree": r["degree"]}
        for r in degree_records
    ]

    return GraphOverviewResponse(
        total_nodes=total_nodes,
        total_links=total_links,
        categories=categories,
        difficulty_distribution=difficulty_distribution,
        most_connected_nodes=most_connected,
    )
