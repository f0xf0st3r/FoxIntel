"""FoxIntel custom exceptions"""


class FoxIntelError(Exception):
    """Base exception for FoxIntel"""
    pass


class ConfigurationError(FoxIntelError):
    """Configuration related errors"""
    pass


class NetworkError(FoxIntelError):
    """Network related errors"""
    pass


class APIError(FoxIntelError):
    """API related errors"""
    def __init__(self, message: str, status_code: int = None, api_service: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.api_service = api_service


class RateLimitError(FoxIntelError):
    """Rate limit exceeded"""
    pass


class AuthenticationError(FoxIntelError):
    """Authentication failed"""
    pass


class ValidationError(FoxIntelError):
    """Input validation errors"""
    pass


class ScannerError(FoxIntelError):
    """Scanner/module errors"""
    pass


class ParseError(FoxIntelError):
    """Data parsing errors"""
    pass


class ResourceNotFoundError(FoxIntelError):
    """Resource not found"""
    pass


class TimeoutError(FoxIntelError):
    """Request timeout"""
    pass