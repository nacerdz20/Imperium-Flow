#!/usr/bin/env python3
"""
Agent Manager - إدارة الوكلاء
"""

import logging
from typing import Dict, Type, Optional, List
from src.agents.base_agent import BaseAgent, GenericAgent


class AgentManager:
    """مدير الوكلاء المسؤول عن تسجيل واسترجاع الوكلاء"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("AgentManager")
        from src.core.skills_registry import SkillsRegistry
        self.skills_registry = SkillsRegistry()
        self._register_default_agents()
    
    def register_agent(self, name: str, agent: BaseAgent):
        """تسجيل وكيل جديد"""
        self.agents[name] = agent
        self.logger.info(f"Agent registered: {name}")
    
    def get_agent(self, name: str) -> BaseAgent:
        """الحصول على وكيل"""
        if name not in self.agents:
            # إرجاع وكيل افتراضي إذا لم يوجد
            return GenericAgent()
        return self.agents[name]
    
    def list_agents(self) -> List[str]:
        """قائمة جميع الوكلاء"""
        return list(self.agents.keys())

    def get_board_members(self) -> Dict[str, BaseAgent]:
        """الحصول على أعضاء مجلس الإدارة"""
        board_roles = ["cto", "cpo", "cso", "coo", "cxo"]
        return {role: self.get_agent(role) for role in board_roles if role in self.agents}

    def _register_default_agents(self):
        """تسجيل الوكلاء الافتراضيين"""
        # Generic Agent
        self.register_agent("generic", GenericAgent())
        
        # Board Members
        # Loading board configuration
        board_roles = ["cto", "cpo", "cso", "coo", "cxo"]
        for role in board_roles:
            self.register_agent(role, GenericAgent(name=role.upper()))
