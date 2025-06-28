import os
import tempfile
from typing import Optional

from fastapi import UploadFile

from .audio_converter import convert_ogg
from .transcriber import transcribe_audio

ALLOWED_FORMATS = {
    "audio/mpeg": "mp3",
    "audio/mp4": "mp4",
    "audio/mpga": "mpga",
    "audio/wav": "wav",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "application/octet-stream": "ogg",  # WhatsApp often sends audio as octet-stream
}


def detect_content_type(file: UploadFile) -> Optional[str]:
    if hasattr(file, "content_type") and file.content_type:
        return file.content_type
    if hasattr(file, "mime_type") and file.mime_type:
        return file.mime_type
    ext = os.path.splitext(file.filename)[1].lower()
    return {
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".mpeg": "audio/mpeg",
        ".mpga": "audio/mpga",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
    }.get(ext)


def detect_audio_format_from_content(content: bytes) -> str:
    """
    Detect audio format from file content (magic bytes)
    """
    if len(content) < 4:
        return "ogg"  # Default to ogg for WhatsApp

    # Check for common audio format signatures
    if content[:4] == b"RIFF" and content[8:12] == b"WAVE":
        return "wav"
    elif content[:3] == b"ID3" or content[:2] == b"\xff\xfb":
        return "mp3"
    elif content[:4] == b"fLaC":
        return "flac"
    elif content[:4] == b"OggS":
        return "ogg"
    elif content[:4] == b"ftyp":
        return "mp4"
    else:
        # For WhatsApp audio, default to ogg since they typically send OGG Opus
        return "ogg"


async def process_audio_file(audio: UploadFile, language: str = "en") -> str:
    content_type = detect_content_type(audio)
    content = await audio.read()

    try:
        # Determine file format
        if content_type == "application/octet-stream":
            # WhatsApp sends audio as octet-stream, detect from content
            file_format = detect_audio_format_from_content(content)
        elif content_type is not None:
            file_format = ALLOWED_FORMATS.get(content_type, "ogg")
        else:
            # Fallback to content detection
            file_format = detect_audio_format_from_content(content)

        # Handle OGG format (common for WhatsApp)
        if file_format == "ogg" or content_type == "audio/ogg":
            audio_path = convert_ogg(content, output_format="mp3")
        else:
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_format}", delete=False
            ) as temp_file:
                temp_file.write(content)
                audio_path = temp_file.name

        return transcribe_audio(audio_path, language=language)
    finally:
        if "audio_path" in locals() and os.path.exists(audio_path):
            os.unlink(audio_path)
