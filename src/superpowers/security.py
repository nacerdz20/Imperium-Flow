"""
Security Scanner Superpower
Basic Static Application Security Testing (SAST) capabilities.
"""

import logging
import re
from typing import List, Dict

class SecurityScanner:
    """
    مهارة الفحص الأمني الساكن (SAST).
    تبحث عن الأنماط الخطرة المعروفة في الكود.
    """
    
    PATTERNS = {
        "api_key": r"(?i)(api_key|apikey|secret|token)\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]",
        "sql_injection": r"(?i)execute\s*\(\s*['\"]select.*%s",
        "hardcoded_password": r"(?i)password\s*=\s*['\"][^'\"]+['\"]",
        "insecure_eval": r"eval\s*\(",
        "debug_true": r"DEBUG\s*=\s*True"
    }

    def __init__(self):
        self.logger = logging.getLogger("Superpowers.Security")

    def scan_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        فحص ملف بحثاً عن الثغرات الأمنية.
        """
        self.logger.info(f"🛡️ Security scan for: {file_path}")
        findings = []
        
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                for check_name, pattern in self.PATTERNS.items():
                    if re.search(pattern, line):
                        findings.append({
                            "type": check_name,
                            "line": i + 1,
                            "content": line.strip(),
                            "severity": "HIGH" if "key" in check_name or "password" in check_name else "MEDIUM"
                        })
        except Exception as e:
            self.logger.error(f"❌ Scan failed for {file_path}: {e}")
            
        return findings
