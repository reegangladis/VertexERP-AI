import re
from typing import Any

from app.core.exceptions import ValidationException


def validate_required(val: Any, field_name: str) -> None:
    """Ensures that a field value is not None or empty."""
    if val is None or (isinstance(val, str) and not val.strip()):
        raise ValidationException(
            message=f"The field '{field_name}' is required and cannot be empty."
        )


def validate_string_length(
    val: str, min_len: int, max_len: int, field_name: str
) -> None:
    """Validates that a string's length falls within minimum and maximum bounds."""
    if not isinstance(val, str):
        raise ValidationException(message=f"The field '{field_name}' must be a string.")
    length = len(val)
    if length < min_len or length > max_len:
        raise ValidationException(
            message=(
                f"The field '{field_name}' must be between {min_len} and "
                f"{max_len} characters long (current length: {length})."
            )
        )


def validate_email(email: str) -> None:
    """Validates basic email structure using regex."""
    validate_required(email, "email")
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        raise ValidationException(message=f"The email address '{email}' is invalid.")
