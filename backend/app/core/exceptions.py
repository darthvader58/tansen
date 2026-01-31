"""
Custom exception classes.
"""
from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    """Error codes for API responses."""
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    TRANSCRIPTION_FAILED = "TRANSCRIPTION_FAILED"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    MAX_CONCURRENT_JOBS = "MAX_CONCURRENT_JOBS"
    INVALID_YOUTUBE_URL = "INVALID_YOUTUBE_URL"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    DOWNLOAD_LIMIT_EXCEEDED = "DOWNLOAD_LIMIT_EXCEEDED"
    INVALID_SCALE = "INVALID_SCALE"
    INVALID_INSTRUMENT = "INVALID_INSTRUMENT"


class APIError(Exception):
    """Base API error class."""
    
    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[dict] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code.value
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RateLimitError(APIError):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=429,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
        )


class AuthenticationError(APIError):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            error_code=ErrorCode.UNAUTHORIZED,
            message=message,
        )


class NotFoundError(APIError):
    """Resource not found error."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            status_code=404,
            error_code=ErrorCode.NOT_FOUND,
            message=message,
        )


class ValidationError(APIError):
    """Validation error."""
    
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.INVALID_FILE_FORMAT):
        super().__init__(
            status_code=400,
            error_code=error_code,
            message=message,
        )
