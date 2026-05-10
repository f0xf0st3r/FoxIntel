"""Wireless access point lookup module"""

from typing import Dict
from core.base import BaseModule
from core.utils import is_valid_mac
from core.exceptions import ValidationError


class AccessPointLookup(BaseModule):
    def lookup(self, mac: str) -> Dict:
        if not is_valid_mac(mac):
            raise ValidationError(f"Invalid MAC address: {mac}")

        self._log_info(f"Access point lookup for: {mac}")

        results = {
            "mac": mac.upper(),
            "vendor": None,
            "location": {},
            "networks": []
        }

        results["vendor"] = self._get_vendor(mac)
        results["location"] = self._search_location(mac)

        return self._format_result(True, results)

    def _get_vendor(self, mac: str) -> str:
        oui = mac.replace(":", "")[:6].upper()

        vendors = {
            "001122": "Example Vendor Inc",
            "AABBCC": "Test Hardware Co",
            "112233": "Network Devices Ltd"
        }

        return vendors.get(oui.upper(), "Unknown Vendor")

    def _search_location(self, mac: str) -> Dict:
        try:
            response = self.http.get(f"https://api.mylnikov.org/search?bssid={mac}")
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "found":
                    return {
                        "source": "mylnikov.org",
                        "coordinates": data.get("data", {}).get("geo")
                    }
        except:
            pass

        return {"found": False}