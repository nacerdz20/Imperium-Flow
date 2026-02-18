"""
Tests for Imperium Metrics — Task tracking, Dashboard, Trends.
"""

import pytest
import time
from src.core.metrics import ImperiumMetrics, TaskMetric


class TestTaskMetric:
    """Test TaskMetric dataclass."""

    def test_duration_when_finished(self):
        m = TaskMetric(task_id="t1", agent_name="bot", task_type="test")
        m.started_at = 100.0
        m.finished_at = 105.5
        assert m.duration_seconds == 5.5

    def test_duration_when_running(self):
        m = TaskMetric(task_id="t1", agent_name="bot", task_type="test")
        # Not finished yet — should be > 0
        assert m.duration_seconds > 0


class TestImperiumMetrics:
    """Test ImperiumMetrics tracking and dashboard."""

    def test_start_and_complete_task(self):
        metrics = ImperiumMetrics()
        metrics.start_task("t1", "codebot", "implement")
        assert "t1" in metrics.active_tasks
        metrics.complete_task("t1", success=True)
        assert "t1" not in metrics.active_tasks
        assert len(metrics.metrics) == 1
        assert metrics.metrics[0].success is True

    def test_complete_with_error(self):
        metrics = ImperiumMetrics()
        metrics.start_task("t1", "bot", "task")
        metrics.complete_task("t1", success=False, error="timeout")
        assert metrics.metrics[0].success is False
        assert metrics.metrics[0].error == "timeout"
        assert metrics.error_counts["timeout"] == 1

    def test_complete_unknown_task_is_safe(self):
        metrics = ImperiumMetrics()
        # Should not raise
        metrics.complete_task("nonexistent")
        assert len(metrics.metrics) == 0

    def test_get_agent_stats_empty(self):
        metrics = ImperiumMetrics()
        stats = metrics.get_agent_stats("bot")
        assert stats["total_tasks"] == 0

    def test_get_agent_stats_with_data(self):
        metrics = ImperiumMetrics()
        for i in range(5):
            metrics.start_task(f"t{i}", "codebot", "implement")
            metrics.complete_task(f"t{i}", success=(i < 4))  # 4 success, 1 fail

        stats = metrics.get_agent_stats("codebot")
        assert stats["total_tasks"] == 5
        assert stats["success_count"] == 4
        assert stats["failure_count"] == 1
        assert stats["success_rate"] == 80.0
        assert "avg_duration_seconds" in stats

    def test_get_dashboard_overview(self):
        metrics = ImperiumMetrics()
        metrics.start_task("t1", "codebot", "fix")
        metrics.complete_task("t1", success=True)
        metrics.start_task("t2", "testbot", "test")
        metrics.complete_task("t2", success=False, error="assertion")
        metrics.start_task("t3", "codebot", "refactor")
        # t3 is still active

        dashboard = metrics.get_dashboard()
        assert dashboard["overview"]["total_tasks"] == 2
        assert dashboard["overview"]["total_success"] == 1
        assert dashboard["overview"]["total_failures"] == 1
        assert dashboard["overview"]["active_tasks"] == 1
        assert "codebot" in dashboard["agents"]
        assert "testbot" in dashboard["agents"]
        assert dashboard["task_distribution"]["codebot"] == 1

    def test_dashboard_empty(self):
        metrics = ImperiumMetrics()
        dashboard = metrics.get_dashboard()
        assert dashboard["overview"]["total_tasks"] == 0
        assert dashboard["overview"]["overall_success_rate"] == 0

    def test_top_errors(self):
        metrics = ImperiumMetrics()
        for i in range(3):
            metrics.start_task(f"e1-{i}", "bot", "t")
            metrics.complete_task(f"e1-{i}", success=False, error="timeout")
        for i in range(2):
            metrics.start_task(f"e2-{i}", "bot", "t")
            metrics.complete_task(f"e2-{i}", success=False, error="assertion")

        dashboard = metrics.get_dashboard()
        errors = dashboard["top_errors"]
        assert errors[0]["error"] == "timeout"
        assert errors[0]["count"] == 3
        assert errors[1]["error"] == "assertion"
        assert errors[1]["count"] == 2

    def test_get_agent_trend(self):
        metrics = ImperiumMetrics()
        for i in range(15):
            metrics.start_task(f"t{i}", "bot", "task")
            metrics.complete_task(f"t{i}", success=(i % 2 == 0))

        trend = metrics.get_agent_trend("bot", last_n=5)
        assert len(trend) == 5
        assert all("task_id" in t for t in trend)
        assert all("success" in t for t in trend)
        assert all("duration" in t for t in trend)

    def test_trend_empty_agent(self):
        metrics = ImperiumMetrics()
        trend = metrics.get_agent_trend("nonexistent")
        assert trend == []

    def test_multiple_agents_stats(self):
        metrics = ImperiumMetrics()
        metrics.start_task("t1", "codebot", "code")
        metrics.complete_task("t1")
        metrics.start_task("t2", "testbot", "test")
        metrics.complete_task("t2")

        assert metrics.get_agent_stats("codebot")["total_tasks"] == 1
        assert metrics.get_agent_stats("testbot")["total_tasks"] == 1
