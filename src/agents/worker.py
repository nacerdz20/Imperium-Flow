"""
Worker Agent Implementation
Defines the WorkerAgent class, which dynamically adapts its behavior based on a role template.
Used for executing specific types of tasks (Coding, Testing, UI, etc.).
"""

from src.agents.base_agent import BaseAgent
from typing import Dict, Any

class WorkerAgent(BaseAgent):
    """
    وكيل عامل (Worker) متعدد الاستخدامات.
    يتشكل بناءً على القالب (Template) الذي يتم تحميله له.
    """
    
    def __init__(self, name: str, role_template: str):
        super().__init__(name)
        self.role_template = role_template
        # Workers automatically get relevant skills
        self._equip_skills()

    def _equip_skills(self):
        """تجهيز المهارات بناءً على الدور"""
        # إذا كان مبرمجاً، نعطيه مهارات البرمجة
        if "code" in self.role_template.lower() or "tdd" in self.role_template.lower():
            # self.add_skill("tdd", registry.get_skill("tdd"))
            pass

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ المهمة باستخدام التقمص (Role Playing).
        """
        # 1. Prepare the Persona Prompt
        system_prompt = self._fill_template(task)
        
        # 2. Add Superpowers to the context
        # (Enhance the prompt with available tools)
        
        # 3. Analyze & Plan
        # (Use LLM to understand what to do)
        response = await self.execute_with_ai(f"Execute Task: {task['description']}", skill_name=None)
        
        return {"status": "completed", "output": response}

    def _fill_template(self, task: Dict[str, Any]) -> str:
        """ملء القالب بالبيانات الحالية مع قيم افتراضية"""
        defaults = {
            "task_id": "UNKNOWN-ID",
            "task_name": "Unnamed Task",
            "track_id": "General",
            "phase": "Execution",
            "files": "None",
            "acceptance": "None",
            "depends_on": "None",
            "base_worker_protocol": "Standard Protocol",
            "message_bus_path": "/tmp/message_bus", # Default message bus path
            "key_feature": "feature",
            "test_coverage": "unit tests"
        }
        # Merge defaults with task data
        data = {**defaults, **task}
        
        # Manual replacement to avoid issues with code blocks containing {}
        result = self.role_template
        for key, value in data.items():
            result = result.replace(f"{{{key}}}", str(value))
            
        return result
