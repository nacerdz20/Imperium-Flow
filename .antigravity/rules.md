# Imperium Flow - Project Rules

## 🎯 Project Identity
- **Name**: Imperium Flow
- **Type**: Agentic Workflow Orchestrator
- **Engine**: Conductor OSS + AI Agents
- **Author**: Eng. Zouaizia Nacer

## 📐 Architectural Standards

### 1. Code Rules
- **Max file length**: 300 lines
- **Max function length**: 50 lines
- **Naming**: snake_case for files/functions, PascalCase for classes
- **Documentation**: Google Docstrings mandatory
- **Logging**: Use `logging` module only, never `print()`

### 2. Agent Rules
- Every agent MUST inherit from `BaseAgent`
- Every agent MUST declare its `skills` explicitly
- Every agent MUST define `constraints` (operational limits)
- CodeBot: MUST follow Red-Green-Refactor TDD protocol
- TestBot: MUST achieve 90% coverage for core logic
- DesignBot: MUST pass WCAG AA accessibility validation
- IntegrationBot: MUST implement 3 error recovery strategies

### 3. Workflow Rules
- Every Workflow passes through 4 phases: Planning → Execution → Quality → Completion
- Parallel execution limited to 5 agents maximum
- Quality Gates are MANDATORY before completion
- Board approval required for complexity > 8

### 4. Imperium Protocol
- All inter-agent communication uses `ImperiumMessage`
- Messages have priority levels: LOW, MEDIUM, HIGH, CRITICAL
- CRITICAL messages bypass queue and execute immediately

### 5. Security Rules
- No secrets in code (use `.env` files)
- Validate all inputs at every entry point
- Log all sensitive operations
- Security scan required before any commit

## 🚫 Prohibitions
- No `print()` statements (use `logging`)
- No synchronous calls within async loops
- No direct modification of `.antigravity/` files
- No bypassing Quality Gates under any circumstance
- No hardcoded API keys or credentials
- No commit without passing Security Scan
