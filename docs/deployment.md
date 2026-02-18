# Deployment & Execution

## Running Locally

### 1. Start Support Services
Ensure Docker containers are running:
```bash
docker-compose up -d
```

### 2. Start the Dashboard (Command Center)
The dashboard provides the UI to monitor the system.
```bash
python3 -m uvicorn src.dashboard.app:app --host 0.0.0.0 --port 8090 --reload
```
Access it at: **http://localhost:8090**

### 3. Run the Orchestrator
To start processing workflows:
```bash
python3 src/main.py
```

## Production Deployment

### Docker Deployment
You can containerize the entire specialized agent system.

`Dockerfile` is provided in the root. Build it:
```bash
docker build -t imperium-flow .
```

Run it:
```bash
docker run -d --name imperium -p 8090:8090 --env-file .env imperium-flow
```

### Scaling
- **Conductor**: Handles scaling of workflow state.
- **Workers**: You can run multiple instances of `src/main.py` (Agents) on different machines/containers to scale processing power. Conductor will dispatch tasks to available workers.
