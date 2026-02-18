"""
Tests for Quality Gates.
Verifies that gates actually validate and can fail.
"""

import pytest
import asyncio
from src.core.quality_gates import QualityGateManager, GateStatus


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestCoverageGate:
    """Test code coverage gate."""

    def test_coverage_passes_above_threshold(self):
        mgr = QualityGateManager()
        result = mgr._check_coverage({"coverage": 85})
        assert result["status"] == GateStatus.PASSED.value

    def test_coverage_fails_below_threshold(self):
        mgr = QualityGateManager()
        result = mgr._check_coverage({"coverage": 40})
        assert result["status"] == GateStatus.FAILED.value
        assert "40%" in result["reason"]

    def test_coverage_uses_estimated_coverage(self):
        mgr = QualityGateManager()
        result = mgr._check_coverage({"estimated_coverage": 90})
        assert result["status"] == GateStatus.PASSED.value


class TestComplexityGate:
    """Test cyclomatic complexity gate."""

    def test_low_complexity_passes(self):
        mgr = QualityGateManager()
        result = mgr._check_complexity({"complexity_score": 5})
        assert result["status"] == GateStatus.PASSED.value

    def test_high_complexity_fails(self):
        mgr = QualityGateManager()
        result = mgr._check_complexity({"complexity_score": 25})
        assert result["status"] == GateStatus.FAILED.value

    def test_boundary_complexity(self):
        mgr = QualityGateManager()
        # Exactly at threshold should pass
        result = mgr._check_complexity({"complexity": 10})
        assert result["status"] == GateStatus.PASSED.value

    def test_no_data_skips(self):
        mgr = QualityGateManager()
        result = mgr._check_complexity({})
        assert result["status"] == GateStatus.SKIPPED.value


class TestSecurityGate:
    """Test security scan gate."""

    def test_clean_code_passes(self):
        mgr = QualityGateManager()
        result = mgr._check_security({
            "security": {"passed": True, "findings": []}
        })
        assert result["status"] == GateStatus.PASSED.value

    def test_findings_fail(self):
        mgr = QualityGateManager()
        result = mgr._check_security({
            "security": {
                "passed": False,
                "findings": [{"type": "api_key", "line": 5}]
            }
        })
        assert result["status"] == GateStatus.FAILED.value

    def test_inline_scan_catches_eval(self):
        mgr = QualityGateManager()
        result = mgr._check_security({
            "code": 'result = eval(user_input)\n'
        })
        assert result["status"] == GateStatus.FAILED.value
        assert len(result["findings"]) > 0


class TestGateOrchestration:
    """Test running multiple gates together."""

    def test_all_gates_pass(self):
        mgr = QualityGateManager()
        results = {"coverage": 90, "complexity_score": 5}
        report = run_async(mgr.check(results, ["code_coverage", "complexity"]))
        assert report["passed"] is True
        assert report["passed_count"] == 2

    def test_one_gate_fails(self):
        mgr = QualityGateManager()
        results = {"coverage": 90, "complexity_score": 20}
        report = run_async(mgr.check(results, ["code_coverage", "complexity"]))
        assert report["passed"] is False
        assert report["failed_count"] == 1
        assert report["failures"][0]["gate"] == "complexity"

    def test_unknown_gate_skipped(self):
        mgr = QualityGateManager()
        report = run_async(mgr.check({}, ["nonexistent_gate"]))
        assert report["passed"] is True  # Skipped gates don't cause failure
        assert report["details"]["nonexistent_gate"]["status"] == GateStatus.SKIPPED.value

    def test_multiple_failures(self):
        mgr = QualityGateManager()
        results = {"coverage": 30, "complexity_score": 50}
        report = run_async(mgr.check(results, ["code_coverage", "complexity"]))
        assert report["passed"] is False
        assert report["failed_count"] == 2
