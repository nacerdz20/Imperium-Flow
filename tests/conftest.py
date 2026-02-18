"""
Shared fixtures for Imperium Flow test suite.
"""

import pytest
import tempfile
import os


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that is cleaned up after each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for analysis/security tests."""
    path = os.path.join(temp_dir, "sample.py")
    with open(path, "w") as f:
        f.write('''"""Sample module for testing."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

class Calculator:
    """Simple calculator."""

    def multiply(self, x: int, y: int) -> int:
        return x * y

    def divide(self, x: int, y: int) -> float:
        if y == 0:
            raise ValueError("Division by zero")
        return x / y
''')
    return path


@pytest.fixture
def insecure_python_file(temp_dir):
    """Create Python file with known security issues."""
    path = os.path.join(temp_dir, "insecure.py")
    with open(path, "w") as f:
        f.write('''
api_key = "sk-abc123456789abcdef012345"
password = "super_secret_password"
DEBUG = True
result = eval(user_input)
''')
    return path


@pytest.fixture
def sample_workflow_tasks():
    """Return sample tasks for orchestrator tests."""
    return [
        {
            "id": "task-1",
            "agent_type": "code_worker",
            "description": "Implement user login",
        },
        {
            "id": "task-2",
            "agent_type": "test_worker",
            "description": "Write tests for login",
            "depends_on": ["task-1"],
        },
    ]
