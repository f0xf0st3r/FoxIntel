"""Domain enumeration module"""

import socket
import dns.resolver
import ipaddress
from typing import List, Dict, Set
from core.base import BaseModule
from core.utils import validate_domain
from core.exceptions import ValidationError


class DomainEnumerator(BaseModule):
    def enumerate(self, domain: str, brute: bool = False, passive: bool = False) -> Dict:
        if not validate_domain(domain):
            raise ValidationError(f"Invalid domain: {domain}")

        self._log_info(f"Starting enumeration for {domain}")

        results = {
            "domain": domain,
            "subdomains": [],
            "dns_records": {},
            "live_hosts": [],
            "info": {}
        }

        results["dns_records"] = self._get_dns_records(domain)
        results["subdomains"] = self._passive_enum(domain)

        if brute:
            results["subdomains"].extend(self._brute_force(domain))

        results["live_hosts"] = self._check_live_hosts(results["subdomains"])
        results["info"]["total_subdomains"] = len(results["subdomains"])
        results["info"]["total_live"] = len(results["live_hosts"])

        return self._format_result(True, results)

    def _get_dns_records(self, domain: str) -> Dict:
        records = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']

        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                records[rtype] = [str(rdata) for rdata in answers]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
                records[rtype] = []

        return records

    def _passive_enum(self, domain: str) -> List[str]:
        subdomains = set()

        crt_api = f"https://crt.sh/?q=%25.{domain}&output=json"
        try:
            response = self.http.get(crt_api)
            if response.status_code == 200:
                import json
                data = json.loads(response.text)
                for entry in data:
                    name = entry.get("name_value", "")
                    for sub in name.split("\n"):
                        if domain in sub:
                            subdomains.add(sub.strip().lower())
        except Exception as e:
            self._log_debug(f"CRT.sh lookup failed: {e}")

        sources = [
            f"https://dns.bufferover.run/dns?q=.{domain}",
            f"https://api.subdomain.center/v1/domain/{domain}",
        ]

        for url in sources:
            try:
                response = self.http.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if "FDNS_A" in data:
                        for record in data["FDNS_A"]:
                            parts = record.split(",")
                            if len(parts) >= 2 and domain in parts[1]:
                                subdomains.add(parts[1].lower())
            except:
                pass

        return list(subdomains)

    def _brute_force(self, domain: str) -> List[str]:
        subdomains = []
        common_subs = [
            "www", "mail", "ftp", "admin", "blog", "dev", "test", "staging",
            "api", "app", "mobile", "secure", "portal", "cdn", "static",
            "assets", "images", "img", "video", "media", "store", "shop",
            "support", "help", "docs", "wiki", "forum", "cloud", "aws",
            "azure", "gcp", "gitlab", "jenkins", "ci", "vpn", "remote"
        ]

        for sub in common_subs:
            target = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(target)
                subdomains.append(target)
                self._log_debug(f"Found: {target} -> {ip}")
            except socket.gaierror:
                pass

        return subdomains

    def _check_live_hosts(self, subdomains: List[str]) -> List[str]:
        live_hosts = []
        for subdomain in subdomains:
            try:
                ip = socket.gethostbyname(subdomain)
                live_hosts.append({"subdomain": subdomain, "ip": ip})
            except socket.gaierror:
                pass
        return live_hosts