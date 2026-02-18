"""
Tests for Board of Directors.
Verifies complexity-based routing, risk assessment, and decision conditions.
"""

import pytest
import asyncio
from src.board.directors import (
    BoardOfDirectors,
    WorkflowProposal,
    BoardDecision,
    DirectorRole,
    RiskLevel,
)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestBoardRouting:
    """Verify Board routes to correct director by complexity."""

    def test_low_complexity_routes_to_coo(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(workflow_type="simple_fix", complexity=2)
        decision = run_async(board.review_workflow(proposal))
        assert decision.approved is True
        assert decision.director == DirectorRole.COO
        assert decision.risk_level == RiskLevel.LOW

    def test_medium_complexity_routes_to_cpo(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(workflow_type="feature", complexity=5)
        decision = run_async(board.review_workflow(proposal))
        assert decision.approved is True
        assert decision.director == DirectorRole.CPO
        assert decision.risk_level == RiskLevel.MEDIUM

    def test_high_complexity_routes_to_cto(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(workflow_type="migration", complexity=7)
        decision = run_async(board.review_workflow(proposal))
        assert decision.approved is True
        assert decision.director == DirectorRole.CTO

    def test_critical_complexity_full_board(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(workflow_type="rewrite", complexity=10)
        decision = run_async(board.review_workflow(proposal))
        assert decision.approved is True
        assert decision.risk_level == RiskLevel.CRITICAL
        assert "rollback_plan_mandatory" in decision.conditions


class TestBoardConditions:
    """Verify Board adds appropriate conditions."""

    def test_cpo_adds_coordination_for_many_agents(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(
            workflow_type="feature",
            complexity=5,
            agents_required=["code_worker", "test_worker", "ui_worker"]
        )
        decision = run_async(board.review_workflow(proposal))
        assert "coordination_checkpoint" in decision.conditions

    def test_cto_adds_integration_test_for_external(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(
            workflow_type="auth",
            complexity=8,
            touches_external_services=True
        )
        decision = run_async(board.review_workflow(proposal))
        assert "integration_test_mandatory" in decision.conditions

    def test_cto_adds_rollback_for_database(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(
            workflow_type="schema_change",
            complexity=7,
            touches_database=True
        )
        decision = run_async(board.review_workflow(proposal))
        assert "migration_rollback_plan" in decision.conditions
        assert decision.risk_level == RiskLevel.HIGH

    def test_critical_adds_security_audit(self):
        board = BoardOfDirectors()
        proposal = WorkflowProposal(workflow_type="infra", complexity=9)
        decision = run_async(board.review_workflow(proposal))
        assert "security_audit_required" in decision.conditions
        assert "cto_final_sign_off" in decision.conditions


class TestBoardHistory:
    """Verify Board tracks decision history."""

    def test_records_decisions(self):
        board = BoardOfDirectors()
        p1 = WorkflowProposal(workflow_type="fix", complexity=1)
        p2 = WorkflowProposal(workflow_type="feature", complexity=6)
        run_async(board.review_workflow(p1))
        run_async(board.review_workflow(p2))
        history = board.get_decision_history()
        assert len(history) == 2
        assert history[0]["director"] == "coo"
        assert history[1]["director"] == "cpo"

    def test_history_has_timestamps(self):
        board = BoardOfDirectors()
        p = WorkflowProposal(workflow_type="test", complexity=3)
        run_async(board.review_workflow(p))
        history = board.get_decision_history()
        assert "timestamp" in history[0]
