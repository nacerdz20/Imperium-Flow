---
description: Implement a new feature using Test-Driven Development
---

# TDD Workflow

## Steps

1. **Analyze requirements** — understand the feature and define acceptance criteria
// turbo
2. Run existing tests to establish baseline: `cd "/home/nacer_00/Documents/cloude ai agent/Imperium-Flow" && python3 -m pytest tests/ -v --tb=short`

3. **RED Phase** — write failing test first
   - Create test file in `tests/unit/`
   - Define test functions covering: happy path, edge cases, error cases
   - Use Arrange-Act-Assert pattern

// turbo
4. Run tests to confirm they fail: `cd "/home/nacer_00/Documents/cloude ai agent/Imperium-Flow" && python3 -m pytest tests/ -v --tb=short`

5. **GREEN Phase** — write minimum code to pass
   - Implement in `src/` matching the test expectations
   - Do NOT add features not covered by tests

// turbo
6. Run tests to confirm they pass: `cd "/home/nacer_00/Documents/cloude ai agent/Imperium-Flow" && python3 -m pytest tests/ -v --tb=short`

7. **REFACTOR Phase** — improve quality
   - Clean up duplication, improve naming
   - Add type hints and docstrings
   - Max complexity: 10, max file length: 300 lines

// turbo
8. Run tests to confirm still green: `cd "/home/nacer_00/Documents/cloude ai agent/Imperium-Flow" && python3 -m pytest tests/ -v --tb=short`

9. **Security scan** — check for vulnerabilities in new code

10. **Commit** using conventional commits format
