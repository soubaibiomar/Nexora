from neo4j import GraphDatabase
from contextlib import contextmanager
from .config import get_settings

settings = get_settings()

# Flag to track if Neo4j is available
_neo4j_available = None


class Neo4jDriver:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
        return cls._driver

    @classmethod
    def close(cls):
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None


def is_neo4j_available() -> bool:
    """Check if Neo4j database is available."""
    global _neo4j_available
    if _neo4j_available is not None:
        return _neo4j_available
    
    try:
        driver = Neo4jDriver.get_driver()
        with driver.session() as session:
            session.run("RETURN 1")
        _neo4j_available = True
    except Exception:
        _neo4j_available = False
    
    return _neo4j_available


@contextmanager
def get_db_session():
    """Context manager for Neo4j database sessions."""
    driver = Neo4jDriver.get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


def get_db():
    """Dependency for FastAPI routes."""
    driver = Neo4jDriver.get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


# Wrapper class for fallback mode
class FallbackSession:
    """A mock session that uses fallback data when Neo4j is unavailable."""
    
    def run(self, query, params=None):
        # This will be handled by the routers directly
        raise NotImplementedError("Fallback mode active")
    
    def close(self):
        pass


def get_db_or_fallback():
    """Return database session or None if fallback mode should be used."""
    if is_neo4j_available():
        return get_db()
    return None
