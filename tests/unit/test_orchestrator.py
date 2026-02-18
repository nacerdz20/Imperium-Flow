"""
Tests for ZNOrchestrator — workflow lifecycle, status, abort.
"""

import pytest
import asyncio
from src.core.orchestrator import ZNOrchestrator, WorkflowStatus


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = ZNOrchestrator()
    assert orchestrator is not None
    assert orchestrator.active_workflows == {}


@pytest.mark.asyncio
async def test_workflow_execution_creates_context():
    orchestrator = ZNOrchestrator()
    plan = [{"id": "t1", "agent_type": "code_worker", "description": "test task"}]
    context = await orchestrator.execute_workflow(
        name="Test Workflow",
        goal="Validate basic workflow",
        initial_plan=plan,
        parallel=True,
    )
    assert context.name == "Test Workflow"
    assert context.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)


@pytest.mark.asyncio
async def test_workflow_status_tracking():
    orchestrator = ZNOrchestrator()
    plan = [{"id": "t1", "agent_type": "code_worker", "description": "simple"}]
    context = await orchestrator.execute_workflow(
        name="Status Test",
        goal="Track status",
        initial_plan=plan,
    )
    # After completion, should be retrievable
    stored = orchestrator.get_status(context.workflow_id)
    assert stored is not None


@pytest.mark.asyncio
async def test_workflow_abort():
    orchestrator = ZNOrchestrator()
    # Register a workflow manually to test abort
    from src.core.orchestrator import WorkflowContext
    ctx = WorkflowContext(name="Abortable", status=WorkflowStatus.EXECUTING)
    orchestrator.active_workflows[ctx.workflow_id] = ctx

    result = await orchestrator.abort_workflow(ctx.workflow_id)
    assert result is True
    assert ctx.status == WorkflowStatus.ABORTED


@pytest.mark.asyncio
async def test_workflow_with_quality_gates():
    orchestrator = ZNOrchestrator()
    plan = [{"id": "t1", "agent_type": "code_worker", "description": "with gates"}]
    context = await orchestrator.execute_workflow(
        name="QG Test",
        goal="Test quality gates",
        initial_plan=plan,
        quality_gates=["complexity"],
    )
    assert context.quality_report is not None
