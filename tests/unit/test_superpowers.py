"""
Tests for Superpowers: SecurityScanner, CodeAnalyzer, TDDExpert.
"""

import pytest
import asyncio
import os
from src.superpowers.security import SecurityScanner
from src.superpowers.code_analysis import CodeAnalyzer
from src.superpowers.tdd import TDDExpert


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ─── SecurityScanner ─────────────────────────────────────────
class TestSecurityScanner:
    """Test SecurityScanner SAST capabilities."""

    def test_scan_clean_file(self, sample_python_file):
        scanner = SecurityScanner()
        findings = scanner.scan_file(sample_python_file)
        assert len(findings) == 0

    def test_scan_detects_api_key(self, insecure_python_file):
        scanner = SecurityScanner()
        findings = scanner.scan_file(insecure_python_file)
        types = [f["type"] for f in findings]
        assert "api_key" in types

    def test_scan_detects_hardcoded_password(self, insecure_python_file):
        scanner = SecurityScanner()
        findings = scanner.scan_file(insecure_python_file)
        types = [f["type"] for f in findings]
        assert "hardcoded_password" in types

    def test_scan_detects_eval(self, insecure_python_file):
        scanner = SecurityScanner()
        findings = scanner.scan_file(insecure_python_file)
        types = [f["type"] for f in findings]
        assert "insecure_eval" in types

    def test_scan_detects_debug_true(self, insecure_python_file):
        scanner = SecurityScanner()
        findings = scanner.scan_file(insecure_python_file)
        types = [f["type"] for f in findings]
        assert "debug_true" in types

    def test_scan_nonexistent_file(self):
        scanner = SecurityScanner()
        findings = scanner.scan_file("/tmp/nonexistent_file_for_test.py")
        assert findings == []

    def test_findings_have_severity(self, insecure_python_file):
        scanner = SecurityScanner()
        findings = scanner.scan_file(insecure_python_file)
        for f in findings:
            assert "severity" in f
            assert f["severity"] in ("HIGH", "MEDIUM")

    def test_findings_have_line_numbers(self, insecure_python_file):
        scanner = SecurityScanner()
        findings = scanner.scan_file(insecure_python_file)
        for f in findings:
            assert "line" in f
            assert isinstance(f["line"], int)


# ─── CodeAnalyzer ────────────────────────────────────────────
class TestCodeAnalyzer:
    """Test CodeAnalyzer AST-based analysis."""

    def test_analyze_sample_file(self, sample_python_file):
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file(sample_python_file)
        assert result["classes"] == 1  # Calculator
        assert result["functions"] >= 3  # add, multiply, divide
        assert result["loc"] > 0
        assert result["imports"] == 0
        assert "complexity_score" in result

    def test_complexity_of_simple_code(self, temp_dir):
        path = os.path.join(temp_dir, "simple.py")
        with open(path, "w") as f:
            f.write("def hello():\n    return 42\n")
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file(path)
        assert result["complexity_score"] == 1  # No branches

    def test_complexity_with_branches(self, temp_dir):
        path = os.path.join(temp_dir, "branchy.py")
        with open(path, "w") as f:
            f.write("""
def check(x):
    if x > 0:
        if x > 10:
            return "big"
        return "small"
    else:
        return "negative"
""")
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file(path)
        assert result["complexity_score"] >= 3

    def test_analyze_nonexistent_file(self):
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file("/tmp/nonexistent_code.py")
        assert "error" in result

    def test_analyze_invalid_python(self, temp_dir):
        path = os.path.join(temp_dir, "bad.py")
        with open(path, "w") as f:
            f.write("def broken(:\n")
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_file(path)
        assert "error" in result


# ─── TDDExpert ───────────────────────────────────────────────
class TestTDDExpert:
    """Test TDDExpert TDD engine."""

    def test_get_prompt(self):
        tdd = TDDExpert()
        prompt = tdd.get_prompt()
        assert "RED" in prompt
        assert "GREEN" in prompt
        assert "REFACTOR" in prompt

    def test_run_tests_passing(self, temp_dir):
        tdd = TDDExpert(work_dir=temp_dir)
        test_file = os.path.join(temp_dir, "test_pass.py")
        with open(test_file, "w") as f:
            f.write("def test_always_pass():\n    assert 1 + 1 == 2\n")
        passed, output = tdd.run_tests(test_file, cwd=temp_dir)
        assert passed is True
        assert "passed" in output.lower()

    def test_run_tests_failing(self, temp_dir):
        tdd = TDDExpert(work_dir=temp_dir)
        test_file = os.path.join(temp_dir, "test_fail.py")
        with open(test_file, "w") as f:
            f.write("def test_always_fail():\n    assert 1 == 2\n")
        passed, output = tdd.run_tests(test_file, cwd=temp_dir)
        assert passed is False

    def test_analyze_failure_assertion(self):
        tdd = TDDExpert()
        result = tdd.analyze_failure("AssertionError: 2 != 3\nassertionerror detail")
        errors = [e["type"] for e in result["errors"]]
        assert "assertion" in errors

    def test_analyze_failure_import(self):
        tdd = TDDExpert()
        result = tdd.analyze_failure("ImportError: No module named 'foo'")
        errors = [e["type"] for e in result["errors"]]
        assert "import" in errors

    def test_analyze_failure_unknown(self):
        tdd = TDDExpert()
        result = tdd.analyze_failure("Something weird happened")
        assert result["errors"][0]["type"] == "unknown"

    def test_generate_test_plan(self):
        tdd = TDDExpert()
        plan = tdd.generate_test_plan("user authentication")
        assert len(plan) == 6
        assert any("happy_path" in t for t in plan)
        assert any("empty_input" in t for t in plan)
        assert any("invalid_type" in t for t in plan)

    def test_execute_cycle_red_green(self):
        tdd = TDDExpert()
        test_code = """
from feature import add
def test_add():
    assert add(2, 3) == 5
"""
        impl_code = """
def add(a, b):
    return a + b
"""
        result = run_async(tdd.execute_cycle("add function", test_code, impl_code))
        assert "phases" in result
        assert result["phases"]["red"]["passed"] is False  # No impl → fail
        assert result["phases"]["red"]["correct_behavior"] is True
        assert result["phases"]["green"]["passed"] is True  # With impl → pass
        assert result["phases"]["green"]["correct_behavior"] is True
        assert result["success"] is True

    def test_cycle_history(self):
        tdd = TDDExpert()
        test_code = "def test_x():\n    assert True\n"
        impl_code = ""
        run_async(tdd.execute_cycle("feature", test_code, impl_code))
        history = tdd.get_cycle_history()
        assert len(history) == 1
        assert history[0]["feature"] == "feature"
