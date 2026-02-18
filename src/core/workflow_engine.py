#!/usr/bin/env python3
"""
Workflow Engine - محرك سير العمل
"""

import logging
from typing import Dict, Any, List, Set

class WorkflowEngine:
    """محرك سير العمل المسؤول عن إدارة دورة حياة سير العمل"""
    
    def __init__(self):
        self.logger = logging.getLogger("WorkflowEngine")
        
    async def validate_workflow(self, workflow_def: Dict[str, Any]) -> bool:
        """التحقق من صحة تعريف سير العمل"""
        # TODO: implementation
        return True

    def get_ready_tasks(self, tasks: List[Dict], completed_ids: Set[int]) -> List[Dict]:
        """
        Get tasks that are ready to run (dependencies met and not yet completed).
        """
        ready = []
        for task in tasks:
            task_id = task.get("id")
            if task_id in completed_ids:
                continue
            
            deps = task.get("dependencies", [])
            # Check if all dependencies are in completed_ids set
            if all(d in completed_ids for d in deps):
                ready.append(task)
        return ready

    def is_workflow_complete(self, tasks: List[Dict], completed_ids: Set[int]) -> bool:
        """Check if all tasks are completed."""
        task_ids = {t["id"] for t in tasks}
        return task_ids.issubset(completed_ids)
