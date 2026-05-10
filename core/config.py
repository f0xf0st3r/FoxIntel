"""FoxIntel configuration management"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json


@dataclass
class Config:
    debug: bool = False
    verbose: bool = False
    output_format: str = "json"
    output_file: Optional[str] = None
    api_keys: dict = field(default_factory=dict)
    rate_limit: int = 10
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = "FoxIntel/2.0"
    Tor_proxy: Optional[str] = None
    proxies: dict = field(default_factory=dict)

    @classmethod
    def from_args(cls, args) -> "Config":
        config = cls()
        config.debug = getattr(args, 'debug', False)
        config.verbose = getattr(args, 'verbose', False)
        config.output_format = getattr(args, 'output', 'json')
        config.output_file = getattr(args, 'output_file', None)
        config.rate_limit = getattr(args, 'rate_limit', 10)
        config.timeout = getattr(args, 'timeout', 30)
        config.max_retries = getattr(args, 'max_retries', 3)

        for key in ['shodan', 'virustotal', 'hunter', 'breachdirectory', 'grayhatwarfare']:
            env_key = f"FOXINTEL_{key.upper()}_API_KEY"
            if os.getenv(env_key):
                config.api_keys[key] = os.getenv(env_key)

        if getattr(args, 'tor', False):
            config.Tor_proxy = "socks5://127.0.0.1:9050"
            config.proxies = {
                'http': 'socks5://127.0.0.1:9050',
                'https': 'socks5://127.0.0.1:9050'
            }

        return config


class ConfigManager:
    def __init__(self, config_dir: Path = Path.home() / ".foxintel"):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"

    def load(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}

    def save(self, config: dict):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def set_api_key(self, service: str, key: str):
        config = self.load()
        config.setdefault('api_keys', {})[service] = key
        self.save(config)

    def get_api_key(self, service: str) -> Optional[str]:
        config = self.load()
        return config.get('api_keys', {}).get(service)