"""Subdomain takeover detection module"""

import socket
from typing import Dict, List
from core.base import BaseModule
from core.utils import validate_domain
from core.exceptions import ValidationError


class TakeoverDetector(BaseModule):
    CNAME_MAPPINGS = {
        "github.io": "GitHub Pages",
        "herokuapp.com": "Heroku",
        "surge.sh": "Surge",
        "vercel.app": "Vercel",
        "netlify.app": "Netlify",
        "readme.io": "ReadMe",
        "ghost.io": "Ghost",
        "ghost.io": "Ghost",
        "wpengine.com": "WP Engine",
        "azurewebsites.net": "Azure",
        "cloudapp.net": "Azure",
        "cdn.azureedge.net": "Azure CDN",
        "s3.amazonaws.com": "AWS S3",
        "elasticbeanstalk.com": "AWS Elastic Beanstalk",
        "cloudfront.net": "AWS CloudFront",
        "fastly.net": "Fastly",
        " Tumblr": "Tumblr",
        "shopify.com": "Shopify",
        "bigcommerce.com": "BigCommerce",
        "wordpress.com": "WordPress",
        "kinsta.com": "Kinsta",
    }

    VULNERABLE_PATTERNS = [
        "does not exist",
        "not found",
        "no such host",
        "not configured",
        "default page",
        "placeholder",
        "under construction",
    ]

    def detect(self, domain: str) -> Dict:
        if not validate_domain(domain):
            raise ValidationError(f"Invalid domain: {domain}")

        self._log_info(f"Subdomain takeover detection for {domain}")

        results = {
            "domain": domain,
            "scan_results": [],
            "vulnerable": []
        }

        subdomains = self._get_subdomains(domain)

        for sub in subdomains:
            check = self._check_takeover(sub)
            results["scan_results"].append(check)
            if check.get("vulnerable"):
                results["vulnerable"].append(check)

        return self._format_result(True, results)

    def _get_subdomains(self, domain: str) -> List[str]:
        subdomains = set()
        try:
            import json
            response = self.http.get(f"https://crt.sh/?q=%25.{domain}&output=json")
            if response.status_code == 200:
                data = json.loads(response.text)
                for entry in data:
                    name = entry.get("name_value", "")
                    for sub in name.split("\n"):
                        if domain in sub and sub not in subdomains:
                            subdomains.add(sub.strip().lower())
        except:
            pass

        return list(subdomains)

    def _check_takeover(self, subdomain: str) -> Dict:
        result = {
            "subdomain": subdomain,
            "cname": None,
            "service": None,
            "vulnerable": False,
            "details": {}
        }

        try:
            import dns.resolver
            cname = dns.resolver.resolve(subdomain, "CNAME")
            cname_value = str(cname[0]).rstrip(".")

            result["cname"] = cname_value

            for provider, name in self.CNAME_MAPPINGS.items():
                if provider in cname_value:
                    result["service"] = name

                    is_vulnerable = self._detect_placeholder(subdomain, cname_value)
                    result["vulnerable"] = is_vulnerable
                    result["details"]["reason"] = "CNAME pointing to unclaimed service" if is_vulnerable else "Service appears to be properly configured"
                    break

        except dns.resolver.NXDOMAIN:
            result["details"]["error"] = "Domain does not exist"
        except dns.resolver.NoAnswer:
            result["details"]["error"] = "No CNAME record"
        except Exception as e:
            result["details"]["error"] = str(e)

        return result

    def _detect_placeholder(self, subdomain: str, cname: str) -> bool:
        try:
            import urllib.request
            url = f"http://{subdomain}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

            try:
                response = urllib.request.urlopen(req, timeout=5)
                body = response.read().decode("utf-8", errors="ignore").lower()

                for pattern in self.VULNERABLE_PATTERNS:
                    if pattern.lower() in body:
                        return True
            except:
                return False

        except:
            return False

        return False