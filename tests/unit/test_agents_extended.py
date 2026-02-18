"""
Extended agent tests — DesignBot (WCAG, responsive, design system),
TestBot (coverage analysis, gap identification),
IntegrationBot (circuit breaker, retry, fallback, env vars).
Targets: designbot.py (66%→80%), testbot.py (60%→80%), integrationbot.py (51%→80%)
"""

import pytest
import time
from unittest.mock import AsyncMock, patch
from src.agents.designbot import DesignBot
from src.agents.testbot import TestBot
from src.agents.integrationbot import IntegrationBot, CircuitBreaker, CircuitState


# ═══════════════════════════════════════════════════════════
# DesignBot
# ═══════════════════════════════════════════════════════════

class TestDesignBotWCAG:
    """Test DesignBot WCAG validation."""

    def setup_method(self):
        self.bot = DesignBot()

    def test_validate_wcag_all_pass(self):
        code = """
        <header aria-label="main header">
            <nav tabindex="0">Menu</nav>
        </header>
        <main>
            <section style="color: var(--text); :focus { outline: 2px solid blue; }">
                Content
            </section>
        </main>
        <footer>Footer</footer>
        """
        result = self.bot._validate_wcag(code)
        assert result["checks"]["semantic_html"] is True
        assert result["checks"]["aria_labels"] is True
        assert result["checks"]["keyboard_navigation"] is True
        assert result["score"] > 0

    def test_validate_wcag_no_semantic(self):
        code = "<div>Hello</div>"
        result = self.bot._validate_wcag(code)
        assert result["checks"]["semantic_html"] is False
        assert "Missing semantic HTML elements" in result["issues"]

    def test_validate_wcag_no_aria(self):
        code = "<header><button>Click</button></header>"
        result = self.bot._validate_wcag(code)
        assert result["checks"]["aria_labels"] is False
        assert "No ARIA attributes found" in result["issues"]

    def test_validate_wcag_no_keyboard(self):
        code = "<header><div>No keyboard</div></header>"
        result = self.bot._validate_wcag(code)
        assert result["checks"]["keyboard_navigation"] is False

    def test_validate_wcag_no_focus(self):
        code = "<header><div>No focus</div></header>"
        result = self.bot._validate_wcag(code)
        assert result["checks"]["focus_states"] is False

    def test_validate_wcag_hardcoded_colors(self):
        code = '<header style="color: #ff0000; background: #000">Hardcoded</header>'
        result = self.bot._validate_wcag(code)
        assert result["checks"]["no_hardcoded_colors"] is False
        assert any("hardcoded colors" in i for i in result["issues"])

    def test_validate_wcag_images_without_alt(self):
        code = '<header><img src="pic.png"></header>'
        result = self.bot._validate_wcag(code)
        assert result["checks"]["image_alt_text"] is False
        assert any("missing alt text" in i for i in result["issues"])

    def test_validate_wcag_images_with_alt(self):
        code = '<header><img src="pic.png" alt="A picture"></header>'
        result = self.bot._validate_wcag(code)
        assert result["checks"]["image_alt_text"] is True

    def test_validate_wcag_score_calculation(self):
        # All fail = 0 score
        code = "<div>nothing</div>"
        result = self.bot._validate_wcag(code)
        assert result["score"] <= 50


class TestDesignBotResponsive:
    """Test DesignBot responsive design checks."""

    def setup_method(self):
        self.bot = DesignBot()

    def test_responsive_with_breakpoints(self):
        code = "@media (min-width: 768px) { .container { width: 100%; } }"
        result = self.bot._check_responsive(code)
        assert result["all_breakpoints_covered"] is True
        assert result["breakpoints"]["tablet"] is True

    def test_responsive_no_media_queries(self):
        code = ".container { width: 100%; }"
        result = self.bot._check_responsive(code)
        assert result["all_breakpoints_covered"] is False

    def test_responsive_with_max_width(self):
        code = "@media (max-width: 600px) { .col { width: 100%; } }"
        result = self.bot._check_responsive(code)
        assert result["all_breakpoints_covered"] is True


