"""
Extended superpower tests — DocumentationGenerator, RefactoringEngine,
SystematicDebugger, PerformanceAnalyzer.
Targets: documentation.py (18%→80%), refactoring.py (30%→80%),
         debugging.py (43%→80%), performance.py (48%→80%)
"""

import pytest
from src.superpowers.documentation import DocumentationGenerator
from src.superpowers.refactoring import RefactoringEngine
from src.superpowers.debugging import SystematicDebugger
from src.superpowers.performance import PerformanceAnalyzer, PerformanceIssue


# ═══════════════════════════════════════════════════════════
# DocumentationGenerator
# ═══════════════════════════════════════════════════════════

class TestDocumentationGenerator:

    def setup_method(self):
        self.gen = DocumentationGenerator()

    def test_get_prompt_not_empty(self):
        prompt = self.gen.get_prompt()
        assert len(prompt) > 100
        assert "Documentation" in prompt

    def test_generate_module_doc_minimal(self):
        info = {"name": "utils", "docstring": "Utility functions"}
        doc = self.gen.generate_module_doc(info)
        assert "# utils" in doc
        assert "Utility functions" in doc

    def test_generate_module_doc_with_classes(self):
        info = {
            "name": "auth",
            "docstring": "Authentication module",
            "classes": [
                {
                    "name": "AuthManager",
                    "docstring": "Manages auth tokens",
                    "methods": [
                        {"name": "login", "params": ["username", "password"], "docstring": "Log in"}
                    ]
                }
            ]
        }
        doc = self.gen.generate_module_doc(info)
        assert "## Classes" in doc
        assert "AuthManager" in doc
        assert "login(username, password)" in doc

    def test_generate_module_doc_with_functions(self):
        info = {
            "name": "helpers",
            "docstring": "Helper functions",
            "functions": [
                {"name": "sanitize", "params": ["text"], "docstring": "Clean input text"}
            ]
        }
        doc = self.gen.generate_module_doc(info)
        assert "## Functions" in doc
        assert "sanitize(text)" in doc

    def test_generate_module_doc_empty(self):
        doc = self.gen.generate_module_doc({})
        assert "# Unknown" in doc

    def test_generate_architecture_diagram_single(self):
        components = [
            {"name": "API Gateway", "depends_on": ["Auth Service"]}
        ]
        diagram = self.gen.generate_architecture_diagram(components)
        assert "mermaid" in diagram
        assert "API_Gateway" in diagram
        assert "Auth_Service" in diagram
        assert "-->" in diagram

    def test_generate_architecture_diagram_multiple(self):
        components = [
            {"name": "Frontend", "depends_on": ["API"]},
            {"name": "API", "depends_on": ["Database"]},
            {"name": "Database", "depends_on": []}
        ]
        diagram = self.gen.generate_architecture_diagram(components)
        assert diagram.count("-->") == 2

    def test_generate_architecture_diagram_no_deps(self):
        components = [{"name": "Standalone", "depends_on": []}]
        diagram = self.gen.generate_architecture_diagram(components)
        assert "Standalone" in diagram
        assert "-->" not in diagram


# ═══════════════════════════════════════════════════════════
# RefactoringEngine
# ═══════════════════════════════════════════════════════════

class TestRefactoringEngine:

    def setup_method(self):
        self.engine = RefactoringEngine()

    def test_init_has_patterns(self):
        assert len(self.engine.refactoring_patterns) == 6
        assert "extract_method" in self.engine.refactoring_patterns

    def test_get_prompt_not_empty(self):
        prompt = self.engine.get_prompt()
        assert "Refactoring" in prompt
        assert "Extract Method" in prompt

    def test_detect_no_smells_clean_code(self):
        metrics = {"line_count": 10, "complexity": 3, "param_count": 2, "nesting_depth": 1}
        smells = self.engine.detect_smells(metrics)
        assert len(smells) == 0

    def test_detect_long_method(self):
        metrics = {"line_count": 50}
        smells = self.engine.detect_smells(metrics)
        assert any(s["smell"] == "Long Method" for s in smells)

    def test_detect_high_complexity(self):
        metrics = {"complexity": 15}
        smells = self.engine.detect_smells(metrics)
        assert any(s["smell"] == "High Complexity" for s in smells)

    def test_detect_long_param_list(self):
        metrics = {"param_count": 7}
        smells = self.engine.detect_smells(metrics)
        assert any(s["smell"] == "Long Parameter List" for s in smells)

    def test_detect_deep_nesting(self):
        metrics = {"nesting_depth": 5}
        smells = self.engine.detect_smells(metrics)
        assert any(s["smell"] == "Deep Nesting" for s in smells)

    def test_detect_multiple_smells(self):
        metrics = {"line_count": 100, "complexity": 20, "param_count": 8, "nesting_depth": 5}
        smells = self.engine.detect_smells(metrics)
        assert len(smells) == 4

    def test_detect_empty_metrics(self):
        smells = self.engine.detect_smells({})
        assert len(smells) == 0

    def test_suggest_refactoring_sorts_by_severity(self):
        smells = [
            {"smell": "Low", "severity": "low"},
            {"smell": "High", "severity": "high"},
            {"smell": "Med", "severity": "medium"},
        ]
        sorted_smells = self.engine.suggest_refactoring(smells)
        assert sorted_smells[0]["severity"] == "high"
        assert sorted_smells[1]["severity"] == "medium"
        assert sorted_smells[2]["severity"] == "low"

    def test_suggest_refactoring_empty(self):
        result = self.engine.suggest_refactoring([])
        assert result == []

    def test_patterns_have_success_rate(self):
        for name, pattern in self.engine.refactoring_patterns.items():
            assert "success_rate" in pattern
            assert 0 < pattern["success_rate"] <= 1.0


