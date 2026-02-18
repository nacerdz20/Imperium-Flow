"""
Imperium Flow Dashboard - Real-time Monitoring.

FastAPI backend with WebSocket support for streaming
metrics, agent status, and workflow progress.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from src.core.metrics import ImperiumMetrics
from src.core.memory import ImperiumMemory

# ── App Setup ────────────────────────────────────────────

if HAS_FASTAPI:
    app = FastAPI(title="Imperium Flow Dashboard", version="1.0.0")
else:
    app = None

metrics = ImperiumMetrics()
memory = ImperiumMemory()


# ── WebSocket Manager ────────────────────────────────────

class ConnectionManager:
    """Manage active WebSocket connections."""

    def __init__(self):
        self.active: list = []

    async def connect(self, ws):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        message = json.dumps(data, default=str)
        for ws in self.active:
            try:
                await ws.send_text(message)
            except Exception:
                pass


manager = ConnectionManager()


# ── API Endpoints ────────────────────────────────────────

if HAS_FASTAPI:

    @app.get("/api/dashboard")
    async def get_dashboard():
        """Get current dashboard overview."""
        return metrics.get_dashboard()

    @app.get("/api/agents/{agent_name}/stats")
    async def get_agent_stats(agent_name: str):
        """Get statistics for a specific agent."""
        return metrics.get_agent_stats(agent_name)

    @app.get("/api/agents/{agent_name}/trend")
    async def get_agent_trend(agent_name: str, limit: int = 20):
        """Get performance trend for an agent."""
        return metrics.get_agent_trend(agent_name, limit)

    @app.get("/api/memory/stats")
    async def get_memory_stats():
        """Get memory statistics."""
        return memory.get_stats()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await manager.connect(websocket)
        try:
            while True:
                # Send dashboard update every 2 seconds
                dashboard = metrics.get_dashboard()
                dashboard["timestamp"] = datetime.now().isoformat()
                await websocket.send_json(dashboard)
                await asyncio.sleep(2)
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    @app.get("/", response_class=HTMLResponse)
    async def serve_dashboard():
        """Serve the dashboard HTML."""
        html_path = Path(__file__).parent / "index.html"
        if html_path.exists():
            return HTMLResponse(html_path.read_text())
        return HTMLResponse("<h1>Imperium Flow Dashboard</h1><p>UI not built yet</p>")
