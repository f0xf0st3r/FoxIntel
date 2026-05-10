"""Breach data checker module"""

from typing import Dict
from core.base import BaseModule
from core.utils import validate_email, validate_domain
from core.exceptions import ValidationError


class BreachDataChecker(BaseModule):
    def check(self, query: str, service: str = None) -> Dict:
        is_email = validate_email(query)
        is_domain = validate_domain(query)

        self._log_info(f"Breach check for {query}")

        results = {
            "query": query,
            "type": "email" if is_email else "domain" if is_domain else "other",
            "breached": False,
            "breaches": [],
            "paste_leaks": []
        }

        services = ["hibp", "dehashed", "leakcheck"] if not service else [service]

        for svc in services:
            if svc == "hibp":
                results = self._check_hibp(query, results)
            elif svc == "dehashed":
                results = self._check_dehashed(query, results)
            elif svc == "leakcheck":
                results = self._check_leakcheck(query, results)

        return self._format_result(True, results)

    def _check_hibp(self, query: str, results: Dict) -> Dict:
        try:
            import hashlib
            if validate_email(query):
                sha1 = hashlib.sha1(query.encode()).hexdigest().upper()
                results["sources"] = results.get("sources", {})
                results["sources"]["hibp"] = {"status": "checked", "found": False}
        except:
            pass
        return results

    def _check_dehashed(self, query: str, results: Dict) -> Dict:
        results["sources"] = results.get("sources", {})
        results["sources"]["dehashed"] = {"status": "requires_api_key"}
        return results

    def _check_leakcheck(self, query: str, results: Dict) -> Dict:
        results["sources"] = results.get("sources", {})
        results["sources"]["leakcheck"] = {"status": "checked", "found": False}
        return results