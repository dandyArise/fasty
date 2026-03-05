"""
Base endpoint handler for dynamic models.

This module provides the base logic for generating CRUD endpoints
automatically based on model configurations.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from fasty.core.models import PaginationParams, PaginatedResponse, ModelConfig
from fasty.core.store import data_store
from fasty.core.exceptions import FastyError, ModelNotFoundError, ItemNotFoundError

router = APIRouter()
T = TypeVar('T', bound=BaseModel)


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    """Get pagination parameters from query."""
    return PaginationParams(page=page, size=size)


def handle_fasty_error(e: FastyError):
    """Convert FastyError to HTTPException."""
    raise HTTPException(
        status_code=e.status_code,
        detail={
            "message": str(e),
            "error": e.__class__.__name__,
            **e.details,
        },
    )


def register_model_endpoints(router: APIRouter, model_name: str):
    """Register CRUD endpoints for a model."""

    @router.get(
        f"/{model_name}",
        response_model=PaginatedResponse[Dict[str, Any]],
        tags=[model_name],
    )
    async def list_items(
        pagination: PaginationParams = Depends(get_pagination_params),
    ):
        """List all items for the model with pagination."""
        try:
            model_config = data_store.get_model(model_name)
            items = data_store.list_items(
                model_name=model_name,
                skip=(pagination.page - 1) * pagination.size,
                limit=pagination.size,
            )
            total = data_store.count_items(model_name)

            # Add HATEOAS links if enabled
            if model_config.hateoas:
                for item in items:
                    item['_links'] = {
                        "self": {"href": f"/{model_name}/{item['id']}", "method": "GET"},
                        "collection": {"href": f"/{model_name}", "method": "GET"}
                    }

            return PaginatedResponse.create(
                items=items,
                total=total,
                page=pagination.page,
                size=pagination.size,
            )
        except FastyError as e:
            handle_fasty_error(e)

    @router.post(
        f"/{model_name}",
        response_model=Dict[str, Any],
        status_code=status.HTTP_201_CREATED,
        tags=[model_name],
    )
    async def create_item(item: Dict[str, Any]):
        """Create a new item for the model."""
        try:
            return data_store.create_item(model_name, item)
        except FastyError as e:
            handle_fasty_error(e)

    @router.get(
        f"/{model_name}/{{item_id}}",
        response_model=Dict[str, Any],
        tags=[model_name],
    )
    async def get_item(item_id: str):
        """Get a single item by ID."""
        try:
            model_config = data_store.get_model(model_name)
            item = data_store.get_item(model_name, item_id)

            if model_config.hateoas:
                item_copy = dict(item)
                item_copy['_links'] = {
                    "self": {"href": f"/{model_name}/{item_id}", "method": "GET"},
                    "collection": {"href": f"/{model_name}", "method": "GET"}
                }
                return item_copy
            return item
        except FastyError as e:
            handle_fasty_error(e)

    @router.put(
        f"/{model_name}/{{item_id}}",
        response_model=Dict[str, Any],
        tags=[model_name],
    )
    async def update_item(item_id: str, item: Dict[str, Any]):
        """Update an existing item."""
        try:
            return data_store.update_item(model_name, item_id, item)
        except FastyError as e:
            handle_fasty_error(e)

    @router.delete(
        f"/{model_name}/{{item_id}}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=[model_name],
    )
    async def delete_item(item_id: str):
        """Delete an item."""
        try:
            data_store.delete_item(model_name, item_id)
            return None
        except FastyError as e:
            handle_fasty_error(e)

    return router
