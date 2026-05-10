"""Hunter.io email discovery module"""

from typing import Dict, List
from core.base import BaseModule
from core.utils import validate_email, validate_domain
from core.exceptions import ValidationError, APIError


class HunterClient(BaseModule):
    BASE_URL = "https://api.hunter.io/v2"

    def search(self, query: str) -> Dict:
        is_email = validate_email(query)
        is_domain = validate_domain(query)

        self._log_info(f"Hunter.io search for {query}")

        results = {
            "query": query,
            "type": "email" if is_email else "domain",
            "emails": [],
            "domains": [],
            "sources": []
        }

        api_key = self.config.api_keys.get("hunter")
        if not api_key:
            results["error"] = "Hunter.io API key required"
            return self._format_result(False, results)

        try:
            if is_email:
                params = {"email": query, "api_key": api_key}
                url = f"{self.BASE_URL}/email-finder"
            else:
                params = {"domain": query, "api_key": api_key}
                url = f"{self.BASE_URL}/domain-search"

            response = self.http.get(url, params=params)

            if response.status_code == 200:
                data = response.json().get("data", {})

                if is_email:
                    results["discoveries"] = data.get("discoveries", [])
                    results["sources"] = data.get("sources", [])
                else:
                    results["emails"] = data.get("emails", [])
                    results["domains"] = data.get("domain", {}).get("disposable", False)
                    results["sources"] = data.get("sources", [])

            elif response.status_code == 401:
                raise APIError("Invalid Hunter.io API key", status_code=401, api_service="hunter")
            else:
                results["error"] = f"API error: {response.status_code}"

        except Exception as e:
            results["error"] = str(e)

        return self._format_result(True, results)