"""
Tests for Specialized Agents.
Verifies that CodeBot, TestBot, DesignBot, IntegrationBot
have distinct skills and behaviors.
"""

import pytest
import asyncio


# ─── Helper to run async tests ───────────────────────────────
def run_async(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ─── Test: Agent Imports ──────────────────────────────────────
class TestAgentImports:
    """Verify all specialized agents can be imported."""

    def test_import_codebot(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        assert bot.name == "CodeBot"

    def test_import_testbot(self):
        from src.agents.testbot import TestBot
        bot = TestBot()
        assert bot.name == "TestBot"

    def test_import_designbot(self):
        from src.agents.designbot import DesignBot
        bot = DesignBot()
        assert bot.name == "DesignBot"

    def test_import_integrationbot(self):
        from src.agents.integrationbot import IntegrationBot
        bot = IntegrationBot()
        assert bot.name == "IntegrationBot"


# ─── Test: CodeBot Specialization ────────────────────────────
class TestCodeBot:
    """Verify CodeBot has TDD-specific skills and constraints."""

    def test_has_tdd_skill(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        assert "tdd" in bot.skills
        assert bot.get_skill("tdd") is not None

    def test_has_security_skill(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        assert "security" in bot.skills

    def test_has_code_analysis_skill(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        assert "code_analysis" in bot.skills

    def test_has_constraints(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        assert len(bot.constraints) > 0
        # Should enforce no code without tests
        assert any("test" in c.lower() for c in bot.constraints)

    def test_generates_commit_message(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        task = {"description": "add user login", "id": "T-001"}
        msg = bot._generate_commit_message(task)
        assert "feat(" in msg
        assert "T-001" in msg
        assert "TDD" in msg

    def test_security_scan_passes_clean_code(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        clean_code = "def hello():\n    return 'world'\n"
        result = bot._run_security_scan(clean_code)
        assert result["passed"] is True

    def test_security_scan_catches_hardcoded_password(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        bad_code = 'password = "super_secret_123"\n'
        result = bot._run_security_scan(bad_code)
        assert result["passed"] is False
        assert len(result["findings"]) > 0

    def test_check_code_quality(self):
        from src.agents.codebot import CodeBot
        bot = CodeBot()
        code = '"""Module doc."""\ndef foo(x: int) -> int:\n    return x + 1\n'
        quality = bot._check_code_quality(code)
        assert quality["has_docstrings"] is True
        assert quality["has_type_hints"] is True
        assert quality["within_limit"] is True


# ─── Test: TestBot Specialization ────────────────────────────
class TestTestBot:
    """Verify TestBot has coverage targets and gap analysis."""

    def test_has_tdd_skill(self):
        from src.agents.testbot import TestBot
        bot = TestBot()
        assert "tdd" in bot.skills

    def test_has_coverage_targets(self):
        from src.agents.testbot import TestBot
        assert TestBot.COVERAGE_TARGETS["business_logic"] == 90
        assert TestBot.COVERAGE_TARGETS["overall"] == 70

    def test_analyze_coverage_with_all_categories(self):
        from src.agents.testbot import TestBot
        bot = TestBot()
        tests = {
            "happy_path": "def test_happy():\n    assert True\n",
            "edge_cases": "def test_edge():\n    assert True\n",
            "error_cases": "def test_error():\n    assert True\n",
            "integration": "def test_integ():\n    assert True\n",
        }
        coverage = bot._analyze_coverage(tests)
        assert coverage["estimated_coverage"] == 100
        assert coverage["meets_targets"] is True

    def test_identify_gaps_missing_categories(self):
        from src.agents.testbot import TestBot
        bot = TestBot()
        coverage = {
            "category_counts": {"happy_path": 3},
            "estimated_coverage": 40,
            "meets_targets": False,
        }
        gaps = bot._identify_gaps(coverage)
        assert len(gaps) > 0
        assert any("edge case" in g.lower() for g in gaps)


# ─── Test: DesignBot Specialization ──────────────────────────
class TestDesignBot:
    """Verify DesignBot validates accessibility."""

    def test_wcag_valid_code(self):
        from src.agents.designbot import DesignBot
        bot = DesignBot()
        good_code = """
        <header aria-label="main header">
            <nav role="navigation" tabindex="0">
                <a href="/" style="color: var(--color-primary)">Home</a>
            </nav>
        </header>
        <main>
            <section>
                <img src="hero.jpg" alt="Hero image" />
            </section>
        </main>
        <style>
        a:focus { outline: 2px solid var(--color-accent); }
        --color-primary: #333;
        @media (min-width: 768px) { }
        </style>
        """
        result = bot._validate_wcag(good_code)
        assert result["score"] > 50

    def test_wcag_catches_missing_aria(self):
        from src.agents.designbot import DesignBot
        bot = DesignBot()
        bad_code = "<div><div>content</div></div>"
        result = bot._validate_wcag(bad_code)
        assert len(result["issues"]) > 0

    def test_design_system_check(self):
        from src.agents.designbot import DesignBot
        bot = DesignBot()
        code_with_tokens = "color: var(--color-primary);"
        result = bot._check_design_system(code_with_tokens)
        assert result["uses_tokens"] is True


# ─── Test: IntegrationBot Specialization ─────────────────────
class TestIntegrationBot:
    """Verify IntegrationBot has circuit breaker and error recovery."""

    def test_circuit_breaker_initially_closed(self):
        from src.agents.integrationbot import IntegrationBot, CircuitState
        bot = IntegrationBot()
        breaker = bot.get_or_create_breaker("test_api")
        assert breaker.state == CircuitState.CLOSED
        assert breaker.can_execute() is True

    def test_circuit_breaker_opens_on_failures(self):
        from src.agents.integrationbot import IntegrationBot, CircuitState
        bot = IntegrationBot()
        breaker = bot.get_or_create_breaker("flaky_api")

        # Record failures up to threshold
        for _ in range(breaker.failure_threshold):
            breaker.record_failure()

        assert breaker.state == CircuitState.OPEN
        assert breaker.can_execute() is False

    def test_circuit_breaker_resets_on_success(self):
        from src.agents.integrationbot import IntegrationBot, CircuitState
        bot = IntegrationBot()
        breaker = bot.get_or_create_breaker("api")
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_success()  # Reset
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_graceful_degradation_with_cache(self):
        from src.agents.integrationbot import IntegrationBot
        bot = IntegrationBot()
        bot.fallback_cache["payment"] = {"status": "cached_ok"}
        result = bot._graceful_degradation({"service": "payment"})
        assert result["source"] == "cache"
        assert result["stale"] is True

    def test_graceful_degradation_without_cache(self):
        from src.agents.integrationbot import IntegrationBot
        bot = IntegrationBot()
        result = bot._graceful_degradation({"service": "unknown"})
        assert result["source"] == "default"
        assert "unavailable" in result["data"]["message"]

    def test_has_security_skill(self):
        from src.agents.integrationbot import IntegrationBot
        bot = IntegrationBot()
        assert "security" in bot.skills


# ─── Test: Agent Manager ─────────────────────────────────────
class TestAgentManager:
    """Verify AgentManager registers specialized agents, not GenericAgent."""

    def test_code_worker_is_codebot(self):
        from src.core.agent_manager import AgentManager
        mgr = AgentManager()
        agent = mgr.get_agent("code_worker")
        assert agent.__class__.__name__ == "CodeBot"

    def test_test_worker_is_testbot(self):
        from src.core.agent_manager import AgentManager
        mgr = AgentManager()
        agent = mgr.get_agent("test_worker")
        assert agent.__class__.__name__ == "TestBot"

    def test_ui_worker_is_designbot(self):
        from src.core.agent_manager import AgentManager
        mgr = AgentManager()
        agent = mgr.get_agent("ui_worker")
        assert agent.__class__.__name__ == "DesignBot"

    def test_integration_worker_is_integrationbot(self):
        from src.core.agent_manager import AgentManager
        mgr = AgentManager()
        agent = mgr.get_agent("integration_worker")
        assert agent.__class__.__name__ == "IntegrationBot"

    def test_unknown_agent_returns_generic(self):
        from src.core.agent_manager import AgentManager
        mgr = AgentManager()
        agent = mgr.get_agent("nonexistent")
        assert agent.__class__.__name__ == "GenericAgent"

    def test_agent_info_shows_skills(self):
        from src.core.agent_manager import AgentManager
        mgr = AgentManager()
        info = mgr.get_agent_info()
        assert "code_worker" in info
        assert len(info["code_worker"]["skills"]) > 0
