"""
Tests for Board of Directors package — routing logic, decision history,
risk assessment, and proposal handling.
Targets: board/__init__.py (57% → 80%+)
"""

import pytest
from src.board import (
    BoardOfDirectors,
    WorkflowProposal,
    BoardDecision,
    DirectorRole,
    RiskLevel,
)


class TestBoardDecision:
    """Test BoardDecision dataclass."""

    def test_create_decision(self):
        d = BoardDecision(
            approved=True,
            director=DirectorRole.CTO,
            reason="Looks good",
        )
        assert d.approved is True
        assert d.director == DirectorRole.CTO
        assert d.risk_level == RiskLevel.LOW  # default
        assert d.conditions == []  # default
        assert d.timestamp is not None

    def test_decision_with_conditions(self):
        d = BoardDecision(
            approved=False,
            director=DirectorRole.CSO,
            reason="Security concern",
            conditions=["pen_test"],
            risk_level=RiskLevel.CRITICAL,
        )
        assert d.conditions == ["pen_test"]
        assert d.risk_level == RiskLevel.CRITICAL


class TestWorkflowProposal:
    """Test WorkflowProposal dataclass."""

    def test_create_minimal(self):
        p = WorkflowProposal(workflow_type="feature", complexity=3)
        assert p.workflow_type == "feature"
        assert p.complexity == 3
        assert p.agents_required == []
        assert p.touches_external_services is False

    def test_create_full(self):
        p = WorkflowProposal(
            workflow_type="deployment",
            complexity=9,
            agents_required=["CodeBot", "TestBot", "IntegrationBot"],
            estimated_duration_minutes=120,
            touches_external_services=True,
            touches_database=True,
            requires_rollback_plan=True,
        )
        assert len(p.agents_required) == 3
        assert p.touches_database is True


class TestBoardRouting:
    """Test how the board routes proposals to the correct director."""

    def setup_method(self):
        self.board = BoardOfDirectors()

    @pytest.mark.asyncio
    async def test_low_complexity_to_coo(self):
        p = WorkflowProposal(workflow_type="fix-typo", complexity=2)
        decision = await self.board.review_workflow(p)
        assert decision.director == DirectorRole.COO
        assert decision.approved is True
        assert decision.risk_level == RiskLevel.LOW

    @pytest.mark.asyncio
    async def test_medium_complexity_to_cpo(self):
        p = WorkflowProposal(workflow_type="add-feature", complexity=5)
        decision = await self.board.review_workflow(p)
        assert decision.director == DirectorRole.CPO
        assert decision.risk_level == RiskLevel.MEDIUM

    @pytest.mark.asyncio
    async def test_cpo_adds_coordination_for_many_agents(self):
        p = WorkflowProposal(
            workflow_type="multi-agent",
            complexity=5,
            agents_required=["A", "B", "C"],
        )
        decision = await self.board.review_workflow(p)
        assert "coordination_checkpoint" in decision.conditions

    @pytest.mark.asyncio
    async def test_high_complexity_to_cto(self):
        p = WorkflowProposal(workflow_type="refactor", complexity=7)
        decision = await self.board.review_workflow(p)
        assert decision.director == DirectorRole.CTO
        assert "code_review_required" in decision.conditions

    @pytest.mark.asyncio
    async def test_cto_adds_integration_test_for_external(self):
        p = WorkflowProposal(
            workflow_type="api",
            complexity=8,
            touches_external_services=True,
        )
        decision = await self.board.review_workflow(p)
        assert "integration_test_mandatory" in decision.conditions

    @pytest.mark.asyncio
    async def test_cto_adds_migration_rollback_for_db(self):
        p = WorkflowProposal(
            workflow_type="migration",
            complexity=7,
            touches_database=True,
        )
        decision = await self.board.review_workflow(p)
        assert "migration_rollback_plan" in decision.conditions
        assert decision.risk_level == RiskLevel.HIGH

    @pytest.mark.asyncio
    async def test_critical_full_board_review(self):
        p = WorkflowProposal(workflow_type="critical-deploy", complexity=10)
        decision = await self.board.review_workflow(p)
        assert decision.risk_level == RiskLevel.CRITICAL
        assert "rollback_plan_mandatory" in decision.conditions
        assert "security_audit_required" in decision.conditions
        assert "cto_final_sign_off" in decision.conditions

    @pytest.mark.asyncio
    async def test_critical_with_external_adds_pen_test(self):
        p = WorkflowProposal(
            workflow_type="critical",
            complexity=9,
            touches_external_services=True,
        )
        decision = await self.board.review_workflow(p)
        assert "penetration_test_before_deploy" in decision.conditions


class TestBoardDecisionHistory:
    """Test decision history tracking."""

    def setup_method(self):
        self.board = BoardOfDirectors()

    @pytest.mark.asyncio
    async def test_empty_history(self):
        assert self.board.get_decision_history() == []

    @pytest.mark.asyncio
    async def test_history_after_reviews(self):
        await self.board.review_workflow(
            WorkflowProposal(workflow_type="a", complexity=1)
        )
        await self.board.review_workflow(
            WorkflowProposal(workflow_type="b", complexity=5)
        )
        history = self.board.get_decision_history()
        assert len(history) == 2
        assert history[0]["director"] == "coo"
        assert history[1]["director"] == "cpo"
        assert "timestamp" in history[0]

    @pytest.mark.asyncio
    async def test_boundary_complexity_3(self):
        p = WorkflowProposal(workflow_type="x", complexity=3)
        d = await self.board.review_workflow(p)
        assert d.director == DirectorRole.COO

    @pytest.mark.asyncio
    async def test_boundary_complexity_6(self):
        p = WorkflowProposal(workflow_type="x", complexity=6)
        d = await self.board.review_workflow(p)
        assert d.director == DirectorRole.CPO

    @pytest.mark.asyncio
    async def test_boundary_complexity_8(self):
        p = WorkflowProposal(workflow_type="x", complexity=8)
        d = await self.board.review_workflow(p)
        assert d.director == DirectorRole.CTO


class TestEnums:
    """Test board enums."""

    def test_director_roles(self):
        assert len(DirectorRole) == 5
        assert DirectorRole.CTO.value == "cto"

    def test_risk_levels(self):
        assert len(RiskLevel) == 4
        assert RiskLevel.CRITICAL.value == "critical"
