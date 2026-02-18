"""
Conductor Worker Bridge
Connects the AI WorkerAgent to the Conductor Server.
Acts as a translator between Conductor Tasks and Agent Prompts.
"""

import logging
import asyncio
from typing import Any, Dict

from conductor.client.http.models.task import Task
from conductor.client.http.models.task_result import TaskResult
from conductor.client.http.models.task_result_status import TaskResultStatus
from conductor.client.worker.worker_interface import WorkerInterface
from conductor.client.http.models.task import Task
from conductor.client.http.models.task_result import TaskResult
from conductor.client.http.models.task_result_status import TaskResultStatus

from src.agents.worker import WorkerAgent

class ConductorWorker(WorkerInterface):
    """
    A Conductor Worker that delegates execution to an AI Agent.
    Inherits directly from WorkerInterface to avoid pickling issues in the generic Worker class.
    """
    
    def __init__(self, task_def_name: str, agent: WorkerAgent, poll_interval: float = 100.0, domain: str = None):
        super().__init__(task_def_name) # WorkerInterface __init__ sets task_definition_name
        self.agent = agent
        self.poll_interval = poll_interval
        self.domain = domain
        self.logger = logging.getLogger(f"ConductorWorker.{agent.name}")
        self.thread_count = 1 # Default thread count

    def execute(self, task: Task) -> TaskResult:
        """
        Executes the task using the AI Agent.
        This method is called by the Conductor TaskRunner.
        """
        self.logger.info(f"📥 Received Task: {task.task_def_name} (ID: {task.task_id})")
        
        # 1. Prepare Task Data
        task_input = task.input_data or {}
        # Improve context with task metadata
        task_input['id'] = task.task_id
        task_input['name'] = task.task_def_name
        
        # 2. Execute Agent Logic
        # Since Worker.execute is synchronous but Agent.execute is async,
        # we need to run it in an event loop.
        try:
            # Check if there is already a running loop
            try:
                loop = asyncio.get_running_loop()
                # If we are already in a loop (e.g. main.py is async), 
                # we might need to handle this differently or ensure Worker is running in a separate thread.
                # However, Conductor's TaskRunner typically runs workers in threads.
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the agent
            if asyncio.get_event_loop().is_running():
                 # Should not happen in thread pool executor usually, but if so:
                 # This is tricky without nesting loops.
                 # For now, assuming new loop safe in thread.
                 pass

            # Safe execution
            result = asyncio.run(self.agent.execute(task_input))
            
            self.logger.info(f"✅ Agent Completed Task: {result.get('status')}")

            # 3. Format Result for Conductor
            task_result = self.get_task_result_from_task(task)
            task_result.status = TaskResultStatus.COMPLETED
            task_result.output_data = result.get('output', {})
            
            return task_result

        except Exception as e:
            self.logger.error(f"❌ Agent Failed: {e}", exc_info=True)
            task_result = self.get_task_result_from_task(task)
            task_result.status = TaskResultStatus.FAILED
            task_result.reason_for_incompletion = str(e)
            return task_result
