class NotFoundError(Exception):
    """Raised when a requested resource or route does not exist."""


class ConflictError(Exception):
    """Raised when a request conflicts with persisted data."""
