#!/usr/bin/env python3
"""
Agent Manager - Manages agent lifecycle and registration.
Registers specialized agents (CodeBot, TestBot, etc.) instead of GenericAgent.
"""

import logging
from typing import Dict, List, Optional
from src.agents.base_agent import BaseAgent, GenericAgent


class AgentManager:
    """
    Agent lifecycle manager.
    
    Registers specialized agents instead of generic ones:
    - CodeBot for code_worker tasks
    - TestBot for test_worker tasks
    - DesignBot for ui_worker tasks
    - IntegrationBot for integration_worker tasks
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("AgentManager")
        from src.core.skills_registry import SkillsRegistry
        self.skills_registry = SkillsRegistry()
        self._register_default_agents()

    def register_agent(self, name: str, agent: BaseAgent):
        """Register an agent."""
        self.agents[name] = agent
        self.logger.info(f"Agent registered: {name} ({agent.__class__.__name__})")

    def get_agent(self, name: str) -> BaseAgent:
        """Get an agent by name/type."""
        if name not in self.agents:
            return GenericAgent()
        return self.agents[name]

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self.agents.keys())

    def get_board_members(self) -> Dict[str, BaseAgent]:
        """Get board member agents."""
        board_roles = ["cto", "cpo", "cso", "coo", "cxo"]
        return {
            role: self.get_agent(role)
            for role in board_roles
            if role in self.agents
        }

    def _register_default_agents(self):
        """Register specialized agents for each role."""
        # Import specialized agents
        from src.agents.codebot import CodeBot
        from src.agents.testbot import TestBot
        from src.agents.designbot import DesignBot
        from src.agents.integrationbot import IntegrationBot

        # Generic fallback
        self.register_agent("generic", GenericAgent())

        # Specialized workers (THE FIX: no more GenericAgent for everything)
        self.register_agent("code_worker", CodeBot())
        self.register_agent("test_worker", TestBot())
        self.register_agent("ui_worker", DesignBot())
        self.register_agent("integration_worker", IntegrationBot())

        # Board Members (use GenericAgent with LLM for advisory role)
        board_roles = ["cto", "cpo", "cso", "coo", "cxo"]
        for role in board_roles:
            agent = GenericAgent(name=role.upper())
            # Equip board members with planning and debugging
            self.skills_registry.equip_agent(agent, "generic")
            self.register_agent(role, agent)

    def get_agent_info(self) -> Dict[str, Dict]:
        """Get info about all registered agents."""
        info = {}
        for name, agent in self.agents.items():
            info[name] = {
                "class": agent.__class__.__name__,
                "skills": list(agent.skills.keys()),
                "constraints": agent.constraints,
            }
        return info
