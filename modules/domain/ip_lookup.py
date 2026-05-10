"""IP intelligence module"""

import socket
import requests
from typing import Dict, List
from core.base import BaseModule
from core.utils import validate_domain, validate_ip
from core.exceptions import ValidationError


class IPLookup(BaseModule):
    def lookup(self, target: str) -> Dict:
        self._log_info(f"IP intelligence for {target}")

        is_domain = validate_domain(target)
        ip = target if validate_ip(target) else self._resolve_ip(target, is_domain)

        if not ip:
            raise ValidationError(f"Could not resolve: {target}")

        results = {
            "input": target,
            "resolved_ip": ip,
            "asn_info": self._get_asn(ip),
            "geo_location": self._get_geo(ip),
            "reputation": self._check_reputation(ip),
            "reverse_dns": self._reverse_dns(ip),
            "ports": self._quick_port_scan(ip)
        }

        return self._format_result(True, results)

    def _resolve_ip(self, target: str, is_domain: bool) -> str:
        if not is_domain:
            return target
        try:
            return socket.gethostbyname(target)
        except socket.gaierror:
            return None

    def _get_asn(self, ip: str) -> Dict:
        try:
            response = self.http.get(f"https://ipinfo.io/{ip}/json")
            if response.status_code == 200:
                data = response.json()
                return {
                    "asn": data.get("org", "").split()[0] if data.get("org") else None,
                    "org": data.get("org"),
                    "asn_details": data.get("org")
                }
        except:
            pass

        return {"asn": None, "org": None}

    def _get_geo(self, ip: str) -> Dict:
        try:
            response = self.http.get(f"https://ipinfo.io/{ip}/json")
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country"),
                    "region": data.get("region"),
                    "city": data.get("city"),
                    "coordinates": data.get("loc"),
                    "timezone": data.get("timezone")
                }
        except:
            pass

        return {}

    def _check_reputation(self, ip: str) -> Dict:
        checks = {
            "virustotal": f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
            "abuseipdb": f"https://api.abuseipdb.com/api/v2/check",
            "ipspamlist": f"http://www.ipspammer.com/check.php?ip={ip}"
        }

        results = {"clean": True, "details": {}}

        try:
            vt_key = self.config.api_keys.get("virustotal")
            if vt_key:
                vt_response = self.http.get(
                    f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
                    headers={"x-apikey": vt_key}
                )
                if vt_response.status_code == 200:
                    data = vt_response.json()
                    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                    results["details"]["virustotal"] = stats
                    if stats.get("malicious", 0) > 0:
                        results["clean"] = False
        except:
            pass

        return results

    def _reverse_dns(self, ip: str) -> str:
        try:
            hostname = socket.gethostbyaddr(ip)
            return hostname[0]
        except:
            return None

    def _quick_port_scan(self, ip: str) -> List[Dict]:
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 8080, 8443]
        open_ports = []

        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append({"port": port, "state": "open"})
                sock.close()
            except:
                pass

        return open_ports