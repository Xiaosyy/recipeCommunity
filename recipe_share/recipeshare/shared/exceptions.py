class RepositoryError(Exception):
    """Base error for persistence failures."""


class DuplicateRecordError(RepositoryError):
    """Raised when a unique database constraint is violated."""


class RecordNotFoundError(RepositoryError):
    """Raised when a requested persisted record does not exist."""