# ═══════════════════════════════════════════════════════════
# SystematicDebugger
# ═══════════════════════════════════════════════════════════

class TestSystematicDebugger:

    def setup_method(self):
        self.debugger = SystematicDebugger()

    def test_analyze_timeout(self):
        result = self.debugger.analyze_failure("Connection timeout after 30s", {})
        assert result["recommended_strategy"] == "check_performance"

    def test_analyze_syntax(self):
        result = self.debugger.analyze_failure("SyntaxError: invalid syntax", {})
        assert result["recommended_strategy"] == "lint_check"

    def test_analyze_generic(self):
        result = self.debugger.analyze_failure("Unexpected error in module X", {})
        assert result["recommended_strategy"] == "trace_root_cause"

    def test_analysis_has_steps(self):
        result = self.debugger.analyze_failure("Error", {})
        assert len(result["steps"]) > 0

    def test_analysis_has_hypothesis(self):
        result = self.debugger.analyze_failure("Error", {})
        assert "root_cause_hypothesis" in result

    def test_suggest_fix(self):
        analysis = {"recommended_strategy": "check_performance"}
        fix = self.debugger.suggest_fix(analysis)
        assert "check_performance" in fix

    def test_suggest_fix_lint(self):
        analysis = {"recommended_strategy": "lint_check"}
        fix = self.debugger.suggest_fix(analysis)
        assert "lint_check" in fix


# ═══════════════════════════════════════════════════════════
# PerformanceAnalyzer
# ═══════════════════════════════════════════════════════════

class TestPerformanceAnalyzer:

    def setup_method(self):
        self.analyzer = PerformanceAnalyzer()

    def test_get_prompt_not_empty(self):
        prompt = self.analyzer.get_prompt()
        assert "Performance" in prompt
        assert len(prompt) > 100

    def test_get_strategies(self):
        strategies = self.analyzer.get_strategies()
        assert "caching" in strategies
        assert "batch_processing" in strategies
        assert len(strategies) == 6

    def test_analyze_clean_code(self):
        issues = self.analyzer.analyze({})
        assert len(issues) == 0

    def test_analyze_nested_loops(self):
        issues = self.analyzer.analyze({"has_nested_loops": True})
        assert len(issues) == 1
        assert issues[0].category == "algorithm"
        assert issues[0].severity == "high"

    def test_analyze_list_search(self):
        issues = self.analyzer.analyze({"uses_list_search": True})
        assert len(issues) == 1
        assert "O(1)" in issues[0].estimated_impact

    def test_analyze_blocking_io(self):
        issues = self.analyzer.analyze({"has_blocking_io": True})
        assert len(issues) == 1
        assert issues[0].category == "io"

    def test_analyze_repeated_computation(self):
        issues = self.analyzer.analyze({"repeated_computation": True})
        assert len(issues) == 1
        assert "cache" in issues[0].recommendation.lower()

    def test_analyze_sequential_io(self):
        issues = self.analyzer.analyze({"sequential_io": True})
        assert len(issues) == 1
        assert "batch" in issues[0].recommendation.lower()

    def test_analyze_multiple_issues(self):
        info = {
            "has_nested_loops": True,
            "uses_list_search": True,
            "has_blocking_io": True,
            "repeated_computation": True,
            "sequential_io": True,
        }
        issues = self.analyzer.analyze(info)
        assert len(issues) == 5

    def test_performance_issue_dataclass(self):
        issue = PerformanceIssue(
            category="memory",
            severity="medium",
            description="High allocation rate",
            recommendation="Use object pooling",
            estimated_impact="30% reduction"
        )
        assert issue.category == "memory"
        assert issue.severity == "medium"
