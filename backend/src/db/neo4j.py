"""Neo4j database connection management."""

from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver

from src.config import get_settings

settings = get_settings()

_neo4j_driver: AsyncDriver | None = None


async def get_neo4j_driver() -> AsyncDriver:
    """Get or create Neo4j driver instance."""
    global _neo4j_driver
    if _neo4j_driver is None:
        _neo4j_driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60,
        )
    return _neo4j_driver


async def close_neo4j() -> None:
    """Close Neo4j driver."""
    global _neo4j_driver
    if _neo4j_driver:
        await _neo4j_driver.close()
        _neo4j_driver = None


async def check_neo4j() -> bool:
    """Check Neo4j connection."""
    try:
        driver = await get_neo4j_driver()
        async with driver.session() as session:
            result = await session.run("RETURN 1 AS result")
            await result.single()
        return True
    except Exception:
        return False


async def neo4j_execute_query(
    cypher: str,
    parameters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute a parameterized Cypher query."""
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run(cypher, parameters or {})
        records = await result.data()
        return records


async def neo4j_execute_write(
    cypher: str,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a parameterized write Cypher query."""
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run(cypher, parameters or {})
        summary = await result.consume()
        return {
            "counters": summary.counters,
            "consumed_queries": summary.consumed_queries,
        }
