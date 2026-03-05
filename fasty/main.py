"""
Fasty - Dynamic REST API Generator

This is the main entry point for the Fasty application.
It initializes the FastAPI application and sets up all the routes.
"""
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fasty.core.config import settings, get_settings
from fasty.core.exceptions import FastyError, http_exception_handler
from fasty.core.store import data_store
from fasty.api.api_v1.api import api_router
from fasty.api.endpoints.base import register_model_endpoints
from fasty.utils.yaml_loader import load_and_validate_config


def reload_routes(app: FastAPI):
    """Reload the YAML configuration and update the routes."""
    try:
        # Load new configuration
        config = load_and_validate_config(settings.CONFIG_FILE)

        # In a real app, we'd want a more sophisticated route swap,
        # but for this mock server we'll just re-register or update the store.
        # Since the store is global, updating its models/data affects existing routes.
        for model_name, model_config in config.models.items():
            data_store.register_model(model_config)
            if model_config.data:
                for item in model_config.data:
                    data_store.create_item(model_name, item)

        print(f"Refreshed configuration from {settings.CONFIG_FILE}")
    except Exception as e:
        print(f"Error reloading configuration: {e}")


class YAMLFileEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self._last_modified = 0

    def on_modified(self, event):
        current_time = time.time()
        if current_time - self._last_modified < 0.5:
            return
        self._last_modified = current_time

        if event.src_path == str(Path(settings.CONFIG_FILE).absolute()):
            self.callback()


def start_file_watcher():
    """Start the watchdog observer."""
    event_handler = YAMLFileEventHandler(lambda: reload_routes(app))
    observer = PollingObserver()
    observer.schedule(event_handler, path=os.path.dirname(
        os.path.abspath(settings.CONFIG_FILE)), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A dynamic REST API generator using YAML configuration",
        version=settings.VERSION,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    app.add_exception_handler(FastyError, http_exception_handler)

    # Load configuration
    try:
        config = load_and_validate_config(settings.CONFIG_FILE)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Register models and load initial data
    for model_name, model_config in config.models.items():
        data_store.register_model(model_config)

        # Register dynamic CRUD endpoints for this model
        register_model_endpoints(api_router, model_name)

        # Load initial data if provided
        if model_config.data:
            for item in model_config.data:
                data_store.create_item(model_name, item)

    # Include API router
    app.include_router(api_router)

    # Register startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Initialize the application on startup."""
        # Start file watcher in a background thread
        watcher_thread = threading.Thread(
            target=start_file_watcher, daemon=True)
        watcher_thread.start()

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}

    # Root endpoint
    @app.get("/")
    async def root() -> Dict[str, str]:
        """Root endpoint with API information."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
        }

    return app


# Create the application
app = create_app()


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description='Run Fasty API server')
    parser.add_argument('--https', action='store_true', help='Enable HTTPS')
    parser.add_argument('--port', type=int,
                        default=settings.PORT, help='Port to run on')
    args = parser.parse_args()

    uvicorn_kwargs = {
        "app": "fasty.main:app",
        "host": settings.HOST,
        "port": args.port,
        "reload": settings.DEBUG,
        "log_level": "info" if settings.DEBUG else "warning",
    }

    if args.https:
        cert_path = settings.CERTS_DIR / "cert.pem"
        key_path = settings.CERTS_DIR / "key.pem"
        if not cert_path.exists() or not key_path.exists():
            print(
                f"Certificates not found at {settings.CERTS_DIR}. Please generate them first.")
            sys.exit(1)
        uvicorn_kwargs["ssl_keyfile"] = str(key_path)
        uvicorn_kwargs["ssl_certfile"] = str(cert_path)

    uvicorn.run(**uvicorn_kwargs)
