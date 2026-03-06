"""
Custom exceptions for Outline CLI.
"""

from typing import Any


class OutlineError(Exception):
    """Base exception for all Outline-related errors."""

    pass


class OutlineAPIError(OutlineError):
    """Exception raised for Outline API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize OutlineAPIError.

        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
            response: API response data (if available)
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[HTTP {self.status_code}] {self.message}"
        return self.message


class OutlineConfigError(OutlineError):
    """Exception raised for configuration errors."""

    pass


class OutlineAuthenticationError(OutlineAPIError):
    """Exception raised for authentication errors."""

    pass


class OutlineNotFoundError(OutlineAPIError):
    """Exception raised when a resource is not found."""

    pass


class OutlineValidationError(OutlineError):
    """Exception raised for validation errors."""

    pass
