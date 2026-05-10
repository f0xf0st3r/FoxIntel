"""WiFi geolocation module"""

from typing import Dict
from core.base import BaseModule
from core.utils import is_valid_mac
from core.exceptions import ValidationError


class WiFiGeolocator(BaseModule):
    WIGLE_API = "https://api.wigle.net/api/v2"

    def locate(self, bssid: str) -> Dict:
        if not is_valid_mac(bssid):
            raise ValidationError(f"Invalid BSSID (MAC address): {bssid}")

        self._log_info(f"WiFi geolocation for: {bssid}")

        results = {
            "bssid": bssid.upper(),
            "location": {},
            "network_info": {},
            "sources": []
        }

        results["sources"] = self._search_wigle(bssid)

        return self._format_result(True, results)

    def _search_wigle(self, bssid: str) -> list:
        sources = [
            {
                "name": "Wigle.net",
                "url": f"https://wigle.net/search?query={bssid}",
                "requires_auth": True
            },
            {
                "name": "Geocoding API",
                "url": f"https://api.mylnikov.org/search?bssid={bssid}",
                "requires_auth": False
            }
        ]

        try:
            response = self.http.get(f"https://api.mylnikov.org/search?bssid={bssid}")
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "found":
                    sources.append({
                        "name": "mylnikov.org",
                        "found": True,
                        "location": data.get("data", {})
                    })
        except:
            pass

        return sources