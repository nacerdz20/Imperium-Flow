# Imperium Flow - Antigravity Rules

## 🎯 Project Identity
- **Name**: Imperium Flow
- **Type**: Agentic Workflow Orchestrator
- **Engine**: Conductor OSS + AI Agents
- **Author**: Eng. Zouaizia Nacer
- **Repository**: https://github.com/nacerdz20/Imperium-Flow

## 📐 Core Principles

### 1. Agent-First Development
- كل ميزة تبدأ بتعريف الوكيل (`@agent define`)
- كل وكيل يجب أن يكون له Skills واضحة
- كل وكيل يجب أن يمر بـ Board Review

### 2. Test-Driven Development
- لا كود بدون اختبار (TDD Red-Green-Refactor)
- Coverage target: 90%+ for business logic
- الاختبارات مستقلة وحتمية

### 3. Workflow-Driven
- لا تنفيذ بدون Workflow معرف
- كل Workflow يمر بـ Board Review + Quality Gates
- Smart Loop: Plan → Execute → Fail → Fix → Retry

### 4. Memory-Aware
- تخزين كل قرار في Imperium Memory
- استرجاع الأنماط الناجحة
- تتبع Success Rate

### 5. Metrics-Driven
- قياس كل شيء (execution time, success rate, errors)
- Dashboard فوري
- تحسين بناءً على البيانات

## 🚫 Hard Constraints
- Max 300 lines per file
- Max 50 lines per function
- 90% test coverage for core logic
- No commit without security scan
- No bypassing Quality Gates
- No hardcoded secrets
- Conventional Commits format