class TestDesignBotDesignSystem:
    """Test DesignBot design system checks."""

    def setup_method(self):
        self.bot = DesignBot()

    def test_uses_css_variables(self):
        code = ".btn { color: var(--primary); }"
        result = self.bot._check_design_system(code)
        assert result["uses_tokens"] is True
        assert result["uses_css_variables"] is True

    def test_defines_tokens(self):
        code = ":root { --color-primary: #007bff; --font-size-lg: 18px; }"
        result = self.bot._check_design_system(code)
        assert result["uses_tokens"] is True
        assert result["defines_tokens"] is True

    def test_no_design_tokens(self):
        code = ".btn { color: red; }"
        result = self.bot._check_design_system(code)
        assert result["uses_tokens"] is False


class TestDesignBotExecute:
    """Test DesignBot execute method."""

    @pytest.mark.asyncio
    async def test_execute_full_flow(self):
        bot = DesignBot()
        bot.execute_with_ai = AsyncMock(return_value=(
            '<header aria-label="h">'
            '<nav tabindex="0" role="nav">M</nav>'
            '</header>'
            '<main><section>C</section></main>'
            '<footer>F</footer>'
            '<style>:focus { outline: 2px; } .x { color: var(--c); }'
            '@media (min-width: 768px) {}</style>'
        ))

        result = await bot.execute({"description": "build nav", "id": "t1"})
        assert result["agent"] == "DesignBot"
        assert result["status"] in ("completed", "needs_review")
        assert "wcag" in result["phases"]
        assert "responsive" in result["phases"]
        assert "design_system" in result["phases"]

    @pytest.mark.asyncio
    async def test_execute_handles_error(self):
        bot = DesignBot()
        bot.execute_with_ai = AsyncMock(side_effect=RuntimeError("LLM down"))

        result = await bot.execute({"description": "fail", "id": "err"})
        assert result["status"] == "failed"
        assert "error" in result


# ═══════════════════════════════════════════════════════════
# TestBot
# ═══════════════════════════════════════════════════════════

class TestTestBotCoverageAnalysis:
    """Test TestBot coverage analysis method."""

    def setup_method(self):
        self.bot = TestBot()

    def test_analyze_coverage_with_all_categories(self):
        tests = {
            "happy_path": "def test_login(): pass\ndef test_register(): pass",
            "edge_cases": "def test_empty_input(): pass",
            "error_cases": "def test_invalid_token(): pass",
            "integration": "def test_full_flow(): pass",
        }
        result = self.bot._analyze_coverage(tests)
        assert result["total_tests"] == 5
        assert result["estimated_coverage"] == 100
        assert result["meets_targets"] is True

    def test_analyze_coverage_empty(self):
        result = self.bot._analyze_coverage({})
        assert result["total_tests"] == 0
        assert result["estimated_coverage"] == 0
        assert result["meets_targets"] is False

    def test_analyze_coverage_happy_only(self):
        tests = {"happy_path": "def test_ok(): pass"}
        result = self.bot._analyze_coverage(tests)
        assert result["estimated_coverage"] == 40
        assert result["meets_targets"] is False

    def test_analyze_coverage_non_string(self):
        tests = {"happy_path": 42}
        result = self.bot._analyze_coverage(tests)
        assert result["category_counts"]["happy_path"] == 0


class TestTestBotGapIdentification:
    """Test TestBot gap identification."""

    def setup_method(self):
        self.bot = TestBot()

    def test_identify_all_gaps(self):
        coverage = {
            "category_counts": {},
            "estimated_coverage": 0,
            "meets_targets": False,
        }
        gaps = self.bot._identify_gaps(coverage)
        assert any("CRITICAL: No happy path" in g for g in gaps)
        assert any("edge case" in g for g in gaps)
        assert any("error case" in g for g in gaps)
        assert any("integration" in g for g in gaps)
        assert any("below target" in g for g in gaps)

    def test_identify_no_gaps(self):
        coverage = {
            "category_counts": {
                "happy_path": 3,
                "edge_cases": 2,
                "error_cases": 1,
                "integration": 1,
            },
            "estimated_coverage": 85,
            "meets_targets": True,
        }
        gaps = self.bot._identify_gaps(coverage)
        assert len(gaps) == 0


class TestTestBotExecute:
    """Test TestBot execute method."""

    @pytest.mark.asyncio
    async def test_execute_full_flow(self):
        bot = TestBot()
        bot.execute_with_ai = AsyncMock(return_value="def test_something(): pass")

        result = await bot.execute({"description": "test auth module", "id": "t1"})
        assert result["agent"] == "TestBot"
        assert result["status"] == "completed"
        assert "analysis" in result["phases"]
        assert "test_plan" in result["phases"]
        assert "coverage" in result["phases"]
        assert "gaps" in result["phases"]

    @pytest.mark.asyncio
    async def test_execute_handles_error(self):
        bot = TestBot()
        bot.execute_with_ai = AsyncMock(side_effect=RuntimeError("Bang"))

        result = await bot.execute({"description": "fail"})
        assert result["status"] == "failed"
        assert "error" in result


