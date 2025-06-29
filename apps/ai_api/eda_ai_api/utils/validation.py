"""
Validation utilities for the AI API application.
Following the principle of input validation and security.
"""

import os
from pathlib import Path
from typing import Optional, List, Set
from fastapi import UploadFile

from eda_config.config import ConfigLoader
from eda_ai_api.utils.exceptions import (
    ValidationError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)

config = ConfigLoader.get_config()


def validate_file_size(
    file: UploadFile, max_size_bytes: Optional[int] = None
) -> None:
    """
    Validate file size against maximum allowed size.

    Args:
        file: Uploaded file to validate
        max_size_bytes: Maximum allowed file size in bytes (defaults to config)

    Raises:
        FileTooLargeError: If file size exceeds limit
    """
    if max_size_bytes is None:
        max_size_bytes = config.services.ai_api.max_file_size_mb * 1024 * 1024

    if file.size and file.size > max_size_bytes:
        max_size_mb = max_size_bytes // (1024 * 1024)
        raise FileTooLargeError(max_size_mb)


def validate_file_type(
    file: UploadFile,
    allowed_types: Optional[Set[str]] = None,
    file_category: str = "file",
) -> None:
    """
    Validate file type against allowed types.

    Args:
        file: Uploaded file to validate
        allowed_types: Set of allowed MIME types (defaults to config)
        file_category: Category name for error messages

    Raises:
        UnsupportedFileTypeError: If file type is not supported
    """
    if allowed_types is None:
        # Use appropriate allowed types based on file category
        if file_category == "image":
            allowed_types = set(config.services.ai_api.allowed_image_types)
        elif file_category == "audio":
            allowed_types = set(config.services.ai_api.allowed_audio_types)
        elif file_category == "document":
            allowed_types = set(config.services.ai_api.allowed_document_types)
        else:
            # Default to all allowed types
            allowed_types = (
                set(config.services.ai_api.allowed_image_types)
                | set(config.services.ai_api.allowed_audio_types)
                | set(config.services.ai_api.allowed_document_types)
            )

    if file.content_type not in allowed_types:
        raise UnsupportedFileTypeError(file.content_type, list(allowed_types))


def validate_image_file(file: UploadFile) -> None:
    """
    Validate image file upload.

    Args:
        file: Uploaded image file to validate

    Raises:
        FileTooLargeError: If file size exceeds limit
        UnsupportedFileTypeError: If file type is not supported
    """
    validate_file_size(file)
    validate_file_type(
        file, set(config.services.ai_api.allowed_image_types), "image"
    )


