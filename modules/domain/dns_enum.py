"""DNS enumeration module"""

import dns.resolver
import dns.query
import dns.zone
import socket
from typing import Dict, List
from core.base import BaseModule
from core.utils import validate_domain
from core.exceptions import ValidationError


class DNSEnumerator(BaseModule):
    def enumerate(self, domain: str, record_type: str = "A") -> Dict:
        if not validate_domain(domain):
            raise ValidationError(f"Invalid domain: {domain}")

        self._log_info(f"DNS enumeration for {domain} (type: {record_type})")

        results = {
            "domain": domain,
            "record_type": record_type,
            "records": [],
            "authoritative_nameservers": []
        }

        try:
            answers = dns.resolver.resolve(domain, record_type)
            results["records"] = [str(rdata) for rdata in answers]
        except dns.resolver.NoAnswer:
            results["records"] = []
        except dns.resolver.NXDOMAIN:
            raise ValidationError(f"Domain does not exist: {domain}")
        except Exception as e:
            self._log_error(f"DNS query failed: {e}")
            results["error"] = str(e)

        try:
            ns = dns.resolver.resolve(domain, "NS")
            results["authoritative_nameservers"] = [str(n) for n in ns]
        except:
            pass

        return self._format_result(True, results)

    def zone_transfer(self, domain: str) -> Dict:
        if not validate_domain(domain):
            raise ValidationError(f"Invalid domain: {domain}")

        self._log_info(f"Attempting zone transfer for {domain}")

        results = {
            "domain": domain,
            "zone_transferuccessful": False,
            "records": []
        }

        try:
            ns = dns.resolver.resolve(domain, "NS")
            nameserver = str(ns[0])

            try:
                zone = dns.zone.from_xfr(dns.query.xfr(nameserver, domain))
                results["zone_transfer_successful"] = True

                for name, node in zone.nodes.items():
                    for rdataset in node.rdatasets:
                        for rdata in rdataset:
                            results["records"].append({
                                "name": str(name),
                                "type": dns.rdatatype.to_text(rdataset.rdtype),
                                "value": str(rdata)
                            })
            except:
                results["error"] = "Zone transfer failed - server not vulnerable"

        except Exception as e:
            results["error"] = str(e)

        return self._format_result(True, results)