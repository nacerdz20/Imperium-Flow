"""
اختبارات موسعة لـ AgentManager — board members, agent info, unknown agents.
الهدف: agent_manager.py (93% → 100%)
"""

import pytest
from src.core.agent_manager import AgentManager
from src.agents.base_agent import GenericAgent


class TestAgentManagerExtended:
    def setup_method(self):
        self.am = AgentManager()

    def test_get_agent_registered(self):
        agent = self.am.get_agent("code_worker")
        assert agent.__class__.__name__ == "CodeBot"

    def test_get_agent_unknown_returns_generic(self):
        """سطر 38: الحصول على وكيل غير مسجل يُرجع GenericAgent."""
        agent = self.am.get_agent("nonexistent_type")
        assert isinstance(agent, GenericAgent)

    def test_list_agents(self):
        agents = self.am.list_agents()
        assert "code_worker" in agents
        assert "test_worker" in agents
        assert "ui_worker" in agents
        assert "generic" in agents

    def test_get_board_members(self):
        """سطور 47-48: الحصول على أعضاء مجلس الإدارة."""
        board = self.am.get_board_members()
        assert isinstance(board, dict)
        # ينبغي أن يحتوي على أدوار المجلس المسجلة
        for role in ["cto", "cpo", "cso", "coo", "cxo"]:
            assert role in board

    def test_get_agent_info_structure(self):
        """سطور 79-88: معلومات الوكلاء."""
        info = self.am.get_agent_info()
        assert isinstance(info, dict)
        assert "code_worker" in info
        assert "class" in info["code_worker"]
        assert "skills" in info["code_worker"]
        assert "constraints" in info["code_worker"]
        assert info["code_worker"]["class"] == "CodeBot"

    def test_register_custom_agent(self):
        custom = GenericAgent(name="CustomBot")
        self.am.register_agent("custom", custom)
        assert self.am.get_agent("custom") is custom
