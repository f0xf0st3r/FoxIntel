"""Email verification module"""

from typing import Dict
from core.base import BaseModule
from core.utils import validate_email
from core.exceptions import ValidationError


class EmailVerifier(BaseModule):
    def verify(self, email: str) -> Dict:
        if not validate_email(email):
            raise ValidationError(f"Invalid email: {email}")

        self._log_info(f"Verifying email: {email}")

        results = {
            "email": email,
            "valid_format": True,
            "disposable": False,
            "deliverable": "unknown",
            "mx_records": [],
            "risk_score": 0
        }

        results["mx_records"] = self._check_mx(email.split("@")[1])
        results["disposable"] = self._check_disposable(email)
        results["risk_score"] = self._calculate_risk(results)

        if results["mx_records"] and not results["disposable"]:
            results["deliverable"] = "likely"

        return self._format_result(True, results)

    def _check_mx(self, domain: str) -> list:
        mx_records = []
        try:
            import dns.resolver
            mx = dns.resolver.resolve(domain, "MX")
            mx_records = [str(r.exchange).rstrip(".") for r in mx]
        except:
            pass
        return mx_records

    def _check_disposable(self, email: str) -> bool:
        disposable_domains = [
            "tempmail.com", "guerrillamail.com", "mailinator.com", "10minutemail.com",
            "throwaway.email", "temp-mail.org", "fakeinbox.com", "trashmail.com"
        ]

        domain = email.split("@")[1].lower()
        return domain in disposable_domains or any(
            domain.endswith(d) for d in disposable_domains
        )

    def _calculate_risk(self, results: Dict) -> int:
        score = 0

        if not results["mx_records"]:
            score += 40

        if results["disposable"]:
            score += 30

        return min(score, 100)