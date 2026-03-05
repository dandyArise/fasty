"""
Core models for the Fasty application.

This module defines the base Pydantic models used for configuration,
data validation, and API responses.
"""
from typing import Any, Dict, List, Literal, Optional, Union, TypeVar, Generic
from pydantic import BaseModel, Field, validator
from pathlib import Path

T = TypeVar('T')


class FieldDefinition(BaseModel):
    """Definition of a field in a model."""
    type: str = "string"
    required: bool = True
    default: Optional[Any] = None
    description: Optional[str] = None
    faker: Optional[str] = None

    class Config:
        extra = "forbid"


class ModelConfig(BaseModel):
    """Configuration for a model in the API."""
    name: str
    description: Optional[str] = None
    pagination: bool = False
    hateoas: bool = True
    fields: Dict[str, Union[FieldDefinition, str]
                 ] = Field(default_factory=dict)
    fake: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "forbid"

    @validator('fields', pre=True)
    def transform_fields(cls, v):
        """Transform string field definitions into FieldDefinition objects."""
        if v is None:
            return {}

        result = {}
        for field_name, field_def in v.items():
            if isinstance(field_def, str):
                result[field_name] = FieldDefinition(type=field_def)
            elif isinstance(field_def, dict):
                result[field_name] = FieldDefinition(**field_def)
            else:
                result[field_name] = field_def
        return result


class AppConfig(BaseModel):
    """Main application configuration model."""
    locale: str = "en_US"
    models: Dict[str, ModelConfig] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ) -> 'PaginatedResponse[T]':
        """Create a paginated response."""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


# Model types for type hinting
ModelType = TypeVar('ModelType', bound=BaseModel)
