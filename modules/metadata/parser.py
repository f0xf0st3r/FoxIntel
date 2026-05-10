"""URL metadata parser module"""

from typing import Dict
from urllib.parse import urlparse
from core.base import BaseModule
from core.exceptions import ValidationError


class URLMetadataParser(BaseModule):
    def parse(self, url: str) -> Dict:
        if not url:
            raise ValidationError("URL required")

        self._log_info(f"Parsing URL metadata: {url}")

        results = {
            "url": url,
            "parsed": {},
            "headers": {},
            "content_preview": {},
            "tech_stack": []
        }

        results["parsed"] = self._parse_url(url)
        results["headers"] = self._fetch_headers(url)
        results["content_preview"] = self._get_preview(url)
        results["tech_stack"] = self._detect_tech(url, results["headers"])

        return self._format_result(True, results)

    def _parse_url(self, url: str) -> Dict:
        try:
            parsed = urlparse(url)
            return {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "hostname": parsed.hostname,
                "port": parsed.port,
                "path": parsed.path,
                "params": parsed.params,
                "query": parsed.query,
                "fragment": parsed.fragment
            }
        except:
            return {}

    def _fetch_headers(self, url: str) -> Dict:
        headers = {}
        try:
            response = self.http.session.head(url, timeout=5, allow_redirects=True)
            for key, value in response.headers.items():
                if key.lower() in ["server", "content-type", "x-powered-by", "x-generator"]:
                    headers[key] = value
        except:
            pass
        return headers

    def _get_preview(self, url: str) -> Dict:
        preview = {}
        try:
            response = self.http.get(url)
            if response.status_code == 200:
                content = response.text[:5000]

                title_match = None
                for tag in ["<title>", "<h1>", "<meta name=\"title\">"]:
                    import re
                    pattern = f"{tag}(.*?)(</title>|</h1>|/>)"
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        title_match = match.group(1).strip()
                        break

                preview = {
                    "title": title_match,
                    "content_length": len(response.text),
                    "content_type": response.headers.get("content-type", "")
                }
        except:
            pass
        return preview

    def _detect_tech(self, url: str, headers: Dict) -> list:
        tech = []
        server = headers.get("server", "").lower()
        powered = headers.get("x-powered-by", "").lower()

        tech_map = {
            "nginx": "Nginx",
            "apache": "Apache",
            "cloudflare": "Cloudflare",
            "iis": "Microsoft IIS",
            "php": "PHP",
            "asp.net": "ASP.NET",
            "express": "Express.js",
            "django": "Django",
            "flask": "Flask",
            "wordpress": "WordPress",
            "wix": "Wix",
            "shopify": "Shopify"
        }

        for keyword, name in tech_map.items():
            if keyword in server or keyword in powered:
                tech.append(name)

        return list(set(tech))