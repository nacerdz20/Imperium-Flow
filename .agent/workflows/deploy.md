---
description: Deploy Imperium Flow to production (Docker Compose + Conductor)
---

# Deploy Workflow

## Prerequisites
- Docker and Docker Compose installed
- Environment variables configured in `.env`

## Steps

// turbo
1. Run tests before deployment: `cd "/home/nacer_00/Documents/cloude ai agent/Imperium-Flow" && python3 -m pytest tests/ -v --tb=short`

2. Verify Docker Compose config: `cd "/home/nacer_00/Documents/cloude ai agent/Imperium-Flow" && docker-compose config`

3. Build and start the stack: `cd "/home/nacer_00/Documents/cloude ai agent/Imperium-Flow" && docker-compose up -d --build`

4. Verify services are running: `docker-compose ps`

5. Check Conductor health: `curl -s http://localhost:8080/health | head -5`

6. Check application logs: `docker-compose logs --tail=20 imperium-flow`
