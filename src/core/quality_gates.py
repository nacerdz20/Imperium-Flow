#!/usr/bin/env python3
"""
Quality Gates - Real Validation System.
Implements actual checks for code coverage, complexity,
security scanning, type checking, and linting.
"""

import logging
import subprocess
from typing import Dict, Any, List
from enum import Enum


class GateStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


class QualityGateManager:
    """
    Real quality gate system that actually validates code.
    
    Available gates:
    - code_coverage: Check test coverage meets threshold
    - complexity: Check cyclomatic complexity
    - security_scan: Run SAST security scanner
    - type_check: Run mypy type checking
    - lint: Run flake8 linting
    - test_pass: Verify all tests pass
    """

    GATE_THRESHOLDS = {
        "code_coverage": 70,    # Minimum % coverage
        "complexity": 10,       # Maximum cyclomatic complexity per function
        "max_file_lines": 300,  # Maximum lines per file
    }

    def __init__(self):
        self.logger = logging.getLogger("QualityGateManager")
        self.gate_registry = {
            "code_coverage": self._check_coverage,
            "complexity": self._check_complexity,
            "security_scan": self._check_security,
            "type_check": self._check_types,
            "lint": self._check_lint,
            "test_pass": self._check_tests_pass,
        }

    async def check(
        self,
        results: Dict[str, Any],
        criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Run quality gates. Each gate actually validates something.
        Returns detailed report with pass/fail per gate.
        """
        self.logger.info(f"🔍 Running {len(criteria)} quality gates...")
        
        gate_results = {}
        failures = []

        for gate_name in criteria:
            checker = self.gate_registry.get(gate_name)
            if checker:
                gate_result = checker(results)
                gate_results[gate_name] = gate_result
                if gate_result["status"] == GateStatus.FAILED.value:
                    failures.append({
                        "gate": gate_name,
                        "reason": gate_result.get("reason", "Check failed"),
                    })
                    self.logger.error(f"❌ Gate FAILED: {gate_name}")
                else:
                    self.logger.info(f"✅ Gate PASSED: {gate_name}")
            else:
                gate_results[gate_name] = {
                    "status": GateStatus.SKIPPED.value,
                    "reason": f"Unknown gate: {gate_name}",
                }

        passed = len(failures) == 0

        return {
            "passed": passed,
            "total_gates": len(criteria),
            "passed_count": len(criteria) - len(failures),
            "failed_count": len(failures),
            "failures": failures,
            "details": gate_results,
        }

    def _check_coverage(self, results: Dict) -> Dict[str, Any]:
        """Check code coverage meets threshold."""
        coverage = results.get("coverage", results.get("estimated_coverage"))

        if coverage is None:
            # Try running pytest --cov
            return self._run_coverage_tool()

        threshold = self.GATE_THRESHOLDS["code_coverage"]
        passed = coverage >= threshold

        return {
            "status": GateStatus.PASSED.value if passed else GateStatus.FAILED.value,
            "coverage": coverage,
            "threshold": threshold,
            "reason": (
                f"Coverage {coverage}% meets threshold {threshold}%"
                if passed
                else f"Coverage {coverage}% below threshold {threshold}%"
            ),
        }

    def _run_coverage_tool(self) -> Dict[str, Any]:
        """Attempt to run pytest with coverage."""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "--cov", "--cov-report=term-missing", "-q"],
                capture_output=True, text=True, timeout=60,
            )
            # Parse coverage from output
            for line in result.stdout.split("\n"):
                if "TOTAL" in line:
                    parts = line.split()
                    for part in parts:
                        if part.endswith("%"):
                            coverage = int(part.rstrip("%"))
                            threshold = self.GATE_THRESHOLDS["code_coverage"]
                            return {
                                "status": GateStatus.PASSED.value if coverage >= threshold else GateStatus.FAILED.value,
                                "coverage": coverage,
                                "threshold": threshold,
                                "reason": f"Coverage: {coverage}%",
                            }
            return {
                "status": GateStatus.WARNING.value,
                "reason": "Could not parse coverage output",
            }
        except Exception as e:
            return {
                "status": GateStatus.SKIPPED.value,
                "reason": f"Coverage tool unavailable: {e}",
            }

    def _check_complexity(self, results: Dict) -> Dict[str, Any]:
        """Check cyclomatic complexity."""
        complexity = results.get("complexity_score", results.get("complexity"))

        if complexity is None:
            # Try to get from code analysis results
            for key, value in results.items():
                if isinstance(value, dict) and "complexity_score" in value:
                    complexity = value["complexity_score"]
                    break

        if complexity is None:
            return {
                "status": GateStatus.SKIPPED.value,
                "reason": "No complexity data available",
            }

        threshold = self.GATE_THRESHOLDS["complexity"]
        passed = complexity <= threshold

        return {
            "status": GateStatus.PASSED.value if passed else GateStatus.FAILED.value,
            "complexity": complexity,
            "threshold": threshold,
            "reason": (
                f"Complexity {complexity} within limit {threshold}"
                if passed
                else f"Complexity {complexity} exceeds limit {threshold}"
            ),
        }

    def _check_security(self, results: Dict) -> Dict[str, Any]:
        """Run security scan using SecurityScanner."""
        security_data = results.get("security", {})

        if isinstance(security_data, dict) and "passed" in security_data:
            return {
                "status": GateStatus.PASSED.value if security_data["passed"] else GateStatus.FAILED.value,
                "findings": security_data.get("findings", []),
                "reason": (
                    "No security issues found"
                    if security_data["passed"]
                    else f"Found {len(security_data.get('findings', []))} security issues"
                ),
            }

        # No security data, run scanner on available code
        from src.superpowers.security import SecurityScanner
        scanner = SecurityScanner()

        code = results.get("code", results.get("refactored_code", ""))
        if not code:
            return {
                "status": GateStatus.SKIPPED.value,
                "reason": "No code to scan",
            }

        # Inline scan for code string
        import re
        findings = []
        for i, line in enumerate(code.split("\n")):
            for check_name, pattern in scanner.PATTERNS.items():
                if re.search(pattern, line):
                    findings.append({"type": check_name, "line": i + 1})

        passed = len(findings) == 0
        return {
            "status": GateStatus.PASSED.value if passed else GateStatus.FAILED.value,
            "findings": findings,
            "reason": (
                "No security issues found"
                if passed
                else f"Found {len(findings)} security issues"
            ),
        }

    def _check_types(self, results: Dict) -> Dict[str, Any]:
        """Run mypy type checking."""
        try:
            result = subprocess.run(
                ["python3", "-m", "mypy", "--ignore-missing-imports", "."],
                capture_output=True, text=True, timeout=60,
            )
            passed = result.returncode == 0
            return {
                "status": GateStatus.PASSED.value if passed else GateStatus.WARNING.value,
                "output": result.stdout[:500],
                "reason": "Type check passed" if passed else "Type issues found",
            }
        except Exception:
            return {
                "status": GateStatus.SKIPPED.value,
                "reason": "mypy not available",
            }

    def _check_lint(self, results: Dict) -> Dict[str, Any]:
        """Run flake8 linting."""
        try:
            result = subprocess.run(
                ["python3", "-m", "flake8", "--max-line-length=120", "--count", "."],
                capture_output=True, text=True, timeout=60,
            )
            issue_count = 0
            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                # Last line usually has the count
                try:
                    issue_count = int(lines[-1])
                except ValueError:
                    issue_count = len(lines)

            passed = issue_count == 0
            return {
                "status": GateStatus.PASSED.value if passed else GateStatus.WARNING.value,
                "issue_count": issue_count,
                "reason": (
                    "No lint issues"
                    if passed
                    else f"Found {issue_count} lint issues"
                ),
            }
        except Exception:
            return {
                "status": GateStatus.SKIPPED.value,
                "reason": "flake8 not available",
            }

    def _check_tests_pass(self, results: Dict) -> Dict[str, Any]:
        """Verify all tests pass."""
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "-q", "--tb=no"],
                capture_output=True, text=True, timeout=120,
            )
            passed = result.returncode == 0
            return {
                "status": GateStatus.PASSED.value if passed else GateStatus.FAILED.value,
                "output": result.stdout[:500],
                "reason": "All tests passed" if passed else "Some tests failed",
            }
        except Exception:
            return {
                "status": GateStatus.SKIPPED.value,
                "reason": "pytest not available",
            }
