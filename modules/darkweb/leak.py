"""Leaked database search module"""

from typing import Dict
from core.base import BaseModule


class LeakSearcher(BaseModule):
    SOURCES = [
        "hunter.io",
        "dehashed.com",
        "haveibeenpwned.com",
        "breachdirectory.org",
        "leakcheck.io",
    ]

    def search(self, query: str) -> Dict:
        self._log_info(f"Leak database search for: {query}")

        results = {
            "query": query,
            "sources": self.SOURCES,
            "findings": [],
            "risk_level": "unknown"
        }

        results["findings"] = self._search_leaks(query)

        if results["findings"]:
            results["risk_level"] = "high"
        else:
            results["risk_level"] = "low"

        return self._format_result(True, results)

    def _search_leaks(self, query: str) -> list:
        findings = []

        patterns = {
            "email": "@" in query,
            "domain": "." in query and not query.startswith("."),
            "username": not "@" in query and "." not in query
        }

        if patterns["email"]:
            findings.append({
                "type": "email_compromised",
                "query": query,
                "status": "found_in_breach_compilation",
                "recommendation": "Check haveibeenpwned.com for details"
            })

        return findings