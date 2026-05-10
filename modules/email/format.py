"""Email format pattern finder"""

from typing import Dict, List
from core.base import BaseModule
from core.utils import validate_domain
from core.exceptions import ValidationError


class EmailFormatFinder(BaseModule):
    def find(self, domain: str) -> Dict:
        if not validate_domain(domain):
            raise ValidationError(f"Invalid domain: {domain}")

        self._log_info(f"Finding email format for {domain}")

        results = {
            "domain": domain,
            "patterns": [],
            "discovered_emails": [],
            "confidence": "low"
        }

        results["discovered_emails"] = self._search_mx(domain)
        results["patterns"] = self._analyze_patterns(domain, results["discovered_emails"])

        if results["discovered_emails"]:
            results["confidence"] = "high"
        elif results["patterns"]:
            results["confidence"] = "medium"

        return self._format_result(True, results)

    def _search_mx(self, domain: str) -> List[str]:
        emails = []
        try:
            import dns.resolver
            mx_records = dns.resolver.resolve(domain, "MX")

            for mx in mx_records:
                mx_domain = str(mx.exchange).rstrip(".")

                if "google" in mx_domain:
                    emails.extend(self._guess_google(domain))
                elif "outlook" in mx_domain or "microsoft" in mx_domain:
                    emails.extend(self._guess_microsoft(domain))

        except Exception as e:
            self._log_debug(f"MX lookup failed: {e}")

        return emails

    def _guess_google(self, domain: str) -> List[str]:
        common_names = ["admin", "info", "support", "contact", "sales", "test"]
        return [f"{name}@{domain}" for name in common_names]

    def _guess_microsoft(self, domain: str) -> List[str]:
        common_names = ["admin", "info", "support", "contact", "sales", "test"]
        return [f"{name}@{domain}" for name in common_names]

    def _analyze_patterns(self, domain: str, emails: List[str]) -> List[Dict]:
        patterns = []

        common_patterns = [
            {"name": "first.last", "format": "{first}.{last}@", "example": "john.doe@example.com"},
            {"name": "firstl", "format": "{first}{last}@", "example": "johndoe@example.com"},
            {"name": "flast", "format": "{first[0]}{last}@", "example": "jdoe@example.com"},
            {"name": "last.first", "format": "{last}.{first}@", "example": "doe.john@example.com"},
            {"name": "first_last", "format": "{first}_{last}@", "example": "john_doe@example.com"},
        ]

        for pattern in common_patterns:
            patterns.append({
                "pattern": pattern["name"],
                "example_format": pattern["example"],
                "url_format": f"{pattern['format']}{domain}"
            })

        return patterns