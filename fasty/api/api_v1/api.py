"""
Fasty API Version 1 Router

This module defines the main router for the v1 API, incorporating all
resource-specific routers.
"""
from fastapi import APIRouter

from fasty.core.config import settings
from fasty.api.endpoints import base

api_router = APIRouter(prefix=settings.API_PREFIX)

# Include all endpoint routers
api_router.include_router(base.router, tags=["base"])
