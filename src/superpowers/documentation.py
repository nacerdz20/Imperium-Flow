"""
Documentation Superpower - Automatic Documentation Generator.
Generates comprehensive documentation from code structure, docstrings,
and architectural patterns.
"""

import logging
from typing import Dict, Any, List


class DocumentationGenerator:
    """
    Superpower that enables agents to auto-generate documentation.
    
    Capabilities:
    - Module documentation from docstrings
    - API reference generation
    - Architecture diagrams (Mermaid)
    - Changelog generation
    """

    def __init__(self):
        self.logger = logging.getLogger("Superpower:Documentation")

    def get_prompt(self) -> str:
        """Return the skill prompt for LLM context."""
        return """
## Documentation Generation Protocol

You have the DOCUMENTATION superpower. When generating documentation:

### Module Documentation
1. Extract all class and function signatures
2. Include docstrings with examples
3. Document parameters, return types, and exceptions
4. Add usage examples for complex APIs

### Architecture Documentation
1. Identify component relationships
2. Generate Mermaid diagrams for:
   - Class hierarchy
   - Data flow
   - Sequence diagrams
3. Document design patterns used

### API Reference
1. List all public endpoints/functions
2. Document request/response formats
3. Include error codes and meanings
4. Provide curl/code examples

### Changelog
1. Group changes by type (feat, fix, docs, refactor)
2. Reference related issues/PRs
3. Note breaking changes prominently
4. Include migration guides for breaking changes

### Output Format
Always use Markdown with:
- Clear heading hierarchy
- Code blocks with language tags
- Tables for structured data
- Mermaid blocks for diagrams
"""

    def generate_module_doc(self, module_info: Dict[str, Any]) -> str:
        """
        Generate documentation for a module.
        
        Args:
            module_info: Dictionary with 'name', 'classes', 'functions', 'docstring'
        
        Returns:
            Markdown documentation string
        """
        name = module_info.get("name", "Unknown")
        docstring = module_info.get("docstring", "No description available.")
        classes = module_info.get("classes", [])
        functions = module_info.get("functions", [])

        doc = f"# {name}\n\n{docstring}\n\n"

        if classes:
            doc += "## Classes\n\n"
            for cls in classes:
                doc += f"### `{cls['name']}`\n\n"
                doc += f"{cls.get('docstring', 'No description.')}\n\n"
                for method in cls.get("methods", []):
                    doc += f"#### `{method['name']}({', '.join(method.get('params', []))})`\n\n"
                    doc += f"{method.get('docstring', '')}\n\n"

        if functions:
            doc += "## Functions\n\n"
            for func in functions:
                doc += f"### `{func['name']}({', '.join(func.get('params', []))})`\n\n"
                doc += f"{func.get('docstring', '')}\n\n"

        return doc

    def generate_architecture_diagram(self, components: List[Dict]) -> str:
        """Generate a Mermaid architecture diagram."""
        diagram = "```mermaid\ngraph TD\n"
        for comp in components:
            name = comp["name"]
            node_id = name.replace(" ", "_")
            diagram += f"    {node_id}[{name}]\n"
            for dep in comp.get("depends_on", []):
                dep_id = dep.replace(" ", "_")
                diagram += f"    {node_id} --> {dep_id}\n"
        diagram += "```\n"
        return diagram
