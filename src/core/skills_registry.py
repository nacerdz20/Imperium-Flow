"""
Skills Registry - SuperpowerRegistry Plugin System.
Maps agent types to their required skills and auto-equips
agents on registration.
"""

import logging
from typing import Dict, Any, Type, List
from src.superpowers.planning import SmartPlanner
from src.superpowers.debugging import SystematicDebugger
from src.superpowers.tdd import TDDExpert
from src.superpowers.code_analysis import CodeAnalyzer
from src.superpowers.security import SecurityScanner
from src.superpowers.documentation import DocumentationGenerator
from src.superpowers.refactoring import RefactoringEngine
from src.superpowers.performance import PerformanceAnalyzer


class SkillsRegistry:
    """
    Central registry mapping agent types to their superpowers.
    
    The plugin system that was missing: automatically equips
    agents with the right skills based on their type.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SkillsRegistry, cls).__new__(cls)
            cls._instance.skills = {}
            cls._instance.agent_skill_map = {}
            cls._instance._register_defaults()
        return cls._instance

    def _register_defaults(self):
        """Register all available skills and agent mappings."""
        # Register all skill classes
        self.register_skill("planning", SmartPlanner)
        self.register_skill("debugging", SystematicDebugger)
        self.register_skill("tdd", TDDExpert)
        self.register_skill("code_analysis", CodeAnalyzer)
        self.register_skill("security", SecurityScanner)
        self.register_skill("documentation", DocumentationGenerator)
        self.register_skill("refactoring", RefactoringEngine)
        self.register_skill("performance", PerformanceAnalyzer)

        # Map agent types to their required skills
        self.agent_skill_map = {
            "code_worker": ["tdd", "security", "code_analysis", "refactoring"],
            "test_worker": ["tdd", "code_analysis", "debugging"],
            "ui_worker": ["code_analysis", "documentation"],
            "integration_worker": ["security", "debugging", "performance"],
            "generic": ["planning", "debugging"],
        }

    def register_skill(self, name: str, skill_class: Type):
        """Register a skill class."""
        self.skills[name] = skill_class

    def get_skill(self, name: str) -> Any:
        """Get a new instance of a skill."""
        skill_class = self.skills.get(name)
        if skill_class:
            return skill_class()
        raise ValueError(f"Skill '{name}' not found in registry.")

    def get_skills_for_agent(self, agent_type: str) -> Dict[str, Any]:
        """
        Get all skill instances for a given agent type.
        This is the plugin system: agent_type → {skill_name: skill_instance}
        """
        skill_names = self.agent_skill_map.get(agent_type, [])
        result = {}
        for name in skill_names:
            try:
                result[name] = self.get_skill(name)
            except ValueError:
                pass
        return result

    def equip_agent(self, agent, agent_type: str):
        """Auto-equip an agent with all skills for its type."""
        skills = self.get_skills_for_agent(agent_type)
        for name, skill in skills.items():
            agent.add_skill(name, skill)

    def list_skills(self) -> List[str]:
        """List all registered skill names."""
        return list(self.skills.keys())

    def list_agent_types(self) -> Dict[str, List[str]]:
        """List all agent type → skill mappings."""
        return dict(self.agent_skill_map)
