"""
Centralized error handling for the AI API application.
Following the principle of consistent error handling and logging.
"""

import traceback
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger

from eda_config.config import ConfigLoader
from eda_ai_api.utils.exceptions import AIAPIException

config = ConfigLoader.get_config()


async def handle_aiapi_exception(
    request: Request, exc: AIAPIException
) -> JSONResponse:
    """
    Handle custom AI API exceptions with structured error responses.

    Args:
        request: FastAPI request object
        exc: AI API exception

    Returns:
        JSONResponse with error details
    """
    error_response = {
        "success": False,
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
        "timestamp": request.headers.get("x-request-id", "unknown"),
    }

    # Log error with context
    logger.error(
        f"AI API Exception: {exc.error_code}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    return JSONResponse(status_code=exc.status_code, content=error_response)


async def handle_validation_error(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handle validation errors with detailed field information.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSONResponse with validation error details
    """
    error_response = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": {"errors": str(exc), "type": "validation_error"},
        },
        "timestamp": request.headers.get("x-request-id", "unknown"),
    }

    logger.warning(
        "Validation Error",
        extra={
            "error": str(exc),
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    return JSONResponse(status_code=400, content=error_response)


async def handle_generic_exception(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handle generic exceptions with safe error responses.

    Args:
        request: FastAPI request object
        exc: Generic exception

    Returns:
        JSONResponse with generic error details
    """
    # Get request ID for tracking
    request_id = request.headers.get("x-request-id", "unknown")

    # Log full error details
    logger.error(
        f"Unhandled Exception: {type(exc).__name__}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "request_id": request_id,
        },
    )

    # Return safe error response without exposing internal details
    error_response = {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": config.services.ai_api.error_messages[
                "SERVICE_UNAVAILABLE"
            ],
            "details": {"request_id": request_id, "type": "internal_error"},
        },
        "timestamp": request_id,
    }

    return JSONResponse(status_code=500, content=error_response)


def log_request_info(
    request: Request, response_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log request information for monitoring and debugging.

    Args:
        request: FastAPI request object
        response_data: Optional response data to log
    """
    log_data = {
        "path": request.url.path,
        "method": request.method,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_length": request.headers.get("content-length", "0"),
        "request_id": request.headers.get("x-request-id", "unknown"),
    }

    if response_data:
        log_data["response_success"] = response_data.get("success", False)
        log_data["response_length"] = len(str(response_data))

    logger.info("API Request", extra=log_data)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response structure.

    Args:
        error_code: Error code identifier
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        Standardized error response dictionary
    """
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
        },
        "status_code": status_code,
    }


def log_operation_error(
    operation: str, error: Exception, context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log operation errors with context for debugging.

    Args:
        operation: Name of the operation that failed
        error: Exception that occurred
        context: Additional context information
    """
    log_data = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }

    if context:
        log_data.update(context)

    logger.error(f"Operation Error: {operation}", extra=log_data)


def handle_file_processing_error(
    operation: str, file_info: Dict[str, Any], error: Exception
) -> Dict[str, Any]:
    """
    Handle file processing errors with detailed logging.

    Args:
        operation: File processing operation
        file_info: Information about the file being processed
        error: Exception that occurred

    Returns:
        Error response dictionary
    """
    log_operation_error(
        operation=operation,
        error=error,
        context={
            "file_info": file_info,
            "file_size": file_info.get("size", "unknown"),
            "file_type": file_info.get("content_type", "unknown"),
        },
    )

    return create_error_response(
        error_code="FILE_PROCESSING_ERROR",
        message=config.services.ai_api.error_messages["PROCESSING_ERROR"],
        details={
            "operation": operation,
            "file_type": file_info.get("content_type", "unknown"),
        },
    )


def handle_external_service_error(
    service_name: str, operation: str, error: Exception
) -> Dict[str, Any]:
    """
    Handle external service errors with retry information.

    Args:
        service_name: Name of the external service
        operation: Operation that failed
        error: Exception that occurred

    Returns:
        Error response dictionary
    """
    log_operation_error(
        operation=f"{service_name}_{operation}",
        error=error,
        context={
            "service_name": service_name,
            "operation": operation,
        },
    )

    return create_error_response(
        error_code="EXTERNAL_SERVICE_ERROR",
        message=f"Service '{service_name}' is temporarily unavailable",
        details={
            "service": service_name,
            "operation": operation,
            "retry_after": 60,  # Suggest retry after 1 minute
        },
    )
