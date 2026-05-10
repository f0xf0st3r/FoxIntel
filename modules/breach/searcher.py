"""Breach data searcher module"""

from typing import Dict
from core.base import BaseModule


class BreachSearcher(BaseModule):
    def search(self, query: str) -> Dict:
        self._log_info(f"Breach data search: {query}")

        results = {
            "query": query,
            "matches": [],
            "total_leaks": 0
        }

        results["matches"] = self._search_breach_compilation(query)

        return self._format_result(True, results)

    def _search_breach_compilation(self, query: str) -> list:
        matches = []

        match_types = []

        if "@" in query:
            match_types.append({
                "type": "email_pattern",
                "value": query,
                "confidence": "high"
            })

        return match_types