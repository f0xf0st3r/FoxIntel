"""Base module class"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from core.config import Config
from core.logger import FoxIntelLogger
from core.utils import HTTPClient


class BaseModule(ABC):
    def __init__(self, config: Config, logger: FoxIntelLogger):
        self.config = config
        self.logger = logger
        self.http = HTTPClient(config, logger)

    def _format_result(self, success: bool, data: Any = None, error: str = None) -> Dict:
        result = {"success": success, "timestamp": self._get_timestamp()}
        if data is not None:
            result["data"] = data
        if error:
            result["error"] = error
        return result

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def _log_info(self, message: str):
        self.logger.info(message, module=self.__class__.__name__)

    def _log_error(self, message: str):
        self.logger.error(message, module=self.__class__.__name__)

    def _log_debug(self, message: str):
        self.logger.debug(message, module=self.__class__.__name__)