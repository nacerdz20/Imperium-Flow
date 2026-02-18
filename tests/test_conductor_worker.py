import unittest
from unittest.mock import MagicMock, patch
from conductor.client.http.models.task import Task
from conductor.client.http.models.task_result_status import TaskResultStatus
from src.integrations.conductor_worker import ConductorWorker
from src.agents.worker import WorkerAgent

class TestConductorWorker(unittest.TestCase):

    def setUp(self):
        # Mock Agent
        self.mock_agent = MagicMock(spec=WorkerAgent)
        self.mock_agent.name = "TestBot"
        # Mock Agent Logic to return a dict
        
        # Create Worker
        self.worker = ConductorWorker("test_task", self.mock_agent)

    def test_execute_success(self):
        # Prepare Task
        task = Task()
        task.task_id = "task-123"
        task.task_def_name = "test_task"
        task.workflow_instance_id = "wf-123"
        task.input_data = {"request": "Write code"}
        
        # Mock Agent Execution result
        async def _mock_execute_success(data):
            return {"status": "completed", "output": {"code": "print('hello')"}}
        
        self.mock_agent.execute.side_effect = _mock_execute_success

        # Execute
        result = self.worker.execute(task)

        # Verify
        self.assertEqual(result.status, TaskResultStatus.COMPLETED)
        self.assertEqual(result.task_id, "task-123")
        self.assertEqual(result.output_data, {"code": "print('hello')"})

    def test_execute_failure(self):
        # Prepare Task
        task = Task()
        task.task_id = "task-456"
        task.task_def_name = "test_task"
        task.workflow_instance_id = "wf-456"
        
        # Mock Agent failure
        async def _mock_execute_fail(data):
            raise Exception("AI Overload")
            
        self.mock_agent.execute.side_effect = _mock_execute_fail

        # Execute
        result = self.worker.execute(task)

        # Verify
        self.assertEqual(result.status, TaskResultStatus.FAILED)
        self.assertIn("AI Overload", result.reason_for_incompletion)

if __name__ == '__main__':
    unittest.main()
