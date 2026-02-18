# Contributing to Imperium Flow

Thank you for your interest in contributing! We welcome all types of contributions.

## Code of Conduct

Please be respectful and professional in all interactions.

## Development Workflow

1.  **Fork** the repository.
2.  **Clone** your fork locally.
3.  **Create a branch** for your feature: `git checkout -b feature/amazing-feature`.
4.  **Install dev dependencies**: `pip install -r requirements-dev.txt` (if available) or `pip install pytest black flake8`.
5.  **Make your changes**.
6.  **Run Tests**: `pytest tests/`. Ensure everything passes!
7.  **Commit**: Use conventional commits (e.g., `feat: add new agent`).
8.  **Push** to your fork.
9.  **Open a Pull Request**.

## Adding a New Agent

To add a new agent type:
1.  Create a new file in `src/agents/`.
2.  Inherit from the base `Agent` class.
3.  Implement the required methods (`execute_task`, etc.).
4.  Register the agent in `src/core/agent_manager.py`.
5.  Add unit tests in `tests/unit/`.

## Reporting Bugs

Please use the GitHub Issue Tracker and include:
- Reproducible steps.
- Expected vs. Actual behavior.
- Logs or screenshots.
