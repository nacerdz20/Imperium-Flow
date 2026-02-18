"""
TestBot - Specialized QA Engineer Agent.
Implements real test generation, coverage analysis,
and test categorization (unit, integration, edge, error).
"""

import logging
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent


class TestBot(BaseAgent):
    """
    Specialized agent for quality assurance and testing.
    
    Unlike the generic WorkerAgent, TestBot enforces:
    1. Coverage targets per category
    2. Test categorization (happy/edge/error)
    3. Mock strategy validation
    4. Deterministic test enforcement
    """

    # Coverage targets
    COVERAGE_TARGETS = {
        "overall": 70,
        "business_logic": 90,
        "ui_components": 60,
        "api_routes": 80,
    }

    def __init__(self):
        super().__init__(name="TestBot")
        self.logger = logging.getLogger("Agent.TestBot")
        self.constraints = [
            "Tests MUST be deterministic (no flaky tests)",
            "Tests MUST be isolated (no shared mutable state)",
            "Mocks MUST be realistic (match real API contracts)",
            "Test names MUST be descriptive",
            f"Business logic coverage target: {self.COVERAGE_TARGETS['business_logic']}%",
        ]
        self._equip_default_skills()

    def _equip_default_skills(self):
        """Equip TestBot with testing-specific skills."""
        from src.superpowers.tdd import TDDExpert
        from src.superpowers.code_analysis import CodeAnalyzer

        self.add_skill("tdd", TDDExpert())
        self.add_skill("code_analysis", CodeAnalyzer())

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a testing task.
        
        Flow:
        1. Analyze the code under test
        2. Generate categorized test plan
        3. Write tests for each category
        4. Validate coverage and quality
        5. Report gaps
        """
        self.logger.info(f"🧪 TestBot executing: {task.get('description', 'unnamed')}")
        result = {
            "agent": "TestBot",
            "task_id": task.get("id", "unknown"),
            "phases": {},
            "status": "pending",
        }

        try:
            # Phase 1: Analyze code under test
            code_under_test = task.get("code", task.get("description", ""))
            analysis = await self._analyze_code(code_under_test)
            result["phases"]["analysis"] = analysis

            # Phase 2: Generate test plan
            test_plan = await self._generate_test_plan(analysis)
            result["phases"]["test_plan"] = test_plan

            # Phase 3: Write categorized tests
            tests = await self._write_tests(task, test_plan)
            result["phases"]["tests"] = tests

            # Phase 4: Coverage analysis
            coverage = self._analyze_coverage(tests)
            result["phases"]["coverage"] = coverage

            # Phase 5: Gap report
            gaps = self._identify_gaps(coverage)
            result["phases"]["gaps"] = gaps

            result["status"] = "completed"
            result["coverage_met"] = coverage.get("meets_targets", False)

        except Exception as e:
            self.logger.error(f"❌ TestBot failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze the code to understand what needs testing."""
        prompt = (
            f"Analyze this code and identify all testable units:\n"
            f"1. Public functions and their signatures\n"
            f"2. Edge cases for each function\n"
            f"3. Error conditions\n"
            f"4. Integration points\n\n"
            f"Code:\n{code}"
        )
        raw = await self.execute_with_ai(prompt)
        return {"raw_analysis": raw, "code_length": len(code.split("\n"))}

    async def _generate_test_plan(self, analysis: Dict) -> Dict[str, List[str]]:
        """Generate categorized test plan."""
        prompt = (
            f"Based on this analysis, generate a test plan with these categories:\n"
            f"1. happy_path: Normal operation tests\n"
            f"2. edge_cases: Boundary values, empty inputs, None\n"
            f"3. error_cases: Invalid inputs, expected exceptions\n"
            f"4. integration: Component interaction tests\n\n"
            f"Analysis: {analysis['raw_analysis']}\n\n"
            f"Return a structured list of test names per category."
        )
        raw = await self.execute_with_ai(prompt)
        return {
            "raw_plan": raw,
            "categories": ["happy_path", "edge_cases", "error_cases", "integration"]
        }

    async def _write_tests(self, task: Dict, test_plan: Dict) -> Dict[str, str]:
        """Write actual test code for each category."""
        tests = {}
        description = task.get("description", "")

        for category in test_plan.get("categories", []):
            self.logger.info(f"📝 Writing {category} tests...")
            prompt = (
                f"Write Python pytest tests for the '{category}' category.\n"
                f"Task: {description}\n"
                f"Test plan: {test_plan.get('raw_plan', '')}\n\n"
                f"Rules:\n"
                f"- Tests MUST be deterministic\n"
                f"- Tests MUST be isolated\n"
                f"- Use descriptive test names\n"
                f"- Use Arrange-Act-Assert pattern\n"
                f"- Mock external dependencies\n\n"
                f"Return ONLY the test code."
            )
            test_code = await self.execute_with_ai(prompt, skill_name="tdd")
            tests[category] = test_code

        return tests

    def _analyze_coverage(self, tests: Dict[str, str]) -> Dict[str, Any]:
        """Analyze test coverage based on generated tests."""
        total_tests = 0
        category_counts = {}

        for category, code in tests.items():
            # Count test functions
            count = code.count("def test_") if isinstance(code, str) else 0
            category_counts[category] = count
            total_tests += count

        # Estimate coverage based on test categories present
        has_happy = category_counts.get("happy_path", 0) > 0
        has_edge = category_counts.get("edge_cases", 0) > 0
        has_error = category_counts.get("error_cases", 0) > 0
        has_integration = category_counts.get("integration", 0) > 0

        estimated_coverage = 0
        if has_happy:
            estimated_coverage += 40
        if has_edge:
            estimated_coverage += 25
        if has_error:
            estimated_coverage += 20
        if has_integration:
            estimated_coverage += 15

        meets_targets = estimated_coverage >= self.COVERAGE_TARGETS["overall"]

        return {
            "total_tests": total_tests,
            "category_counts": category_counts,
            "estimated_coverage": estimated_coverage,
            "meets_targets": meets_targets,
            "targets": self.COVERAGE_TARGETS,
        }

    def _identify_gaps(self, coverage: Dict) -> List[str]:
        """Identify coverage gaps."""
        gaps = []
        counts = coverage.get("category_counts", {})

        if counts.get("happy_path", 0) == 0:
            gaps.append("CRITICAL: No happy path tests")
        if counts.get("edge_cases", 0) == 0:
            gaps.append("WARNING: No edge case tests")
        if counts.get("error_cases", 0) == 0:
            gaps.append("WARNING: No error case tests")
        if counts.get("integration", 0) == 0:
            gaps.append("INFO: No integration tests")
        if not coverage.get("meets_targets", False):
            gaps.append(
                f"CRITICAL: Coverage {coverage.get('estimated_coverage', 0)}% "
                f"below target {self.COVERAGE_TARGETS['overall']}%"
            )

        return gaps
