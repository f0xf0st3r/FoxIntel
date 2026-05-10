"""SSID lookup module"""

from typing import Dict, List
from core.base import BaseModule


class SSIDLookup(BaseModule):
    def lookup(self, ssid: str) -> Dict:
        self._log_info(f"SSID lookup for: {ssid}")

        results = {
            "ssid": ssid,
            "known_locations": [],
            "related_networks": [],
            "risk_assessment": {}
        }

        results["known_locations"] = self._search_ssid(ssid)
        results["related_networks"] = self._find_related(ssid)
        results["risk_assessment"] = self._assess_ssid_risk(ssid)

        return self._format_result(True, results)

    def _search_ssid(self, ssid: str) -> List[Dict]:
        locations = []

        try:
            response = self.http.get(
                "https://api.wigle.net/api/v2/network/search",
                params={"ssid": ssid}
            )
        except:
            pass

        return locations

    def _find_related(self, ssid: str) -> list:
        return []

    def _assess_ssid_risk(self, ssid: str) -> Dict:
        risk = {"score": 0, "indicators": []}

        common_ssids = ["FBI Van", "Free WiFi", "FREE_INTERNET", "Default", "linksys", "NETGEAR", "dlink"]
        if ssid in common_ssids:
            risk["score"] += 30
            risk["indicators"].append("Common SSID - could be honeypot")

        if any(word in ssid.lower() for word in ["police", "gov", ".gov", "army"]):
            risk["score"] += 50
            risk["indicators"].append("Government-themed SSID - verify legitimacy")

        return risk