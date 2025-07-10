"""
FastAPI server for exposing UIStateManager state via REST API and Server-Sent Events.
Provides real-time state updates to HTML5 clients using the best available facilities.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from .llm_logging import get_llm_logger
from .ui_state_manager import UIStateManager

# Set up logging
logger = logging.getLogger(__name__)
llm_logger = get_llm_logger("state_api")

# Global state manager instance
state_manager: Optional[UIStateManager] = None
connected_clients: List[asyncio.Queue] = []


class StateUpdate(BaseModel):
    """Model for state updates sent to clients."""

    timestamp: str
    type: str  # 'state_change', 'log_entry', 'summary'
    data: Dict[str, Any]


class LogEntry(BaseModel):
    """Model for log entries."""

    timestamp: str
    level: str
    message: str
    context: Dict[str, Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global state_manager

    # Initialize state manager
    state_manager = UIStateManager()
    llm_logger.info("State API server started")

    yield

    # Cleanup
    llm_logger.info("State API server shutting down")


# Create FastAPI app
app = FastAPI(
    title="UIStateManager API",
    description="Real-time state management API for SVG Image Generator",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for HTML5 client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_state_manager() -> UIStateManager:
    """Get the global state manager instance."""
    if state_manager is None:
        raise HTTPException(status_code=500, detail="State manager not initialized")
    return state_manager


async def notify_clients(update: StateUpdate):
    """Notify all connected clients of a state update."""
    if connected_clients:
        # Remove disconnected clients
        connected_clients[:] = [
            client for client in connected_clients if not client.full()
        ]

        # Send update to all connected clients
        for client in connected_clients:
            try:
                await client.put(update.dict())
            except Exception as e:
                logger.warning(f"Failed to send update to client: {e}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HTML dashboard."""
    with open("ui_observability_demo.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/state")
async def get_state():
    """Get current state."""
    sm = get_state_manager()
    return {
        "current_step": sm.get_current_step(),
        "form_data": sm.get_form_data(),
        "validation_errors": sm.get_validation_errors(),
        "loading_states": sm.get_all_state().get("loading_states", {}),
        "user_context": sm.get("user_context"),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/state/step")
async def set_step(data: Dict[str, Any]):
    """Set current step."""
    step = data.get("step")
    if not step:
        raise HTTPException(status_code=400, detail="step parameter is required")

    sm = get_state_manager()
    sm.set_current_step(step)

    update = StateUpdate(
        timestamp=datetime.now().isoformat(),
        type="state_change",
        data={"action": "set_step", "step": step},
    )
    await notify_clients(update)

    return {"status": "success", "step": step}


@app.post("/api/state/form")
async def update_form_data(form_data: Dict[str, Any]):
    """Update form data."""
    sm = get_state_manager()
    sm.set_form_data(form_data)

    update = StateUpdate(
        timestamp=datetime.now().isoformat(),
        type="state_change",
        data={"action": "update_form_data", "form_data": form_data},
    )
    await notify_clients(update)

    return {"status": "success", "form_data": form_data}


@app.post("/api/state/loading")
async def set_loading_state(data: Dict[str, Any]):
    """Set loading state for a component."""
    component = data.get("component")
    is_loading = data.get("is_loading")

    if component is None or is_loading is None:
        raise HTTPException(
            status_code=400, detail="component and is_loading parameters are required"
        )

    sm = get_state_manager()
    sm.set_loading_state(component, is_loading)

    update = StateUpdate(
        timestamp=datetime.now().isoformat(),
        type="state_change",
        data={
            "action": "set_loading_state",
            "component": component,
            "is_loading": is_loading,
        },
    )
    await notify_clients(update)

    return {"status": "success", "component": component, "is_loading": is_loading}


@app.post("/api/state/validation-error")
async def add_validation_error(data: Dict[str, Any]):
    """Add validation error."""
    field = data.get("field")
    message = data.get("message")

    if not field or not message:
        raise HTTPException(
            status_code=400, detail="field and message parameters are required"
        )

    sm = get_state_manager()
    sm.set_validation_error(field, message)

    update = StateUpdate(
        timestamp=datetime.now().isoformat(),
        type="state_change",
        data={"action": "add_validation_error", "field": field, "message": message},
    )
    await notify_clients(update)

    return {"status": "success", "field": field, "message": message}


@app.delete("/api/state/validation-errors")
async def clear_validation_errors():
    """Clear all validation errors."""
    sm = get_state_manager()
    sm.clear_validation_errors()

    update = StateUpdate(
        timestamp=datetime.now().isoformat(),
        type="state_change",
        data={"action": "clear_validation_errors"},
    )
    await notify_clients(update)

    return {"status": "success"}


@app.post("/api/state/reset")
async def reset_state():
    """Reset all state to defaults."""
    sm = get_state_manager()
    sm.reset()

    update = StateUpdate(
        timestamp=datetime.now().isoformat(),
        type="state_change",
        data={"action": "reset_state"},
    )
    await notify_clients(update)

    return {"status": "success"}


@app.get("/api/logs")
async def get_logs():
    """Get recent logs (placeholder - would need to capture logs from UIStateManager)."""
    return {
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": "API endpoint accessed",
                "context": {"endpoint": "/api/logs"},
            }
        ]
    }


@app.get("/api/events")
async def events():
    """Server-Sent Events endpoint for real-time updates."""

    async def event_generator():
        # Create a queue for this client
        client_queue = asyncio.Queue()
        connected_clients.append(client_queue)

        try:
            while True:
                # Wait for updates
                update = await client_queue.get()

                # Send SSE data
                yield f"data: {json.dumps(update)}\n\n"

        except asyncio.CancelledError:
            # Client disconnected
            if client_queue in connected_clients:
                connected_clients.remove(client_queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the FastAPI server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
