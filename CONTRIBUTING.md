# Contributing to Zouaizia Nacer Orchestrator

Thank you for your interest in contributing! We welcome contributions from the community to help make this agentic orchestrator even better.

## 🛠️ How to Contribute

### 1. Reporting Bugs
- Ensure the bug was not already reported.
- Open a new Issue using the **Bug Report** template.
- Include a minimal reproduction case.

### 2. Requesting Features
- Open a new Issue using the **Feature Request** template.
- Explain *why* this feature would be useful.

### 3. Pull Requests
- Fork the repository.
- Create a new branch: `git checkout -b feature/amazing-feature`.
- Make your changes.
- **Run Tests**: `python3 -m unittest discover tests`
- Commit your changes: `git commit -m 'feat: add amazing feature'`.
- Push to the branch: `git push origin feature/amazing-feature`.
- Open a Pull Request.

## 🧪 Development Guidelines

- **Code Style**: We follow PEP 8.
- **Testing**: All new features must include unit tests.
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/).

## 🤖 Agents & Skills
If you are adding a new Agent or Skill:
1.  Add the skill implementation in `src/superpowers/`.
2.  Register it in `src/core/skills_registry.py`.
3.  Update `src/config/worker_templates.py` if a new persona is needed.

Thank you for building the future of AI orchestration with us! 🚀
