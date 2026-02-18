# System Architecture

Imperium Flow is designed as a modular, event-driven system leveraging the **Agentic Workflow** pattern. It separates orchestration logic from agent execution, ensuring scalability and resilience.

## High-Level Overview

The system consists of three main layers:
1. **Orchestration Layer**: Manages workflow state and task distribution (Conductor).
2. **Agent Layer**: Specialized workers that execute tasks (CodeBot, TestBot, etc.).
3. **Interface Layer**: Real-time dashboard and API for monitoring and control.

```mermaid
graph TD
    User[User / External System] -->|API Request| API[FastAPI Gateway]
    User -->|WebSocket| Dashboard[Command Center]
    
    API -->|Start Workflow| Conductor[Conductor Server]
    
    subgraph "Imperium Core"
        Orchestrator[Orchestrator Service]
        exclude[Self-Healing Module]
        Memory[Shared Memory Store]
    end
    
    Conductor -->|Poll Tasks| Orchestrator
    Orchestrator -->|Dispatch| Agents
    
    subgraph "Agent Swarm"
        CB[CodeBot]
        TB[TestBot]
        DB[DesignBot]
        IB[IntegrationBot]
    end
    
    Agents --> CB & TB & DB & IB
    
    CB & TB & DB & IB -->|Read/Write| Memory
    CB & TB & DB & IB -->|Update Status| Conductor
    
    Orchestrator -->|Stream Events| Dashboard
```

## Core Components

### 1. Orchestrator (`src.core.orchestrator`)
The central brain that polls Conductor for tasks and delegates them to the appropriate agents. It implements the **Board of Directors** pattern, where different "personalities" (CTO, CSO, Product Owner) review decisions.

### 2. Agents (`src.agents`)
Autonomous units with specific "Superpowers".
- **CodeBot**: Generates and refactors code using LLMs.
- **TestBot**: Writes and executes TDD cycles.
- **DesignBot**: Handles UI/UX tasks.
- **IntegrationBot**: Manages API integrations and deployments.

### 3. Shared Memory (`src.core.memory`)
A semantic knowledge store that allows agents to share context.
- **Short-term**: Current workflow context.
- **Long-term**: Learned patterns and successful strategies.

### 4. Self-Healing (`src.core.maintenance`)
Monitors for deadlocks, timeouts, and failures. It can trigger retry strategies or escalate to human intervention.

## Workflow Execution Flow

A typical "Feature Implementation" workflow follows this Red-Green-Refactor cycle:

```mermaid
sequenceDiagram
    participant User
    participant Orch as Orchestrator
    participant CB as CodeBot
    participant TB as TestBot
    participant Mem as Memory
    
    User->>Orch: Start Feature Workflow
    Orch->>TB: Task: Write Failing Test in TDDExpert
    TB->>Mem: Store Test Context
    TB-->>Orch: Test Created (Red)
    
    Orch->>CB: Task: Implement Feature
    CB->>Mem: Retrieve Test Context
    CB->>CB: Generate Code
    CB-->>Orch: Implementation Done
    
    Orch->>TB: Task: Run Tests
    TB->>TB: Execute Pytest
    alt Tests Pass
        TB-->>Orch: Success (Green)
        Orch->>CB: Task: Refactor
    else Tests Fail
        TB-->>Orch: Failure
        Orch->>CB: Task: Fix Code
    end
```

## Directory Structure

```plaintext
Imperium-Flow/
├── src/
│   ├── agents/         # Specific agent implementations
│   ├── core/           # Core logic (Orchestrator, Memory, Config)
│   ├── dashboard/      # FastAPI + HTML/JS Dashboard
│   ├── superpowers/    # Pluggable capabilities (TDD, Planning)
│   └── main.py         # Entry point
├── tests/              # Unit and Integration tests
├── docs/               # Documentation
└── ...
```

## Tech Stack

- **Language**: Python 3.9+
- **Orchestration**: Netflix Conductor (via `conductor-python`)
- **Web Framework**: FastAPI (Dashboard & API)
- **Frontend**: HTML5, TailwindCSS, Chart.js, WebSockets
- **Containerization**: Docker & Docker Compose
