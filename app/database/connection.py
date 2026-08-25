"""
CognoDB connection management.
Single driver instance created at startup, shared across requests.
"""

from neo4j import GraphDatabase, Driver


class GraphDatabaseConnection:
    """
    Wrapper around the official Neo4j Python driver.
    Manages connection pooling and session lifecycle.
    """

    def __init__(self, uri: str, username: str, password: str) -> None:
        self.driver: Driver = GraphDatabase.driver(
            uri,
            auth=(username, password),
            max_connection_pool_size=50,
            connection_timeout=30,
        )

    def verify_connectivity(self) -> None:
        """Verify that we can reach CognoDB. Raises on failure."""
        self.driver.verify_connectivity()

    def get_session(self):
        """Return a new session. Caller must close it."""
        return self.driver.session()

    def close(self) -> None:
        """Close the driver and drain the connection pool."""
        self.driver.close()
