"""
Imperium Flow Dashboard - Real-time Monitoring.

FastAPI backend with WebSocket support for streaming
metrics, agent status, and workflow progress.
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from src.core.metrics import ImperiumMetrics
from src.core.memory import ImperiumMemory

# ── App Setup ────────────────────────────────────────────

if HAS_FASTAPI:
    app = FastAPI(title="Imperium Flow Dashboard", version="2.1.0")
    
    # CORS for mobile/external access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
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


# ── Demo Data Seeder ─────────────────────────────────────

def _seed_demo_data():
    """Seed realistic demo data for visualization."""
    agents = ["CodeBot", "TestBot", "DesignBot", "IntegrationBot"]
    task_types = ["code_review", "testing", "ui_design", "api_integration",
                  "refactoring", "debugging", "documentation", "deployment"]
    errors = [
        "TimeoutError: LLM response exceeded 30s",
        "AssertionError: Test assertion failed",
        "ConnectionError: API endpoint unreachable",
        "SyntaxError: Invalid generated code",
        "ImportError: Missing dependency",
    ]

    for i in range(85):
        agent = random.choice(agents)
        task_type = random.choice(task_types)
        task_id = f"task-{i+1:04d}"
        metrics.start_task(task_id, agent, task_type)
        success = random.random() > 0.12
        error = None if success else random.choice(errors)
        metrics.complete_task(task_id, success=success, error=error)

    # Store some memory entries
    patterns = [
        ("CodeBot", "refactoring", "extract_method", 0.96),
        ("CodeBot", "refactoring", "rename_variable", 0.92),
        ("CodeBot", "debugging", "stack_trace_analysis", 0.88),
        ("TestBot", "testing", "boundary_testing", 0.94),
        ("TestBot", "testing", "mock_strategy", 0.91),
        ("DesignBot", "ui_patterns", "responsive_grid", 0.95),
        ("DesignBot", "ui_patterns", "dark_mode_palette", 0.89),
        ("IntegrationBot", "api_patterns", "retry_with_backoff", 0.93),
        ("IntegrationBot", "api_patterns", "circuit_breaker", 0.87),
        ("CodeBot", "security", "input_validation", 0.98),
        ("TestBot", "testing", "snapshot_testing", 0.85),
        ("CodeBot", "performance", "lazy_loading", 0.90),
    ]
    for agent, cat, key, rate in patterns:
        memory.store_memory(agent, cat, key, {
            "description": f"{key.replace('_', ' ').title()} pattern",
            "usage_contexts": ["general"],
        }, success_rate=rate)

    # Keep some active tasks for "live" feel
    for i in range(4):
        agent = agents[i]
        metrics.start_task(f"active-{i+1}", agent, random.choice(task_types))


_demo_seeded = False


# ── API Endpoints ────────────────────────────────────────

if HAS_FASTAPI:

    @app.on_event("startup")
    async def startup():
        global _demo_seeded
        if not _demo_seeded:
            _seed_demo_data()
            _demo_seeded = True

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

    @app.get("/api/system")
    async def get_system_info():
        """Get system-level info."""
        return {
            "name": "Imperium Flow",
            "version": "2.1.0",
            "status": "operational",
            "uptime": datetime.now().isoformat(),
            "agents_registered": 4,
            "superpowers_loaded": 8,
            "board_members": 5,
        }

    @app.get("/api/mobile/summary")
    async def mobile_summary():
        """Lightweight endpoint for mobile clients."""
        dashboard = metrics.get_dashboard()
        return {
            "kpi": {
                "total": dashboard["overview"]["total_tasks"],
                "success_rate": dashboard["overview"]["overall_success_rate"],
                "active": dashboard["overview"]["active_tasks"],
                "failures": dashboard["overview"]["total_failures"]
            },
            "agents": [
                {
                    "name": name,
                    "status": "active" if stats.get("success_rate", 0) > 90 else "warning",
                    "rate": stats.get("success_rate", 0)
                }
                for name, stats in dashboard["agents"].items()
            ],
            "timestamp": datetime.now().isoformat()
        }

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await manager.connect(websocket)
        client_type = websocket.headers.get("x-client-type", "desktop")
        
        try:
            while True:
                # Optimized payload for mobile could be implemented here
                # For now we send full data but control frequency
                dashboard = metrics.get_dashboard()
                dashboard["timestamp"] = datetime.now().isoformat()
                
                if client_type == "mobile":
                     # Send lightweight data for mobile if needed, 
                     # but utilizing existing structure for compatibility
                     pass
                else:
                    dashboard["memory"] = memory.get_stats()
                
                await websocket.send_json(dashboard)
                
                # Slower refresh for mobile to save battery/data
                await asyncio.sleep(2 if client_type == "mobile" else 1)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    @app.get("/", response_class=HTMLResponse)
    async def serve_dashboard():
        """Serve the dashboard HTML."""
        html_path = Path(__file__).parent / "index.html"
        if html_path.exists():
            return HTMLResponse(html_path.read_text())
        return HTMLResponse("<h1>Imperium Flow Dashboard</h1><p>UI not built yet</p>")
