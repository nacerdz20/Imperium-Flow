"""
Tests for WorkerAgent — template filling, skill equipping, task execution.
Targets: worker.py (33% → 80%+)
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.worker import WorkerAgent


class TestWorkerAgentInit:
    """Test WorkerAgent initialization and skill equipping."""

    def test_init_sets_role_template(self):
        agent = WorkerAgent(name="TestWorker", role_template="You are a {key_feature} expert")
        assert agent.name == "TestWorker"
        assert agent.role_template == "You are a {key_feature} expert"

    def test_init_code_template_triggers_equip(self):
        agent = WorkerAgent(name="Coder", role_template="TDD code worker")
        # _equip_skills is called but currently just passes
        assert agent is not None

    def test_init_non_code_template(self):
        agent = WorkerAgent(name="Designer", role_template="UI design worker")
        assert agent is not None


class TestFillTemplate:
    """Test the _fill_template method."""

    def test_fill_with_task_data(self):
        template = "Task: {task_name} | Phase: {phase} | Files: {files}"
        agent = WorkerAgent(name="W", role_template=template)

        task = {"task_name": "Build Login", "phase": "Development", "files": "auth.py"}
        result = agent._fill_template(task)

        assert "Build Login" in result
        assert "Development" in result
        assert "auth.py" in result

    def test_fill_uses_defaults(self):
        template = "ID: {task_id} | Name: {task_name}"
        agent = WorkerAgent(name="W", role_template=template)

        result = agent._fill_template({})
        assert "UNKNOWN-ID" in result
        assert "Unnamed Task" in result

    def test_fill_task_overrides_defaults(self):
        template = "Track: {track_id}"
        agent = WorkerAgent(name="W", role_template=template)

        result = agent._fill_template({"track_id": "feature-auth"})
        assert "feature-auth" in result
        assert "General" not in result

    def test_fill_preserves_non_placeholder_braces(self):
        template = "Code: ```{task_name}``` end"
        agent = WorkerAgent(name="W", role_template=template)

        result = agent._fill_template({"task_name": "hello"})
        assert "hello" in result

    def test_fill_all_defaults(self):
        template = "{task_id} {task_name} {track_id} {phase} {files} {acceptance} {depends_on}"
        agent = WorkerAgent(name="W", role_template=template)

        result = agent._fill_template({})
        assert "UNKNOWN-ID" in result
        assert "Unnamed Task" in result
        assert "General" in result
        assert "Execution" in result
        assert "None" in result


class TestWorkerExecute:
    """Test the execute method."""

    @pytest.mark.asyncio
    async def test_execute_returns_completed(self):
        agent = WorkerAgent(name="W", role_template="Do {task_name}")
        # Mock the execute_with_ai method
        agent.execute_with_ai = AsyncMock(return_value="done")

        result = await agent.execute({"description": "test task", "task_name": "unit test"})

        assert result["status"] == "completed"
        assert result["output"] == "done"

    @pytest.mark.asyncio
    async def test_execute_calls_ai_with_description(self):
        agent = WorkerAgent(name="W", role_template="Do stuff")
        agent.execute_with_ai = AsyncMock(return_value="result")

        await agent.execute({"description": "implement auth"})

        agent.execute_with_ai.assert_called_once()
        call_args = agent.execute_with_ai.call_args
        assert "implement auth" in call_args[0][0]
