---
description: Create a new feature using the Imperium Flow TDD workflow
---

# New Feature Workflow

## Steps

1. Create a branch for the feature:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && git checkout -b feature/<feature-name>
```

2. Write the failing test first (RED phase):
   - Create `tests/test_<feature>.py`
   - Write tests covering: happy path, edge cases, error cases
   - Run and verify they FAIL:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/test_<feature>.py -v
```

3. Write the minimal implementation (GREEN phase):
   - Create `src/<module>/<feature>.py`
   - Write the MINIMUM code to make tests pass
   - Run and verify they PASS:
// turbo
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/test_<feature>.py -v
```

4. Refactor the code (REFACTOR phase):
   - Improve naming, add type hints, add docstrings
   - Verify tests still pass:
// turbo
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/test_<feature>.py -v
```

5. Run security scan:
// turbo
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -c "from src.superpowers.security import SecurityScanner; s = SecurityScanner(); print(s.scan_file('src/<module>/<feature>.py'))"
```

6. Run full test suite to ensure no regressions:
// turbo
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/ -v
```

7. Commit with Conventional Commit message:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && git add -A && git commit -m "feat(<scope>): <description>"
```
