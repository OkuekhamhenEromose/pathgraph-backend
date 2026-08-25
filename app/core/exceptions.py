"""
Custom application exceptions.
These are caught by global exception handlers in main.py.
"""


class DatabaseError(Exception):
    """Raised when CognoDB is unreachable or query fails."""
    pass


class NotFoundError(Exception):
    """Raised when a requested resource does not exist in the graph."""
    pass
