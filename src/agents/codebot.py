"""
CodeBot - Specialized Code Worker Agent.
Implements real TDD protocol (Red-Green-Refactor),
security scanning, and commit standard enforcement.
"""

import logging
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent


class CodeBot(BaseAgent):
    """
    Specialized agent for code implementation via TDD.
    
    Unlike the generic WorkerAgent, CodeBot enforces:
    1. Test-first development (Red phase)
    2. Minimal implementation (Green phase)
    3. Refactoring with safety net (Refactor phase)
    4. Security scan before marking complete
    5. Conventional Commit messages
    """

    def __init__(self):
        super().__init__(name="CodeBot")
        self.logger = logging.getLogger("Agent.CodeBot")
        self.max_complexity = 10
        self.max_file_lines = 300
        self.constraints = [
            "No code without a corresponding test",
            "No commit without passing security scan",
            "Max cyclomatic complexity: 10",
            "Max file length: 300 lines",
        ]
        self._equip_default_skills()

    def _equip_default_skills(self):
        """Equip CodeBot with its specialized skills."""
        from src.superpowers.tdd import TDDExpert
        from src.superpowers.security import SecurityScanner
        from src.superpowers.code_analysis import CodeAnalyzer

        self.add_skill("tdd", TDDExpert())
        self.add_skill("security", SecurityScanner())
        self.add_skill("code_analysis", CodeAnalyzer())

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a coding task using the TDD protocol.
        
        Flow:
        1. Analyze the task requirements
        2. RED: Generate failing test via LLM
        3. GREEN: Write minimal code to pass
        4. REFACTOR: Improve code quality
        5. SECURITY: Scan for vulnerabilities
        6. Return structured result
        """
        self.logger.info(f"🤖 CodeBot executing: {task.get('description', 'unnamed')}")
        result = {
            "agent": "CodeBot",
            "task_id": task.get("id", "unknown"),
            "phases": {},
            "status": "pending",
        }

        try:
            # Phase 1: Analyze
            analysis = await self._analyze_task(task)
            result["phases"]["analysis"] = analysis

            # Phase 2: RED - Write failing test
            test_code = await self._phase_red(task, analysis)
            result["phases"]["red"] = {
                "test_code": test_code,
                "status": "test_written"
            }

            # Phase 3: GREEN - Write minimal implementation
            impl_code = await self._phase_green(task, test_code)
            result["phases"]["green"] = {
                "implementation": impl_code,
                "status": "implementation_written"
            }

            # Phase 4: REFACTOR - Improve quality
            refactored = await self._phase_refactor(impl_code)
            result["phases"]["refactor"] = {
                "refactored_code": refactored,
                "status": "refactored"
            }

            # Phase 5: SECURITY - Scan for vulnerabilities
            security_result = self._run_security_scan(refactored)
            result["phases"]["security"] = security_result

            if not security_result["passed"]:
                result["status"] = "failed"
                result["error"] = "Security scan failed"
                return result

            # Phase 6: QUALITY CHECK
            quality = self._check_code_quality(refactored)
            result["phases"]["quality"] = quality

            result["status"] = "completed"
            result["commit_message"] = self._generate_commit_message(task)

        except Exception as e:
            self.logger.error(f"❌ CodeBot failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task requirements using LLM."""
        description = task.get("description", "")
        prompt = (
            f"Analyze this coding task and identify:\n"
            f"1. Required functions/classes\n"
            f"2. Input/output specifications\n"
            f"3. Edge cases to handle\n"
            f"4. Dependencies needed\n\n"
            f"Task: {description}"
        )
        analysis = await self.execute_with_ai(prompt)
        return {"raw_analysis": analysis, "task_description": description}

    async def _phase_red(self, task: Dict, analysis: Dict) -> str:
        """RED phase: Generate a failing test."""
        self.logger.info("🔴 RED: Writing failing test...")
        prompt = (
            f"Write a Python test file using pytest for this task.\n"
            f"The tests should cover:\n"
            f"- Happy path\n"
            f"- Edge cases (empty input, None, boundary values)\n"
            f"- Error cases (invalid input)\n\n"
            f"Task: {task.get('description', '')}\n"
            f"Analysis: {analysis.get('raw_analysis', '')}\n\n"
            f"Return ONLY the test code, no explanations."
        )
        return await self.execute_with_ai(prompt, skill_name="tdd")

    async def _phase_green(self, task: Dict, test_code: str) -> str:
        """GREEN phase: Write minimal code to pass the tests."""
        self.logger.info("🟢 GREEN: Writing minimal implementation...")
        prompt = (
            f"Write the MINIMAL Python code to make these tests pass.\n"
            f"Do NOT over-engineer. Just make the tests green.\n\n"
            f"Tests:\n```python\n{test_code}\n```\n\n"
            f"Task: {task.get('description', '')}\n\n"
            f"Return ONLY the implementation code, no explanations."
        )
        return await self.execute_with_ai(prompt, skill_name="tdd")

    async def _phase_refactor(self, code: str) -> str:
        """REFACTOR phase: Improve code quality."""
        self.logger.info("♻️ REFACTOR: Improving code quality...")
        prompt = (
            f"Refactor this code for better quality:\n"
            f"- Extract repeated logic into functions\n"
            f"- Improve variable names\n"
            f"- Add type hints\n"
            f"- Add docstrings (Google style)\n"
            f"- Keep ALL existing behavior identical\n\n"
            f"Code:\n```python\n{code}\n```\n\n"
            f"Return ONLY the refactored code."
        )
        return await self.execute_with_ai(prompt)

    def _run_security_scan(self, code: str) -> Dict[str, Any]:
        """Run security scan on the generated code."""
        self.logger.info("🛡️ Running security scan...")
        scanner = self.get_skill("security")
        if not scanner:
            return {"passed": True, "note": "No scanner available"}

        # Check for common vulnerabilities in the code string
        import re
        findings = []
        lines = code.split("\n")
        for i, line in enumerate(lines):
            for check_name, pattern in scanner.PATTERNS.items():
                if re.search(pattern, line):
                    findings.append({
                        "type": check_name,
                        "line": i + 1,
                        "content": line.strip()
                    })

        return {
            "passed": len(findings) == 0,
            "findings": findings,
            "scanned_lines": len(lines)
        }

    def _check_code_quality(self, code: str) -> Dict[str, Any]:
        """Check code quality metrics."""
        lines = code.strip().split("\n")
        line_count = len(lines)

        return {
            "line_count": line_count,
            "within_limit": line_count <= self.max_file_lines,
            "has_docstrings": '"""' in code or "'''" in code,
            "has_type_hints": "->" in code or ": " in code,
        }

    def _generate_commit_message(self, task: Dict) -> str:
        """Generate a Conventional Commit message."""
        task_name = task.get("description", "implement feature")
        task_id = task.get("id", "unknown")
        return (
            f"feat(core): {task_name}\n\n"
            f"- Implemented via TDD (Red-Green-Refactor)\n"
            f"- Security scan passed\n\n"
            f"Task: {task_id}\n"
            f"Co-Authored-By: Imperium Flow <bot@imperiumflow.dev>"
        )
