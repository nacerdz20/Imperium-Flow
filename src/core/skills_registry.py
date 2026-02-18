"""
Skills Registry
A central hub for managing and dispensing superpowers to agents.
"""

from typing import Dict, Any, Type
from src.superpowers.planning import SmartPlanner
from src.superpowers.debugging import SystematicDebugger
from src.superpowers.tdd import TDDExpert
from src.superpowers.code_analysis import CodeAnalyzer
from src.superpowers.security import SecurityScanner

class SkillsRegistry:
    """
    سجل المهارات المركزي.
    يسمح بتسجيل واسترجاع القدرات الخارقة (Superpowers).
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SkillsRegistry, cls).__new__(cls)
            cls._instance.skills = {}
            cls._instance._register_defaults()
        return cls._instance
    
    def _register_defaults(self):
        """تسجيل المهارات الافتراضية"""
        self.register_skill("planning", SmartPlanner)
        self.register_skill("debugging", SystematicDebugger)
        self.register_skill("tdd", TDDExpert)
        self.register_skill("code_analysis", CodeAnalyzer)
        self.register_skill("security", SecurityScanner)
        
    def register_skill(self, name: str, skill_class: Type):
        """تسجيل مهارة جديدة"""
        self.skills[name] = skill_class
        
    def get_skill(self, name: str) -> Any:
        """استرجاع نسخة جديدة من المهارة"""
        skill_class = self.skills.get(name)
        if skill_class:
            return skill_class()
        raise ValueError(f"Skill '{name}' not found in registry.")
