import pytest
import pytest_asyncio
from src.core.orchestrator import ZNOrchestrator, WorkflowStatus

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = ZNOrchestrator()
    assert orchestrator is not None
    assert orchestrator.active_workflows == {}

@pytest.mark.asyncio
async def test_workflow_execution_flow():
    orchestrator = ZNOrchestrator()
    tasks = [{"id": 1, "action": "test", "agent_type": "generic"}]
    
    context = await orchestrator.execute_workflow(
        name="Test Workflow",
        tasks=tasks,
        parallel=True
    )
    
    assert context.status == WorkflowStatus.COMPLETED
    assert context.name == "Test Workflow"
    assert len(context.results["task_results"]) == 1
    assert context.results["task_results"][0]["status"] == "completed"
