# API Reference

Imperium Flow exposes a RESTful API via FastAPI, primarily used by the Dashboard and external integrations.

## Accessing Interactive Documentation

When the application is running (locally or in production), you can access the automatically generated interactive documentation:

- **Swagger UI**: [http://localhost:8090/docs](http://localhost:8090/docs)
- **ReDoc**: [http://localhost:8090/redoc](http://localhost:8090/redoc)

## Key Endpoints

### System Information

- `GET /api/system`: Returns current system status, uptime, and version.

### Dashboard Stats

- `GET /api/dashboard`: Returns aggregate metrics for the dashboard overview.
- `GET /api/mobile/summary`: Optimized lightweight JSON for mobile apps.

### Agent Metrics

- `GET /api/agents/{agent_name}/stats`: detailed performance stats for a specific agent.
- `GET /api/agents/{agent_name}/trend`: Historical trend data for visualizations.

### Memory & Learning

- `GET /api/memory/stats`: Returns memory distribution and usage statistics.

## WebSocket Real-time Feed

- `WS /ws`: Connect to this endpoint to receive real-time JSON updates.
    - **Header**: `x-client-type: mobile` (optional) to receive optimized mobile payloads.
