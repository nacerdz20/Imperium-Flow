"""
Code Analysis Superpower
Provides deep insights into code quality, complexity, and style.
"""

import ast
import logging
from typing import Dict, Any, List

class CodeAnalyzer:
    """
    مهارة تحليل الكود.
    تستخدم AST (Abstract Syntax Tree) لفهم هيكل الكود وحساب التعقيد.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Superpowers.CodeAnalysis")

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        تحليل ملف بايثون واستخراج المقاييس.
        """
        self.logger.info(f"🔍 Analyzing file: {file_path}")
        try:
            with open(file_path, "r") as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            return {
                "loc": len(source.splitlines()),
                "classes": self._count_nodes(tree, ast.ClassDef),
                "functions": self._count_nodes(tree, ast.FunctionDef),
                "imports": self._count_nodes(tree, (ast.Import, ast.ImportFrom)),
                "complexity_score": self._calculate_complexity(tree)
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze {file_path}: {e}")
            return {"error": str(e)}

    def _count_nodes(self, tree: ast.AST, node_type) -> int:
        return len([node for node in ast.walk(tree) if isinstance(node, node_type)])

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """
        حساب تعقيد سايكلوماتيك بسيط (Cyclomatic Complexity).
        """
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Assert, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, (ast.BoolOp)):
                complexity += len(node.values) - 1
        return complexity
