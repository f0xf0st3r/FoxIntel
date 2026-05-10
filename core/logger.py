"""FoxIntel logging system"""

import logging
import sys
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class LogEntry:
    timestamp: str
    level: str
    module: str
    message: str
    data: Optional[dict] = None


class FoxIntelLogger:
    def __init__(self, debug_mode: bool = False, output_format: str = "text"):
        self._debug = debug_mode
        self.format = output_format
        self.logger = logging.getLogger("foxintel")
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        self._setup_handlers()

    def _setup_handlers(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if self._debug else logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _format_json(self, level: str, module: str, message: str, data: dict = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "module": module,
            "message": message,
        }
        if data:
            entry["data"] = data
        return json.dumps(entry)

    def debug(self, message: str, module: str = "core", data: dict = None):
        if self._debug:
            self._log("DEBUG", module, message, data)

    def info(self, message: str, module: str = "core", data: dict = None):
        self._log("INFO", module, message, data)

    def warning(self, message: str, module: str = "core", data: dict = None):
        self._log("WARNING", module, message, data)

    def error(self, message: str, module: str = "core", data: dict = None):
        self._log("ERROR", module, message, data)

    def critical(self, message: str, module: str = "core", data: dict = None):
        self._log("CRITICAL", module, message, data)

    def _log(self, level: str, module: str, message: str, data: dict = None):
        if self.format == "json":
            print(self._format_json(level, module, message, data))
        else:
            self.logger.log(
                getattr(logging, level),
                f"[{module}] {message}"
            )


def setup_logger(debug: bool = False, format: str = "text") -> FoxIntelLogger:
    return FoxIntelLogger(debug_mode=debug, output_format=format)