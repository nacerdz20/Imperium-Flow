"""
اختبارات موسعة لـ SmartPlanner و PlanStep.
الهدف: planning.py (76% → 100%)
"""

import pytest
from src.superpowers.planning import SmartPlanner, PlanStep


class TestPlanStep:
    def test_create_step(self):
        step = PlanStep(id=1, description="Analyze", dependencies=[])
        assert step.id == 1
        assert step.description == "Analyze"
        assert step.agent_type == "generic"

    def test_custom_agent_type(self):
        step = PlanStep(id=2, description="Code", dependencies=[1], agent_type="developer")
        assert step.agent_type == "developer"
        assert step.dependencies == [1]


class TestSmartPlanner:
    def setup_method(self):
        self.planner = SmartPlanner()

    def test_create_plan_returns_list(self):
        plan = self.planner.create_plan("Build auth module")
        assert isinstance(plan, list)
        assert len(plan) == 5

    def test_create_plan_structure(self):
        plan = self.planner.create_plan("Build feature")
        for step in plan:
            assert "id" in step
            assert "description" in step
            assert "dependencies" in step
            assert "agent_type" in step

    def test_create_plan_dependencies_valid(self):
        """التبعيات يجب أن تشير فقط لمهام سابقة."""
        plan = self.planner.create_plan("test")
        ids = {s["id"] for s in plan}
        for step in plan:
            for dep in step["dependencies"]:
                assert dep in ids
                assert dep < step["id"]

    def test_create_plan_with_context(self):
        """السطور 40-78: create_plan مع سياق."""
        plan = self.planner.create_plan("Build", context={"scope": "backend"})
        assert len(plan) == 5  # نفس البنية الحالية

    def test_create_plan_first_step_no_deps(self):
        plan = self.planner.create_plan("x")
        assert plan[0]["dependencies"] == []

    def test_create_plan_last_step_has_deps(self):
        plan = self.planner.create_plan("x")
        assert len(plan[-1]["dependencies"]) > 0

    def test_validate_plan_returns_true(self):
        """السطر 85: validate_plan."""
        plan = self.planner.create_plan("x")
        assert self.planner.validate_plan(plan) is True

    def test_validate_plan_empty(self):
        assert self.planner.validate_plan([]) is True
