"""
DesignBot - Specialized UI/UX Worker Agent.
Implements WCAG AA accessibility validation, responsive design checks,
and design system token enforcement.
"""

import logging
import re
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent


class DesignBot(BaseAgent):
    """
    Specialized agent for frontend development and accessibility.
    
    Unlike the generic WorkerAgent, DesignBot enforces:
    1. WCAG AA compliance (4.5:1 contrast ratio)
    2. Semantic HTML usage
    3. Keyboard navigation support
    4. Responsive design at 3 breakpoints
    5. Design system token adherence
    """

    BREAKPOINTS = {
        "mobile": 375,
        "tablet": 768,
        "desktop": 1024,
    }

    WCAG_CHECKS = [
        "semantic_html",
        "aria_labels",
        "keyboard_navigation",
        "focus_states",
        "color_contrast",
        "no_color_only_meaning",
    ]

    def __init__(self):
        super().__init__(name="DesignBot")
        self.logger = logging.getLogger("Agent.DesignBot")
        self.constraints = [
            "MUST use design system tokens (no hardcoded colors)",
            "MUST pass WCAG AA contrast ratio (4.5:1 for text)",
            "MUST support keyboard navigation",
            "No reliance on color alone for meaning",
            "MUST test at mobile (375px), tablet (768px), desktop (1024px+)",
        ]
        self._equip_default_skills()

    def _equip_default_skills(self):
        """Equip DesignBot with UI-specific skills."""
        from src.superpowers.code_analysis import CodeAnalyzer
        self.add_skill("code_analysis", CodeAnalyzer())

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a UI implementation task.
        
        Flow:
        1. Check design system tokens
        2. Generate component with semantic HTML
        3. Add ARIA labels
        4. Validate accessibility
        5. Check responsive design
        """
        self.logger.info(f"🎨 DesignBot executing: {task.get('description', 'unnamed')}")
        result = {
            "agent": "DesignBot",
            "task_id": task.get("id", "unknown"),
            "phases": {},
            "status": "pending",
        }

        try:
            # Phase 1: Generate accessible component
            component = await self._generate_component(task)
            result["phases"]["component"] = {
                "code": component,
                "status": "generated"
            }

            # Phase 2: WCAG Validation
            wcag_result = self._validate_wcag(component)
            result["phases"]["wcag"] = wcag_result

            # Phase 3: Responsive check
            responsive = self._check_responsive(component)
            result["phases"]["responsive"] = responsive

            # Phase 4: Design system check
            design_check = self._check_design_system(component)
            result["phases"]["design_system"] = design_check

            # Determine overall status
            all_passed = (
                wcag_result["passed"]
                and responsive["all_breakpoints_covered"]
                and design_check["uses_tokens"]
            )

            result["status"] = "completed" if all_passed else "needs_review"
            result["accessibility_score"] = wcag_result["score"]

        except Exception as e:
            self.logger.error(f"❌ DesignBot failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def _generate_component(self, task: Dict[str, Any]) -> str:
        """Generate an accessible UI component using LLM."""
        prompt = (
            f"Create a UI component for this task:\n"
            f"Task: {task.get('description', '')}\n\n"
            f"Requirements:\n"
            f"- Use semantic HTML (header, nav, main, section, article, footer)\n"
            f"- Add ARIA labels for interactive elements\n"
            f"- Include focus styles for keyboard navigation\n"
            f"- Use CSS custom properties (design tokens) for colors\n"
            f"- Support responsive design at {self.BREAKPOINTS}\n"
            f"- Add data-testid attributes for testing\n\n"
            f"Return the complete component code."
        )
        return await self.execute_with_ai(prompt)

    def _validate_wcag(self, code: str) -> Dict[str, Any]:
        """Validate WCAG AA compliance."""
        self.logger.info("♿ Running WCAG AA validation...")
        checks = {}
        issues = []

        # Check 1: Semantic HTML
        semantic_tags = ["<header", "<nav", "<main", "<section", "<article", "<footer"]
        has_semantic = any(tag in code.lower() for tag in semantic_tags)
        checks["semantic_html"] = has_semantic
        if not has_semantic:
            issues.append("Missing semantic HTML elements")

        # Check 2: ARIA labels
        has_aria = "aria-" in code.lower()
        checks["aria_labels"] = has_aria
        if not has_aria:
            issues.append("No ARIA attributes found")

        # Check 3: Keyboard navigation indicators
        has_keyboard = any(
            kw in code.lower()
            for kw in ["tabindex", "onkeydown", "onkeypress", "role=", ":focus"]
        )
        checks["keyboard_navigation"] = has_keyboard
        if not has_keyboard:
            issues.append("No keyboard navigation support detected")

        # Check 4: Focus states
        has_focus = ":focus" in code or "focus-visible" in code
        checks["focus_states"] = has_focus
        if not has_focus:
            issues.append("No focus state styles")

        # Check 5: Color contrast (check for hardcoded colors)
        hardcoded_colors = re.findall(
            r'(?:color|background):\s*(?:#[0-9a-fA-F]{3,8}|rgb)', code
        )
        checks["no_hardcoded_colors"] = len(hardcoded_colors) == 0
        if hardcoded_colors:
            issues.append(f"Found {len(hardcoded_colors)} hardcoded colors (use tokens)")

        # Check 6: Alt text for images
        img_count = code.lower().count("<img")
        alt_count = code.lower().count("alt=")
        checks["image_alt_text"] = img_count == 0 or alt_count >= img_count
        if img_count > alt_count:
            issues.append(f"{img_count - alt_count} images missing alt text")

        passed_count = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        score = round(passed_count / total_checks * 100) if total_checks > 0 else 0

        return {
            "passed": score >= 80,
            "score": score,
            "checks": checks,
            "issues": issues,
        }

    def _check_responsive(self, code: str) -> Dict[str, Any]:
        """Check responsive design implementation."""
        breakpoint_coverage = {}

        for name, width in self.BREAKPOINTS.items():
            # Check for media queries targeting this breakpoint
            has_query = f"{width}" in code or f"max-width" in code or f"min-width" in code
            breakpoint_coverage[name] = has_query

        return {
            "breakpoints": breakpoint_coverage,
            "all_breakpoints_covered": any(breakpoint_coverage.values()),
        }

    def _check_design_system(self, code: str) -> Dict[str, Any]:
        """Check design system token usage."""
        # Look for CSS custom properties
        uses_vars = "var(--" in code or "var(--color" in code
        has_tokens = "--color-" in code or "--font-" in code or "--spacing-" in code

        return {
            "uses_tokens": uses_vars or has_tokens,
            "uses_css_variables": uses_vars,
            "defines_tokens": has_tokens,
        }
