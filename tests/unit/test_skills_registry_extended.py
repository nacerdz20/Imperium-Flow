"""
اختبارات موسعة لـ SkillsRegistry — get_skill ValueError, unknown agent, list methods.
الهدف: skills_registry.py (91% → 100%)
"""

import pytest
from src.core.skills_registry import SkillsRegistry
from src.agents.base_agent import GenericAgent


class TestSkillsRegistryExtended:
    def setup_method(self):
        # Reset singleton for clean tests
        SkillsRegistry._instance = None
        self.registry = SkillsRegistry()

    def test_get_skill_valid(self):
        skill = self.registry.get_skill("tdd")
        assert skill.__class__.__name__ == "TDDExpert"

    def test_get_skill_invalid_raises(self):
        """سطر 67: ValueError عند طلب مهارة غير موجودة."""
        with pytest.raises(ValueError, match="not found"):
            self.registry.get_skill("nonexistent_skill")

    def test_get_skills_for_agent_code_worker(self):
        skills = self.registry.get_skills_for_agent("code_worker")
        assert "tdd" in skills
        assert "security" in skills

    def test_get_skills_for_agent_unknown(self):
        """سطور 79-80: نوع وكيل غير معروف يُرجع قاموساً فارغاً."""
        skills = self.registry.get_skills_for_agent("unknown_type")
        assert skills == {}

    def test_equip_agent(self):
        """سطور 83-87: تجهيز وكيل بالمهارات."""
        agent = GenericAgent(name="Test")
        self.registry.equip_agent(agent, "code_worker")
        assert "tdd" in agent.skills
        assert "security" in agent.skills

    def test_list_skills(self):
        """سطور 89-91: قائمة المهارات."""
        skills = self.registry.list_skills()
        assert "planning" in skills
        assert "debugging" in skills
        assert "tdd" in skills
        assert len(skills) == 8

    def test_list_agent_types(self):
        """سطور 93-95: تعيينات أنواع الوكلاء."""
        types = self.registry.list_agent_types()
        assert "code_worker" in types
        assert "generic" in types
        assert isinstance(types["code_worker"], list)

    def test_singleton_behavior(self):
        reg2 = SkillsRegistry()
        assert reg2 is self.registry

    def test_register_custom_skill(self):
        class CustomSkill:
            pass
        self.registry.register_skill("custom", CustomSkill)
        skill = self.registry.get_skill("custom")
        assert isinstance(skill, CustomSkill)
