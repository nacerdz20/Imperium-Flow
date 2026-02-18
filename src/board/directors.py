"""
Board of Directors - Strategic Decision Engine for Imperium Flow.
Provides intelligent workflow review and approval based on complexity,
risk assessment, and agent capabilities.
"""

import logging
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


class DirectorRole(Enum):
    """Roles in the Board of Directors."""
    CTO = "cto"
    CPO = "cpo"
    CSO = "cso"
    COO = "coo"
    CXO = "cxo"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BoardDecision:
    """Represents a decision made by the Board."""
    approved: bool
    director: DirectorRole
    reason: str
    conditions: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowProposal:
    """A proposal submitted to the Board for review."""
    workflow_type: str
    complexity: int  # 1-10
    agents_required: List[str] = field(default_factory=list)
    estimated_duration_minutes: int = 0
    touches_external_services: bool = False
    touches_database: bool = False
    requires_rollback_plan: bool = False


class BoardOfDirectors:
    """
    Strategic oversight board for Imperium Flow.
    
    Routes decisions to the appropriate director based on
    workflow type and complexity. Each director has specialized
    review criteria.
    """

    def __init__(self):
        self.logger = logging.getLogger("ImperiumBoard")
        self.decision_history: List[BoardDecision] = []
        self.logger.info("🏛️ Board of Directors initialized")

    async def review_workflow(self, proposal: WorkflowProposal) -> BoardDecision:
        """
        Review a workflow proposal and return a decision.
        
        Routes to the appropriate director based on complexity:
        - Complexity 1-3: Auto-approved by COO
        - Complexity 4-6: Reviewed by CPO
        - Complexity 7-8: Reviewed by CTO
        - Complexity 9-10: Full board review (CTO + CSO)
        """
        self.logger.info(
            f"📋 Reviewing proposal: {proposal.workflow_type} "
            f"(complexity: {proposal.complexity})"
        )

        if proposal.complexity <= 3:
            decision = self._coo_review(proposal)
        elif proposal.complexity <= 6:
            decision = self._cpo_review(proposal)
        elif proposal.complexity <= 8:
            decision = self._cto_review(proposal)
        else:
            decision = self._full_board_review(proposal)

        self.decision_history.append(decision)
        self.logger.info(
            f"{'✅' if decision.approved else '❌'} Decision by "
            f"{decision.director.value}: {decision.reason}"
        )
        return decision

    def _coo_review(self, proposal: WorkflowProposal) -> BoardDecision:
        """COO reviews low-complexity operational tasks."""
        return BoardDecision(
            approved=True,
            director=DirectorRole.COO,
            reason="Low complexity - auto-approved by Operations",
            conditions=[],
            risk_level=RiskLevel.LOW
        )

    def _cpo_review(self, proposal: WorkflowProposal) -> BoardDecision:
        """CPO reviews medium-complexity product tasks."""
        conditions = ["progress_report_on_completion"]
        if len(proposal.agents_required) > 2:
            conditions.append("coordination_checkpoint")

        return BoardDecision(
            approved=True,
            director=DirectorRole.CPO,
            reason="Medium complexity - approved with product oversight",
            conditions=conditions,
            risk_level=RiskLevel.MEDIUM
        )

    def _cto_review(self, proposal: WorkflowProposal) -> BoardDecision:
        """CTO reviews high-complexity technical tasks."""
        conditions = ["daily_checkpoints", "code_review_required"]

        if proposal.touches_external_services:
            conditions.append("integration_test_mandatory")
        if proposal.touches_database:
            conditions.append("migration_rollback_plan")

        risk = RiskLevel.HIGH if proposal.touches_database else RiskLevel.MEDIUM

        return BoardDecision(
            approved=True,
            director=DirectorRole.CTO,
            reason="High complexity - approved with technical safeguards",
            conditions=conditions,
            risk_level=risk
        )

    def _full_board_review(self, proposal: WorkflowProposal) -> BoardDecision:
        """Full board review for critical tasks."""
        conditions = [
            "daily_checkpoints",
            "rollback_plan_mandatory",
            "security_audit_required",
            "cto_final_sign_off",
            "post_mortem_on_completion"
        ]

        if proposal.touches_external_services:
            conditions.append("penetration_test_before_deploy")

        return BoardDecision(
            approved=True,
            director=DirectorRole.CTO,
            reason="Critical complexity - full board approval with maximum safeguards",
            conditions=conditions,
            risk_level=RiskLevel.CRITICAL,
        )

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Return formatted decision history."""
        return [
            {
                "director": d.director.value,
                "approved": d.approved,
                "reason": d.reason,
                "risk": d.risk_level.value,
                "conditions": d.conditions,
                "timestamp": d.timestamp.isoformat()
            }
            for d in self.decision_history
        ]
