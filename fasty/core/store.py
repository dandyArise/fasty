"""
Data store for the Fasty application.

This module provides an in-memory data store with thread-safe operations
for managing dynamic models and their data.
"""
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
from uuid import uuid4
import threading
from pydantic import BaseModel

from fasty.core.models import ModelConfig
from fasty.core.exceptions import FastyError, ItemNotFoundError, ModelNotFoundError

T = TypeVar('T', bound=BaseModel)


class DataStore:
    """Thread-safe in-memory data store for dynamic models."""

    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._models: Dict[str, ModelConfig] = {}
        self._lock = threading.RLock()

    def register_model(self, model_config: ModelConfig) -> None:
        """Register a new model configuration."""
        with self._lock:
            self._models[model_config.name] = model_config
            if model_config.name not in self._data:
                self._data[model_config.name] = {}

    def get_model(self, model_name: str) -> ModelConfig:
        """Get a model configuration by name."""
        model = self._models.get(model_name)
        if not model:
            raise ModelNotFoundError(model_name)
        return model

    def list_models(self) -> List[str]:
        """List all registered model names."""
        return list(self._models.keys())

    def create_item(self, model_name: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in the specified model."""
        with self._lock:
            if model_name not in self._data:
                raise ModelNotFoundError(model_name)

            # Generate ID if not provided
            if 'id' not in item_data:
                item_data['id'] = str(uuid4())

            item_id = str(item_data['id'])
            self._data[model_name][item_id] = item_data
            return item_data

    def get_item(self, model_name: str, item_id: str) -> Dict[str, Any]:
        """Get an item by ID from the specified model."""
        with self._lock:
            if model_name not in self._data:
                raise ModelNotFoundError(model_name)

            item = self._data[model_name].get(str(item_id))
            if not item:
                raise ItemNotFoundError(model_name, item_id)

            return item

    def list_items(
        self,
        model_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List items from the specified model with pagination."""
        with self._lock:
            if model_name not in self._data:
                raise ModelNotFoundError(model_name)

            items = list(self._data[model_name].values())
            return items[skip:skip + limit]

    def update_item(
        self,
        model_name: str,
        item_id: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing item."""
        with self._lock:
            if model_name not in self._data:
                raise ModelNotFoundError(model_name)

            item_id = str(item_id)
            if item_id not in self._data[model_name]:
                raise ItemNotFoundError(model_name, item_id)

            # Preserve the ID
            item_data['id'] = item_id
            self._data[model_name][item_id] = item_data
            return item_data

    def delete_item(self, model_name: str, item_id: str) -> None:
        """Delete an item from the specified model."""
        with self._lock:
            if model_name not in self._data:
                raise ModelNotFoundError(model_name)

            item_id = str(item_id)
            if item_id not in self._data[model_name]:
                raise ItemNotFoundError(model_name, item_id)

            del self._data[model_name][item_id]

    def count_items(self, model_name: str) -> int:
        """Count the number of items in a model."""
        with self._lock:
            if model_name not in self._data:
                raise ModelNotFoundError(model_name)

            return len(self._data[model_name])


# Global data store instance
data_store = DataStore()
