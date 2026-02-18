"""
اختبارات موسعة لـ BaseAgent و GenericAgent.
تغطية: execute_with_ai (مع/بدون مهارة)، add_skill، get_skill، GenericAgent.execute.
الهدف: base_agent.py (86% → 100%)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.base_agent import BaseAgent, GenericAgent


class ConcreteAgent(BaseAgent):
    """وكيل اختباري ملموس (لأن BaseAgent مجرد)."""
    async def execute(self, task):
        return {"status": "done", "task": task}


class TestBaseAgentInit:
    def test_default_name(self):
        agent = ConcreteAgent()
        assert agent.name == "BaseAgent"
        assert agent.skills == {}
        assert agent.constraints == []

    def test_custom_name(self):
        agent = ConcreteAgent(name="MyBot")
        assert agent.name == "MyBot"


class TestBaseAgentSkills:
    def test_add_and_get_skill(self):
        agent = ConcreteAgent()
        skill = MagicMock()
        agent.add_skill("planning", skill)
        assert agent.get_skill("planning") is skill

    def test_get_missing_skill(self):
        agent = ConcreteAgent()
        assert agent.get_skill("nonexistent") is None


class TestExecuteWithAI:

    @pytest.mark.asyncio
    async def test_without_skill(self):
        agent = ConcreteAgent(name="TestBot")
        agent.llm.generate_response = AsyncMock(return_value="AI response")
        result = await agent.execute_with_ai("Do something")
        agent.llm.generate_response.assert_called_once()
        assert result == "AI response"

    @pytest.mark.asyncio
    async def test_with_skill_having_get_prompt(self):
        agent = ConcreteAgent(name="TestBot")
        agent.llm.generate_response = AsyncMock(return_value="skill response")
        skill = MagicMock()
        skill.get_prompt.return_value = "I am a planning skill"
        agent.add_skill("planning", skill)

        result = await agent.execute_with_ai("Plan this", skill_name="planning")
        assert result == "skill response"
        # التأكد أن prompt النظام يحتوي على prompt المهارة
        call_args = agent.llm.generate_response.call_args
        system_prompt = call_args[0][0]
        assert "I am a planning skill" in system_prompt

    @pytest.mark.asyncio
    async def test_with_skill_without_get_prompt(self):
        """سطور 28-29: المهارة بدون get_prompt تُحوَّل إلى نص."""
        agent = ConcreteAgent(name="TestBot")
        agent.llm.generate_response = AsyncMock(return_value="str skill response")

        class SimpleSkill:
            def __str__(self):
                return "Simple skill instructions"

        agent.add_skill("simple", SimpleSkill())
        result = await agent.execute_with_ai("Do it", skill_name="simple")
        assert result == "str skill response"
        call_args = agent.llm.generate_response.call_args
        system_prompt = call_args[0][0]
        assert "Simple skill instructions" in system_prompt

    @pytest.mark.asyncio
    async def test_with_nonexistent_skill(self):
        agent = ConcreteAgent(name="TestBot")
        agent.llm.generate_response = AsyncMock(return_value="no skill response")
        result = await agent.execute_with_ai("Do it", skill_name="missing")
        assert result == "no skill response"


class TestGenericAgent:

    @pytest.mark.asyncio
    async def test_execute_returns_completed(self):
        agent = GenericAgent(name="Generic")
        task = {"id": "t1", "description": "simple task"}
        result = await agent.execute(task)
        assert result["status"] == "completed"
        assert result["agent"] == "Generic"
        assert result["task"] == task

    def test_generic_agent_init(self):
        agent = GenericAgent()
        assert agent.name == "BaseAgent"
