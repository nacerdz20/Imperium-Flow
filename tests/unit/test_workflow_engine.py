"""
اختبارات لـ WorkflowEngine — get_ready_tasks, is_workflow_complete, validate_workflow.
الهدف: workflow_engine.py (90% → 100%)
"""

import pytest
from src.core.workflow_engine import WorkflowEngine


class TestGetReadyTasks:
    def setup_method(self):
        self.engine = WorkflowEngine()

    def test_no_deps_all_ready(self):
        tasks = [
            {"id": "a", "dependencies": []},
            {"id": "b", "dependencies": []},
        ]
        ready = self.engine.get_ready_tasks(tasks, set())
        assert len(ready) == 2

    def test_with_deps_not_met(self):
        tasks = [
            {"id": "a", "dependencies": []},
            {"id": "b", "dependencies": ["a"]},
        ]
        ready = self.engine.get_ready_tasks(tasks, set())
        assert len(ready) == 1
        assert ready[0]["id"] == "a"

    def test_with_deps_met(self):
        tasks = [
            {"id": "a", "dependencies": []},
            {"id": "b", "dependencies": ["a"]},
        ]
        ready = self.engine.get_ready_tasks(tasks, {"a"})
        assert len(ready) == 1
        assert ready[0]["id"] == "b"

    def test_completed_tasks_excluded(self):
        tasks = [{"id": "a", "dependencies": []}]
        ready = self.engine.get_ready_tasks(tasks, {"a"})
        assert len(ready) == 0

    def test_complex_dag(self):
        tasks = [
            {"id": 1, "dependencies": []},
            {"id": 2, "dependencies": [1]},
            {"id": 3, "dependencies": [1]},
            {"id": 4, "dependencies": [2, 3]},
        ]
        ready = self.engine.get_ready_tasks(tasks, {1})
        assert len(ready) == 2
        ids = [t["id"] for t in ready]
        assert 2 in ids and 3 in ids

    def test_no_tasks_missing_deps_field(self):
        tasks = [{"id": "x"}]
        ready = self.engine.get_ready_tasks(tasks, set())
        assert len(ready) == 1


class TestIsWorkflowComplete:
    def setup_method(self):
        self.engine = WorkflowEngine()

    def test_complete(self):
        tasks = [{"id": "a"}, {"id": "b"}]
        assert self.engine.is_workflow_complete(tasks, {"a", "b"}) is True

    def test_incomplete(self):
        tasks = [{"id": "a"}, {"id": "b"}]
        assert self.engine.is_workflow_complete(tasks, {"a"}) is False

    def test_empty(self):
        assert self.engine.is_workflow_complete([], set()) is True


class TestValidateWorkflow:
    @pytest.mark.asyncio
    async def test_validate_returns_true(self):
        engine = WorkflowEngine()
        result = await engine.validate_workflow({"tasks": []})
        assert result is True
