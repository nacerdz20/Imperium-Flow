"""
TDD Superpower - Real Test-Driven Development Engine.
Implements the actual Red-Green-Refactor cycle with test execution,
failure analysis, and iterative code improvement.
"""

import subprocess
import os
import tempfile
import logging
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger("Superpowers.TDD")


class TDDExpert:
    """
    Real TDD Engine implementing Red-Green-Refactor.
    
    This is NOT a simulation. It:
    1. Writes test files to disk
    2. Runs pytest and captures results
    3. Analyzes failures with categorized error types
    4. Provides the prompt context for LLM-driven code generation
    """

    def __init__(self, work_dir: str = "."):
        self.work_dir = work_dir
        self.cycle_history: List[Dict[str, Any]] = []

    def get_prompt(self) -> str:
        """Return TDD-specific prompt for LLM context."""
        return """
## TDD Protocol (Red-Green-Refactor)

You are operating under strict TDD discipline:

### Phase 1: RED — Write Failing Test First
- Write a test that describes the EXPECTED behavior
- The test MUST fail when run (there's no implementation yet)
- Use pytest with descriptive test names
- Cover: happy path, edge cases, error cases
- Use Arrange-Act-Assert pattern

### Phase 2: GREEN — Write Minimal Code
- Write the MINIMUM code to make the test pass
- Do NOT add features not covered by tests
- Do NOT optimize yet
- Focus only on making tests green

### Phase 3: REFACTOR — Improve Quality
- Clean up duplication
- Improve naming
- Add type hints and docstrings
- Extract helper functions if needed
- ALL tests must remain green after refactoring

### Rules
- NEVER write code before a test
- NEVER skip the refactor phase
- One behavior per test function
- Tests must be deterministic and isolated
"""

    async def execute_cycle(
        self,
        feature_description: str,
        test_code: str,
        implementation_code: str,
    ) -> Dict[str, Any]:
        """
        Execute a full TDD cycle.
        
        Args:
            feature_description: What we're implementing.
            test_code: The test code (from RED phase).
            implementation_code: The implementation (from GREEN phase).
            
        Returns:
            Cycle result with test outcomes and analysis.
        """
        cycle = {
            "feature": feature_description,
            "phases": {},
            "success": False,
        }

        # RED: Save and run test (should fail without implementation)
        red_result = self._run_test_phase(
            test_code,
            implementation_code=None,
            phase="red"
        )
        cycle["phases"]["red"] = red_result

        # GREEN: Run test with implementation (should pass)
        green_result = self._run_test_phase(
            test_code,
            implementation_code=implementation_code,
            phase="green"
        )
        cycle["phases"]["green"] = green_result

        cycle["success"] = green_result["passed"]
        self.cycle_history.append(cycle)
        return cycle

    def _run_test_phase(
        self,
        test_code: str,
        implementation_code: Optional[str],
        phase: str,
    ) -> Dict[str, Any]:
        """
        Run a test phase by writing files to a temp directory
        and executing pytest.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write test file
            test_path = os.path.join(tmpdir, "test_feature.py")
            with open(test_path, "w") as f:
                f.write(test_code)

            # Write implementation if provided (GREEN/REFACTOR phases)
            if implementation_code:
                impl_path = os.path.join(tmpdir, "feature.py")
                with open(impl_path, "w") as f:
                    f.write(implementation_code)

            # Run pytest
            passed, output = self.run_tests(test_path, cwd=tmpdir)

            return {
                "phase": phase,
                "passed": passed,
                "output": output[:2000],  # Truncate long output
                "expected_pass": phase != "red",
                "correct_behavior": (
                    (phase == "red" and not passed)
                    or (phase != "red" and passed)
                ),
            }

    def run_tests(self, test_file: str, cwd: str = None) -> Tuple[bool, str]:
        """
        Run pytest on a test file and return results.
        """
        run_dir = cwd or self.work_dir
        logger.info(f"🏃 Running tests: {test_file}")

        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=run_dir,
                timeout=30,
            )
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            return passed, output
        except FileNotFoundError:
            return False, "pytest not found. Install with: pip install pytest"
        except subprocess.TimeoutExpired:
            return False, "Test execution timed out (30s)"
        except Exception as e:
            return False, f"Test execution error: {str(e)}"

    def analyze_failure(self, output: str) -> Dict[str, Any]:
        """
        Analyze test failure output and categorize the error.
        """
        error_categories = {
            "assertion": "Logic Error: Test assertion failed",
            "import": "Dependency Error: Module not found",
            "attribute": "Interface Error: Wrong attribute/method name",
            "type": "Type Error: Wrong argument type",
            "name": "Reference Error: Undefined variable",
            "syntax": "Syntax Error: Invalid Python syntax",
            "timeout": "Performance Error: Execution too slow",
            "index": "Boundary Error: Index out of range",
            "key": "Data Error: Missing dictionary key",
        }

        output_lower = output.lower()
        detected = []

        for keyword, description in error_categories.items():
            if f"{keyword}error" in output_lower:
                detected.append({"type": keyword, "description": description})

        if not detected:
            detected.append({
                "type": "unknown",
                "description": "Unknown error type"
            })

        return {
            "error_count": len(detected),
            "errors": detected,
            "raw_output": output[:1000],
        }

    def generate_test_plan(self, feature_description: str) -> List[str]:
        """
        Generate a test plan from a feature description.
        Returns test function names covering all categories.
        """
        logger.info(f"🧪 Generating test plan for: {feature_description}")

        base_name = feature_description.lower().replace(" ", "_")[:30]
        return [
            f"test_{base_name}_happy_path",
            f"test_{base_name}_empty_input",
            f"test_{base_name}_none_input",
            f"test_{base_name}_boundary_values",
            f"test_{base_name}_invalid_type",
            f"test_{base_name}_expected_exception",
        ]

    def get_cycle_history(self) -> List[Dict]:
        """Return the history of TDD cycles."""
        return self.cycle_history
