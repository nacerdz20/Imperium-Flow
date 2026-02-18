#!/usr/bin/env python3
"""
Base Agent - الفئة الأساسية لجميع الوكلاء
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """الفئة الأساسية المجردة لجميع الوكلاء"""
    
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        self.skills: Dict[str, Any] = {}
        self.constraints: List[str] = []
        from src.core.llm import LLMClient
        self.llm = LLMClient()
        
    async def execute_with_ai(self, task_description: str, skill_name: str = None) -> str:
        """تنفيذ مهمة باستخدام الذكاء الاصطناعي ومهارة محددة"""
        system_prompt = f"You are agent {self.name}."
        
        if skill_name:
            skill = self.get_skill(skill_name)
            if skill and hasattr(skill, 'get_prompt'):
                system_prompt += "\n\n" + skill.get_prompt()
            elif skill:
                system_prompt += "\n\n" + str(skill)
                
        return await self.llm.generate_response(system_prompt, task_description)

    def add_skill(self, name: str, skill_instance: Any):
        """Add a skill instance to the agent."""
        self.skills[name] = skill_instance
        
    def get_skill(self, name: str) -> Any:
        """Retrieve a skill by name."""
        return self.skills.get(name)
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Any:
        """تنفيذ المهمة - يجب تنفيذها في الفئات الفرعية"""
        pass
    


class GenericAgent(BaseAgent):
    """وكيل عام للمهام البسيطة"""
    
    async def execute(self, task: Dict[str, Any]) -> Any:
        """تنفيذ عام"""
        return {"status": "completed", "agent": self.name, "task": task}
