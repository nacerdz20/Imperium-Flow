"""
Example: Security Audit

Demonstrates how to scan a project for security vulnerabilities
using the SecurityScanner superpower.
"""

import os
import tempfile
from src.superpowers.security import SecurityScanner


def main():
    scanner = SecurityScanner()

    # Create sample file with vulnerabilities
    vuln_code = '''
import os

# BAD: Hardcoded API key
api_key = "sk-1234567890abcdefghij"

# BAD: Hardcoded password
DB_PASSWORD = "supersecretpassword123"

# BAD: Using eval
user_input = input("Enter expression: ")
result = eval(user_input)

# BAD: Debug mode in production
DEBUG = True

# GOOD: Using environment variables
safe_key = os.environ.get("API_KEY", "")
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(vuln_code)
        temp_path = f.name

    try:
        findings = scanner.scan_file(temp_path)

        print(f"🔍 Scanned: {temp_path}")
        print(f"⚠️  Found {len(findings)} vulnerability(ies)\n")

        for i, finding in enumerate(findings, 1):
            severity_icon = "🔴" if finding["severity"] == "critical" else "🟡"
            print(f"  {severity_icon} [{i}] {finding['type']}")
            print(f"     Line {finding['line']}: {finding['content'].strip()}")
            print(f"     Severity: {finding['severity']}")
            print()

    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    main()
