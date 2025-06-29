"""
Custom exceptions for the AI API application.
Following the principle of meaningful error handling.
"""

from typing import Optional, Dict, Any


class AIAPIException(Exception):
    """Base exception for AI API errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code


class ValidationError(AIAPIException):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {},
            status_code=400,
        )


class AuthenticationError(AIAPIException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message, error_code="AUTHENTICATION_ERROR", status_code=401
        )


class FileProcessingError(AIAPIException):
    """Raised when file processing fails"""

    def __init__(self, message: str, file_type: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="FILE_PROCESSING_ERROR",
            details={"file_type": file_type} if file_type else {},
            status_code=400,
        )


class FileTooLargeError(FileProcessingError):
    """Raised when uploaded file exceeds size limit"""

    def __init__(self, max_size_mb: int):
        super().__init__(
            message=f"File size exceeds maximum allowed size of {max_size_mb}MB",
            file_type="size_limit",
        )


class UnsupportedFileTypeError(FileProcessingError):
    """Raised when file type is not supported"""

    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            message=f"File type '{file_type}' not supported. Allowed types: {', '.join(allowed_types)}",
            file_type=file_type,
        )


class TTSGenerationError(AIAPIException):
    """Raised when TTS generation fails"""

    def __init__(self, message: str, text_length: Optional[int] = None):
        super().__init__(
            message=message,
            error_code="TTS_GENERATION_ERROR",
            details={"text_length": text_length} if text_length else {},
            status_code=500,
        )


class TranscriptionError(AIAPIException):
    """Raised when audio transcription fails"""

    def __init__(self, message: str, audio_format: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="TRANSCRIPTION_ERROR",
            details={"audio_format": audio_format} if audio_format else {},
            status_code=500,
        )


class MemoryError(AIAPIException):
    """Raised when memory operations fail"""

    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="MEMORY_ERROR",
            details={"operation": operation} if operation else {},
            status_code=500,
        )


class AgentError(AIAPIException):
    """Raised when agent operations fail"""

    def __init__(self, message: str, agent_type: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="AGENT_ERROR",
            details={"agent_type": agent_type} if agent_type else {},
            status_code=500,
        )


class RateLimitError(AIAPIException):
    """Raised when rate limit is exceeded"""

    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after} if retry_after else {},
            status_code=429,
        )


class ServiceUnavailableError(AIAPIException):
    """Raised when external service is unavailable"""

    def __init__(self, service_name: str, message: Optional[str] = None):
        super().__init__(
            message=message
            or f"Service '{service_name}' is temporarily unavailable",
            error_code="SERVICE_UNAVAILABLE",
            details={"service_name": service_name},
            status_code=503,
        )


class TimeoutError(AIAPIException):
    """Raised when operation times out"""

    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(
            message=f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            error_code="TIMEOUT_ERROR",
            details={
                "operation": operation,
                "timeout_seconds": timeout_seconds,
            },
            status_code=408,
        )