# ═══════════════════════════════════════════════════════════
# IntegrationBot — CircuitBreaker
# ═══════════════════════════════════════════════════════════

class TestCircuitBreaker:
    """Test CircuitBreaker standalone."""

    def test_initial_state_closed(self):
        cb = CircuitBreaker(service_name="api")
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True

    def test_record_failure_opens_after_threshold(self):
        cb = CircuitBreaker(service_name="api", failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_open_blocks_execution(self):
        cb = CircuitBreaker(service_name="api", failure_threshold=1, recovery_timeout=9999)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False

    def test_open_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker(service_name="api", failure_threshold=1, recovery_timeout=0.0)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        # recovery_timeout=0 means it should immediately transition
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN

    def test_record_success_resets(self):
        cb = CircuitBreaker(service_name="api", failure_threshold=2)
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED

    def test_half_open_allows_execution(self):
        cb = CircuitBreaker(service_name="api")
        cb.state = CircuitState.HALF_OPEN
        assert cb.can_execute() is True


class TestIntegrationBotMethods:
    """Test IntegrationBot helpers."""

    def setup_method(self):
        self.bot = IntegrationBot()

    def test_get_or_create_breaker_new(self):
        cb = self.bot.get_or_create_breaker("stripe")
        assert cb.service_name == "stripe"
        assert "stripe" in self.bot.circuit_breakers

    def test_get_or_create_breaker_existing(self):
        cb1 = self.bot.get_or_create_breaker("stripe")
        cb2 = self.bot.get_or_create_breaker("stripe")
        assert cb1 is cb2

    def test_graceful_degradation_no_cache(self):
        result = self.bot._graceful_degradation({"service": "unknown_svc"})
        assert result["source"] == "default"
        assert result["stale"] is True

    def test_graceful_degradation_with_cache(self):
        self.bot.fallback_cache["my_api"] = {"data": "cached stuff"}
        result = self.bot._graceful_degradation({"service": "my_api"})
        assert result["source"] == "cache"
        assert result["data"]["data"] == "cached stuff"

    def test_check_env_vars_known_service(self):
        result = self.bot._check_env_vars({"service": "supabase"})
        assert "SUPABASE_URL" in result["required_env_vars"]

    def test_check_env_vars_unknown_service(self):
        result = self.bot._check_env_vars({"service": "custom"})
        assert "CUSTOM_API_KEY" in result["required_env_vars"]

    def test_get_circuit_status_empty(self):
        assert self.bot.get_circuit_status() == {}

    def test_get_circuit_status_with_breakers(self):
        self.bot.get_or_create_breaker("a")
        self.bot.get_or_create_breaker("b")
        status = self.bot.get_circuit_status()
        assert status == {"a": "closed", "b": "closed"}


class TestIntegrationBotExecute:
    """Test IntegrationBot execute with retry."""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        bot = IntegrationBot()
        bot.execute_with_ai = AsyncMock(return_value="ok")

        result = await bot.execute({"description": "call api", "service": "test_svc"})
        assert result["status"] == "completed"
        assert result["recovery_strategy"] == "none_needed"
        assert "test_svc" in bot.fallback_cache

    @pytest.mark.asyncio
    async def test_execute_circuit_open_uses_fallback(self):
        bot = IntegrationBot()
        # Pre-open the circuit
        cb = bot.get_or_create_breaker("broken_svc")
        cb.state = CircuitState.OPEN
        cb.last_failure_time = time.time()
        cb.recovery_timeout = 9999

        bot.execute_with_ai = AsyncMock(return_value="ok")

        result = await bot.execute({"description": "call api", "service": "broken_svc"})
        assert result["status"] == "degraded"
        assert result["recovery_strategy"] == "graceful_degradation"

    @pytest.mark.asyncio
    async def test_execute_handles_exception(self):
        bot = IntegrationBot()
        bot.execute_with_ai = AsyncMock(side_effect=RuntimeError("Network down"))

        result = await bot.execute({"description": "fail", "service": "err_svc"})
        # After all retries exhaust, circuit should have failures recorded
        assert result["status"] in ("failed", "degraded")
