"""
Skill Loader System
Responsible for dynamically loading and parsing skill definitions from external sources.
Transforms Markdown-based skill definitions into executable DynamicSkill objects.
"""

import logging
import os
from typing import Dict, Any, Type
from src.agents.base_agent import BaseAgent

class DynamicSkill:
    """
    Represents a skill loaded dynamically at runtime.
    Encapsulates the skill's instructions and prompt logic.
    """
    
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions
        
    def get_prompt(self) -> str:
        """Returns the system prompt associated with this skill."""
        return self.instructions

class SkillLoader:
    """
    Core component for loading skills from the file system.
    Scans directories for 'SKILL.md' files and registers them.
    """
    
    def __init__(self, skills_dir: str):
        self.logger = logging.getLogger("core.SkillLoader")
        self.skills_dir = skills_dir
        
    def load_all_skills(self) -> Dict[str, DynamicSkill]:
        """
        Scans the configured directory and loads all available skills.
        
        Returns:
            Dict[str, DynamicSkill]: A dictionary mapping skill names to DynamicSkill objects.
        """
        loaded_skills = {}
        
        if not os.path.exists(self.skills_dir):
            self.logger.error(f"❌ Skills directory not found: {self.skills_dir}")
            return {}
            
        self.logger.info(f"📂 Scanning for skills in: {self.skills_dir}")
        
        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            md_path = os.path.join(skill_path, "SKILL.md")
            
            if os.path.isdir(skill_path) and os.path.exists(md_path):
                try:
                    with open(md_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Clean Frontmatter (YAML)
                        instructions = self._clean_markdown(content)
                        loaded_skills[skill_name] = DynamicSkill(skill_name, instructions)
                        self.logger.info(f"✅ Loaded skill: {skill_name}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to load {skill_name}: {e}")
                    
        return loaded_skills

    def _clean_markdown(self, content: str) -> str:
        """
        Removes YAML frontmatter from the markdown content.
        
        Args:
            content (str): Raw markdown content.
            
        Returns:
            str: Cleaned markdown content without frontmatter.
        """
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
