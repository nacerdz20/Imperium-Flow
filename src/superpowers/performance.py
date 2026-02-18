"""
Performance Superpower - Code Performance Analyzer.
Provides agents with performance analysis capabilities,
including time complexity estimation, bottleneck detection,
and optimization recommendations.
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PerformanceIssue:
    """Represents a detected performance issue."""
    category: str       # e.g., "algorithm", "io", "memory", "concurrency"
    severity: str       # "low", "medium", "high", "critical"
    description: str
    recommendation: str
    estimated_impact: str  # e.g., "50% reduction in response time"


class PerformanceAnalyzer:
    """
    Superpower that enables agents to analyze and optimize code performance.
    
    Capabilities:
    - Time complexity estimation
    - Bottleneck detection
    - Memory usage analysis
    - I/O optimization suggestions
    - Caching strategy recommendations
    """

    def __init__(self):
        self.logger = logging.getLogger("Superpower:Performance")
        self.optimization_strategies = {
            "caching": {
                "trigger": "Repeated expensive computations",
                "solution": "Implement LRU cache or memoization",
                "impact": "Up to 90% reduction for cached calls"
            },
            "batch_processing": {
                "trigger": "Multiple sequential I/O operations",
                "solution": "Use batch APIs or asyncio.gather",
                "impact": "N-fold speedup for N operations"
            },
            "indexing": {
                "trigger": "Linear search in large datasets",
                "solution": "Use dict/set for O(1) lookups or sorted + bisect",
                "impact": "O(n) → O(1) or O(log n)"
            },
            "lazy_loading": {
                "trigger": "Loading all data upfront",
                "solution": "Load data on demand using generators",
                "impact": "Reduced memory and faster startup"
            },
            "connection_pooling": {
                "trigger": "Creating new connections per request",
                "solution": "Use connection pool (e.g., aiohttp.ClientSession)",
                "impact": "50-80% reduction in connection overhead"
            },
            "async_execution": {
                "trigger": "Blocking I/O in async context",
                "solution": "Use async libraries or run_in_executor",
                "impact": "Better throughput under concurrent load"
            }
        }

    def get_prompt(self) -> str:
        """Return the skill prompt for LLM context."""
        return """
## Performance Analysis Protocol

You have the PERFORMANCE superpower. When analyzing performance:

### Time Complexity Analysis
1. Identify nested loops and their iteration counts
2. Check for hidden O(n) operations (e.g., `in` on lists)
3. Estimate Big-O for critical paths
4. Flag any O(n²) or worse algorithms

### Common Performance Anti-patterns
1. **N+1 Query**: Loading related data in a loop → Use batch/join
2. **Unbounded Growth**: Lists/dicts growing without limits → Add size caps
3. **Synchronous I/O**: Blocking calls in async code → Use async alternatives
4. **String Concatenation**: Building strings in loops → Use join() or StringIO
5. **Repeated Parsing**: Parsing same data multiple times → Cache parsed result

### Optimization Priorities
1. **Algorithm** (biggest impact): Better data structures, reduce complexity
2. **I/O** (common bottleneck): Batch, cache, async
3. **Memory** (scalability): Generators, streaming, cleanup
4. **Concurrency** (throughput): async/await, thread pools

### Measurement First
- ALWAYS measure before optimizing
- Use `time.perf_counter()` for wall time
- Use `tracemalloc` for memory
- Profile before assuming bottleneck location
- Document baseline metrics before changes

### Safety Rules
- Don't optimize prematurely
- Prefer readability over micro-optimization
- Always benchmark before and after changes
- Keep the same test results after optimization
"""

    def analyze(self, code_info: Dict[str, Any]) -> List[PerformanceIssue]:
        """
        Analyze code for performance issues.
        
        Args:
            code_info: Dict with keys like 'has_nested_loops', 'uses_list_search',
                      'has_blocking_io', 'loop_count', etc.
        
        Returns:
            List of detected performance issues with recommendations
        """
        issues = []

        if code_info.get("has_nested_loops", False):
            issues.append(PerformanceIssue(
                category="algorithm",
                severity="high",
                description="Nested loops detected - potential O(n²) complexity",
                recommendation=self.optimization_strategies["indexing"]["solution"],
                estimated_impact=self.optimization_strategies["indexing"]["impact"]
            ))

        if code_info.get("uses_list_search", False):
            issues.append(PerformanceIssue(
                category="algorithm",
                severity="medium",
                description="Linear search in list - O(n) per lookup",
                recommendation="Convert to set/dict for O(1) lookups",
                estimated_impact="O(n) → O(1)"
            ))

        if code_info.get("has_blocking_io", False):
            issues.append(PerformanceIssue(
                category="io",
                severity="high",
                description="Blocking I/O detected in async context",
                recommendation=self.optimization_strategies["async_execution"]["solution"],
                estimated_impact=self.optimization_strategies["async_execution"]["impact"]
            ))

        if code_info.get("repeated_computation", False):
            issues.append(PerformanceIssue(
                category="algorithm",
                severity="medium",
                description="Repeated expensive computation detected",
                recommendation=self.optimization_strategies["caching"]["solution"],
                estimated_impact=self.optimization_strategies["caching"]["impact"]
            ))

        if code_info.get("sequential_io", False):
            issues.append(PerformanceIssue(
                category="io",
                severity="high",
                description="Sequential I/O operations can be parallelized",
                recommendation=self.optimization_strategies["batch_processing"]["solution"],
                estimated_impact=self.optimization_strategies["batch_processing"]["impact"]
            ))

        return issues

    def get_strategies(self) -> Dict[str, Dict]:
        """Return all available optimization strategies."""
        return self.optimization_strategies
