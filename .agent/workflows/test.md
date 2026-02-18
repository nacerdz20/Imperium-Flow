---
description: Run the Imperium Flow test suite
---

# Test Workflow

## Steps

// turbo-all

1. Run the full test suite with verbose output:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/ -v --tb=short
```

2. Run tests with coverage report:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/ --cov=src --cov-report=term-missing
```

3. Run only agent tests:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/test_agents.py -v
```

4. Run only board tests:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/test_board.py -v
```

5. Run only quality gate tests:
```bash
cd /home/nacer_00/Documents/cloude\ ai\ agent/zouaizia-nacer-orchestrator && python3 -m pytest tests/test_quality_gates.py -v
```
