"""IP geolocation module"""

from typing import Dict
from core.base import BaseModule
from core.utils import validate_ip
from core.exceptions import ValidationError


class IPGeolocator(BaseModule):
    PROVIDERS = ["ipinfo", "ip-api", "ipstack"]

    def locate(self, ip: str) -> Dict:
        if not validate_ip(ip):
            raise ValidationError(f"Invalid IP address: {ip}")

        self._log_info(f"IP geolocation for: {ip}")

        results = {
            "ip": ip,
            "geolocation": {},
            "asn": {},
            "hosting": {},
            "risk": {}
        }

        results["geolocation"] = self._get_geo_from_ipinfo(ip)
        results["asn"] = self._get_asn_info(ip)
        results["hosting"] = self._check_hosting(ip)
        results["risk"] = self._assess_risk(ip, results)

        return self._format_result(True, results)

    def _get_geo_from_ipinfo(self, ip: str) -> Dict:
        try:
            response = self.http.get(f"https://ipinfo.io/{ip}/json")
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country"),
                    "region": data.get("region"),
                    "city": data.get("city"),
                    "coordinates": data.get("loc"),
                    "timezone": data.get("timezone"),
                    "org": data.get("org")
                }
        except:
            pass

        return {}

    def _get_asn_info(self, ip: str) -> Dict:
        try:
            response = self.http.get(f"https://ipinfo.io/{ip}/json")
            if response.status_code == 200:
                data = response.json()
                org = data.get("org", "")
                if "AS" in org:
                    asn = org.split()[0]
                    return {
                        "asn": asn,
                        "provider": " ".join(org.split()[1:])
                    }
        except:
            pass

        return {}

    def _check_hosting(self, ip: str) -> Dict:
        hosting_indicators = ["amazon", "digitalocean", "linode", "vultr", "ovh", "hetzner", "google", "microsoft", "cloudflare", "akamai"]

        try:
            response = self.http.get(f"https://ipinfo.io/{ip}/json")
            if response.status_code == 200:
                org = response.json().get("org", "").lower()
                is_hosting = any(ind in org for ind in hosting_indicators)
                return {
                    "is_hosting_provider": is_hosting,
                    "provider": org if is_hosting else None
                }
        except:
            pass

        return {"is_hosting_provider": False}

    def _assess_risk(self, ip: str, results: Dict) -> Dict:
        risk = {"score": 0, "indicators": []}

        if results["hosting"].get("is_hosting_provider"):
            risk["score"] += 20
            risk["indicators"].append("Hosting provider (VPN/Proxy likely)")

        return risk