"""
Custom exceptions for the Fasty application.

This module defines custom exceptions that are used throughout the application
to provide consistent error handling.
"""
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from typing import Any, Dict, Optional


class FastyError(Exception):
    """Base exception for all Fasty application errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ConfigError(FastyError):
    """Raised when there is an error in the application configuration."""

    def __init__(
        self,
        message: str = "Configuration error",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ModelNotFoundError(FastyError):
    """Raised when a requested model is not found."""

    def __init__(self, model_name: str) -> None:
        super().__init__(
            message=f"Model '{model_name}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"model": model_name},
        )


class ItemNotFoundError(FastyError):
    """Raised when a requested item is not found."""

    def __init__(self, model_name: str, item_id: Any) -> None:
        super().__init__(
            message=f"Item with ID '{item_id}' not found in model '{model_name}'",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"model": model_name, "item_id": item_id},
        )


def http_exception_handler(request, exc: FastyError):
    """Convert FastyError to HTTPException for FastAPI error handling."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error": exc.__class__.__name__,
            **exc.details,
        },
    )