def validate_audio_file(file: UploadFile) -> None:
    """
    Validate audio file upload.

    Args:
        file: Uploaded audio file to validate

    Raises:
        FileTooLargeError: If file size exceeds limit
        UnsupportedFileTypeError: If file type is not supported
    """
    validate_file_size(file)

    # For audio files, be more lenient with MIME types
    # WhatsApp often sends audio as application/octet-stream
    allowed_types = set(config.services.ai_api.allowed_audio_types)

    # If the content type is not in our allowed list, check if it might be audio
    if file.content_type not in allowed_types:
        # Check if it's a generic binary type that might be audio
        if file.content_type in [
            "application/octet-stream",
            "binary/octet-stream",
        ]:
            # Allow these types but log a warning
            import logging

            logging.warning(
                f"Audio file with generic MIME type: {file.content_type}"
            )
            return

        # Check file extension as fallback
        if file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            audio_extensions = [".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".webm"]
            if ext in audio_extensions:
                return  # Allow based on file extension

        # If we get here, it's really not an audio file
        validate_file_type(file, allowed_types, "audio")


def validate_document_file(file: UploadFile) -> None:
    """
    Validate document file upload.

    Args:
        file: Uploaded document file to validate

    Raises:
        FileTooLargeError: If file size exceeds limit
        UnsupportedFileTypeError: If file type is not supported
    """
    validate_file_size(file)
    validate_file_type(
        file, set(config.services.ai_api.allowed_document_types), "document"
    )


def validate_filename(filename: str) -> None:
    """
    Validate filename for security and length.

    Args:
        filename: Filename to validate

    Raises:
        ValidationError: If filename is invalid
    """
    if not filename:
        raise ValidationError("Filename cannot be empty", "filename")

    if len(filename) > config.services.ai_api.max_filename_length:
        raise ValidationError(
            f"Filename too long. Maximum length is {config.services.ai_api.max_filename_length} characters",
            "filename",
        )

    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValidationError(
            "Invalid filename contains path traversal characters", "filename"
        )

    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in config.services.ai_api.allowed_file_extensions:
        raise ValidationError(
            f"File extension '{file_ext}' not allowed", "filename"
        )


def validate_platform(platform: str) -> None:
    """
    Validate platform identifier.

    Args:
        platform: Platform identifier to validate

    Raises:
        ValidationError: If platform is not supported
    """
    if platform not in config.services.ai_api.supported_platforms:
        raise ValidationError(
            f"Platform '{platform}' not supported. Supported platforms: {', '.join(config.services.ai_api.supported_platforms)}",
            "platform",
        )


def validate_session_id(session_id: str) -> None:
    """
    Validate session ID format and length.

    Args:
        session_id: Session ID to validate

    Raises:
        ValidationError: If session ID is invalid
    """
    if not session_id:
        raise ValidationError("Session ID cannot be empty", "session_id")

    if len(session_id) > 255:
        raise ValidationError("Session ID too long", "session_id")

    # Check for potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", "|", ";", "`"]
    for char in dangerous_chars:
        if char in session_id:
            raise ValidationError(
                f"Session ID contains invalid character: {char}", "session_id"
            )


def validate_text_input(
    text: str, max_length: int = 10000, field_name: str = "text"
) -> None:
    """
    Validate text input for length and content.

    Args:
        text: Text to validate
        max_length: Maximum allowed length
        field_name: Field name for error messages

    Raises:
        ValidationError: If text is invalid
    """
    if not text or not text.strip():
        raise ValidationError(f"{field_name} cannot be empty", field_name)

    if len(text) > max_length:
        raise ValidationError(
            f"{field_name} too long. Maximum length is {max_length} characters",
            field_name,
        )

    # Check for potentially dangerous content
    dangerous_patterns = [
        "<script",
        "javascript:",
        "data:text/html",
        "vbscript:",
        "onload=",
        "onerror=",
    ]
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            raise ValidationError(
                f"{field_name} contains potentially dangerous content",
                field_name,
            )


def validate_file_path(file_path: str) -> None:
    """
    Validate file path for security.

    Args:
        file_path: File path to validate

    Raises:
        ValidationError: If file path is invalid
    """
    if not file_path:
        raise ValidationError("File path cannot be empty", "file_path")

    # Check for path traversal attempts
    if ".." in file_path:
        raise ValidationError(
            "File path contains path traversal characters", "file_path"
        )

    # Ensure path is within allowed directory
    if not file_path.startswith(config.services.ai_api.temp_dir_prefix):
        raise ValidationError(
            f"File path must be within {config.services.ai_api.temp_dir_prefix} directory",
            "file_path",
        )

    # Check if file exists
    if not os.path.exists(file_path):
        raise ValidationError("File does not exist", "file_path")

    # Check if it's actually a file
    if not os.path.isfile(file_path):
        raise ValidationError("Path is not a file", "file_path")


def validate_tts_parameters(
    text: str,
    language_code: Optional[str] = None,
    voice_name: Optional[str] = None,
    pitch: Optional[float] = None,
    speaking_rate: Optional[float] = None,
) -> None:
    """
    Validate TTS parameters.

    Args:
        text: Text to convert to speech
        language_code: Language code
        voice_name: Voice name
        pitch: Pitch adjustment
        speaking_rate: Speaking rate adjustment

    Raises:
        ValidationError: If parameters are invalid
    """
    # Validate text
    validate_text_input(text, max_length=5000, field_name="text")

    # Validate language code
    if language_code and len(language_code) != 5:
        raise ValidationError(
            "Language code must be 5 characters (e.g., 'pt-BR', 'en-US')",
            "language_code",
        )

    # Validate pitch
    if pitch is not None and not (-20.0 <= pitch <= 20.0):
        raise ValidationError("Pitch must be between -20.0 and 20.0", "pitch")

    # Validate speaking rate
    if speaking_rate is not None and not (0.25 <= speaking_rate <= 4.0):
        raise ValidationError(
            "Speaking rate must be between 0.25 and 4.0", "speaking_rate"
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators and dangerous characters
    dangerous_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(" .")

    # Ensure filename is not too long
    if len(sanitized) > config.services.ai_api.max_filename_length:
        name, ext = os.path.splitext(sanitized)
        max_name_length = config.services.ai_api.max_filename_length - len(ext)
        sanitized = name[:max_name_length] + ext

    return sanitized or "unnamed_file"


def get_safe_temp_path(filename: str) -> str:
    """
    Get safe temporary file path.

    Args:
        filename: Original filename

    Returns:
        Safe temporary file path
    """
    sanitized_filename = sanitize_filename(filename)
    return os.path.join(
        config.services.ai_api.temp_dir_prefix, sanitized_filename
    )
