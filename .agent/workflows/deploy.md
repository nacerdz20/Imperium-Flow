---
description: Deploy Imperium Flow to production (Docker Compose + Conductor)
---

# Deploy Workflow

## Steps

// turbo-all

1. Verify all tests pass before deploying:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/ -v
```

2. Build and start Docker containers:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && docker compose up -d
```

3. Verify Conductor Server is running:
```bash
curl -s http://localhost:8080/api/health | python3 -m json.tool
```

4. Verify Conductor UI is accessible:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000
```

5. Start the Imperium Flow orchestrator:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m src.main
```
