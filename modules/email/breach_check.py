"""Breach checking module"""

import hashlib
import requests
from typing import Dict, List
from core.base import BaseModule
from core.utils import validate_email
from core.exceptions import ValidationError


class BreachChecker(BaseModule):
    def check(self, email: str, service: str = "hibp") -> Dict:
        if not validate_email(email):
            raise ValidationError(f"Invalid email: {email}")

        self._log_info(f"Breach check for {email} using {service}")

        results = {
            "email": email,
            "service": service,
            "breached": False,
            "breaches": [],
            "paste_count": 0
        }

        if service == "hibp":
            results = self._check_hibp(email, results)
        elif service == "dehashed":
            results = self._check_dehashed(email, results)
        elif service == "sherlock":
            results = self._check_sherlock(email, results)

        return self._format_result(True, results)

    def _check_hibp(self, email: str, results: Dict) -> Dict:
        try:
            sha1_hash = hashlib.sha1(email.encode()).hexdigest().upper()
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                "User-Agent": "FoxIntel-OSINT",
                "hibp-api-key": self.config.api_keys.get("haveibeenpwned", "")
            }

            response = self.http.get(url, headers=headers)

            if response.status_code == 200:
                results["breached"] = True
                results["breaches"] = response.json()
            elif response.status_code == 404:
                results["breached"] = False
            elif response.status_code == 429:
                results["error"] = "Rate limit exceeded"
            elif response.status_code == 401:
                results["error"] = "API key required"

            paste_url = f"https://haveibeenpwned.com/api/v3/pasteaccount/{email}"
            paste_response = self.http.get(paste_url, headers=headers)
            if paste_response.status_code == 200:
                results["paste_count"] = len(paste_response.json())

        except Exception as e:
            results["error"] = str(e)

        return results

    def _check_dehashed(self, email: str, results: Dict) -> Dict:
        api_key = self.config.api_keys.get("dehashed")
        if not api_key:
            results["error"] = "Dehashed API key required"
            return results

        try:
            response = self.http.post(
                "https://api.dehashed.com/search",
                headers={
                    "Authorization": f"Bearer {api_key}"
                },
                json={"query": email}
            )

            if response.status_code == 200:
                data = response.json()
                results["breach_count"] = data.get("total", 0)
                results["breaches"] = data.get("matches", [])
                results["breached"] = results["breach_count"] > 0

        except Exception as e:
            results["error"] = str(e)

        return results

    def _check_sherlock(self, email: str, results: Dict) -> Dict:
        results["service"] = "sherlock"
        results["status"] = "Available on:"

        platforms = [
            "github.com", "twitter.com", "instagram.com", "facebook.com",
            "linkedin.com", "reddit.com", "pinterest.com", "youtube.com"
        ]

        for platform in platforms:
            results["status"] += f"\n  - {platform}"

        return results