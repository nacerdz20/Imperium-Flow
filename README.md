# Imperium Flow ⚡

![Imperium Flow Dashboard](/home/nacer_00/.gemini/antigravity/brain/71a5d329-8239-4315-a7ae-df51c16e061c/dashboard_top_1771424721397.png)

> **Agentic Workflow Orchestrator & Command Center**
>
> An advanced system for orchestrating AI agents in complex workflows, featuring a real-time monitoring dashboard, TDD enforcement, and self-healing capabilities.

---

## 🌟 Key Features

- **🤖 Multi-Agent Orchestration**: Coordinate specialized agents (CodeBot, TestBot, DesignBot, IntegrationBot) to solve complex tasks.
- **📊 Professional Dashboard**: Real-time monitoring with Dark/Light mode, mobile responsiveness, and live WebSocket updates.
- **🔄 Resilient Workflows**: Built-in retry mechanisms, deadlock detection, and self-healing logic.
- **🧪 TDD at Core**: `TDDExpert` module ensures "Red-Green-Refactor" cycles for high code quality.
- **🧠 Shared Memory**: Persistent knowledge store allowing agents to learn from past executions.
- **📱 Mobile First**: Fully responsive UI adaptable to any device size.

---

## 📸 Screenshots

### Command Center (Desktop)
A comprehensive view of system health, active tasks, and agent performance.

![Desktop Dashboard](/home/nacer_00/.gemini/antigravity/brain/71a5d329-8239-4315-a7ae-df51c16e061c/dashboard_top_1771424721397.png)

### Mobile & Light Mode
Optimized for on-the-go monitoring with full theme support.

| Mobile View | Light Mode |
|-------------|------------|
| ![Mobile View](/home/nacer_00/.gemini/antigravity/brain/71a5d329-8239-4315-a7ae-df51c16e061c/dashboard_mobile_view_final_1771425229716.png) | ![Light Mode](/home/nacer_00/.gemini/antigravity/brain/71a5d329-8239-4315-a7ae-df51c16e061c/dashboard_light_mode_1771425173962.png) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- `pip`

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Startouf/Imperium-Flow.git
   cd Imperium-Flow
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn  # For the dashboard
   ```

---

## 🖥️ Running the Dashboard

Launch the Imperium Command Center to monitor your agents in real-time.

```bash
# Start the backend server
python3 -m uvicorn src.dashboard.app:app --host 0.0.0.0 --port 8090 --reload
```

Open your browser at: **[http://localhost:8090](http://localhost:8090)**

> **Note:** The dashboard uses WebSocket for live updates. Ensure you have `uvicorn[standard]` installed for best performance.

---

## 🧪 Running Tests

Imperium Flow maintains high code coverage (>94%) to ensure reliability.

```bash
# Run all unit tests
pytest tests/unit

# Run specific test file
pytest tests/unit/test_orchestrator.py

# Check coverage
pytest --cov=src tests/unit
```

---

## 🏗️ Architecture Overview

- **`src/core`**: The brain of the system. Contains the `Orchestrator`, `AgentManager`, `Memory`, and `WorkflowEngine`.
- **`src/agents`**: Specialized AI agent implementations (`CodeBot`, `TestBot`, etc.).
- **`src/dashboard`**: FastAPI backend and HTML/JS frontend for the Command Center.
- **`src/superpowers`**: Pluggable capabilities like `TDDExpert` and `SmartPlanner`.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ by [Eng. Zouaizia Nacer](https://www.zouaizianacer.top/)**
