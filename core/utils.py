"""Utility functions for requests with rate limiting and proxy support"""

import time
import requests
from typing import Optional, Dict
from core.exceptions import NetworkError, RateLimitError, TimeoutError as FoxTimeoutError


class HTTPClient:
    def __init__(self, config, logger, rate_limit: int = 10):
        self.config = config
        self.logger = logger
        self.rate_limit = rate_limit
        self.last_request = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })

    def _rate_limit(self):
        min_interval = 1.0 / self.rate_limit if self.rate_limit > 0 else 0
        elapsed = time.time() - self.last_request
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request = time.time()

    def get(self, url: str, params: dict = None, **kwargs) -> requests.Response:
        self._rate_limit()
        try:
            response = self.session.get(
                url, params=params, timeout=self.config.timeout,
                proxies=self.config.proxies, **kwargs
            )
            self._check_response(response)
            return response
        except requests.Timeout:
            raise FoxTimeoutError(f"Request timeout for {url}")
        except requests.RequestException as e:
            raise NetworkError(f"Request failed: {e}")

    def post(self, url: str, json: dict = None, data: dict = None, **kwargs) -> requests.Response:
        self._rate_limit()
        try:
            response = self.session.post(
                url, json=json, data=data, timeout=self.config.timeout,
                proxies=self.config.proxies, **kwargs
            )
            self._check_response(response)
            return response
        except requests.Timeout:
            raise FoxTimeoutError(f"Request timeout for {url}")
        except requests.RequestException as e:
            raise NetworkError(f"Request failed: {e}")

    def _check_response(self, response: requests.Response):
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        if response.status_code >= 400:
            raise NetworkError(f"HTTP {response.status_code}: {response.reason}")


def extract_domain(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc or parsed.path


def validate_domain(domain: str) -> bool:
    import re
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_ip(ip: str) -> bool:
    import re
    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    return bool(re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip))


def is_valid_mac(mac: str) -> bool:
    import re
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))


def format_output(data: dict, format: str) -> str:
    if format == "json":
        import json
        return json.dumps(data, indent=2, default=str)
    elif format == "yaml":
        import yaml
        return yaml.dump(data, default_flow_style=False)
    elif format == "csv":
        import csv
        import io
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if isinstance(data, list) else data.keys())
            writer.writeheader()
            writer.writerows(data if isinstance(data, list) else [data])
        return output.getvalue()
    return str(data)