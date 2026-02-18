"""
TDD Superpower - The "Test-First" Engine
This superpower enables any agent to become a TDD expert.
It follows the Red-Green-Refactor cycle autonomously.
"""

import subprocess
import os
from typing import Dict, List, Tuple
import logging

class TDDExpert:
    """
    مهارة التطوير القائم على الاختبار (TDD).
    تمنح الوكيل القدرة على:
    1. كتابة اختبارات للفشل (Red).
    2. تنفيذ الكود لتمرير الاختبار (Green).
    3. تحسين الكود (Refactor).
    """

    def __init__(self, work_dir: str = "."):
        self.logger = logging.getLogger("Superpowers.TDD")
        self.work_dir = work_dir

    def generate_test_plan(self, feature_description: str) -> List[str]:
        """
        تقوم بإنشاء قائمة بحالات الاختبار المطلوبة بناءً على الوصف.
        (في الواقع، هذا سيستخدم LLM لإنشاء الكود، هنا سنحاكي المنطق)
        """
        self.logger.info(f"🧪 Generating test plan for: {feature_description}")
        return [
            "test_happy_path",
            "test_edge_case_empty_input",
            "test_edge_case_invalid_input"
        ]

    def run_tests(self, test_file: str) -> Tuple[bool, str]:
        """
        تشغيل الاختبارات وإرجاع النتيجة.
        """
        self.logger.info(f"🏃 Running tests in {test_file}...")
        try:
            result = subprocess.run(
                ["pytest", test_file],
                capture_output=True,
                text=True,
                cwd=self.work_dir,
                timeout=30
            )
            passed = result.returncode == 0
            return passed, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def analyze_test_failure(self, output: str) -> str:
        """
        تحليل سبب فشل الاختبار.
        """
        if "AssertionError" in output:
            return "Logic Error: Assertion failed."
        elif "ImportError" in output:
            return "Dependency Error: Module not found."
        return "Unknown Error"

    # Future: This would interface with an LLM to actually write the code.
    def write_test_code(self, test_plan: List[str], file_path: str) -> str:
        """
        كتابة كود الاختبار (محاكاة).
        """
        code = "import pytest\n\n"
        for test in test_plan:
            code += f"def {test}():\n    assert True\n\n"
        return code
