# Getting Started with Imperium Flow

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for Conductor)
- Git

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/nacerdz20/Imperium-Flow.git
cd Imperium-Flow
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Start Conductor (Optional — for full orchestration)

```bash
docker-compose up -d
```

### 4. Run Tests

```bash
pytest tests/ -v --tb=short
```

### 5. Run the Application

```bash
PYTHONPATH=. python src/main.py
```

## Your First Workflow

```python
import asyncio
from src.core.orchestrator import ZNOrchestrator

async def main():
    orchestrator = ZNOrchestrator()
    
    context = await orchestrator.execute_workflow(
        name="my-first-feature",
        goal="Create a calculator module",
        initial_plan=[
            {"id": "t1", "agent_type": "code_worker", "description": "Implement calculator"},
        ],
        quality_gates=["complexity", "security"],
    )
    
    print(f"Status: {context.status}")
    print(f"Results: {context.results}")

asyncio.run(main())
```

## Using the Agents

### CodeBot — TDD Implementation

```python
from src.agents.codebot import CodeBot

bot = CodeBot()
# CodeBot follows TDD: Red → Green → Refactor → Security
```

### Board of Directors — Review

```python
import asyncio
from src.board.directors import BoardOfDirectors, WorkflowProposal

async def review():
    board = BoardOfDirectors()
    proposal = WorkflowProposal(
        workflow_type="feature",
        complexity=7,
        agents_required=["code_worker", "test_worker"],
    )
    decision = await board.review_workflow(proposal)
    print(f"Approved: {decision.approved}")
    print(f"Conditions: {decision.conditions}")

asyncio.run(review())
```

### Memory — Knowledge Store

```python
from src.core.memory import ImperiumMemory

memory = ImperiumMemory(persistence_path="./data/memory.json")
memory.store_memory("codebot", "patterns", "retry", {"strategy": "exponential"}, 0.95)

# Recall later
result = memory.recall("codebot", "patterns", "retry")
```

## Project Structure

```
Imperium-Flow/
├── src/
│   ├── agents/          # Specialized AI agents
│   ├── board/           # Board of Directors
│   ├── core/            # Orchestrator, Protocol, Memory, Metrics
│   ├── superpowers/     # Agent skills (TDD, Security, etc.)
│   └── main.py          # Entry point
├── tests/               # 142+ tests
├── config/              # Configuration files
├── docs/                # Documentation
├── .agent/              # Antigravity IDE definitions
└── .github/workflows/   # CI/CD pipelines
```

## Next Steps

- Read the [Architecture Guide](architecture.md)
- Explore the [Agent Definitions](../.agent/)
- Check out the [API Reference](../src/)
