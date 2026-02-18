"""
Integration Tests — Agent Collaboration, Skills Registry, Full System.
"""

import pytest
import asyncio
from src.core.agent_manager import AgentManager
from src.core.skills_registry import SkillsRegistry
from src.core.memory import ImperiumMemory
from src.core.metrics import ImperiumMetrics
from src.core.protocol import MessageBus, ImperiumMessage, AgentType, Priority, IntentType
from src.board.directors import BoardOfDirectors, WorkflowProposal


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestSkillsRegistryIntegration:
    """Verify SkillsRegistry correctly equips agents."""

    def test_codebot_equipped_with_tdd(self):
        mgr = AgentManager()
        agent = mgr.get_agent("code_worker")
        assert "tdd" in agent.skills

    def test_testbot_equipped_with_tdd(self):
        mgr = AgentManager()
        agent = mgr.get_agent("test_worker")
        assert "tdd" in agent.skills

    def test_designbot_equipped_with_code_analysis(self):
        mgr = AgentManager()
        agent = mgr.get_agent("ui_worker")
        assert "code_analysis" in agent.skills

    def test_integrationbot_equipped_with_security(self):
        mgr = AgentManager()
        agent = mgr.get_agent("integration_worker")
        assert "security" in agent.skills


class TestAgentProtocolCommunication:
    """Verify agents can communicate via MessageBus."""

    def test_orchestrator_to_codebot_request(self):
        bus = MessageBus()
        msg = ImperiumMessage(
            sender=AgentType.ORCHESTRATOR,
            receiver=AgentType.CODE_WORKER,
            intent=IntentType.DELEGATE,
            priority=Priority.HIGH,
            payload={"task": "implement login"},
        )
        mid = bus.send(msg)
        received = bus.receive(AgentType.CODE_WORKER)
        assert received is not None
        assert received.message_id == mid
        assert received.payload["task"] == "implement login"

    def test_codebot_reports_to_orchestrator(self):
        bus = MessageBus()
        msg = ImperiumMessage(
            sender=AgentType.CODE_WORKER,
            receiver=AgentType.ORCHESTRATOR,
            intent=IntentType.REPORT,
            payload={"status": "completed", "lines_written": 42},
        )
        bus.send(msg)
        received = bus.receive(AgentType.ORCHESTRATOR)
        assert received.payload["status"] == "completed"

    def test_agent_escalation_to_board(self):
        bus = MessageBus()
        msg = ImperiumMessage(
            sender=AgentType.CODE_WORKER,
            receiver=AgentType.BOARD,
            intent=IntentType.ESCALATE,
            priority=Priority.CRITICAL,
            payload={"issue": "security vulnerability found"},
        )
        escalated = []
        bus.subscribe(AgentType.BOARD, lambda m: escalated.append(m))
        bus.send(msg)
        assert len(escalated) == 1
        assert escalated[0].payload["issue"] == "security vulnerability found"


class TestMemoryMetricsIntegration:
    """Verify Memory and Metrics work together as they would in the orchestrator."""

    def test_metrics_then_memory_workflow(self):
        metrics = ImperiumMetrics()
        memory = ImperiumMemory()

        # Simulate orchestrator tracking a task
        metrics.start_task("t1", "codebot", "implement")
        metrics.complete_task("t1", success=True)

        # Store the result in memory
        memory.store_memory(
            agent_name="codebot",
            category="task_result",
            key="t1",
            value={"status": "completed"},
            success_rate=1.0,
        )

        # Verify both systems tracked it
        stats = metrics.get_agent_stats("codebot")
        assert stats["total_tasks"] == 1
        result = memory.recall("codebot", "task_result", "t1")
        assert result["status"] == "completed"

    def test_cross_agent_learning(self):
        memory = ImperiumMemory()

        # Multiple agents store best practices
        memory.store_memory("codebot", "patterns", "retry", {"strategy": "exponential"}, 0.9)
        memory.store_memory("integrationbot", "patterns", "retry", {"strategy": "linear"}, 0.7)

        # Cross-agent recall finds both
        results = memory.recall_cross_agent("patterns", min_success_rate=0.5)
        assert len(results) == 2


class TestBoardWorkflowIntegration:
    """Verify Board reviews work with real workflow data."""

    def test_simple_task_auto_approved(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(
            workflow_type="bug_fix",
            complexity=2,
            agents_required=["code_worker"],
        )
        decision = run_async(board.review_workflow(proposal))
        assert decision.approved is True
        assert len(decision.conditions) == 0

    def test_complex_task_with_conditions(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(
            workflow_type="database_migration",
            complexity=8,
            agents_required=["code_worker", "integration_worker"],
            touches_database=True,
            touches_external_services=True,
        )
        decision = run_async(board.review_workflow(proposal))
        assert decision.approved is True
        assert "migration_rollback_plan" in decision.conditions
        assert "integration_test_mandatory" in decision.conditions

    def test_full_workflow_simulation(self):
        """Simulate a full workflow: Board Review → Agent Assignment → Metrics → Memory."""
        board = BoardOfDirectors()
        metrics = ImperiumMetrics()
        memory = ImperiumMemory()
        bus = MessageBus()

        # 1. Board reviews
        proposal = WorkflowProposal(workflow_type="feature", complexity=5)
        decision = run_async(board.review_workflow(proposal))
        assert decision.approved is True

        # 2. Orchestrator delegates to agent
        bus.send(ImperiumMessage(
            sender=AgentType.ORCHESTRATOR,
            receiver=AgentType.CODE_WORKER,
            intent=IntentType.DELEGATE,
            payload={"task": "implement feature"},
        ))

        # 3. Agent receives task
        msg = bus.receive(AgentType.CODE_WORKER)
        assert msg is not None

        # 4. Track in metrics
        metrics.start_task("feat-1", "codebot", "implement")
        metrics.complete_task("feat-1", success=True)

        # 5. Store result in memory
        memory.store_memory("codebot", "completed", "feat-1", {"status": "done"}, 1.0)

        # 6. Verify everything tracked
        assert metrics.get_agent_stats("codebot")["success_count"] == 1
        assert memory.recall("codebot", "completed", "feat-1")["status"] == "done"
        assert len(board.get_decision_history()) == 1
        assert bus.get_history() != []
