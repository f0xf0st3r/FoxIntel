"""SSL/TLS certificate analysis module"""

import ssl
import socket
import json
from datetime import datetime
from typing import Dict, List
from core.base import BaseModule
from core.utils import validate_domain
from core.exceptions import ValidationError


class SSLAnalyzer(BaseModule):
    def analyze(self, domain: str) -> Dict:
        if not validate_domain(domain):
            raise ValidationError(f"Invalid domain: {domain}")

        self._log_info(f"SSL/TLS analysis for {domain}")

        results = {
            "domain": domain,
            "certificate": {},
            "cipher_suites": [],
            "vulnerabilities": [],
            "chain": []
        }

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert(binary_form=True)

                    results["certificate"] = {
                        "subject": dict(x[0] for x in ssock.getpeercert().get("subject", [])),
                        "issuer": dict(x[0] for x in ssock.getpeercert().get("issuer", [])),
                        "version": ssock.getpeercert().get("version"),
                        "serial_number": ssock.getpeercert().get("serialNumber"),
                        "not_before": ssock.getpeercert().get("notBefore"),
                        "not_after": ssock.getpeercert().get("notAfter"),
                        "san": ssock.getpeercert().get("subjectAltName", []),
                        "signature_algorithm": ssock.getpeercert().get("signatureAlgorithm"),
                        "key_size": self._get_key_size(cert)
                    }

                    results["cipher_suite"] = ssock.cipher()
                    results["protocol"] = ssock.version()

            results["vulnerabilities"] = self._check_vulnerabilities(domain)
            results["chain"] = self._get_cert_chain(domain)

        except Exception as e:
            results["error"] = str(e)

        return self._format_result(True, results)

    def _get_key_size(self, cert_bytes: bytes) -> int:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        try:
            cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
            key = cert.public_key()
            return key.key_size
        except:
            return None

    def _check_vulnerabilities(self, domain: str) -> List[Dict]:
        vulns = []

        checks = {
            "SSLv3": {"name": "POODLE", "cve": "CVE-2014-3566"},
            "TLSv1.0": {"name": "TLS 1.0 Deprecated", "cve": None},
            "TLSv1.1": {"name": "TLS 1.1 Deprecated", "cve": None},
        }

        try:
            for protocol in ["SSLv3", "TLSv1", "TLSv1.1"]:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.minimum_version = getattr(ssl.TLSVersion, protocol, None) or ssl.TLSVersion.TLSv1

                with socket.create_connection((domain, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        pass
        except ssl.SSLError as e:
            if "unsupported protocol" in str(e).lower():
                pass

        return vulns

    def _get_cert_chain(self, domain: str) -> List[Dict]:
        chain = []
        try:
            import subprocess
            result = subprocess.run(
                ["openssl", "s_client", "-showcerts", "-connect", f"{domain}:443"],
                capture_output=True, text=True, timeout=10
            )
            output = result.stdout

            certs = output.split("Certificate chain")[1] if "Certificate chain" in output else ""
            in_cert = False
            for line in certs.split("\n"):
                if "-----BEGIN CERTIFICATE-----" in line:
                    in_cert = True
                    cert_data = line
                elif "-----END CERTIFICATE-----" in line and in_cert:
                    cert_data += line
                    chain.append({"cert": cert_data})
                    in_cert = False
        except:
            pass

        return chain