"""WHOIS lookup module"""

import socket
from typing import Dict
from datetime import datetime
from core.base import BaseModule
from core.utils import validate_domain
from core.exceptions import ValidationError


class WhoisLookup(BaseModule):
    def lookup(self, domain: str) -> Dict:
        if not validate_domain(domain):
            raise ValidationError(f"Invalid domain: {domain}")

        self._log_info(f"WHOIS lookup for {domain}")

        whois_data = {
            "domain": domain,
            "registrar": None,
            "registrant": None,
            "nameservers": [],
            "creation_date": None,
            "expiration_date": None,
            "updated_date": None,
            "status": [],
            "dnssec": None
        }

        try:
            import whois
            w = whois.whois(domain)

            if w:
                whois_data["registrar"] = w.get("registrar")
                whois_data["creation_date"] = str(w.get("creation_date"))
                whois_data["expiration_date"] = str(w.get("expiration_date"))
                whois_data["updated_date"] = str(w.get("updated_date"))
                whois_data["status"] = w.get("status", [])
                whois_data["dnssec"] = w.get("dnssec")
                whois_data["name_servers"] = w.get("name_servers", [])
                whois_data["emails"] = w.get("emails", [])

                if isinstance(w.get("registrant"), dict):
                    whois_data["registrant"] = {
                        "name": w["registrant"].get("name"),
                        "organization": w["registrant"].get("org"),
                        "country": w["registrant"].get("country"),
                    }
                else:
                    whois_data["registrant"] = w.get("registrant")

        except Exception as e:
            self._log_error(f"WHOIS lookup failed: {e}")
            whois_data["error"] = str(e)

        return self._format_result(True, whois_data)