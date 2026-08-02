import uuid
from typing import Any


def new_uuid() -> uuid.UUID:
    """Generates a new random UUID (UUID4)."""
    return uuid.uuid4()


def is_valid_uuid(val: Any) -> bool:
    """Checks whether the input is a valid UUID representation."""
    if isinstance(val, uuid.UUID):
        return True
    if not isinstance(val, str):
        return False
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False


def to_uuid(val: str | uuid.UUID) -> uuid.UUID:
    """Safely converts a string to a UUID object.

    Raises ValueError if invalid.
    """
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(val)
