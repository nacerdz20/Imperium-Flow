"""
Imperium Metrics - Agent Performance Dashboard.
Tracks execution times, success rates, task distribution,
and common errors for all agents in the Imperium system.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class TaskMetric:
    """Metrics for a single task execution."""
    task_id: str
    agent_name: str
    task_type: str
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    success: bool = False
    error: Optional[str] = None

    @property
    def duration_seconds(self) -> float:
        """Calculate execution duration."""
        end = self.finished_at or time.time()
        return end - self.started_at


class ImperiumMetrics:
    """
    Performance monitoring dashboard for Imperium Flow agents.
    
    Tracks:
    - Success rate per agent
    - Average execution time per agent
    - Most common errors
    - Task distribution across agents
    - Real-time performance trends
    """

    def __init__(self):
        self.logger = logging.getLogger("ImperiumMetrics")
        self.metrics: List[TaskMetric] = []
        self.active_tasks: Dict[str, TaskMetric] = {}
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.logger.info("📊 Imperium Metrics initialized")

    def start_task(self, task_id: str, agent_name: str, task_type: str) -> None:
        """Record the start of a task execution."""
        metric = TaskMetric(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type
        )
        self.active_tasks[task_id] = metric
        self.logger.debug(f"⏱️ Started tracking: {agent_name}/{task_id}")

    def complete_task(self, task_id: str, success: bool = True, error: str = None) -> None:
        """Record the completion of a task."""
        metric = self.active_tasks.pop(task_id, None)
        if metric:
            metric.finished_at = time.time()
            metric.success = success
            metric.error = error
            self.metrics.append(metric)

            if error:
                self.error_counts[error] += 1

            status = "✅" if success else "❌"
            self.logger.info(
                f"{status} {metric.agent_name}/{task_id}: "
                f"{metric.duration_seconds:.2f}s"
            )

    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get performance statistics for a specific agent."""
        agent_metrics = [m for m in self.metrics if m.agent_name == agent_name]

        if not agent_metrics:
            return {"agent": agent_name, "total_tasks": 0}

        successes = sum(1 for m in agent_metrics if m.success)
        durations = [m.duration_seconds for m in agent_metrics]

        return {
            "agent": agent_name,
            "total_tasks": len(agent_metrics),
            "success_count": successes,
            "failure_count": len(agent_metrics) - successes,
            "success_rate": round(successes / len(agent_metrics) * 100, 1),
            "avg_duration_seconds": round(sum(durations) / len(durations), 2),
            "min_duration_seconds": round(min(durations), 2),
            "max_duration_seconds": round(max(durations), 2),
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """
        Get a complete dashboard overview.
        Returns stats for all agents, error summary, and task distribution.
        """
        agents = set(m.agent_name for m in self.metrics)
        agent_stats = {agent: self.get_agent_stats(agent) for agent in agents}

        # Task distribution
        distribution = defaultdict(int)
        for m in self.metrics:
            distribution[m.agent_name] += 1

        # Top errors
        top_errors = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        total = len(self.metrics)
        total_success = sum(1 for m in self.metrics if m.success)

        return {
            "overview": {
                "total_tasks": total,
                "total_success": total_success,
                "total_failures": total - total_success,
                "overall_success_rate": round(
                    total_success / total * 100, 1
                ) if total > 0 else 0,
                "active_tasks": len(self.active_tasks)
            },
            "agents": agent_stats,
            "task_distribution": dict(distribution),
            "top_errors": [
                {"error": err, "count": count}
                for err, count in top_errors
            ]
        }

    def get_agent_trend(self, agent_name: str, last_n: int = 10) -> List[Dict]:
        """Get recent execution trend for an agent."""
        agent_metrics = [
            m for m in self.metrics if m.agent_name == agent_name
        ][-last_n:]

        return [
            {
                "task_id": m.task_id,
                "success": m.success,
                "duration": round(m.duration_seconds, 2),
                "error": m.error
            }
            for m in agent_metrics
        ]
