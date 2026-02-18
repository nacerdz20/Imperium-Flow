"""
Tests for ZNOrchestrator — workflow lifecycle, status, abort,
planning phase, quality check, board approval, batch execution.
Targets: orchestrator.py (69% → 80%+)
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.orchestrator import ZNOrchestrator, WorkflowStatus, WorkflowContext


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
    ctx = WorkflowContext(name="Abortable", status=WorkflowStatus.EXECUTING)
    orchestrator.active_workflows[ctx.workflow_id] = ctx

    result = await orchestrator.abort_workflow(ctx.workflow_id)
    assert result is True
    assert ctx.status == WorkflowStatus.ABORTED


@pytest.mark.asyncio
async def test_abort_nonexistent_workflow():
    orchestrator = ZNOrchestrator()
    result = await orchestrator.abort_workflow("fake-id")
    assert result is False


@pytest.mark.asyncio
async def test_get_status_nonexistent():
    orchestrator = ZNOrchestrator()
    assert orchestrator.get_status("missing") is None


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


# ═══════════════════════════════════════════════════════════
# Phase: Planning
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_phase_planning_sets_agents():
    orchestrator = ZNOrchestrator()
    ctx = WorkflowContext(name="plan-test")
    tasks = [
        {"id": "t1", "agent_type": "code_worker"},
        {"id": "t2", "agent_type": "test_worker"},
        {"id": "t3", "agent_type": "code_worker"},  # duplicate
    ]
    await orchestrator._phase_planning(ctx, tasks)
    assert ctx.status == WorkflowStatus.PLANNING
    assert "code_worker" in ctx.agents_involved
    assert "test_worker" in ctx.agents_involved
    assert ctx.metadata["planned_tasks"] == 3


@pytest.mark.asyncio
async def test_phase_planning_generic_agent():
    orchestrator = ZNOrchestrator()
    ctx = WorkflowContext(name="generic")
    tasks = [{"id": "t1"}]  # No agent_type
    await orchestrator._phase_planning(ctx, tasks)
    assert "generic" in ctx.agents_involved


# ═══════════════════════════════════════════════════════════
# Phase: Quality Check
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_phase_quality_check_passes():
    orchestrator = ZNOrchestrator()
    ctx = WorkflowContext(name="qc-pass")
    ctx.results = {"complexity_score": 5}
    await orchestrator._phase_quality_check(ctx, ["complexity"])
    assert ctx.quality_report is not None
    assert ctx.quality_report["passed"] is True


@pytest.mark.asyncio
async def test_phase_quality_check_fails():
    orchestrator = ZNOrchestrator()
    ctx = WorkflowContext(name="qc-fail")
    ctx.results = {"coverage": 30}
    await orchestrator._phase_quality_check(ctx, ["code_coverage"])
    assert ctx.status == WorkflowStatus.FAILED
    assert ctx.quality_report["passed"] is False


# ═══════════════════════════════════════════════════════════
# Phase: Completion
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_phase_completion():
    orchestrator = ZNOrchestrator()
    ctx = WorkflowContext(name="done")
    await orchestrator._phase_completion(ctx)
    assert ctx.status == WorkflowStatus.COMPLETED
    assert ctx.updated_at is not None


# ═══════════════════════════════════════════════════════════
# Board Approval
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_board_approval_approved():
    orchestrator = ZNOrchestrator()
    ctx = WorkflowContext(name="board-test")
    ctx.agents_involved = ["CodeBot"]
    ctx.metadata["complexity"] = 3

    approved = await orchestrator._request_board_approval(ctx)
    assert approved is True
    assert "board_conditions" in ctx.metadata
    assert "board_director" in ctx.metadata


@pytest.mark.asyncio
async def test_workflow_with_board_approval():
    orchestrator = ZNOrchestrator()
    plan = [{"id": "t1", "agent_type": "code_worker", "description": "board task"}]
    context = await orchestrator.execute_workflow(
        name="Board WF",
        goal="Test board",
        initial_plan=plan,
        require_board_approval=True,
    )
    assert context.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.ABORTED)


# ═══════════════════════════════════════════════════════════
# Batch Execution + Metrics/Memory
# ═══════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_execute_batch():
    orchestrator = ZNOrchestrator()
    tasks = [
        {"id": "b1", "agent_type": "code_worker", "description": "batch item 1"},
        {"id": "b2", "agent_type": "code_worker", "description": "batch item 2"},
    ]
    results = await orchestrator._execute_batch(tasks)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_execute_single_task_tracks_metrics():
    orchestrator = ZNOrchestrator()
    task = {"id": "m1", "agent_type": "code_worker", "description": "metrics test"}
    result = await orchestrator._execute_single_task(task)
    # Check metrics recorded
    stats = orchestrator.metrics.get_agent_stats("code_worker")
    assert stats["total_tasks"] >= 1


@pytest.mark.asyncio
async def test_execute_single_task_stores_memory():
    orchestrator = ZNOrchestrator()
    task = {"id": "mem1", "agent_type": "code_worker", "description": "memory test"}
    await orchestrator._execute_single_task(task)
    # Check memory stored
    entries = orchestrator.memory.recall_by_category("code_worker", category="task_result")
    assert len(entries) > 0


# ═══════════════════════════════════════════════════════════
# WorkflowContext + WorkflowStatus
# ═══════════════════════════════════════════════════════════

class TestWorkflowContext:
    def test_defaults(self):
        ctx = WorkflowContext()
        assert ctx.status == WorkflowStatus.PENDING
        assert ctx.name == ""
        assert ctx.results == {}
        assert ctx.quality_report is None

    def test_custom_name(self):
        ctx = WorkflowContext(name="My WF")
        assert ctx.name == "My WF"


class TestWorkflowStatusEnum:
    def test_all_statuses(self):
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.PLANNING.value == "planning"
        assert WorkflowStatus.EXECUTING.value == "executing"
        assert WorkflowStatus.QUALITY_CHECK.value == "quality_check"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.ABORTED.value == "aborted"
