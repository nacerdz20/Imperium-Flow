"""
Refactoring Superpower - Code Improvement Automation.
Provides agents with strategies and patterns for code refactoring,
including complexity reduction, pattern extraction, and code smell detection.
"""

import logging
from typing import Dict, Any, List


class RefactoringEngine:
    """
    Superpower that enables agents to analyze and refactor code.
    
    Capabilities:
    - Code smell detection
    - Extract Method / Extract Class patterns
    - Dead code identification
    - Duplication analysis
    - Naming improvement suggestions
    """

    def __init__(self):
        self.logger = logging.getLogger("Superpower:Refactoring")
        self.refactoring_patterns = {
            "extract_method": {
                "trigger": "Function exceeds 20 lines",
                "action": "Extract cohesive blocks into named methods",
                "success_rate": 0.94
            },
            "extract_class": {
                "trigger": "Class has more than 5 responsibilities",
                "action": "Split into focused single-responsibility classes",
                "success_rate": 0.88
            },
            "rename_variable": {
                "trigger": "Variable name is unclear (single letter, abbreviation)",
                "action": "Use descriptive, intention-revealing names",
                "success_rate": 0.97
            },
            "remove_dead_code": {
                "trigger": "Unreachable code or unused imports",
                "action": "Remove safely after confirming no side effects",
                "success_rate": 0.99
            },
            "simplify_conditional": {
                "trigger": "Nested if/else deeper than 3 levels",
                "action": "Use early returns, guard clauses, or strategy pattern",
                "success_rate": 0.91
            },
            "introduce_parameter_object": {
                "trigger": "Function has more than 4 parameters",
                "action": "Group related parameters into a dataclass",
                "success_rate": 0.85
            }
        }

    def get_prompt(self) -> str:
        """Return the skill prompt for LLM context."""
        return """
## Refactoring Protocol

You have the REFACTORING superpower. When refactoring code:

### Code Smell Detection
1. **Long Method**: Functions > 20 lines → Extract Method
2. **Large Class**: Classes > 200 lines → Extract Class
3. **Long Parameter List**: > 4 params → Introduce Parameter Object
4. **Duplicate Code**: Similar blocks → Extract shared function
5. **Deep Nesting**: > 3 levels → Guard Clauses / Early Returns
6. **Dead Code**: Unused imports/functions → Remove safely

### Refactoring Workflow
1. **Identify** the code smell using static analysis
2. **Write Tests** covering current behavior (safety net)
3. **Apply** the refactoring pattern
4. **Verify** all tests still pass
5. **Document** the change with clear commit message

### Safety Rules
- NEVER refactor without tests
- NEVER change behavior during refactoring
- Make ONE type of refactoring per commit
- If in doubt, commit the current state and discuss

### Pattern Application Priority
1. Extract Method (safest, highest impact)
2. Rename Variable (easy, improves readability)
3. Remove Dead Code (safe with verification)
4. Simplify Conditional (moderate risk)
5. Extract Class (complex, needs careful planning)
"""

    def detect_smells(self, code_metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Detect code smells based on metrics.
        
        Args:
            code_metrics: Dict with keys like 'line_count', 'complexity',
                         'param_count', 'nesting_depth', etc.
        
        Returns:
            List of detected code smells with recommended actions
        """
        smells = []

        if code_metrics.get("line_count", 0) > 20:
            smells.append({
                "smell": "Long Method",
                "severity": "medium",
                "pattern": "extract_method",
                **self.refactoring_patterns["extract_method"]
            })

        if code_metrics.get("complexity", 0) > 10:
            smells.append({
                "smell": "High Complexity",
                "severity": "high",
                "pattern": "simplify_conditional",
                **self.refactoring_patterns["simplify_conditional"]
            })

        if code_metrics.get("param_count", 0) > 4:
            smells.append({
                "smell": "Long Parameter List",
                "severity": "medium",
                "pattern": "introduce_parameter_object",
                **self.refactoring_patterns["introduce_parameter_object"]
            })

        if code_metrics.get("nesting_depth", 0) > 3:
            smells.append({
                "smell": "Deep Nesting",
                "severity": "high",
                "pattern": "simplify_conditional",
                **self.refactoring_patterns["simplify_conditional"]
            })

        return smells

    def suggest_refactoring(self, smells: List[Dict]) -> List[Dict]:
        """Prioritize and suggest refactoring steps based on detected smells."""
        priority_order = {
            "high": 0,
            "medium": 1,
            "low": 2
        }
        sorted_smells = sorted(
            smells,
            key=lambda s: priority_order.get(s.get("severity", "low"), 2)
        )
        return sorted_smells
