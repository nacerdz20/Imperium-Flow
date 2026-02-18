"""
Extended Quality Gates tests — coverage gate, complexity gate, security gate,
check() orchestration, gate registry, and unknown gates.
Targets: quality_gates.py (61% → 80%+)
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.quality_gates import QualityGateManager, GateStatus


class TestGateStatus:
    """Test the GateStatus enum."""

    def test_all_statuses_exist(self):
        assert GateStatus.PASSED.value == "passed"
        assert GateStatus.FAILED.value == "failed"
        assert GateStatus.SKIPPED.value == "skipped"
        assert GateStatus.WARNING.value == "warning"


class TestQualityGateManagerInit:
    """Test QGM initialization."""

    def test_has_gate_registry(self):
        qm = QualityGateManager()
        assert "code_coverage" in qm.gate_registry
        assert "complexity" in qm.gate_registry
        assert "security_scan" in qm.gate_registry
        assert "type_check" in qm.gate_registry
        assert "lint" in qm.gate_registry
        assert "test_pass" in qm.gate_registry

    def test_has_thresholds(self):
        qm = QualityGateManager()
        assert qm.GATE_THRESHOLDS["code_coverage"] == 70
        assert qm.GATE_THRESHOLDS["complexity"] == 10


class TestCheckMethod:
    """Test the check() orchestration method."""

    @pytest.mark.asyncio
    async def test_check_all_pass(self):
        qm = QualityGateManager()
        results = {"coverage": 85, "complexity_score": 5}
        report = await qm.check(results, ["code_coverage", "complexity"])
        assert report["passed"] is True
        assert report["total_gates"] == 2
        assert report["passed_count"] == 2
        assert report["failed_count"] == 0

    @pytest.mark.asyncio
    async def test_check_with_failure(self):
        qm = QualityGateManager()
        results = {"coverage": 30}
        report = await qm.check(results, ["code_coverage"])
        assert report["passed"] is False
        assert report["failed_count"] == 1
        assert len(report["failures"]) == 1

    @pytest.mark.asyncio
    async def test_check_unknown_gate(self):
        qm = QualityGateManager()
        report = await qm.check({}, ["nonexistent_gate"])
        assert report["details"]["nonexistent_gate"]["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_check_empty_criteria(self):
        qm = QualityGateManager()
        report = await qm.check({}, [])
        assert report["passed"] is True
        assert report["total_gates"] == 0

    @pytest.mark.asyncio
    async def test_check_mixed_results(self):
        qm = QualityGateManager()
        results = {"coverage": 85, "complexity_score": 15}
        report = await qm.check(results, ["code_coverage", "complexity"])
        assert report["passed"] is False
        assert report["passed_count"] == 1
        assert report["failed_count"] == 1


class TestCoverageGate:
    """Test _check_coverage."""

    def test_coverage_passes(self):
        qm = QualityGateManager()
        result = qm._check_coverage({"coverage": 80})
        assert result["status"] == "passed"
        assert result["coverage"] == 80

    def test_coverage_fails(self):
        qm = QualityGateManager()
        result = qm._check_coverage({"coverage": 50})
        assert result["status"] == "failed"
        assert "below threshold" in result["reason"]

    def test_coverage_estimated(self):
        qm = QualityGateManager()
        result = qm._check_coverage({"estimated_coverage": 75})
        assert result["status"] == "passed"

    def test_coverage_at_threshold(self):
        qm = QualityGateManager()
        result = qm._check_coverage({"coverage": 70})
        assert result["status"] == "passed"

    def test_coverage_no_data_runs_tool(self):
        qm = QualityGateManager()
        with patch.object(qm, "_run_coverage_tool", return_value={"status": "skipped", "reason": "no data"}) as mock_tool:
            result = qm._check_coverage({})
            mock_tool.assert_called_once()


class TestComplexityGate:
    """Test _check_complexity."""

    def test_complexity_passes(self):
        qm = QualityGateManager()
        result = qm._check_complexity({"complexity_score": 5})
        assert result["status"] == "passed"

    def test_complexity_fails(self):
        qm = QualityGateManager()
        result = qm._check_complexity({"complexity_score": 15})
        assert result["status"] == "failed"
        assert "exceeds" in result["reason"]

    def test_complexity_at_threshold(self):
        qm = QualityGateManager()
        result = qm._check_complexity({"complexity_score": 10})
        assert result["status"] == "passed"

    def test_complexity_no_data(self):
        qm = QualityGateManager()
        result = qm._check_complexity({})
        assert result["status"] == "skipped"

    def test_complexity_from_nested_dict(self):
        qm = QualityGateManager()
        result = qm._check_complexity({"analysis": {"complexity_score": 8}})
        assert result["status"] == "passed"

    def test_complexity_uses_alias(self):
        qm = QualityGateManager()
        result = qm._check_complexity({"complexity": 3})
        assert result["status"] == "passed"


class TestSecurityGate:
    """Test _check_security."""

    def test_security_with_passed_data(self):
        qm = QualityGateManager()
        result = qm._check_security({"security": {"passed": True, "findings": []}})
        assert result["status"] == "passed"

    def test_security_with_failed_data(self):
        qm = QualityGateManager()
        result = qm._check_security({
            "security": {"passed": False, "findings": [{"type": "api_key"}]}
        })
        assert result["status"] == "failed"
        assert len(result["findings"]) == 1

    def test_security_inline_scan_clean(self):
        qm = QualityGateManager()
        result = qm._check_security({"code": "x = 42\nprint(x)"})
        assert result["status"] == "passed"

    def test_security_inline_scan_finds_issues(self):
        qm = QualityGateManager()
        result = qm._check_security({"code": 'API_KEY = "sk-abc123"\neval(data)'})
        assert result["status"] == "failed"
        assert len(result["findings"]) > 0

    def test_security_no_code(self):
        qm = QualityGateManager()
        result = qm._check_security({})
        assert result["status"] == "skipped"


class TestTypeCheckGate:
    """Test _check_types with mocked subprocess."""

    def test_types_pass(self):
        qm = QualityGateManager()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        with patch("subprocess.run", return_value=mock_result):
            result = qm._check_types({})
            assert result["status"] == "passed"

    def test_types_warning(self):
        qm = QualityGateManager()
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "error x"
        with patch("subprocess.run", return_value=mock_result):
            result = qm._check_types({})
            assert result["status"] == "warning"

    def test_types_skipped(self):
        qm = QualityGateManager()
        with patch("subprocess.run", side_effect=Exception("mypy not installed")):
            result = qm._check_types({})
            assert result["status"] == "skipped"


class TestLintGate:
    """Test _check_lint with mocked subprocess."""

    def test_lint_clean(self):
        qm = QualityGateManager()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            result = qm._check_lint({})
            assert result["status"] == "passed"

    def test_lint_issues(self):
        qm = QualityGateManager()
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "file.py:1:1: E302\n1"
        with patch("subprocess.run", return_value=mock_result):
            result = qm._check_lint({})
            assert result["status"] == "warning"
            assert result["issue_count"] == 1

    def test_lint_skipped(self):
        qm = QualityGateManager()
        with patch("subprocess.run", side_effect=Exception("no flake8")):
            result = qm._check_lint({})
            assert result["status"] == "skipped"


class TestTestPassGate:
    """Test _check_tests_pass with mocked subprocess."""

    def test_tests_pass(self):
        qm = QualityGateManager()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "5 passed"
        with patch("subprocess.run", return_value=mock_result):
            result = qm._check_tests_pass({})
            assert result["status"] == "passed"

    def test_tests_fail(self):
        qm = QualityGateManager()
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "2 failed"
        with patch("subprocess.run", return_value=mock_result):
            result = qm._check_tests_pass({})
            assert result["status"] == "failed"

    def test_tests_skipped(self):
        qm = QualityGateManager()
        with patch("subprocess.run", side_effect=Exception("no pytest")):
            result = qm._check_tests_pass({})
            assert result["status"] == "skipped"
