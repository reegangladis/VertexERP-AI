from typing import Any


class BaseException(Exception):  # noqa: N818
    """Base exception class for all custom application errors."""

    status_code: int = 500
    message: str = "An internal server error occurred"

    def __init__(self, message: str | None = None, details: Any = None) -> None:
        super().__init__(message or self.message)
        if message:
            self.message = message
        self.details = details


class ValidationException(BaseException):
    """Exception raised when request parameters or data validation fails."""

    status_code: int = 422
    message: str = "Validation failed for request parameters"


class NotFoundException(BaseException):
    """Exception raised when a requested resource is not found."""

    status_code: int = 404
    message: str = "The requested resource was not found"


class ConflictException(BaseException):
    """Exception raised when a database or logical conflict occurs."""

    status_code: int = 409
    message: str = "A conflict occurred with the current state of the resource"


class UnauthorizedException(BaseException):
    """Exception raised when authentication credentials are missing or invalid."""

    status_code: int = 401
    message: str = "Authentication credentials were not provided or are invalid"


class ForbiddenException(BaseException):
    """Exception raised when a user is authenticated but not authorized."""

    status_code: int = 403
    message: str = "You do not have permission to access this resource"


class InternalServerException(BaseException):
    """Exception raised when an internal server error occurs."""

    status_code: int = 500
    message: str = "An unexpected internal server error occurred"
